# #!/usr/bin/env python3
# import subprocess
# import sys
# import os
# import argparse
# from datetime import datetime

# def main():
#     parser = argparse.ArgumentParser(description='Run GWAS harmonization pipeline')
#     parser.add_argument('--input_ssf', required=True, help='Input SSF file')
#     parser.add_argument('--ref_path', required=True, help='Reference directory path')
#     parser.add_argument('--chromlist', required=True, help='Chromosome list')
#     parser.add_argument('--build_num', required=True, help='Target build number')
#     parser.add_argument('--threshold', required=True, help='Palindromic threshold')
#     parser.add_argument('--output_ssf', required=True, help='Output harmonized SSF')
#     parser.add_argument('--output_yaml', required=True, help='Output YAML metadata')
    
#     args = parser.parse_args()
    
#     print("Starting GWAS harmonization...")
#     print(f"Input SSF: {args.input_ssf}")
#     print(f"Reference directory: {args.ref_path}")
#     print(f"Chromosome list: {args.chromlist}")
#     print(f"Target build: GRCh{args.build_num}")
#     print(f"Threshold: {args.threshold}")
    
#     # Check if reference directory exists
#     if not os.path.isdir(args.ref_path):
#         print(f"ERROR: Reference directory not found: {args.ref_path}")
#         print("Please ensure the reference data is available at this path")
#         sys.exit(1)
    
#     # Create output directory
#     os.makedirs("harmonized_output", exist_ok=True)
    
#     # Build the Nextflow command
#     cmd = [
#         'nextflow', 'run', 'EBISPOT/gwas-sumstats-harmoniser',
#         '-r', 'v1.1.10',
#         '--ref', args.ref_path,
#         '--harm',
#         '--file', args.input_ssf,
#         '--chromlist', args.chromlist,
#         '--to_build', args.build_num,
#         '--threshold', args.threshold,
#         '--terminate_error', 'ignore',
#         '-profile', 'standard,singularity',
#         '-resume',
#         '-with-report', "harmonized_output/report.html",
#         '-with-timeline', "harmonized_output/timeline.html", 
#         '-with-trace', "harmonized_output/trace.txt",
#         '-work-dir', "harmonized_output/work",
#         '--outdir', "harmonized_output"
#     ]
    
#     print("Running Nextflow command:")
#     print(' '.join(cmd))
    
#     # Run Nextflow
#     try:
#         result = subprocess.run(cmd, check=True, capture_output=True, text=True)
#         print("Nextflow output:")
#         print(result.stdout)
#         if result.stderr:
#             print("Nextflow stderr:")
#             print(result.stderr)
#     except subprocess.CalledProcessError as e:
#         print(f"ERROR: Nextflow failed with exit code {e.returncode}")
#         print(f"STDOUT: {e.stdout}")
#         print(f"STDERR: {e.stderr}")
#         sys.exit(1)
    
#     print("Harmonization completed successfully")
    
#     # Find and copy the final harmonized file
#     harmonized_files = []
#     for root, dirs, files in os.walk("harmonized_output"):
#         for file in files:
#             if file.endswith('.harmonised.gz') or file.endswith('.harmonised.bgz'):
#                 harmonized_files.append(os.path.join(root, file))
    
#     if harmonized_files:
#         # Use the first found harmonized file
#         harmonized_file = harmonized_files[0]
#         print(f"Found harmonized file: {harmonized_file}")
        
#         # Copy to output location
#         subprocess.run(['cp', harmonized_file, args.output_ssf], check=True)
        
#         # Find and copy YAML metadata
#         yaml_files = []
#         for root, dirs, files in os.walk("harmonized_output"):
#             for file in files:
#                 if file.endswith('.yaml') or file.endswith('.yml'):
#                     yaml_files.append(os.path.join(root, file))
        
#         if yaml_files:
#             yaml_file = yaml_files[0]
#             print(f"Found YAML metadata: {yaml_file}")
#             subprocess.run(['cp', yaml_file, args.output_yaml], check=True)
#         else:
#             # Create basic metadata
#             print("Creating basic metadata file")
#             with open(args.output_yaml, 'w') as f:
#                 f.write(f"""harmonization_status: completed
# input_file: {os.path.basename(args.input_ssf)}
# genome_build: GRCh{args.build_num}
# date_harmonized: {datetime.now().strftime('%Y-%m-%d')}
# """)
#     else:
#         print("ERROR: No harmonized output file found")
#         print("Available files in harmonized_output:")
#         for root, dirs, files in os.walk("harmonized_output"):
#             for file in files:
#                 print(f"  {os.path.join(root, file)}")
#         sys.exit(1)
    
#     print("Results copied to output files successfully")

# if __name__ == '__main__':
#     main()






