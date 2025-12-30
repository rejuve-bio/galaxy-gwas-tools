#!/usr/bin/env python3
import sys
import os
import gzip
import argparse
import subprocess
from datetime import datetime
import hashlib

def main():
    parser = argparse.ArgumentParser(description='Convert GWAS summary statistics to SSF format')
    parser.add_argument('--input', required=True, help='Input GWAS file')
    parser.add_argument('--build', required=True, choices=['GRCh37', 'GRCh38'], help='Genome build')
    parser.add_argument('--coord', required=True, choices=['1-based', '0-based'], help='Coordinate system')
    parser.add_argument('--output_ssf', required=True, help='Output SSF file')
    parser.add_argument('--output_yaml', required=True, help='Output YAML file')
    parser.add_argument('--output_chromosomes', required=True, help='Output chromosome list')
    
    args = parser.parse_args()
    
    # Determine if input is compressed
    is_compressed = args.input.endswith('.gz') or args.input.endswith('.bgz')
    
    # Read and process the file
    try:
        if is_compressed:
            with gzip.open(args.input, 'rt') as f:
                process_file(f, args)
        else:
            with open(args.input, 'r') as f:
                process_file(f, args)
    except Exception as e:
        sys.stderr.write(f"ERROR: Failed to process file: {str(e)}\n")
        sys.exit(1)

def process_file(file_handle, args):
    """Process the GWAS file and convert to SSF format"""
    
    # Read header
    header_line = file_handle.readline().strip()
    header = header_line.split('\t')
    header_lower = [col.lower() for col in header]
    
    # Create column mapping
    col_map = {}
    for i, col in enumerate(header_lower):
        col_map[col] = i
    
    # Detect format
    is_neale = ('variant' in col_map and 
                ('beta' in col_map or 'or' in col_map) and 
                ('se' in col_map or 'stderr' in col_map or 'standard_error' in col_map) and 
                ('pval' in col_map or 'p' in col_map))
    
    is_plink = ((('chr' in col_map or 'chrom' in col_map) and 
                ('bp' in col_map or 'pos' in col_map) and 
                'a1' in col_map and 'a2' in col_map and 
                ('beta' in col_map or 'or' in col_map) and 
                ('se' in col_map or 'stderr' in col_map or 'standard_error' in col_map) and 
                ('p' in col_map or 'pval' in col_map)))
    
    if not is_neale and not is_plink:
        sys.stderr.write("ERROR: unknown layout - cannot detect Neale or PLINK format\n")
        sys.stderr.write(f"Available columns: {', '.join(header_lower)}\n")
        sys.exit(1)
    
    print(f"Detected format: {'Neale' if is_neale else 'PLINK'}")
    
    # Process data and write to temporary file
    temp_tsv = "temp_output.tsv"
    chromosomes_found = set()
    
    with open(temp_tsv, 'w') as out_file:
        # Write SSF header
        out_file.write("chromosome\tbase_pair_location\teffect_allele\tother_allele\tbeta\tstandard_error\tp_value\teffect_allele_frequency\trsid\n")
        
        line_count = 0
        for line in file_handle:
            fields = line.strip().split('\t')
            
            chrom, pos, ea, oa, beta, se, p, eaf, rsid = extract_fields(fields, col_map, is_neale)
            
            # Normalize chromosome
            chrom = normalize_chromosome(chrom)
            
            # Skip X, Y, MT chromosomes
            if chrom in ['X', 'Y', 'MT']:
                continue
            
            # Track chromosomes
            if chrom:
                chromosomes_found.add(chrom)
            
            # Write to output
            out_file.write(f"{chrom}\t{pos}\t{ea}\t{oa}\t{beta}\t{se}\t{p}\t{eaf}\t{rsid}\n")
            line_count += 1
    
    print(f"Processed {line_count} variants")
    
    if line_count == 0:
        sys.stderr.write("ERROR: No variants processed after filtering\n")
        sys.exit(1)
    
    # Compress the output
    compress_output(temp_tsv, args.output_ssf)
    
    # Create YAML metadata
    create_yaml_metadata(args.output_ssf, args.build, args.coord, args.output_yaml)
    
    # Create chromosome list
    create_chromosome_list(chromosomes_found, args.output_chromosomes)
    
    # Clean up
    if os.path.exists(temp_tsv):
        os.remove(temp_tsv)

