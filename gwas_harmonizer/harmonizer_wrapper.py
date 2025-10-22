# #!/usr/bin/env python3
# import os
# import sys
# import argparse
# import subprocess
# import tempfile
# import shutil
# import json
# from pathlib import Path

# def resolve_path(path, base_dir=None):
#     """Resolve path relative to base directory"""
#     if base_dir is None:
#         base_dir = os.getcwd()
    
#     if not os.path.isabs(path):
#         path = os.path.join(base_dir, path)
    
#     return os.path.abspath(path)

# def to_gwas_ssf(input_file, output_dir, build):
#     """Convert input file to GWAS-SSF format"""
#     import pandas as pd
#     import gzip
#     import hashlib
    
#     # Read input file
#     if input_file.endswith('.gz'):
#         df = pd.read_csv(input_file, compression='gzip', sep='\t')
#     else:
#         df = pd.read_csv(input_file, sep='\t')
    
#     # Convert to lowercase for case-insensitive matching
#     df.columns = df.columns.str.lower()
    
#     # Map columns to GWAS-SSF format
#     output_data = []
    
#     for _, row in df.iterrows():
#         chrom = row.get('chr', row.get('chromosome', row.get('chrom', '')))
#         pos = row.get('bp', row.get('pos', row.get('position', '')))
#         ea = row.get('a1', row.get('effect_allele', row.get('allele1', '')))
#         oa = row.get('a2', row.get('other_allele', row.get('allele2', '')))
#         beta = row.get('beta', row.get('or', ''))  # Handle OR as beta for now
#         se = row.get('se', row.get('standard_error', row.get('stderr', '')))
#         pval = row.get('p', row.get('pval', row.get('p_value', '')))
#         eaf = row.get('eaf', row.get('effect_allele_frequency', row.get('frq', 'NA')))
#         rsid = row.get('rsid', row.get('snp', row.get('id', 'NA')))
        
#         output_data.append([chrom, pos, ea.upper() if pd.notna(ea) else '', 
#                           oa.upper() if pd.notna(oa) else '', beta, se, pval, eaf, rsid])
    
#     # Create output DataFrame
#     output_df = pd.DataFrame(output_data, columns=[
#         'chromosome', 'base_pair_location', 'effect_allele', 'other_allele',
#         'beta', 'standard_error', 'p_value', 'effect_allele_frequency', 'rsid'
#     ])
    
#     # Save to file
#     output_tsv = os.path.join(output_dir, 'converted_sumstats.tsv')
#     output_gz = output_tsv + '.gz'
    
#     output_df.to_csv(output_tsv, sep='\t', index=False)
    
#     # Compress
#     with open(output_tsv, 'rb') as f_in:
#         with gzip.open(output_gz, 'wb') as f_out:
#             shutil.copyfileobj(f_in, f_out)
    
#     # Calculate MD5
#     with open(output_gz, 'rb') as f:
#         md5 = hashlib.md5(f.read()).hexdigest()
    
#     # Create YAML metadata
#     yaml_content = f"""# Study meta-data
# date_metadata_last_modified: 2024-01-01

# # Genotyping Information
# genome_assembly: {build}
# coordinate_system: 1-based

# # Summary Statistic information
# data_file_name: {os.path.basename(output_gz)}
# file_type: GWAS-SSF v0.1
# data_file_md5sum: {md5}

# # Harmonization status
# is_harmonised: false
# is_sorted: false
# """
    
#     yaml_file = output_gz + '-meta.yaml'
#     with open(yaml_file, 'w') as f:
#         f.write(yaml_content)
    
#     return output_gz, yaml_file

# def chromlist_from_ssf(ssf_file):
#     """Extract chromosome list from SSF file"""
#     import gzip
#     import pandas as pd
    
#     # Read the SSF file
#     if ssf_file.endswith('.gz'):
#         df = pd.read_csv(ssf_file, compression='gzip', sep='\t')
#     else:
#         df = pd.read_csv(ssf_file, sep='\t')
    
#     # Get unique chromosomes
#     chromosomes = df['chromosome'].unique()
    
#     # Normalize chromosome names
#     normalized_chroms = []
#     for chrom in chromosomes:
#         chrom_str = str(chrom).upper()
#         if chrom_str.startswith('CHR'):
#             chrom_str = chrom_str[3:]
        
#         # Map numeric to canonical names
#         if chrom_str == '23': chrom_str = 'X'
#         elif chrom_str == '24': chrom_str = 'Y'
#         elif chrom_str == '26': chrom_str = 'MT'
        
#         normalized_chroms.append(chrom_str)
    
#     # Filter to allowed chromosomes and maintain order
#     allowed_chroms = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15',
#                      '16','17','18','19','20','21','22','X','Y','MT']
    
#     present_chroms = [c for c in allowed_chroms if c in normalized_chroms]
    
#     if not present_chroms:
#         # Fallback to all chromosomes if none detected
#         present_chroms = allowed_chroms
    
#     return ','.join(present_chroms)

