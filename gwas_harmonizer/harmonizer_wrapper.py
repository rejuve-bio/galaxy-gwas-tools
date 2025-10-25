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










# #!/usr/bin/env python3
# import os
# import sys
# import argparse
# import subprocess
# import tempfile
# import shutil

# def main():
#     parser = argparse.ArgumentParser(description='GWAS Harmonizer Wrapper - Calls original bash script')
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
    
#     # Create a temporary bash script that replicates your working harmonizer.sh
#     bash_script = f'''#!/bin/bash
# set -euo pipefail

# # Set variables from Python arguments
# SUMSTATS="{args.input}"
# BUILD="{args.build}"
# THRESHOLD="{args.threshold}"
# REF_DIR="{args.ref_dir}"
# CODE_REPO="{args.code_repo}"
# BASEDIR="$(pwd -P)"

# # Your original resolve_path function
# resolve_path() {{
#   local p="$1"
#   case "$p" in
#     /*) : ;;
#     ~*) p="${{p/#\\~/$HOME}}";;
#     *)  p="${{BASEDIR%/}}/$p";;
#   esac
#   if command -v realpath >/dev/null 2>&1; then
#     realpath -m -- "$p"
#   elif command -v python3 >/dev/null 2>&1; then
#     python3 - "$p" <<'PY'
# import os, sys
# print(os.path.abspath(sys.argv[1]))
# PY
#   else
#     printf '%s\\n' "$p"
#   fi
# }}

# # Your original to_gwas_ssf function
# to_gwas_ssf() {{
#   set -euo pipefail
#   : "${{SUMSTATS:?Set SUMSTATS to the input sumstats path}}"
#   BUILD="${{BUILD:-GRCh37}}"
#   COORD="${{COORD:-1-based}}"

#   SRC="$(resolve_path "$SUMSTATS")"

#   # Output dir
#   OUT_DIR="$(dirname -- "$SRC")"
#   mkdir -p "$OUT_DIR"

#   # Normalize stem name
#   _stem_from_name() {{
#     local n="$1"
#     n="${{n##*/}}"
#     n="${{n%.tsv.gz}}"
#     n="${{n%.tsv.bgz}}"
#     n="${{n%.bgz}}"
#     n="${{n%.gz}}"
#     n="${{n%.tsv}}"
#     echo "$n"
#   }}

#   STEM="$(_stem_from_name "$SRC")"

#   OUT_TSV="${{OUT_DIR%/}}/${{STEM}}.tsv"
#   OUT_GZ="${{OUT_TSV}}.gz"
#   OUT_YAML="${{OUT_GZ}}-meta.yaml"

#   # Reader based on extension
#   READER="cat"
#   case "$SRC" in *.gz|*.bgz) READER="bgzip -dc";; esac

#   # Build GWAS-SSF - using your exact awk logic
#   $READER "$SRC" | awk -v OFS="\\t" '
#     BEGIN{{ print "chromosome\\tbase_pair_location\\teffect_allele\\tother_allele\\tbeta\\tstandard_error\\tp_value\\teffect_allele_frequency\\trsid" }}
#     NR==1{{
#       for(i=1;i<=NF;i++) h[tolower($i)]=i
#       is_neale = h["variant"] && (h["beta"]||h["or"]) && (h["se"]||h["stderr"]||h["standard_error"]) && (h["pval"]||h["p"])
#       if(!is_neale){{ print "ERROR: unknown layout" > "/dev/stderr"; exit 2 }}
#       next
#     }}
#     {{
#       chrom=""; pos=""; ea=""; oa=""; beta=""; se=""; p=""; eaf=""; rsid=""
#       if(is_neale){{
#         split($h["variant"], v, ":"); chrom=v[1]; pos=v[2]; oa=v[3]; ea=v[4]
#         if(h["beta"]) beta=$h["beta"]
#         if(h["se"]) se=$h["se"]; else if(h["stderr"]) se=$h["stderr"]; else if(h["standard_error"]) se=$h["standard_error"]
#         if(h["pval"]) p=$h["pval"]; else if(h["p"]) p=$h["p"]
#         if(h["minor_af"]) eaf=$h["minor_af"]
#         rsid="NA"
#       }}
#       if(eaf=="") eaf="NA"; if(rsid=="") rsid="NA"
#       print chrom, pos, toupper(ea), toupper(oa), beta, se, p, eaf, rsid
#     }}
#   ' > "$OUT_TSV"

#   # Compress and index
#   bgzip -f "$OUT_TSV"
#   tabix -c N -S 1 -s 1 -b 2 -e 2 "$OUT_GZ" 2>/dev/null || true

#   # Compute md5
#   MD5="$(md5sum < "$OUT_GZ" | awk '{{print $1}}')"

#   # Sidecar YAML
#   cat > "$OUT_YAML" <<YAML
# # Study meta-data
# date_metadata_last_modified: $(date +%F)

# # Genotyping Information
# genome_assembly: GRCh${{BUILD}}
# coordinate_system: ${{COORD}}

# # Summary Statistic information
# data_file_name: $(basename "$OUT_GZ")
# file_type: GWAS-SSF v0.1
# data_file_md5sum: ${{MD5}}