def extract_fields(fields, col_map, is_neale):
    """Extract fields based on detected format"""
    chrom = ''; pos = ''; ea = ''; oa = ''; beta = ''; se = ''; p = ''; eaf = ''; rsid = ''
    
    try:
        if is_neale:
            if 'variant' in col_map:
                variant_parts = fields[col_map['variant']].split(':')
                if len(variant_parts) >= 4:
                    chrom = variant_parts[0]
                    pos = variant_parts[1]
                    oa = variant_parts[2]
                    ea = variant_parts[3]
            
            beta = get_field(fields, col_map, ['beta', 'or'])
            se = get_field(fields, col_map, ['se', 'stderr', 'standard_error'])
            p = get_field(fields, col_map, ['pval', 'p'])
            eaf = get_field(fields, col_map, ['af', 'minor_af', 'effect_allele_frequency'])
            rsid = get_field(fields, col_map, ['rsid', 'snp'])
            
        else:  # PLINK format
            chrom = get_field(fields, col_map, ['chr', 'chrom'])
            pos = get_field(fields, col_map, ['bp', 'pos'])
            ea = get_field(fields, col_map, ['a1'])
            oa = get_field(fields, col_map, ['a2'])
            beta = get_field(fields, col_map, ['beta', 'or'])
            se = get_field(fields, col_map, ['se', 'stderr', 'standard_error'])
            p = get_field(fields, col_map, ['p', 'pval'])
            eaf = get_field(fields, col_map, ['a1_freq', 'frq', 'effect_allele_frequency'])
            rsid = get_field(fields, col_map, ['id', 'snp', 'rsid'])
        
        # Convert to uppercase and handle missing values
        ea = ea.upper() if ea else 'NA'
        oa = oa.upper() if oa else 'NA'
        eaf = eaf if eaf else 'NA'
        rsid = rsid if rsid else 'NA'
        
    except Exception as e:
        sys.stderr.write(f"Warning: Error extracting fields: {str(e)}\n")
    
    return chrom, pos, ea, oa, beta, se, p, eaf, rsid

def get_field(fields, col_map, possible_names):
    """Get field value using possible column names"""
    for name in possible_names:
        if name in col_map:
            value = fields[col_map[name]]
            if value and value != 'NA':
                return value
    return ''

def normalize_chromosome(chrom):
    """Normalize chromosome naming"""
    if not chrom:
        return ''
    
    # Remove 'chr' prefix
    if chrom.startswith('chr'):
        chrom = chrom[3:]
    
    # Convert numeric codes
    if chrom == '23':
        chrom = 'X'
    elif chrom == '24':
        chrom = 'Y'
    elif chrom == '26':
        chrom = 'MT'
    
    return chrom

def compress_output(input_tsv, output_gz):
    """Compress TSV file and create tabix index"""
    # Compress with bgzip
    subprocess.run(['bgzip', '-f', input_tsv], check=True)
    
    # Rename to desired output name
    temp_gz = input_tsv + '.gz'
    if os.path.exists(temp_gz):
        os.rename(temp_gz, output_gz)
    
    # Create tabix index
    try:
        subprocess.run(['tabix', '-c', 'N', '-S', '1', '-s', '1', '-b', '2', '-e', '2', output_gz], 
                      check=True, stderr=subprocess.DEVNULL)
    except:
        pass  # Ignore tabix errors as in original script

def create_yaml_metadata(ssf_file, build, coord, yaml_file):
    """Create YAML metadata file"""
    # Calculate MD5
    with open(ssf_file, 'rb') as f:
        md5_hash = hashlib.md5(f.read()).hexdigest()
    
    build_num = '37' if build == 'GRCh37' else '38'
    
    with open(yaml_file, 'w') as f:
        f.write(f"""# Study meta-data
date_metadata_last_modified: {datetime.now().strftime('%Y-%m-%d')}

# Genotyping Information
genome_assembly: GRCh{build_num}
coordinate_system: {coord}

# Summary Statistic information
data_file_name: {os.path.basename(ssf_file)}
file_type: GWAS-SSF v0.1
data_file_md5sum: {md5_hash}

# Harmonization status
is_harmonised: false
is_sorted: false
""")

def create_chromosome_list(chromosomes_found, output_file):
    """Create ordered chromosome list"""
    order = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','X','Y','MT']
    
    # Filter to only include chromosomes that were found
    have = [ch for ch in order if ch in chromosomes_found]
    
    # If none found, use full list
    if not have:
        have = order
    
    with open(output_file, 'w') as f:
        f.write(','.join(have))

if __name__ == '__main__':
    main()