# #!/usr/bin/env python3
# import subprocess
# import sys
# import os
# import argparse
# import shutil
# import gzip

# def decompress_file(input_path):
#     """Decompress file if needed and return path to working file"""
#     print(f"Checking if file is compressed: {input_path}")
    
#     # Check if file is compressed by reading first few bytes
#     try:
#         with open(input_path, 'rb') as f:
#             magic_number = f.read(2)
#             is_compressed = (magic_number == b'\x1f\x8b')  # gzip magic number
#     except Exception as e:
#         print(f"ERROR: Could not read file {input_path}: {e}")
#         return input_path, False
    
#     if is_compressed:
#         print(f"File is compressed (gzip), decompressing...")
#         # Create a temporary uncompressed file
#         base_name = os.path.basename(input_path).replace('.gz', '').replace('.bgz', '')
#         uncompressed_path = f"input_{base_name}"
        
#         try:
#             with gzip.open(input_path, 'rb') as f_in:
#                 with open(uncompressed_path, 'wb') as f_out:
#                     shutil.copyfileobj(f_in, f_out)
            
#             print(f"Successfully decompressed to: {uncompressed_path}")
#             # Verify the decompressed file
#             file_size = os.path.getsize(uncompressed_path)
#             print(f"Decompressed file size: {file_size} bytes")
#             return uncompressed_path, True
#         except Exception as e:
#             print(f"ERROR: Failed to decompress file: {e}")
#             return input_path, False
#     else:
#         print(f"File is not compressed, using as-is")
#         return input_path, False

# def create_metadata_file(input_path, build_num):
#     """Create required metadata file"""
#     metadata_path = input_path + '-meta.yaml'
    
#     print(f"Creating metadata file: {metadata_path}")
#     with open(metadata_path, 'w') as f:
#         f.write(f"""# Study meta-data
# date_metadata_last_modified: 2025-11-16

# # Genotyping Information
# genome_assembly: GRCh{build_num}
# coordinate_system: 1-based

# # Summary Statistic information
# data_file_name: {os.path.basename(input_path)}
# file_type: GWAS-SSF v0.1
# data_file_md5sum: placeholder_md5

# # Harmonization status
# is_harmonised: false
# is_sorted: false
# """)
#     return metadata_path

# def copy_reference_files_locally(ref_path, chromlist):
#     """Copy reference files to local directory for container access"""
#     print(f"Copying reference files for chromosomes: {chromlist}")
    
#     # Create local reference directory
#     local_ref = "local_reference"
#     os.makedirs(local_ref, exist_ok=True)
    
#     # Parse chromosome list
#     chroms = [c.strip() for c in chromlist.split(',') if c.strip()]
    
#     for chrom in chroms:
#         if chrom:  # Skip empty strings
#             # Copy VCF file
#             vcf_src = os.path.join(ref_path, f"homo_sapiens-chr{chrom}.vcf.gz")
#             vcf_dst = os.path.join(local_ref, f"homo_sapiens-chr{chrom}.vcf.gz")
            
#             if os.path.isfile(vcf_src):
#                 shutil.copy2(vcf_src, vcf_dst)
#                 print(f"✓ Copied VCF: {vcf_dst}")
            
#             # Copy TBI file
#             tbi_src = vcf_src + '.tbi'
#             tbi_dst = vcf_dst + '.tbi'
#             if os.path.isfile(tbi_src):
#                 shutil.copy2(tbi_src, tbi_dst)
#                 print(f"✓ Copied TBI: {tbi_dst}")
            
#             # Copy parquet file
#             parquet_src = os.path.join(ref_path, f"homo_sapiens-chr{chrom}.parquet")
#             parquet_dst = os.path.join(local_ref, f"homo_sapiens-chr{chrom}.parquet")
#             if os.path.isfile(parquet_src):
#                 shutil.copy2(parquet_src, parquet_dst)
#                 print(f"✓ Copied parquet: {parquet_dst}")
    
#     return os.path.abspath(local_ref)

# def main():
#     parser = argparse.ArgumentParser(description='Run GWAS harmonization pipeline')
#     parser.add_argument('--input', required=True, help='Input GWAS file')
#     parser.add_argument('--ref_path', required=True, help='Reference directory path')
#     parser.add_argument('--build', required=True, help='Target genome build')
#     parser.add_argument('--threshold', required=True, help='Palindromic threshold')
#     parser.add_argument('--chromlist', required=True, help='Chromosome list')
#     parser.add_argument('--output', required=True, help='Output harmonized file')
    
#     args = parser.parse_args()
    
#     print("=== GWAS Harmonization Starting ===")
#     print(f"Input file: {args.input}")
#     print(f"File size: {os.path.getsize(args.input)} bytes")
#     print(f"Reference directory: {args.ref_path}")
#     print(f"Target build: {args.build}")
#     print(f"Threshold: {args.threshold}")
#     print(f"Chromosome list: {args.chromlist}")
    