# def main():
#     parser = argparse.ArgumentParser(description='GWAS Harmonizer Wrapper')
#     parser.add_argument('--input', required=True, help='Input GWAS summary statistics file')
#     parser.add_argument('--build', required=True, choices=['GRCh37', 'GRCh38'], help='Target genome build')
#     parser.add_argument('--threshold', type=float, default=0.99, help='Palindromic variants threshold')
#     parser.add_argument('--ref-dir', required=True, help='Reference data directory')
#     parser.add_argument('--code-repo', required=True, help='Path to harmonizer code repository')
    
#     args = parser.parse_args()
    
#     # Validate inputs
#     if not os.path.isfile(args.input):
#         sys.exit(f"Error: Input file not found: {args.input}")
    
#     if not os.path.isdir(args.ref_dir):
#         sys.exit(f"Error: Reference directory not found: {args.ref_dir}")
    
#     if not os.path.isdir(args.code_repo):
#         sys.exit(f"Error: Code repository not found: {args.code_repo}")
    
#     # Create working directory
#     work_dir = os.getcwd()
#     temp_dir = tempfile.mkdtemp(dir=work_dir)
    
#     try:
#         # Step 1: Convert to GWAS-SSF format
#         print("Converting input to GWAS-SSF format...")
#         ssf_file, yaml_file = to_gwas_ssf(args.input, temp_dir, args.build)
        
#         # Step 2: Extract chromosome list
#         print("Extracting chromosome list...")
#         chromlist = chromlist_from_ssf(ssf_file)
#         print(f"Chromosomes detected: {chromlist}")
        
#         # Step 3: Set up environment
#         env = os.environ.copy()
#         env['PATH'] = f"{args.code_repo}:{env['PATH']}"
        
#         # Step 4: Run Nextflow harmonization
#         print("Running harmonization...")
        
#         # Build Nextflow command
#         cmd = [
#             'nextflow', 'run', args.code_repo,
#             '-profile', 'standard',
#             '--harm',
#             '--ref', args.ref_dir,
#             '--file', ssf_file,
#             '--chromlist', chromlist,
#             '--to_build', '38' if args.build == 'GRCh38' else '37',
#             '--threshold', str(args.threshold),
#             '-with-report', 'harm_report.html',
#             '-with-timeline', 'harm_timeline.html',
#             '-with-trace', 'harm_trace.txt'
#         ]
        
#         # Run Nextflow
#         with open('harmonization_logs.txt', 'w') as log_file:
#             process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, 
#                                      stderr=subprocess.STDOUT, text=True)
            
#             for line in process.stdout:
#                 print(line, end='')
#                 log_file.write(line)
#                 log_file.flush()
            
#             return_code = process.wait()
        
#         if return_code != 0:
#             sys.exit(f"Harmonization failed with return code: {return_code}")
        
#         # Step 5: Collect outputs
#         # Look for harmonized output files
#         output_patterns = ['*harmonised*', '*final*', '*.tsv', '*.gz']
#         harmonized_files = []
        
#         for pattern in output_patterns:
#             for root, dirs, files in os.walk('.'):
#                 for file in files:
#                     if any(patt in file for patt in ['harmonised', 'final']):
#                         harmonized_files.append(os.path.join(root, file))
        
#         if harmonized_files:
#             # Use the first harmonized file found as output
#             shutil.copy2(harmonized_files[0], 'harmonized_output.tsv')
#         else:
#             # Create empty output if no harmonized file found
#             with open('harmonized_output.tsv', 'w') as f:
#                 f.write("# No harmonized output generated\n")
        
#         print("Harmonization completed successfully!")
        
#     except Exception as e:
#         sys.exit(f"Error during harmonization: {str(e)}")
#     finally:
#         # Clean up temporary directory
#         shutil.rmtree(temp_dir, ignore_errors=True)

# if __name__ == '__main__':
#     main()




# #!/usr/bin/env python3
# import os
# import sys
# import argparse
# import subprocess
# import tempfile
# import shutil
# import json
# import glob
# import gzip
# from pathlib import Path

# def resolve_path(path, base_dir=None):
#     """Resolve path relative to base directory"""
#     if base_dir is None:
#         base_dir = os.getcwd()
    
#     if not os.path.isabs(path):
#         path = os.path.join(base_dir, path)
    
#     return os.path.abspath(path)

# def to_gwas_ssf(input_file, output_dir, build):
#     """Convert input file to GWAS-SSF format"""
#     import pandas as pd
#     import gzip
#     import hashlib
    
#     # Read input file
#     if input_file.endswith('.gz'):
#         df = pd.read_csv(input_file, compression='gzip', sep='\t')
#     else:
#         df = pd.read_csv(input_file, sep='\t')
    
#     # Convert to lowercase for case-insensitive matching
#     df.columns = df.columns.str.lower()
    
#     # Map columns to GWAS-SSF format
#     output_data = []
    
