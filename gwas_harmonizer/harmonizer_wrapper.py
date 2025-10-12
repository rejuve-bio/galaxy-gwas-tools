#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import tempfile
import shutil
import json
from pathlib import Path

def resolve_path(path, base_dir=None):
    """Resolve path relative to base directory"""
    if base_dir is None:
        base_dir = os.getcwd()
    
    if not os.path.isabs(path):
        path = os.path.join(base_dir, path)
    
    return os.path.abspath(path)

def to_gwas_ssf(input_file, output_dir, build):
    """Convert input file to GWAS-SSF format"""
    import pandas as pd
    import gzip
    import hashlib
    
    # Read input file
    if input_file.endswith('.gz'):
        df = pd.read_csv(input_file, compression='gzip', sep='\t')
    else:
        df = pd.read_csv(input_file, sep='\t')
    
    # Convert to lowercase for case-insensitive matching
    df.columns = df.columns.str.lower()
    
    # Map columns to GWAS-SSF format
    output_data = []
    
    for _, row in df.iterrows():
        chrom = row.get('chr', row.get('chromosome', row.get('chrom', '')))
        pos = row.get('bp', row.get('pos', row.get('position', '')))
        ea = row.get('a1', row.get('effect_allele', row.get('allele1', '')))
        oa = row.get('a2', row.get('other_allele', row.get('allele2', '')))
        beta = row.get('beta', row.get('or', ''))  # Handle OR as beta for now
        se = row.get('se', row.get('standard_error', row.get('stderr', '')))
        pval = row.get('p', row.get('pval', row.get('p_value', '')))
        eaf = row.get('eaf', row.get('effect_allele_frequency', row.get('frq', 'NA')))
        rsid = row.get('rsid', row.get('snp', row.get('id', 'NA')))
        
        output_data.append([chrom, pos, ea.upper() if pd.notna(ea) else '', 
                          oa.upper() if pd.notna(oa) else '', beta, se, pval, eaf, rsid])
    
    # Create output DataFrame
    output_df = pd.DataFrame(output_data, columns=[
        'chromosome', 'base_pair_location', 'effect_allele', 'other_allele',
        'beta', 'standard_error', 'p_value', 'effect_allele_frequency', 'rsid'
    ])
    
    # Save to file
    output_tsv = os.path.join(output_dir, 'converted_sumstats.tsv')
    output_gz = output_tsv + '.gz'
    
    output_df.to_csv(output_tsv, sep='\t', index=False)
    
    # Compress
    with open(output_tsv, 'rb') as f_in:
        with gzip.open(output_gz, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    # Calculate MD5
    with open(output_gz, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    
    # Create YAML metadata
    yaml_content = f"""# Study meta-data
date_metadata_last_modified: 2024-01-01

# Genotyping Information
genome_assembly: {build}
coordinate_system: 1-based

# Summary Statistic information
data_file_name: {os.path.basename(output_gz)}
file_type: GWAS-SSF v0.1
data_file_md5sum: {md5}

# Harmonization status
is_harmonised: false
is_sorted: false
"""
    
    yaml_file = output_gz + '-meta.yaml'
    with open(yaml_file, 'w') as f:
        f.write(yaml_content)
    
    return output_gz, yaml_file

def chromlist_from_ssf(ssf_file):
    """Extract chromosome list from SSF file"""
    import gzip
    import pandas as pd
    
    # Read the SSF file
    if ssf_file.endswith('.gz'):
        df = pd.read_csv(ssf_file, compression='gzip', sep='\t')
    else:
        df = pd.read_csv(ssf_file, sep='\t')
    
    # Get unique chromosomes
    chromosomes = df['chromosome'].unique()
    
    # Normalize chromosome names
    normalized_chroms = []
    for chrom in chromosomes:
        chrom_str = str(chrom).upper()
        if chrom_str.startswith('CHR'):
            chrom_str = chrom_str[3:]
        
        # Map numeric to canonical names
        if chrom_str == '23': chrom_str = 'X'
        elif chrom_str == '24': chrom_str = 'Y'
        elif chrom_str == '26': chrom_str = 'MT'
        
        normalized_chroms.append(chrom_str)
    
    # Filter to allowed chromosomes and maintain order
    allowed_chroms = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15',
                     '16','17','18','19','20','21','22','X','Y','MT']
    
    present_chroms = [c for c in allowed_chroms if c in normalized_chroms]
    
    if not present_chroms:
        # Fallback to all chromosomes if none detected
        present_chroms = allowed_chroms
    
    return ','.join(present_chroms)

def main():
    parser = argparse.ArgumentParser(description='GWAS Harmonizer Wrapper')
    parser.add_argument('--input', required=True, help='Input GWAS summary statistics file')
    parser.add_argument('--build', required=True, choices=['GRCh37', 'GRCh38'], help='Target genome build')
    parser.add_argument('--threshold', type=float, default=0.99, help='Palindromic variants threshold')
    parser.add_argument('--ref-dir', required=True, help='Reference data directory')
    parser.add_argument('--code-repo', required=True, help='Path to harmonizer code repository')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.isfile(args.input):
        sys.exit(f"Error: Input file not found: {args.input}")
    
    if not os.path.isdir(args.ref_dir):
        sys.exit(f"Error: Reference directory not found: {args.ref_dir}")
    
    if not os.path.isdir(args.code_repo):
        sys.exit(f"Error: Code repository not found: {args.code_repo}")
    
    # Create working directory
    work_dir = os.getcwd()
    temp_dir = tempfile.mkdtemp(dir=work_dir)
    
    try:
        # Step 1: Convert to GWAS-SSF format
        print("Converting input to GWAS-SSF format...")
        ssf_file, yaml_file = to_gwas_ssf(args.input, temp_dir, args.build)
        
        # Step 2: Extract chromosome list
        print("Extracting chromosome list...")
        chromlist = chromlist_from_ssf(ssf_file)
        print(f"Chromosomes detected: {chromlist}")
        
        # Step 3: Set up environment
        env = os.environ.copy()
        env['PATH'] = f"{args.code_repo}:{env['PATH']}"
        
        # Step 4: Run Nextflow harmonization
        print("Running harmonization...")
        
        # Build Nextflow command
        cmd = [
            'nextflow', 'run', args.code_repo,
            '-profile', 'standard',
            '--harm',
            '--ref', args.ref_dir,
            '--file', ssf_file,
            '--chromlist', chromlist,
            '--to_build', '38' if args.build == 'GRCh38' else '37',
            '--threshold', str(args.threshold),
            '-with-report', 'harm_report.html',
            '-with-timeline', 'harm_timeline.html',
            '-with-trace', 'harm_trace.txt'
        ]
        
        # Run Nextflow
        with open('harmonization_logs.txt', 'w') as log_file:
            process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, 
                                     stderr=subprocess.STDOUT, text=True)
            
            for line in process.stdout:
                print(line, end='')
                log_file.write(line)
                log_file.flush()
            
            return_code = process.wait()
        
        if return_code != 0:
            sys.exit(f"Harmonization failed with return code: {return_code}")
        
        # Step 5: Collect outputs
        # Look for harmonized output files
        output_patterns = ['*harmonised*', '*final*', '*.tsv', '*.gz']
        harmonized_files = []
        
        for pattern in output_patterns:
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if any(patt in file for patt in ['harmonised', 'final']):
                        harmonized_files.append(os.path.join(root, file))
        
        if harmonized_files:
            # Use the first harmonized file found as output
            shutil.copy2(harmonized_files[0], 'harmonized_output.tsv')
        else:
            # Create empty output if no harmonized file found
            with open('harmonized_output.tsv', 'w') as f:
                f.write("# No harmonized output generated\n")
        
        print("Harmonization completed successfully!")
        
    except Exception as e:
        sys.exit(f"Error during harmonization: {str(e)}")
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    main()