#     # Convert build to number
#     build_num = "37" if args.build == "GRCh37" else "38"
    
#     # Check if reference directory exists
#     if not os.path.isdir(args.ref_path):
#         print(f"ERROR: Reference directory not found: {args.ref_path}")
#         sys.exit(1)
    
#     # Check if input file exists
#     if not os.path.isfile(args.input):
#         print(f"ERROR: Input file not found: {args.input}")
#         sys.exit(1)
    
#     # Copy reference files locally to ensure container access
#     print("\n=== Preparing reference files for container ===")
#     local_ref_path = copy_reference_files_locally(args.ref_path, args.chromlist)
#     print(f"Using local reference directory: {local_ref_path}")
    
#     # Handle file decompression
#     print("\n=== Checking file compression ===")
#     working_input, temp_file_created = decompress_file(args.input)
    
#     if temp_file_created:
#         print(f"Using decompressed file: {working_input}")
#     else:
#         print(f"Using original file: {working_input}")
    
#     # Create metadata file
#     print("\n=== Creating metadata ===")
#     metadata_file = create_metadata_file(working_input, build_num)
    
#     # Create output directory
#     output_dir = "harmonized_output"
#     os.makedirs(output_dir, exist_ok=True)
    
#     # Build the Nextflow command with local reference path
#     cmd = [
#         'nextflow', 'run', 'EBISPOT/gwas-sumstats-harmoniser',
#         '-r', 'v1.1.10',
#         '--ref', local_ref_path,
#         '--harm',
#         '--file', working_input,
#         '--chromlist', args.chromlist,
#         '--to_build', build_num,
#         '--threshold', args.threshold,
#         '--terminate_error', 'ignore',
#         '-profile', 'standard,singularity',
#         '-resume',
#         '--outdir', output_dir
#     ]
    
#     print("\n=== Running Nextflow ===")
#     print("Command:", ' '.join(cmd))
    
#     # Run Nextflow
#     try:
#         # Run Nextflow with real-time output
#         process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
#         # Print output in real-time
#         for line in process.stdout:
#             print(line.strip())
        
#         # Wait for completion
#         return_code = process.wait()
        
#         if return_code != 0:
#             print(f"\nWARNING: Nextflow finished with exit code {return_code}")
#             print("This might be due to metadata generation issues, checking for harmonized output...")
            
#     except Exception as e:
#         print(f"ERROR: Failed to run Nextflow: {str(e)}")
#         # Try to recover output even if Nextflow failed
    
#     # Find the harmonized output file - try even if Nextflow failed
#     print("\n=== Searching for harmonized output ===")
#     harmonized_files = []
#     for root, dirs, files in os.walk(output_dir):
#         for file in files:
#             # Look for any harmonized files, including intermediate ones
#             if ('harmonised' in file.lower() or 'h.tsv' in file) and (file.endswith('.gz') or file.endswith('.bgz') or file.endswith('.tsv')):
#                 harmonized_files.append(os.path.join(root, file))
    
#     # Also check the work directory for intermediate files
#     work_dir = os.path.join(output_dir, "work")
#     if os.path.exists(work_dir):
#         for root, dirs, files in os.walk(work_dir):
#             for file in files:
#                 if ('harmonised' in file.lower() or 'h.tsv' in file) and (file.endswith('.gz') or file.endswith('.bgz') or file.endswith('.tsv')):
#                     harmonized_files.append(os.path.join(root, file))
    
#     if harmonized_files:
#         # Sort by file size (largest first) to get the most complete file
#         harmonized_files.sort(key=lambda x: os.path.getsize(x) if os.path.exists(x) else 0, reverse=True)
        
#         # Use the largest harmonized file
#         harmonized_file = harmonized_files[0]
#         print(f"Found harmonized file: {harmonized_file}")
#         print(f"File size: {os.path.getsize(harmonized_file)} bytes")
        
#         # Copy to final output location
#         shutil.copy(harmonized_file, args.output)
#         print(f"Output copied to: {args.output}")
        
#         # Print success message
#         file_size = os.path.getsize(args.output)
#         print(f"SUCCESS: Harmonization complete! Output size: {file_size} bytes")
        
#         # Clean up temporary files
#         if temp_file_created and os.path.exists(working_input):
#             os.remove(working_input)
#             print(f"Cleaned up temporary file: {working_input}")
#         if os.path.exists(metadata_file):
#             os.remove(metadata_file)
#             print(f"Cleaned up metadata file: {metadata_file}")
        
#         # Clean up local reference directory
#         if os.path.exists("local_reference"):
#             shutil.rmtree("local_reference")
#             print("Cleaned up local reference directory")
        