#     for _, row in df.iterrows():
#         chrom = row.get('chr', row.get('chromosome', row.get('chrom', '')))
#         pos = row.get('bp', row.get('pos', row.get('position', '')))
#         ea = row.get('a1', row.get('effect_allele', row.get('allele1', '')))
#         oa = row.get('a2', row.get('other_allele', row.get('allele2', '')))
#         beta = row.get('beta', row.get('or', ''))  # Handle OR as beta for now
#         se = row.get('se', row.get('standard_error', row.get('stderr', '')))
#         pval = row.get('p', row.get('pval', row.get('p_value', '')))
#         eaf = row.get('eaf', row.get('effect_allele_frequency', row.get('frq', 'NA')))
#         rsid = row.get('rsid', row.get('snp', row.get('id', 'NA')))
        
#         output_data.append([chrom, pos, ea.upper() if pd.notna(ea) else '', 
#                           oa.upper() if pd.notna(oa) else '', beta, se, pval, eaf, rsid])
    
#     # Create output DataFrame
#     output_df = pd.DataFrame(output_data, columns=[
#         'chromosome', 'base_pair_location', 'effect_allele', 'other_allele',
#         'beta', 'standard_error', 'p_value', 'effect_allele_frequency', 'rsid'
#     ])
    
#     # Save to file
#     output_tsv = os.path.join(output_dir, 'converted_sumstats.tsv')
#     output_gz = output_tsv + '.gz'
    
#     output_df.to_csv(output_tsv, sep='\t', index=False)
    
#     # Compress
#     with open(output_tsv, 'rb') as f_in:
#         with gzip.open(output_gz, 'wb') as f_out:
#             shutil.copyfileobj(f_in, f_out)
    
#     # Calculate MD5
#     with open(output_gz, 'rb') as f:
#         md5 = hashlib.md5(f.read()).hexdigest()
    
#     # Create YAML metadata
#     yaml_content = f"""# Study meta-data
# date_metadata_last_modified: 2024-01-01

# # Genotyping Information
# genome_assembly: {build}
# coordinate_system: 1-based

# # Summary Statistic information
# data_file_name: {os.path.basename(output_gz)}
# file_type: GWAS-SSF v0.1
# data_file_md5sum: {md5}

# # Harmonization status
# is_harmonised: false
# is_sorted: false
# """
    
#     yaml_file = output_gz + '-meta.yaml'
#     with open(yaml_file, 'w') as f:
#         f.write(yaml_content)
    
#     return output_gz, yaml_file

# def chromlist_from_ssf(ssf_file):
#     """Extract chromosome list from SSF file"""
#     import gzip
#     import pandas as pd
    
#     # Read the SSF file
#     if ssf_file.endswith('.gz'):
#         df = pd.read_csv(ssf_file, compression='gzip', sep='\t')
#     else:
#         df = pd.read_csv(ssf_file, sep='\t')
    
#     # Get unique chromosomes
#     chromosomes = df['chromosome'].unique()
    
#     # Normalize chromosome names
#     normalized_chroms = []
#     for chrom in chromosomes:
#         chrom_str = str(chrom).upper()
#         if chrom_str.startswith('CHR'):
#             chrom_str = chrom_str[3:]
        
#         # Map numeric to canonical names
#         if chrom_str == '23': chrom_str = 'X'
#         elif chrom_str == '24': chrom_str = 'Y'
#         elif chrom_str == '26': chrom_str = 'MT'
        
#         normalized_chroms.append(chrom_str)
    
#     # Filter to allowed chromosomes and maintain order
#     allowed_chroms = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15',
#                      '16','17','18','19','20','21','22','X','Y','MT']
    
#     present_chroms = [c for c in allowed_chroms if c in normalized_chroms]
    
#     if not present_chroms:
#         # Fallback to all chromosomes if none detected
#         present_chroms = allowed_chroms
    
#     return ','.join(present_chroms)

# def main():
#     parser = argparse.ArgumentParser(description='GWAS Harmonizer Wrapper')
#     parser.add_argument('--input', required=True, help='Input GWAS summary statistics file')
#     parser.add_argument('--build', required=True, choices=['GRCh37', 'GRCh38'], help='Target genome build')
#     parser.add_argument('--threshold', type=float, default=0.99, help='Palindromic variants threshold')
#     parser.add_argument('--ref-dir', required=True, help='Reference data directory')
#     parser.add_argument('--code-repo', required=True, help='Path to harmonizer code repository')
    
#     args = parser.parse_args()
    
#     # Validate inputs
#     if not os.path.isfile(args.input):
#         sys.exit(f"Error: Input file not found: {args.input}")
    
#     if not os.path.isdir(args.ref_dir):
#         sys.exit(f"Error: Reference directory not found: {args.ref_dir}")
    
#     if not os.path.isdir(args.code_repo):
#         sys.exit(f"Error: Code repository not found: {args.code_repo}")
    
#     # Create working directory
#     work_dir = os.getcwd()
#     temp_dir = tempfile.mkdtemp(dir=work_dir)
    
#     try:
#         # Step 1: Convert to GWAS-SSF format
#         print("Converting input to GWAS-SSF format...")
#         ssf_file, yaml_file = to_gwas_ssf(args.input, temp_dir, args.build)
        
#         # Step 2: Extract chromosome list
#         print("Extracting chromosome list...")
#         chromlist = chromlist_from_ssf(ssf_file)
#         print(f"Chromosomes detected: {chromlist}")
        