# # Harmonization status
# is_harmonised: false
# is_sorted: false
# YAML

#   echo "$OUT_GZ"
# }}

# # Your original chromlist_from_ssf function
# chromlist_from_ssf() {{
#    local ssf="$1"
#   [[ -r "$ssf" ]] || {{ echo "cannot read SSF: $ssf" >&2; exit 1; }}

#   local reader="cat"
#   case "$ssf" in *.gz|*.bgz) reader="bgzip -dc";; esac

#   mapfile -t present < <(
#     $reader "$ssf" | awk -F'\\t' '
#       NR==1 {{ for(i=1;i<=NF;i++) if($i=="chromosome") c=i; next }}
#       {{
#         chr=$c
#         sub(/^chr/,"",chr)
#         if(chr=="23") chr="X"
#         else if(chr=="24") chr="Y"
#         else if(chr=="26") chr="MT"
#         print chr
#       }}
#     ' | awk 'NF' | sort -u
#   )

#   local order=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 X Y MT)

#   local have=()
#   for ch in "${{order[@]}}"; do
#     if printf '%s\\n' "${{present[@]}}" | grep -qx "$ch"; then
#       have+=("$ch")
#     fi
#   done

#   if [[ ${{#have[@]}} -eq 0 ]]; then
#     echo "WARN: No chromosomes detected in SSF; using full list" >&2
#     echo "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y,MT"
#     return 0
#   fi

#   (IFS=,; echo "${{have[*]}}")
# }}

# # Main execution
# echo "==== VALIDATE INPUT SUMSTATS ===="

# OUT_GZ="$(to_gwas_ssf)" 
# echo "SSF file: $OUT_GZ"
# CHROMLIST="$(chromlist_from_ssf "$OUT_GZ")"
# echo "Chromosomes detected: $CHROMLIST"

# REF_DIR_ABS="$(resolve_path "$REF_DIR")"

# SUMSTATS_DIR=$(dirname -- "$SUMSTATS")
# cd "$SUMSTATS_DIR"

# LOG_DIR="$SUMSTATS_DIR/logs"
# mkdir -p "$LOG_DIR"

# export PATH="$CODE_REPO:$PATH"

# echo "==== HARMONISE SUMSTATS ===="
# nextflow run "$CODE_REPO" -profile standard \\
#   --harm \\
#   --ref "$REF_DIR_ABS" \\
#   --file "$OUT_GZ" \\
#   --chromlist "$CHROMLIST" \\
#   --to_build "$BUILD" \\
#   --threshold "$THRESHOLD"  \\
#   -resume \\
#   -with-report   "logs/harm-report-$(date +%s).html" \\
#   -with-timeline "logs/harm-timeline-$(date +%s).html" \\
#   -with-trace    "logs/harm-trace-$(date +%s).txt" \\
#   |& tee -a "$LOG_DIR/harm.log"

# # Copy the harmonized output
# HARMONIZED_FILE=$(find . -name "*harmonised*" -type f | head -1)
# if [[ -n "$HARMONIZED_FILE" ]]; then
#     cp "$HARMONIZED_FILE" "harmonized_output.tsv"
#     echo "Harmonization completed successfully!"
# else
#     echo "# ERROR: No harmonized output found" > "harmonized_output.tsv"
#     echo "Harmonization completed but no output file found"
# fi
# '''
    
#     # Write the bash script to a temporary file
#     with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
#         f.write(bash_script)
#         bash_script_path = f.name
    
#     try:
#         # Make it executable
#         os.chmod(bash_script_path, 0o755)
        
#         # Run the bash script
#         result = subprocess.run(['bash', bash_script_path], capture_output=True, text=True)
        
#         # Print output
#         print(result.stdout)
#         if result.stderr:
#             print("STDERR:", result.stderr, file=sys.stderr)
        
#         if result.returncode != 0:
#             sys.exit(f"Bash script failed with return code: {result.returncode}")
            
#         print("Harmonization completed successfully via bash script!")
        
#     finally:
#         # Clean up
#         os.unlink(bash_script_path)

# if __name__ == '__main__':
#     main()











#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description='GWAS Harmonizer Wrapper - Direct bash call')
    parser.add_argument('--input', required=True, help='Input GWAS summary statistics file')
    parser.add_argument('--build', required=True, choices=['GRCh37', 'GRCh38'], help='Target genome build')
    parser.add_argument('--threshold', type=float, default=0.99, help='Palindromic variants threshold')
    parser.add_argument('--ref-dir', required=True, help='Reference data directory')
    parser.add_argument('--code-repo', required=True, help='Path to harmonizer code repository')
    
    args = parser.parse_args()
    
    # Build the command to call your original harmonizer.sh
    cmd = [
        'bash',
        '/mnt/hdd_1/ofgeha/gwas-sumstats-harmoniser/harmonizer.sh',  # You need to set this path
        '--input', args.input,
        '--build', args.build,
        '--threshold', str(args.threshold),
        '--ref', args.ref_dir,
        '--code-repo', args.code_repo
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr, file=sys.stderr)
    
    if result.returncode != 0:
        sys.exit(f"Command failed with return code: {result.returncode}")
    
    print("Harmonization completed successfully!")

if __name__ == '__main__':
    main()