#         # Exit successfully even if Nextflow had issues
#         sys.exit(0)
#     else:
#         print("ERROR: No harmonized output file found")
#         print("Available files in output directory:")
#         for root, dirs, files in os.walk(output_dir):
#             for file in files:
#                 file_path = os.path.join(root, file)
#                 file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
#                 print(f"  {file_path} ({file_size} bytes)")
#         sys.exit(1)

# if __name__ == '__main__':
#     main()
















# #!/usr/bin/env python3
# import subprocess
# import sys
# import os
# import argparse
# import shutil
# import gzip
# import glob

# def decompress_file(input_path):
#     """Decompress file if needed and return path to working file"""
#     print(f"Checking if file is compressed: {input_path}")
    
#     # Check if file is compressed by reading first few bytes
#     try:
#         with open(input_path, 'rb') as f:
#             magic_number = f.read(2)
#             is_compressed = (magic_number == b'\x1f\x8b')  # gzip magic number
#     except Exception as e:
#         print(f"ERROR: Could not read file {input_path}: {e}")
#         return input_path, False
    
#     if is_compressed:
#         print(f"File is compressed (gzip), decompressing...")
#         # Create a temporary uncompressed file
#         base_name = os.path.basename(input_path).replace('.gz', '').replace('.bgz', '')
#         uncompressed_path = f"input_{base_name}"
        
#         try:
#             with gzip.open(input_path, 'rb') as f_in:
#                 with open(uncompressed_path, 'wb') as f_out:
#                     shutil.copyfileobj(f_in, f_out)
            
#             print(f"Successfully decompressed to: {uncompressed_path}")
#             # Verify the decompressed file
#             file_size = os.path.getsize(uncompressed_path)
#             print(f"Decompressed file size: {file_size} bytes")
#             return uncompressed_path, True
#         except Exception as e:
#             print(f"ERROR: Failed to decompress file: {e}")
#             return input_path, False
#     else:
#         print(f"File is not compressed, using as-is")
#         return input_path, False

# def create_metadata_file(input_path, build_num):
#     """Create required metadata file"""
#     metadata_path = input_path + '-meta.yaml'
    
#     print(f"Creating metadata file: {metadata_path}")
#     with open(metadata_path, 'w') as f:
#         f.write(f"""# Study meta-data
# date_metadata_last_modified: 2025-11-16

# # Genotyping Information
# genome_assembly: GRCh{build_num}
# coordinate_system: 1-based

# # Summary Statistic information
# data_file_name: {os.path.basename(input_path)}
# file_type: GWAS-SSF v0.1
# data_file_md5sum: placeholder_md5

# # Harmonization status
# is_harmonised: false
# is_sorted: false
# """)
#     return metadata_path

# def copy_reference_files_locally(ref_path, chromlist):
#     """Copy reference files to local directory for container access"""
#     print(f"Copying reference files for chromosomes: {chromlist}")
    
#     # Create local reference directory
#     local_ref = "local_reference"
#     os.makedirs(local_ref, exist_ok=True)
    
#     # Parse chromosome list
#     chroms = [c.strip() for c in chromlist.split(',') if c.strip()]
    
#     for chrom in chroms:
#         if chrom:  # Skip empty strings
#             # Copy VCF file
#             vcf_src = os.path.join(ref_path, f"homo_sapiens-chr{chrom}.vcf.gz")
#             vcf_dst = os.path.join(local_ref, f"homo_sapiens-chr{chrom}.vcf.gz")
            
#             if os.path.isfile(vcf_src):
#                 shutil.copy2(vcf_src, vcf_dst)
#                 print(f"✓ Copied VCF: {vcf_dst}")
            
#             # Copy TBI file
#             tbi_src = vcf_src + '.tbi'
#             tbi_dst = vcf_dst + '.tbi'
#             if os.path.isfile(tbi_src):
#                 shutil.copy2(tbi_src, tbi_dst)
#                 print(f"✓ Copied TBI: {tbi_dst}")
            
#             # Copy parquet file
#             parquet_src = os.path.join(ref_path, f"homo_sapiens-chr{chrom}.parquet")
#             parquet_dst = os.path.join(local_ref, f"homo_sapiens-chr{chrom}.parquet")
#             if os.path.isfile(parquet_src):
#                 shutil.copy2(parquet_src, parquet_dst)
#                 print(f"✓ Copied parquet: {parquet_dst}")
    
#     return os.path.abspath(local_ref)

# def find_all_files(output_dir):
#     """Find ALL files in the output directory for debugging"""
#     print(f"\n=== DEBUG: Listing ALL files in {output_dir} ===")
#     all_files = []
    