#         # Step 3: Set up environment
#         env = os.environ.copy()
#         env['PATH'] = f"{args.code_repo}:{env['PATH']}"
        
#         # Step 4: Run Nextflow harmonization
#         print("Running harmonization...")
        
#         # Build Nextflow command
#         cmd = [
#             'nextflow', 'run', args.code_repo,
#             '-profile', 'standard',
#             '--harm',
#             '--ref', args.ref_dir,
#             '--file', ssf_file,
#             '--chromlist', chromlist,
#             '--to_build', '38' if args.build == 'GRCh38' else '37',
#             '--threshold', str(args.threshold),
#             '-with-report', 'harm_report.html',
#             '-with-timeline', 'harm_timeline.html',
#             '-with-trace', 'harm_trace.txt'
#         ]
        
#         # Run Nextflow
#         with open('harmonization_logs.txt', 'w') as log_file:
#             process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, 
#                                      stderr=subprocess.STDOUT, text=True)
            
#             for line in process.stdout:
#                 print(line, end='')
#                 log_file.write(line)
#                 log_file.flush()
            
#             return_code = process.wait()
        
#         if return_code != 0:
#             sys.exit(f"Harmonization failed with return code: {return_code}")
        
#         # Step 5: Collect outputs - FIXED VERSION
#         print("Collecting harmonized outputs...")
        
#         # Look for harmonized output files in the work directory
#         harmonized_files = []
#         for root, dirs, files in os.walk('.'):
#             for file in files:
#                 file_path = os.path.join(root, file)
#                 # Look for files with "harmonised" in name AND actual data content
#                 if any(pattern in file.lower() for pattern in ['harmonised', 'final']) and file.endswith(('.tsv', '.gz', '.tsv.gz')):
#                     # Check if file has actual data (not just headers)
#                     try:
#                         if file.endswith('.gz'):
#                             with gzip.open(file_path, 'rt') as f:
#                                 lines = sum(1 for _ in f)
#                         else:
#                             with open(file_path, 'r') as f:
#                                 lines = sum(1 for _ in f)
                        
#                         if lines > 1:  # Has data beyond header
#                             harmonized_files.append(file_path)
#                             print(f"Found harmonized file: {file_path} with {lines} lines")
#                     except:
#                         continue

#         # Also check the main output directory structure
#         output_dirs = ['results', 'output', 'final', 'harmonised']
#         for output_dir in output_dirs:
#             if os.path.exists(output_dir):
#                 for root, dirs, files in os.walk(output_dir):
#                     for file in files:
#                         if file.endswith(('.tsv', '.gz', '.tsv.gz')):
#                             harmonized_files.append(os.path.join(root, file))

#         # Look for Nextflow's output pattern (dated folders)
#         nextflow_outputs = glob.glob('20*')  # Pattern for dated folders
#         for nf_out in nextflow_outputs:
#             if os.path.isdir(nf_out):
#                 print(f"Checking Nextflow output directory: {nf_out}")
#                 for root, dirs, files in os.walk(nf_out):
#                     for file in files:
#                         if 'harmonised' in file.lower() and file.endswith(('.tsv', '.gz')):
#                             harmonized_files.append(os.path.join(root, file))

#         if harmonized_files:
#             # Use the largest file found (most likely the main output)
#             largest_file = max(harmonized_files, key=lambda x: os.path.getsize(x))
#             print(f"Using output file: {largest_file}")
            
#             # If it's gzipped, decompress it for Galaxy
#             if largest_file.endswith('.gz'):
#                 with gzip.open(largest_file, 'rt') as f_in:
#                     with open('harmonized_output.tsv', 'w') as f_out:
#                         shutil.copyfileobj(f_in, f_out)
#             else:
#                 shutil.copy2(largest_file, 'harmonized_output.tsv')
#         else:
#             # Create debug output to see what's available
#             print("No harmonized files found. Available files:")
#             for root, dirs, files in os.walk('.'):
#                 for file in files:
#                     if file.endswith(('.tsv', '.gz', '.parquet')):
#                         file_path = os.path.join(root, file)
#                         size = os.path.getsize(file_path)
#                         print(f"  {file_path} ({size} bytes)")
            
#             # Create empty output with error message
#             with open('harmonized_output.tsv', 'w') as f:
#                 f.write("# ERROR: No harmonized output generated\n")
#                 f.write("# The harmonizer ran but produced no output files\n")
#                 f.write("# Check the harmonization logs for details\n")
        
#         print("Harmonization completed successfully!")
        
#     except Exception as e:
#         sys.exit(f"Error during harmonization: {str(e)}")
#     finally:
#         # Clean up temporary directory
#         shutil.rmtree(temp_dir, ignore_errors=True)

# if __name__ == '__main__':
#     main()






#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import tempfile
import shutil
import json
import glob
import gzip
from pathlib import Path

def resolve_path(path, base_dir=None):
    """Resolve path relative to base directory"""
    if base_dir is None:
        base_dir = os.getcwd()
    
    if not os.path.isabs(path):
        path = os.path.join(base_dir, path)
    
    return os.path.abspath(path)