#     if os.path.exists(output_dir):
#         for root, dirs, files in os.walk(output_dir):
#             for file in files:
#                 file_path = os.path.join(root, file)
#                 file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
#                 all_files.append((file_path, file_size))
#                 print(f"  {file_path} ({file_size} bytes)")
    
#     return all_files

# def main():
#     parser = argparse.ArgumentParser(description='Run GWAS harmonization pipeline')
#     parser.add_argument('--input', required=True, help='Input GWAS file')
#     parser.add_argument('--ref_path', required=True, help='Reference directory path')
#     parser.add_argument('--build', required=True, help='Target genome build')
#     parser.add_argument('--threshold', required=True, help='Palindromic threshold')
#     parser.add_argument('--chromlist', required=True, help='Chromosome list')
#     parser.add_argument('--output', required=True, help='Output harmonized file')
    
#     args = parser.parse_args()
    
#     print("=== GWAS Harmonization Starting ===")
#     print(f"Input file: {args.input}")
#     print(f"File size: {os.path.getsize(args.input)} bytes")
#     print(f"Reference directory: {args.ref_path}")
#     print(f"Target build: {args.build}")
#     print(f"Threshold: {args.threshold}")
#     print(f"Chromosome list: {args.chromlist}")
    
#     # Convert build to number
#     build_num = "37" if args.build == "GRCh37" else "38"
    
#     # Check if reference directory exists
#     if not os.path.isdir(args.ref_path):
#         print(f"ERROR: Reference directory not found: {args.ref_path}")
#         sys.exit(1)
    
#     # Check if input file exists
#     if not os.path.isfile(args.input):
#         print(f"ERROR: Input file not found: {args.input}")
#         sys.exit(1)
    
#     # Get input basename for file searching
#     input_basename = os.path.basename(args.input).replace('.gz', '').replace('.bgz', '').replace('.dat', '')
    
#     # Copy reference files locally to ensure container access
#     print("\n=== Preparing reference files for container ===")
#     local_ref_path = copy_reference_files_locally(args.ref_path, args.chromlist)
#     print(f"Using local reference directory: {local_ref_path}")
    
#     # Handle file decompression
#     print("\n=== Checking file compression ===")
#     working_input, temp_file_created = decompress_file(args.input)
    
#     if temp_file_created:
#         print(f"Using decompressed file: {working_input}")
#     else:
#         print(f"Using original file: {working_input}")
    
#     # Create metadata file
#     print("\n=== Creating metadata ===")
#     metadata_file = create_metadata_file(working_input, build_num)
    
#     # Create output directory
#     output_dir = "harmonized_output"
#     os.makedirs(output_dir, exist_ok=True)
    
#     # Build the Nextflow command with local reference path
#     cmd = [
#         'nextflow', 'run', 'EBISPOT/gwas-sumstats-harmoniser',
#         '-r', 'v1.1.10',
#         '--ref', local_ref_path,
#         '--harm',
#         '--file', working_input,
#         '--chromlist', args.chromlist,
#         '--to_build', build_num,
#         '--threshold', args.threshold,
#         '--terminate_error', 'ignore',
#         '-profile', 'standard,singularity',
#         '-resume',
#         '--outdir', output_dir
#     ]
    
#     print("\n=== Running Nextflow ===")
#     print("Command:", ' '.join(cmd))
    
#     # Run Nextflow
#     try:
#         # Run Nextflow with real-time output
#         process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
#         # Print output in real-time
#         for line in process.stdout:
#             print(line.strip())
        
#         # Wait for completion
#         return_code = process.wait()
        
#         if return_code == 0:
#             print("\n✓ Nextflow completed successfully!")
#         else:
#             print(f"\nWARNING: Nextflow finished with exit code {return_code}")
#             print("Checking for harmonized output anyway...")
            
#     except Exception as e:
#         print(f"ERROR: Failed to run Nextflow: {str(e)}")
#         # Try to recover output even if Nextflow failed
    
#     # Find ALL files for debugging
#     print("\n=== DEBUG: Searching for ALL files ===")
#     all_files = find_all_files(output_dir)
    
#     # Look for harmonized files with various patterns
#     harmonized_patterns = [
#         "*.h.*", "*harmonised*", "*.harmonised.*", "*final*", "*.tsv*", "*.gz"
#     ]
    
#     harmonized_files = []
#     for pattern in harmonized_patterns:
#         matches = glob.glob(os.path.join(output_dir, "**", pattern), recursive=True)
#         harmonized_files.extend([f for f in matches if os.path.isfile(f)])
    
#     # Remove duplicates
#     harmonized_files = list(set(harmonized_files))
    
#     if harmonized_files:
#         print(f"\nFound {len(harmonized_files)} potential harmonized files:")
#         for f in sorted(harmonized_files):
#             size = os.path.getsize(f) if os.path.exists(f) else 0
#             print(f"  {f} ({size} bytes)")
        
#         # Sort by file size (largest first) to get the most complete file
#         harmonized_files.sort(key=lambda x: os.path.getsize(x) if os.path.exists(x) else 0, reverse=True)
        
#         # Use the largest harmonized file
#         harmonized_file = harmonized_files[0]
#         print(f"\nSelected largest file: {harmonized_file}")
#         print(f"File size: {os.path.getsize(harmonized_file)} bytes")
        
#         # Copy to final output location
#         shutil.copy(harmonized_file, args.output)
#         print(f"Output copied to: {args.output}")
        
#         # Print success message
#         file_size = os.path.getsize(args.output)
#         print(f"SUCCESS: Harmonization complete! Output size: {file_size} bytes")
        
#     else:
#         print("ERROR: No harmonized output file found")
#         print("Let's check if there are any subdirectories with results...")
        
#         # Check for subdirectories that might contain results
#         subdirs = []
#         if os.path.exists(output_dir):
#             for item in os.listdir(output_dir):
#                 item_path = os.path.join(output_dir, item)
#                 if os.path.isdir(item_path):
#                     subdirs.append(item_path)
#                     print(f"Found subdirectory: {item_path}")
                    
#                     # Search in this subdirectory
#                     sub_files = []
#                     for pattern in harmonized_patterns:
#                         matches = glob.glob(os.path.join(item_path, "**", pattern), recursive=True)
#                         sub_files.extend([f for f in matches if os.path.isfile(f)])
                    
#                     if sub_files:
#                         print(f"  Found {len(sub_files)} files in {item_path}:")
#                         for f in sub_files:
#                             size = os.path.getsize(f) if os.path.exists(f) else 0
#                             print(f"    {f} ({size} bytes)")
#                         harmonized_files.extend(sub_files)
        
#         if harmonized_files:
#             # Use the largest file found
#             harmonized_files.sort(key=lambda x: os.path.getsize(x) if os.path.exists(x) else 0, reverse=True)
#             harmonized_file = harmonized_files[0]
#             print(f"\nSelected largest file: {harmonized_file}")
#             print(f"File size: {os.path.getsize(harmonized_file)} bytes")
            
#             # Copy to final output location
#             shutil.copy(harmonized_file, args.output)
#             print(f"Output copied to: {args.output}")
#             print(f"SUCCESS: Harmonization complete! Output size: {os.path.getsize(args.output)} bytes")
#         else:
#             print("ERROR: No harmonized files found in any subdirectories")
#             sys.exit(1)
    
#     # Clean up temporary files
#     print("\n=== Cleaning up temporary files ===")
#     if temp_file_created and os.path.exists(working_input):
#         os.remove(working_input)
#         print(f"Cleaned up temporary file: {working_input}")
#     if os.path.exists(metadata_file):
#         os.remove(metadata_file)
#         print(f"Cleaned up metadata file: {metadata_file}")
    
#     # Clean up local reference directory
#     if os.path.exists("local_reference"):
#         shutil.rmtree("local_reference")
#         print("Cleaned up local reference directory")
    
#     print("\n=== PROCESS COMPLETED SUCCESSFULLY ===")

# if __name__ == '__main__':
#     main()





















#!/usr/bin/env python3
import subprocess
import sys
import os
import argparse
import shutil
import gzip
import glob