def setup_compatible_environment(temp_dir):
    """Create a temporary virtual environment with compatible dependencies"""
    venv_path = os.path.join(temp_dir, "harmonizer_venv")
    
    print(f"Setting up compatible environment in {venv_path}...")
    
    # Create virtual environment
    subprocess.run([sys.executable, "-m", "venv", venv_path], check=True, capture_output=True)
    
    # Get pip path
    if sys.platform == "win32":
        pip_path = os.path.join(venv_path, "Scripts", "pip")
        python_path = os.path.join(venv_path, "Scripts", "python")
    else:
        pip_path = os.path.join(venv_path, "bin", "pip")
        python_path = os.path.join(venv_path, "bin", "python")
    
    # Install compatible versions
    requirements = [
        "numpy>=1.21,<1.24",
        "pandas>=1.5,<2.0", 
        "pydantic>=1.10.4,<2.0.0",
        "ruamel.yaml==0.17.32"
    ]
    
    for req in requirements:
        print(f"Installing {req}...")
        result = subprocess.run([pip_path, "install", req], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Warning: Failed to install {req}: {result.stderr}")
    
    return venv_path, python_path

def patch_metadata_issue():
    """Patch the metadata issue by modifying the problematic file"""
    try:
        # Try to import to see if patching is needed
        from gwas_sumstats_tools.schema.metadata import SumStatsMetadata
        print("No patching needed - imports work correctly")
        return True
    except TypeError as e:
        if "constr() got an unexpected keyword argument 'regex'" in str(e):
            print("Patching metadata issue...")
            # Find the metadata.py file
            metadata_file = None
            for path in sys.path:
                potential_file = os.path.join(path, 'gwas_sumstats_tools', 'schema', 'metadata.py')
                if os.path.exists(potential_file):
                    metadata_file = potential_file
                    break
            
            if metadata_file:
                print(f"Found metadata file: {metadata_file}")
                # Create backup
                backup_file = metadata_file + '.backup'
                shutil.copy2(metadata_file, backup_file)
                
                # Read and patch
                with open(metadata_file, 'r') as f:
                    content = f.read()
                
                # Replace the problematic line
                if "constr(regex=r'^GCST\\d+$')" in content:
                    content = content.replace(
                        "gwas_id: Optional[constr(regex=r'^GCST\\d+$')] = None",
                        "gwas_id: Optional[str] = None  # Patched: removed regex for compatibility"
                    )
                    
                    with open(metadata_file, 'w') as f:
                        f.write(content)
                    print("Metadata file patched successfully")
                    
                    # Test if patch worked
                    try:
                        from gwas_sumstats_tools.schema.metadata import SumStatsMetadata
                        print("Patch successful - imports now work")
                        return True
                    except Exception as e2:
                        print(f"Patch failed: {e2}")
                        # Restore backup
                        shutil.copy2(backup_file, metadata_file)
                        return False
                else:
                    print("No need to patch - line already modified")
                    return True
            else:
                print("Could not find metadata.py to patch")
                return False
        else:
            print(f"Different error during import: {e}")
            return False
    except Exception as e:
        print(f"Unexpected error during import test: {e}")
        return False

def run_harmonizer_in_compatible_env(args, temp_dir):
    """Run the harmonizer in a compatible environment"""
    # First try to patch the current environment
    if patch_metadata_issue():
        print("Using patched current environment")
        return run_harmonizer_direct(args, temp_dir)
    else:
        print("Patching failed, setting up compatible environment...")
        # Set up compatible environment
        venv_path, python_path = setup_compatible_environment(temp_dir)
        
        try:
            # Run the harmonizer steps in the compatible environment
            harmonizer_script = f"""
import os
import sys
import subprocess
import tempfile

# Add code repo to path
sys.path.insert(0, '{args.code_repo}')

# Set up environment
env = os.environ.copy()
env['PATH'] = "{args.code_repo}:" + env['PATH']

# Build Nextflow command
cmd = [
    'nextflow', 'run', '{args.code_repo}',
    '-profile', 'standard',
    '--harm',
    '--ref', '{args.ref_dir}',
    '--file', '{args.ssf_file}',
    '--chromlist', '{args.chromlist}',
    '--to_build', '{args.to_build}',
    '--threshold', '{args.threshold}',
    '-with-report', 'harm_report.html',
    '-with-timeline', 'harm_timeline.html', 
    '-with-trace', 'harm_trace.txt'
]

# Run Nextflow
print("Running harmonization in compatible environment...")
process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, 
                         stderr=subprocess.STDOUT, text=True)

for line in process.stdout:
    print(line, end='')

return_code = process.wait()
sys.exit(return_code)
"""
            # Write the script to a temporary file
            script_file = os.path.join(temp_dir, "run_harmonizer.py")
            with open(script_file, 'w') as f:
                f.write(harmonizer_script)
            
            # Run the script in the compatible environment
            result = subprocess.run([python_path, script_file], capture_output=True, text=True)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
                
            return result.returncode
            
        finally:
            # Clean up the temporary environment
            shutil.rmtree(venv_path, ignore_errors=True)

def to_gwas_ssf(input_file, output_dir, build):
    """Convert input file to GWAS-SSF format"""
    # ... [Keep your existing to_gwas_ssf implementation unchanged] ...
    # [Your complete existing to_gwas_ssf function here]
    import pandas as pd
    import gzip
    import hashlib
    
    # DEBUG: Check the actual input file structure
    print(f"\n=== DEBUG: Analyzing input file ===")
    print(f"Input file: {input_file}")
    
    # Read first few lines to see the actual format
    with open(input_file, 'r') as f:
        lines = [next(f) for _ in range(5)]
    print("First 5 lines of input:")
    for i, line in enumerate(lines):
        print(f"Line {i+1}: {line.strip()}")
    
    # Try different separators
    separators = ['\t', ',', ' ', ';']
    df = None
    used_sep = None
    
    for sep in separators:
        try:
            if input_file.endswith('.gz'):
                df_test = pd.read_csv(input_file, compression='gzip', sep=sep, nrows=5, engine='python')
            else:
                df_test = pd.read_csv(input_file, sep=sep, nrows=5, engine='python')
            
            if len(df_test.columns) > 1:
                df = df_test
                used_sep = sep
                print(f"Detected separator: '{sep}' with {len(df.columns)} columns")
                print(f"Columns: {list(df.columns)}")
                break
        except Exception as e:
            continue
    
    if df is None:
        # Try with no header and tab separator (most common for GWAS)
        try:
            if input_file.endswith('.gz'):
                df = pd.read_csv(input_file, compression='gzip', sep='\t', header=None, nrows=5, engine='python')
            else:
                df = pd.read_csv(input_file, sep='\t', header=None, nrows=5, engine='python')
            print(f"No header detected. Using default column names")
            print(f"Columns: {list(df.columns)}")
            used_sep = '\t'
        except Exception as e:
            raise Exception(f"Cannot parse input file with any separator. Error: {e}")
    
    # Now read the full file with the detected separator
    try:
        if input_file.endswith('.gz'):
            df = pd.read_csv(input_file, compression='gzip', sep=used_sep, engine='python')
        else:
            df = pd.read_csv(input_file, sep=used_sep, engine='python')
    except Exception as e:
        raise Exception(f"Failed to read full file: {e}")
    
    print(f"Full dataset: {len(df)} rows, {len(df.columns)} columns")
    if len(df) > 0:
        print(f"Sample data:")
        print(df.head(3))
    
    # Convert to lowercase for case-insensitive matching
    original_columns = list(df.columns)
    df.columns = df.columns.str.lower()
    print(f"\nLowercase columns: {list(df.columns)}")
    
    # Check for variant column format (chrom:pos:ref:alt)
    variant_col = None
    for col in df.columns:
        if 'variant' in col:
            variant_col = col
            break
    
    if variant_col:
        print(f"Found variant column: {variant_col}")
        # Check if it's in chrom:pos:ref:alt format
        sample_variant = str(df[variant_col].iloc[0]) if len(df) > 0 else ""
        print(f"Sample variant: {sample_variant}")
        
        if ':' in sample_variant:
            print("Detected chrom:pos:ref:alt format in variant column")
            # Parse the variant column
            def parse_variant(variant_str):
                try:
                    parts = variant_str.split(':')
                    if len(parts) >= 4:
                        return parts[0], parts[1], parts[2], parts[3]  # chrom, pos, ref, alt
                    elif len(parts) >= 2:
                        return parts[0], parts[1], '', ''  # chrom, pos only
                    else:
                        return '', '', '', ''
                except:
                    return '', '', '', ''
            
            # Apply parsing
            parsed = df[variant_col].apply(parse_variant)
            df['chromosome'] = parsed.apply(lambda x: x[0])
            df['base_pair_location'] = parsed.apply(lambda x: x[1])
            df['ref_allele'] = parsed.apply(lambda x: x[2])
            df['alt_allele'] = parsed.apply(lambda x: x[3])
            
            print(f"Parsed variant column - Sample: {df[['chromosome', 'base_pair_location', 'ref_allele', 'alt_allele']].iloc[0].tolist()}")
            
            # Use parsed columns
            chrom_col = 'chromosome'
            pos_col = 'base_pair_location'
            # For allele columns, we need to determine which is effect allele
            # In your format, minor_allele is likely the effect allele
            ea_col = 'minor_allele'
            oa_col = None  # We'll determine this based on ref/alt
            
        else:
            raise Exception(f"Variant column exists but not in expected chrom:pos:ref:alt format. Found: {sample_variant}")
    else:
        # Original column detection logic for separate columns
        required_patterns = ['chr', 'pos', 'bp', 'allele', 'a1', 'a2']
        optional_patterns = ['beta', 'or', 'se', 'p', 'freq', 'rsid', 'snp', 'id']
        
        available_columns = list(df.columns)
        print(f"All available columns: {available_columns}")
        
        # Find best matches for required fields
        chrom_col = None
        pos_col = None
        ea_col = None
        oa_col = None
        
        # Look for chromosome column
        for pattern in ['chr', 'chrom', 'chromosome']:
            for col in available_columns:
                if pattern in col:
                    chrom_col = col
                    break
            if chrom_col:
                break
        
        # Look for position column
        for pattern in ['pos', 'bp', 'position']:
            for col in available_columns:
                if pattern in col:
                    pos_col = col
                    break
            if pos_col:
                break
        
        # Look for effect allele column
        for pattern in ['a1', 'effect_allele', 'allele1', 'ea']:
            for col in available_columns:
                if pattern in col:
                    ea_col = col
                    break
            if ea_col:
                break
        
        # Look for other allele column
        for pattern in ['a2', 'other_allele', 'allele2', 'oa']:
            for col in available_columns:
                if pattern in col:
                    oa_col = col
                    break
            if oa_col:
                break
    
    print(f"\nDetected columns:")
    print(f"  Chromosome: {chrom_col}")
    print(f"  Position: {pos_col}")
    print(f"  Effect allele: {ea_col}")
    print(f"  Other allele: {oa_col}")
    
    if not chrom_col or not pos_col:
        raise Exception(f"Missing required columns. Need chromosome and position. Found columns: {original_columns}")
    
    # Map columns to GWAS-SSF format
    output_data = []
    successful_rows = 0
    
    for idx, row in df.iterrows():
        try:
            chrom = str(row[chrom_col]) if pd.notna(row[chrom_col]) else ''
            pos = str(row[pos_col]) if pd.notna(row[pos_col]) else ''
            
            # Handle alleles based on format
            if variant_col and ':' in str(df[variant_col].iloc[0]):
                # For variant column format, we have ref and alt alleles
                ref_allele = str(row['ref_allele']) if 'ref_allele' in df.columns and pd.notna(row.get('ref_allele', '')) else ''
                alt_allele = str(row['alt_allele']) if 'alt_allele' in df.columns and pd.notna(row.get('alt_allele', '')) else ''
                minor_allele = str(row[ea_col]) if ea_col and pd.notna(row[ea_col]) else ''
                
                # Determine effect and other alleles
                # In UK Biobank format, minor_allele is the effect allele
                # The other allele is the one that's NOT the minor allele
                if minor_allele and ref_allele and alt_allele:
                    if minor_allele == ref_allele:
                        ea = ref_allele
                        oa = alt_allele
                    elif minor_allele == alt_allele:
                        ea = alt_allele
                        oa = ref_allele
                    else:
                        # If minor allele doesn't match ref/alt, use minor as effect
                        ea = minor_allele
                        oa = ref_allele  # default to ref as other
                else:
                    # Fallback: use minor_allele as effect, ref as other
                    ea = minor_allele
                    oa = ref_allele
                    
                # Ensure we have valid alleles
                if not ea or ea == 'nan' or len(ea) != 1:
                    continue
                if not oa or oa == 'nan' or len(oa) != 1:
                    continue
            else:
                # Standard separate column format
                ea = str(row[ea_col]).upper() if ea_col and pd.notna(row[ea_col]) else ''
                oa = str(row[oa_col]).upper() if oa_col and pd.notna(row[oa_col]) else ''
            
            # Skip rows with missing essential data
            if not chrom or not pos or not ea or not oa:
                continue
            
            # Handle optional columns - FIXED: Ensure numeric values
            beta_col = next((col for col in df.columns if any(p in col for p in ['beta', 'or'])), None)
            se_col = next((col for col in df.columns if any(p in col for p in ['se', 'standard_error', 'stderr'])), None)
            pval_col = next((col for col in df.columns if any(p in col for p in ['p', 'pval', 'p_value'])), None)
            eaf_col = next((col for col in df.columns if any(p in col for p in ['eaf', 'effect_allele_frequency', 'frq', 'freq', 'minor_af'])), None)
            rsid_col = next((col for col in df.columns if any(p in col for p in ['rsid', 'snp', 'id'])), None)
            
            # Ensure numeric values for beta, se, pval
            beta_val = ''
            if beta_col and pd.notna(row[beta_col]):
                try:
                    beta_val = str(float(row[beta_col]))
                except (ValueError, TypeError):
                    beta_val = ''  # Skip if not convertible to float
            
            se_val = ''
            if se_col and pd.notna(row[se_col]):
                try:
                    se_val = str(float(row[se_col]))
                except (ValueError, TypeError):
                    se_val = ''
            
            pval_val = ''
            if pval_col and pd.notna(row[pval_col]):
                try:
                    pval_val = str(float(row[pval_col]))
                except (ValueError, TypeError):
                    pval_val = ''
            
            eaf_val = 'NA'
            if eaf_col and pd.notna(row[eaf_col]):
                try:
                    eaf_val = str(float(row[eaf_col]))
                except (ValueError, TypeError):
                    eaf_val = 'NA'
            
            rsid_val = 'NA'
            if rsid_col and pd.notna(row[rsid_col]):
                rsid_val = str(row[rsid_col])
            
            # Skip rows with missing essential numeric data
            if not beta_val and not pval_val:
                continue
            
            output_data.append([chrom, pos, ea.upper(), oa.upper(), beta_val, se_val, pval_val, eaf_val, rsid_val])
            successful_rows += 1
            
        except Exception as e:
            if successful_rows < 5:  # Only show first few errors
                print(f"Warning: Skipping row {idx} due to error: {e}")
            continue
    
    print(f"Successfully processed {successful_rows} out of {len(df)} rows")
    
    if successful_rows == 0:
        raise Exception("No valid rows found in the input file. Check the data format.")
    
    # Create output DataFrame
    output_df = pd.DataFrame(output_data, columns=[
        'chromosome', 'base_pair_location', 'effect_allele', 'other_allele',
        'beta', 'standard_error', 'p_value', 'effect_allele_frequency', 'rsid'
    ])
    
    # DEBUG: Check the first few rows of output
    print(f"\nFirst 3 rows of converted data:")
    print(output_df.head(3))
    
    # Validate that no allele data ended up in numeric columns
    print(f"\nValidating converted data...")
    print(f"Beta column sample: {output_df['beta'].head(3).tolist()}")
    print(f"Effect allele sample: {output_df['effect_allele'].head(3).tolist()}")
    print(f"Other allele sample: {output_df['other_allele'].head(3).tolist()}")
    
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
    
    print(f"Successfully converted {successful_rows} variants to GWAS-SSF format")
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

def run_harmonizer_direct(args, temp_dir):
    """Run harmonizer directly (attempt in current environment)"""
    # Set up environment
    env = os.environ.copy()
    env['PATH'] = f"{args.code_repo}:{env['PATH']}"
    
    # Build Nextflow command
    cmd = [
        'nextflow', 'run', args.code_repo,
        '-profile', 'standard',
        '--harm',
        '--ref', args.ref_dir,
        '--file', args.ssf_file,
        '--chromlist', args.chromlist,
        '--to_build', args.to_build,
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
    
    return return_code

def collect_outputs():
    """Collect harmonized output files"""
    # Look for harmonized output files in the work directory
    harmonized_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            file_path = os.path.join(root, file)
            # Look for files with "harmonised" in name AND actual data content
            if any(pattern in file.lower() for pattern in ['harmonised', 'final']) and file.endswith(('.tsv', '.gz', '.tsv.gz')):
                # Check if file has actual data (not just headers)
                try:
                    if file.endswith('.gz'):
                        with gzip.open(file_path, 'rt') as f:
                            lines = sum(1 for _ in f)
                    else:
                        with open(file_path, 'r') as f:
                            lines = sum(1 for _ in f)
                    
                    if lines > 1:  # Has data beyond header
                        harmonized_files.append(file_path)
                        print(f"Found harmonized file: {file_path} with {lines} lines")
                except:
                    continue

    # Also check the main output directory structure
    output_dirs = ['results', 'output', 'final', 'harmonised']
    for output_dir in output_dirs:
        if os.path.exists(output_dir):
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(('.tsv', '.gz', '.tsv.gz')):
                        harmonized_files.append(os.path.join(root, file))

    # Look for Nextflow's output pattern (dated folders)
    nextflow_outputs = glob.glob('20*')  # Pattern for dated folders
    for nf_out in nextflow_outputs:
        if os.path.isdir(nf_out):
            print(f"Checking Nextflow output directory: {nf_out}")
            for root, dirs, files in os.walk(nf_out):
                for file in files:
                    if 'harmonised' in file.lower() and file.endswith(('.tsv', '.gz')):
                        harmonized_files.append(os.path.join(root, file))

    if harmonized_files:
        # Use the largest file found (most likely the main output)
        largest_file = max(harmonized_files, key=lambda x: os.path.getsize(x))
        print(f"Using output file: {largest_file}")
        
        # If it's gzipped, decompress it for Galaxy
        if largest_file.endswith('.gz'):
            with gzip.open(largest_file, 'rt') as f_in:
                with open('harmonized_output.tsv', 'w') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            shutil.copy2(largest_file, 'harmonized_output.tsv')
    else:
        # Create debug output to see what's available
        print("No harmonized files found. Available files:")
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.tsv', '.gz', '.parquet')):
                    file_path = os.path.join(root, file)
                    size = os.path.getsize(file_path)
                    print(f"  {file_path} ({size} bytes)")
        
        # Create empty output with error message
        with open('harmonized_output.tsv', 'w') as f:
            f.write("# ERROR: No harmonized output generated\n")
            f.write("# The harmonizer ran but produced no output files\n")
            f.write("# Check the harmonization logs for details\n")

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
        
        # Add derived arguments for subprocess
        args.ssf_file = ssf_file
        args.chromlist = chromlist
        args.to_build = '38' if args.build == 'GRCh38' else '37'
        
        # Step 3: Run harmonization with compatibility handling
        print("Running harmonization with compatibility handling...")
        
        return_code = run_harmonizer_in_compatible_env(args, temp_dir)
        
        if return_code != 0:
            sys.exit(f"Harmonization failed with return code: {return_code}")
        
        # Step 4: Collect outputs
        print("Collecting harmonized outputs...")
        collect_outputs()
        
        print("Harmonization completed successfully!")
        
    except Exception as e:
        sys.exit(f"Error during harmonization: {str(e)}")
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    main()