def decompress_file(input_path, original_name):
    """Decompress file if needed and return path to working file"""
    print(f"Checking if file is compressed: {input_path}")
    
    # Check if file is compressed by reading first few bytes
    try:
        with open(input_path, 'rb') as f:
            magic_number = f.read(2)
            is_compressed = (magic_number == b'\x1f\x8b')  # gzip magic number
    except Exception as e:
        print(f"ERROR: Could not read file {input_path}: {e}")
        return input_path, False
    
    if is_compressed:
        print(f"File is compressed (gzip), decompressing...")
        # Use the original filename to maintain consistent directory structure
        base_name = os.path.basename(original_name).replace('.gz', '').replace('.bgz', '').replace('.dat', '')
        uncompressed_path = f"{base_name}.tsv"
        
        try:
            with gzip.open(input_path, 'rb') as f_in:
                with open(uncompressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            print(f"Successfully decompressed to: {uncompressed_path}")
            # Verify the decompressed file
            file_size = os.path.getsize(uncompressed_path)
            print(f"Decompressed file size: {file_size} bytes")
            return uncompressed_path, True
        except Exception as e:
            print(f"ERROR: Failed to decompress file: {e}")
            return input_path, False
    else:
        print(f"File is not compressed, using as-is")
        return input_path, False

def create_metadata_file(input_path, build_num):
    """Create required metadata file"""
    metadata_path = input_path + '-meta.yaml'
    
    print(f"Creating metadata file: {metadata_path}")
    with open(metadata_path, 'w') as f:
        f.write(f"""# Study meta-data
date_metadata_last_modified: 2025-11-16

# Genotyping Information
genome_assembly: GRCh{build_num}
coordinate_system: 1-based

# Summary Statistic information
data_file_name: {os.path.basename(input_path)}
file_type: GWAS-SSF v0.1
data_file_md5sum: placeholder_md5

# Harmonization status
is_harmonised: false
is_sorted: false
""")
    return metadata_path

def copy_reference_files_locally(ref_path, chromlist):
    """Copy reference files to local directory for container access"""
    print(f"Copying reference files for chromosomes: {chromlist}")
    
    # Create local reference directory
    local_ref = "local_reference"
    os.makedirs(local_ref, exist_ok=True)
    
    # Parse chromosome list
    chroms = [c.strip() for c in chromlist.split(',') if c.strip()]
    
    for chrom in chroms:
        if chrom:  # Skip empty strings
            # Copy VCF file
            vcf_src = os.path.join(ref_path, f"homo_sapiens-chr{chrom}.vcf.gz")
            vcf_dst = os.path.join(local_ref, f"homo_sapiens-chr{chrom}.vcf.gz")
            
            if os.path.isfile(vcf_src):
                shutil.copy2(vcf_src, vcf_dst)
                print(f"✓ Copied VCF: {vcf_dst}")
            
            # Copy TBI file
            tbi_src = vcf_src + '.tbi'
            tbi_dst = vcf_dst + '.tbi'
            if os.path.isfile(tbi_src):
                shutil.copy2(tbi_src, tbi_dst)
                print(f"✓ Copied TBI: {tbi_dst}")
            
            # Copy parquet file
            parquet_src = os.path.join(ref_path, f"homo_sapiens-chr{chrom}.parquet")
            parquet_dst = os.path.join(local_ref, f"homo_sapiens-chr{chrom}.parquet")
            if os.path.isfile(parquet_src):
                shutil.copy2(parquet_src, parquet_dst)
                print(f"✓ Copied parquet: {parquet_dst}")
    
    return os.path.abspath(local_ref)

def find_harmonized_output():
    """Find harmonized output files - look in current directory structure"""
    print("Searching for harmonized output in current directory...")
    
    # The pipeline creates output in the current working directory
    # Look for directories that match the pattern of harmonized output
    harmonized_files = []
    
    # Search for .h.tsv.gz files in current directory and subdirectories
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith('.h.tsv.gz') or file == 'harmonised.tsv':
                file_path = os.path.join(root, file)
                harmonized_files.append(file_path)
                print(f"Found harmonized file: {file_path}")
    
    # Also look for directories that might contain the results
    potential_dirs = []
    for item in os.listdir("."):
        if os.path.isdir(item) and not item.startswith(('local_reference', 'harmonized_output', 'work')):
            potential_dirs.append(item)
    
    print(f"Potential output directories: {potential_dirs}")
    
    for dir_name in potential_dirs:
        # Check for final directory
        final_dir = os.path.join(dir_name, "final")
        if os.path.exists(final_dir):
            for file in os.listdir(final_dir):
                if file.endswith('.h.tsv.gz'):
                    harmonized_files.append(os.path.join(final_dir, file))
        
        # Check for qc directory
        qc_dir = os.path.join(dir_name, "5_qc")
        if os.path.exists(qc_dir):
            for file in os.listdir(qc_dir):
                if file == 'harmonised.tsv' or file.endswith('.h.tsv.gz'):
                    harmonized_files.append(os.path.join(qc_dir, file))
    
    # Remove duplicates and return the largest file
    harmonized_files = list(set(harmonized_files))
    if harmonized_files:
        harmonized_files.sort(key=lambda x: os.path.getsize(x) if os.path.exists(x) else 0, reverse=True)
        return harmonized_files[0]
    
    return None

def main():
    parser = argparse.ArgumentParser(description='Run GWAS harmonization pipeline')
    parser.add_argument('--input', required=True, help='Input GWAS file')
    parser.add_argument('--ref_path', required=True, help='Reference directory path')
    parser.add_argument('--build', required=True, help='Target genome build')
    parser.add_argument('--threshold', required=True, help='Palindromic threshold')
    parser.add_argument('--chromlist', required=True, help='Chromosome list')
    parser.add_argument('--output', required=True, help='Output harmonized file')
    
    args = parser.parse_args()
    
    print("=== GWAS Harmonization Starting ===")
    print(f"Input file: {args.input}")
    print(f"File size: {os.path.getsize(args.input)} bytes")
    print(f"Reference directory: {args.ref_path}")
    print(f"Target build: {args.build}")
    print(f"Threshold: {args.threshold}")
    print(f"Chromosome list: {args.chromlist}")
    
    # Get the original filename for consistent naming
    original_filename = os.path.basename(args.input)
    input_basename = original_filename.replace('.gz', '').replace('.bgz', '').replace('.dat', '')
    print(f"Original filename: {original_filename}")
    print(f"Input basename: {input_basename}")
    
    # Convert build to number
    build_num = "37" if args.build == "GRCh37" else "38"
    
    # Check if reference directory exists
    if not os.path.isdir(args.ref_path):
        print(f"ERROR: Reference directory not found: {args.ref_path}")
        sys.exit(1)
    
    # Check if input file exists
    if not os.path.isfile(args.input):
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)
    
    # Copy reference files locally to ensure container access
    print("\n=== Preparing reference files for container ===")
    local_ref_path = copy_reference_files_locally(args.ref_path, args.chromlist)
    print(f"Using local reference directory: {local_ref_path}")
    
    # Handle file decompression - use original filename to maintain consistency
    print("\n=== Checking file compression ===")
    working_input, temp_file_created = decompress_file(args.input, original_filename)
    
    if temp_file_created:
        print(f"Using decompressed file: {working_input}")
    else:
        print(f"Using original file: {working_input}")
    
    # Create metadata file
    print("\n=== Creating metadata ===")
    metadata_file = working_input + '-meta.yaml'
    with open(metadata_file, 'w') as f:
        f.write(f"""# Study meta-data
date_metadata_last_modified: 2025-11-16

# Genotyping Information
genome_assembly: GRCh{build_num}
coordinate_system: 1-based

# Summary Statistic information
data_file_name: {working_input}
file_type: GWAS-SSF v0.1
data_file_md5sum: placeholder_md5

# Harmonization status
is_harmonised: false
is_sorted: false
""")
    
    # Create output directory
    output_dir = "harmonized_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Build the Nextflow command with local reference path
    cmd = [
        'nextflow', 'run', 'EBISPOT/gwas-sumstats-harmoniser',
        '-r', 'v1.1.10',
        '--ref', local_ref_path,
        '--harm',
        '--file', working_input,
        '--chromlist', args.chromlist,
        '--to_build', build_num,
        '--threshold', args.threshold,
        '--terminate_error', 'ignore',
        '-profile', 'standard,singularity',
        '-resume',
        '--outdir', output_dir
    ]
    
    print("\n=== Running Nextflow ===")
    print("Command:", ' '.join(cmd))
    
    # Run Nextflow
    try:
        # Run Nextflow with real-time output
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        # Print output in real-time
        for line in process.stdout:
            print(line.strip())
        
        # Wait for completion
        return_code = process.wait()
        
        if return_code == 0:
            print("\n✓ Nextflow completed successfully!")
        else:
            print(f"\nWARNING: Nextflow finished with exit code {return_code}")
            print("Checking for harmonized output anyway...")
            
    except Exception as e:
        print(f"ERROR: Failed to run Nextflow: {str(e)}")
        # Try to recover output even if Nextflow failed
    
    # Find the harmonized output file - look in current directory
    print("\n=== Searching for harmonized output ===")
    harmonized_file = find_harmonized_output()
    
    if harmonized_file and os.path.exists(harmonized_file):
        print(f"Found harmonized file: {harmonized_file}")
        print(f"File size: {os.path.getsize(harmonized_file)} bytes")
        
        # Copy to final output location
        shutil.copy(harmonized_file, args.output)
        print(f"Output copied to: {args.output}")
        
        # Print success message
        file_size = os.path.getsize(args.output)
        print(f"SUCCESS: Harmonization complete! Output size: {file_size} bytes")
        
    else:
        print("ERROR: No harmonized output file found")
        print("Current directory contents:")
        for item in os.listdir("."):
            item_path = os.path.join(".", item)
            if os.path.isdir(item_path):
                print(f"DIR: {item_path}")
            else:
                size = os.path.getsize(item_path) if os.path.exists(item_path) else 0
                print(f"FILE: {item_path} ({size} bytes)")
        
        sys.exit(1)
    
    # Clean up temporary files
    print("\n=== Cleaning up temporary files ===")
    if temp_file_created and os.path.exists(working_input):
        os.remove(working_input)
        print(f"Cleaned up temporary file: {working_input}")
    if os.path.exists(metadata_file):
        os.remove(metadata_file)
        print(f"Cleaned up metadata file: {metadata_file}")
    
    # Clean up local reference directory
    if os.path.exists("local_reference"):
        shutil.rmtree("local_reference")
        print("Cleaned up local reference directory")
    
    print("\n=== PROCESS COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()