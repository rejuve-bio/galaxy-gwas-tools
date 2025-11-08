#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path
import datetime
import hashlib
import yaml
import importlib
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='GWAS Harmonizer Wrapper')
    parser.add_argument('--code-repo', required=True, help='Path to harmonizer code repository')
    parser.add_argument('--ref-dir', required=True, help='Reference data directory (from setup)')
    parser.add_argument('--data-file', required=True, help='Path to input GWAS data file (TSV/TXT)')
    parser.add_argument('--meta-file', default=None, help='Path to metadata YAML file (optional)')
    parser.add_argument('--genome-assembly', default='GRCh38', help='Genome assembly (if no meta file)')
    parser.add_argument('--coordinate-system', default='1-based', help='Coordinate system (if no meta file)')
    parser.add_argument('--output-dir', default='harmonized_output', help='Output directory for results')
    
    args = parser.parse_args()
    
    args.output_dir = os.path.abspath(args.output_dir)
    args.ref_dir = os.path.abspath(args.ref_dir)
    args.code_repo = os.path.abspath(args.code_repo)
    
    # Install missing packages inside virtualenv
    packages = [
        ('duckdb', '1.1.1'),
        ('pyarrow', '15.0.1'),
        ('pyliftover', '0.4'),
        ('pandas', '2.2.3'),
        ('gwas_sumstats_tools', '1.2.0')
    ]
    for pkg, version in packages:
        try:
            importlib.import_module(pkg)
        except ImportError:
            print(f"Installing {pkg}=={version}")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', f"{pkg}=={version}"])
    
    # Set environment
    env = os.environ.copy()
    env['PATH'] = f"{args.code_repo}:{env.get('PATH', '')}"
    
    # Validate inputs
    if not os.path.isdir(args.code_repo):
        sys.exit(f"Error: Code repository not found: {args.code_repo}")
    if not os.path.isdir(args.ref_dir):
        sys.exit(f"Error: Reference directory not found: {args.ref_dir}")
    if not os.path.exists(args.data_file):
        sys.exit(f"Error: Data file not found: {args.data_file}")
    if args.meta_file and not os.path.exists(args.meta_file):
        sys.exit(f"Error: Meta file not found: {args.meta_file}")
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Set up work directory for inputs
    work_dir = os.path.join(args.output_dir, 'input')
    os.makedirs(work_dir, exist_ok=True)
    
    # Copy data file to work_dir with standard name
    data_base = 'input.tsv'
    data_target = os.path.join(work_dir, data_base)
    shutil.copy2(args.data_file, data_target)
    
    # Preprocess the input file to standardize column names
    df = pd.read_csv(data_target, sep='\t')
    df.columns = df.columns.str.strip().str.lower()
    
    # If columns are 'column 1', 'column 2', etc., rename to standard headers
    if all(col.startswith('column') for col in df.columns):
        standard_headers = ['variant', 'minor_allele', 'minor_af', 'low_confidence_variant', 'n_complete_samples', 'ac', 'ytx', 'beta', 'se', 'tstat', 'pval']
        if len(df.columns) == len(standard_headers):
            df.columns = standard_headers
    
    column_map = {
        'chr': 'chromosome',
        'chrom': 'chromosome',
        'chromosome': 'chromosome',
        'chrm': 'chromosome',
        'pos': 'base_pair_location',
        'bp': 'base_pair_location',
        'position': 'base_pair_location',
        'base_pair': 'base_pair_location',
        'ea': 'effect_allele',
        'a1': 'effect_allele',
        'effect': 'effect_allele',
        'alt': 'effect_allele',
        'oa': 'other_allele',
        'a2': 'other_allele',
        'other': 'other_allele',
        'ref': 'other_allele',
        'snp': 'variant_id',
        'rsid': 'rsid',
        'id': 'variant_id',
        'marker': 'variant_id',
        'markername': 'variant_id',
        'variant': 'variant_id'  # Added this
    }
    df.rename(columns=column_map, inplace=True)
    
    # If 'chromosome' and 'base_pair_location' are not present but 'variant_id' is, try to parse variant_id
    if 'chromosome' not in df.columns and 'base_pair_location' not in df.columns and 'variant_id' in df.columns:
        try:
            parsed = df['variant_id'].str.split(':', expand=True)
            if parsed.shape[1] >= 4:
                df['chromosome'] = parsed[0]
                df['base_pair_location'] = parsed[1]
                df['other_allele'] = parsed[2]
                df['effect_allele'] = parsed[3]
                df['base_pair_location'] = pd.to_numeric(df['base_pair_location'], errors='coerce')
            elif parsed.shape[1] >= 2:
                df['chromosome'] = parsed[0]
                df['base_pair_location'] = parsed[1]
                df['base_pair_location'] = pd.to_numeric(df['base_pair_location'], errors='coerce')
        except Exception as e:
            print(f"Warning: Could not parse variant_id: {str(e)}")
    
    # Save the preprocessed file
    df.to_csv(data_target, sep='\t', index=False)
    
    # Compute MD5
    with open(data_target, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    
    # Set up meta YAML
    meta_base = data_base + '-meta.yaml'
    meta_target = os.path.join(work_dir, meta_base)
    
    if args.meta_file:
        # Load provided meta, update fields
        with open(args.meta_file, 'r') as f:
            meta_data = yaml.safe_load(f)
        meta_data['data_file_name'] = data_base
        meta_data['data_file_md5sum'] = md5
        # Update date if not set
        if 'date_metadata_last_modified' not in meta_data:
            meta_data['date_metadata_last_modified'] = datetime.datetime.now().strftime("%Y-%m-%d")
    else:
        # Generate default meta
        meta_data = {
            'date_metadata_last_modified': datetime.datetime.now().strftime("%Y-%m-%d"),
            'genome_assembly': args.genome_assembly,
            'coordinate_system': args.coordinate_system,
            'data_file_name': data_base,
            'file_type': 'txt',
            'data_file_md5sum': md5,
            'is_harmonised': False,
            'is_sorted': False
        }
    
    # Write meta YAML
    with open(meta_target, 'w') as f:
        yaml.safe_dump(meta_data, f)
    
    # Use absolute path to nextflow
    nextflow_path = os.path.join(args.code_repo, 'nextflow')
    if not os.path.exists(nextflow_path):
        nextflow_path = shutil.which('nextflow')
        if not nextflow_path:
            sys.exit("Error: Nextflow not found in code repo or PATH")
    
    # Create log directory inside output directory
    log_dir = os.path.join(args.output_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    print(f"Starting GWAS Harmonizer")
    print(f"Code repo: {args.code_repo}")
    print(f"Reference dir: {args.ref_dir}")
    print(f"Data file: {data_target}")
    print(f"Meta file: {meta_target}")
    print(f"Output dir: {args.output_dir}")
    print(f"Log dir: {log_dir}")
    print(f"Nextflow path: {nextflow_path}")
    
    # Build Nextflow command
    cmd = [
        nextflow_path, 'run', args.code_repo,
        '-profile', 'standard',
        '--harm',
        '--ref', args.ref_dir,
        '--file', data_target,
        '--outdir', args.output_dir,
        '-with-report', os.path.join(log_dir, 'harm-report.html'),
        '-with-timeline', os.path.join(log_dir, 'harm-timeline.html'),
        '-with-trace', os.path.join(log_dir, 'harm-trace.txt'),
        '-with-dag', os.path.join(log_dir, 'harm-dag.html')
    ]
    
    print(f"Nextflow command: {' '.join(cmd)}")
    
    # Run Nextflow
    log_file = os.path.join(log_dir, 'harm.log')
    try:
        with open(log_file, 'w') as log_f:
            log_f.write(f"Command: {' '.join(cmd)}\n")
            log_f.write(f"Reference directory: {args.ref_dir}\n")
            log_f.write(f"Data file: {data_target}\n")
            log_f.write(f"Meta file: {meta_target}\n")
            log_f.write(f"Output directory: {args.output_dir}\n")
            log_f.write(f"Log directory: {log_dir}\n")
            log_f.flush()
            
            process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            # Stream output with timestamps
            line_count = 0
            for line in process.stdout:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                output_line = f"[{timestamp}] {line}"
                print(output_line, end='')
                log_f.write(output_line)
                log_f.flush()
                
                line_count += 1
                if line_count % 50 == 0:
                    print(f"=== Processed {line_count} lines of output ===")
            
            return_code = process.wait()
            
        if return_code != 0:
            print(f"Nextflow process failed with return code: {return_code}")
            sys.exit(return_code)
            
        print("Harmonizer completed successfully!")
        
        # Find the harmonized output file (assuming pattern *.h.tsv.gz)
        harmonized_files = list(Path(args.output_dir).glob('*.h.tsv.gz'))
        if not harmonized_files:
            print("Warning: No harmonized output file found")
        else:
            primary_output = harmonized_files[0]
            shutil.copy2(primary_output, 'harmonized_output.tsv.gz')
            print(f"Copied primary output to harmonized_output.tsv.gz")
            
            # Also copy index if exists
            index_file = primary_output.with_suffix('.tsv.gz.tbi')
            if index_file.exists():
                shutil.copy2(index_file, 'harmonized_output.tsv.gz.tbi')
        
        # Create output files for Galaxy
        with open('log_dir.txt', 'w') as f:
            f.write(log_dir)
            
        # Copy report files to current directory for Galaxy outputs
        report_files = {
            'harm-report.html': 'report',
            'harm-timeline.html': 'timeline'
        }
        
        for src_file, dest_name in report_files.items():
            src = os.path.join(log_dir, src_file)
            if os.path.exists(src):
                shutil.copy2(src, dest_name)
                print(f"Copied {src} to {dest_name}")
            else:
                print(f"Warning: {src} not found")
                
    except Exception as e:
        sys.exit(f"Error running harmonizer: {str(e)}")

if __name__ == '__main__':
    main()







# #!/usr/bin/env python3
# import os
# import sys
# import argparse
# import subprocess
# import shutil
# from pathlib import Path
# import datetime
# import hashlib
# import yaml
# import importlib
# import pandas as pd


# def install_package(pkg, version, fallback_version=None):
#     """
#     Attempt to install a package with subprocess. If installation fails and a fallback version is
#     provided, attempt to install the fallback version.
#     """
#     try:
#         print(f"Installing {pkg}=={version}")
#         subprocess.check_call([sys.executable, "-m", "pip", "install", f"{pkg}=={version}"])
#     except subprocess.CalledProcessError as e:
#         if fallback_version:
#             print(f"⚠️ Failed to install {pkg}=={version} — trying fallback {pkg}=={fallback_version}")
#             try:
#                 subprocess.check_call([sys.executable, "-m", "pip", "install", f"{pkg}=={fallback_version}"])
#                 print(f"✅ Successfully installed {pkg}=={fallback_version}")
#             except subprocess.CalledProcessError:
#                 sys.exit(f"❌ Both {pkg}=={version} and fallback {pkg}=={fallback_version} failed. Error: {str(e)}")
#         else:
#             sys.exit(f"❌ Failed to install {pkg}=={version}. Error: {str(e)}")


# def main():
#     parser = argparse.ArgumentParser(description="GWAS Harmonizer Wrapper")
#     parser.add_argument("--code-repo", required=True, help="Path to harmonizer code repository")
#     parser.add_argument("--ref-dir", required=True, help="Reference data directory (from setup)")
#     parser.add_argument("--data-file", required=True, help="Path to input GWAS data file (TSV/TXT)")
#     parser.add_argument("--meta-file", default=None, help="Path to metadata YAML file (optional)")
#     parser.add_argument("--genome-assembly", default="GRCh38", help="Genome assembly (if no meta file)")
#     parser.add_argument("--coordinate-system", default="1-based", help="Coordinate system (if no meta file)")
#     parser.add_argument("--output-dir", default="harmonized_output", help="Output directory for results")

#     args = parser.parse_args()

#     args.output_dir = os.path.abspath(args.output_dir)
#     args.ref_dir = os.path.abspath(args.ref_dir)
#     args.code_repo = os.path.abspath(args.code_repo)

#     # --- Handle Python version for gwas_sumstats_tools ---
#     py_major, py_minor = sys.version_info[:2]
#     if py_major == 3 and py_minor >= 12:
#         gwas_version = "1.0.5"  # Fallback for Python 3.12+
#     else:
#         gwas_version = "1.2.0"

#     # --- Install required packages ---
#     packages = [
#         ("duckdb", "1.1.1"),
#         ("pyarrow", "15.0.1"),
#         ("pyliftover", "0.4"),
#         ("pandas", "2.2.3"),
#         ("gwas_sumstats_tools", gwas_version),
#     ]

#     for pkg, version in packages:
#         try:
#             importlib.import_module(pkg)
#         except ImportError:
#             if pkg == "gwas_sumstats_tools" and version == "1.2.0":
#                 install_package(pkg, version, fallback_version="1.0.5")
#             else:
#                 install_package(pkg, version)

#     # --- Set environment ---
#     env = os.environ.copy()
#     env["PATH"] = f"{args.code_repo}:{env.get('PATH', '')}"

#     # --- Validate inputs ---
#     if not os.path.isdir(args.code_repo):
#         sys.exit(f"Error: Code repository not found: {args.code_repo}")
#     if not os.path.isdir(args.ref_dir):
#         sys.exit(f"Error: Reference directory not found: {args.ref_dir}")
#     if not os.path.exists(args.data_file):
#         sys.exit(f"Error: Data file not found: {args.data_file}")
#     if args.meta_file and not os.path.exists(args.meta_file):
#         sys.exit(f"Error: Meta file not found: {args.meta_file}")

#     # --- Prepare directories ---
#     os.makedirs(args.output_dir, exist_ok=True)
#     work_dir = os.path.join(args.output_dir, "input")
#     os.makedirs(work_dir, exist_ok=True)

#     # --- Copy input file ---
#     data_base = "input.tsv"
#     data_target = os.path.join(work_dir, data_base)
#     shutil.copy2(args.data_file, data_target)

#     # --- Preprocess file ---
#     df = pd.read_csv(data_target, sep="\t")
#     df.columns = df.columns.str.strip().str.lower()

#     if all(col.startswith("column") for col in df.columns):
#         standard_headers = [
#             "variant",
#             "minor_allele",
#             "minor_af",
#             "low_confidence_variant",
#             "n_complete_samples",
#             "ac",
#             "ytx",
#             "beta",
#             "se",
#             "tstat",
#             "pval",
#         ]
#         if len(df.columns) == len(standard_headers):
#             df.columns = standard_headers

#     column_map = {
#         "chr": "chromosome",
#         "chrom": "chromosome",
#         "chromosome": "chromosome",
#         "chrm": "chromosome",
#         "pos": "base_pair_location",
#         "bp": "base_pair_location",
#         "position": "base_pair_location",
#         "base_pair": "base_pair_location",
#         "ea": "effect_allele",
#         "a1": "effect_allele",
#         "effect": "effect_allele",
#         "alt": "effect_allele",
#         "oa": "other_allele",
#         "a2": "other_allele",
#         "other": "other_allele",
#         "ref": "other_allele",
#         "snp": "variant_id",
#         "rsid": "rsid",
#         "id": "variant_id",
#         "marker": "variant_id",
#         "markername": "variant_id",
#         "variant": "variant_id",
#     }
#     df.rename(columns=column_map, inplace=True)

#     if "chromosome" not in df.columns and "base_pair_location" not in df.columns and "variant_id" in df.columns:
#         try:
#             parsed = df["variant_id"].str.split(":", expand=True)
#             if parsed.shape[1] >= 4:
#                 df["chromosome"] = parsed[0]
#                 df["base_pair_location"] = pd.to_numeric(parsed[1], errors="coerce")
#                 df["other_allele"] = parsed[2]
#                 df["effect_allele"] = parsed[3]
#             elif parsed.shape[1] >= 2:
#                 df["chromosome"] = parsed[0]
#                 df["base_pair_location"] = pd.to_numeric(parsed[1], errors="coerce")
#         except Exception as e:
#             print(f"Warning: Could not parse variant_id: {str(e)}")

#     df.to_csv(data_target, sep="\t", index=False)

#     # --- Compute MD5 ---
#     with open(data_target, "rb") as f:
#         md5 = hashlib.md5(f.read()).hexdigest()

#     # --- Generate or update meta file ---
#     meta_base = data_base + "-meta.yaml"
#     meta_target = os.path.join(work_dir, meta_base)

#     if args.meta_file:
#         with open(args.meta_file, "r") as f:
#             meta_data = yaml.safe_load(f)
#         meta_data["data_file_name"] = data_base
#         meta_data["data_file_md5sum"] = md5
#         meta_data.setdefault("date_metadata_last_modified", datetime.datetime.now().strftime("%Y-%m-%d"))
#     else:
#         meta_data = {
#             "date_metadata_last_modified": datetime.datetime.now().strftime("%Y-%m-%d"),
#             "genome_assembly": args.genome_assembly,
#             "coordinate_system": args.coordinate_system,
#             "data_file_name": data_base,
#             "file_type": "txt",
#             "data_file_md5sum": md5,
#             "is_harmonised": False,
#             "is_sorted": False,
#         }

#     with open(meta_target, "w") as f:
#         yaml.safe_dump(meta_data, f)

#     # --- Locate Nextflow ---
#     nextflow_path = os.path.join(args.code_repo, "nextflow")
#     if not os.path.exists(nextflow_path):
#         nextflow_path = shutil.which("nextflow")
#         if not nextflow_path:
#             sys.exit("Error: Nextflow not found in code repo or PATH")

#     # --- Logging setup ---
#     log_dir = os.path.join(args.output_dir, "logs")
#     os.makedirs(log_dir, exist_ok=True)

#     print(f"Starting GWAS Harmonizer")
#     print(f"Nextflow: {nextflow_path}")
#     print(f"Data: {data_target}")
#     print(f"Meta: {meta_target}")

#     # --- Build and run Nextflow command ---
#     cmd = [
#         nextflow_path,
#         "run",
#         args.code_repo,
#         "-profile",
#         "standard",
#         "--harm",
#         "--ref",
#         args.ref_dir,
#         "--file",
#         data_target,
#         "--outdir",
#         args.output_dir,
#         "-with-report",
#         os.path.join(log_dir, "harm-report.html"),
#         "-with-timeline",
#         os.path.join(log_dir, "harm-timeline.html"),
#         "-with-trace",
#         os.path.join(log_dir, "harm-trace.txt"),
#         "-with-dag",
#         os.path.join(log_dir, "harm-dag.html"),
#     ]

#     log_file = os.path.join(log_dir, "harm.log")
#     try:
#         with open(log_file, "w") as log_f:
#             log_f.write(f"Command: {' '.join(cmd)}\n")
#             process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
#             for line in process.stdout:
#                 timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                 output_line = f"[{timestamp}] {line}"
#                 print(output_line, end="")
#                 log_f.write(output_line)
#             return_code = process.wait()

#         if return_code != 0:
#             sys.exit(f"Nextflow process failed with return code {return_code}")

#         print("Harmonizer completed successfully!")

#         # --- Handle outputs ---
#         harmonized_files = list(Path(args.output_dir).glob("*.h.tsv.gz"))
#         if harmonized_files:
#             primary_output = harmonized_files[0]
#             shutil.copy2(primary_output, "harmonized_output.tsv.gz")
#             index_file = primary_output.with_suffix(".tsv.gz.tbi")
#             if index_file.exists():
#                 shutil.copy2(index_file, "harmonized_output.tsv.gz.tbi")
#         else:
#             print("Warning: No harmonized output file found")

#         with open("log_dir.txt", "w") as f:
#             f.write(log_dir)

#         for src_file, dest_name in {
#             "harm-report.html": "report",
#             "harm-timeline.html": "timeline",
#         }.items():
#             src = os.path.join(log_dir, src_file)
#             if os.path.exists(src):
#                 shutil.copy2(src, dest_name)
#                 print(f"Copied {src} to {dest_name}")
#             else:
#                 print(f"Warning: {src} not found")

#     except Exception as e:
#         sys.exit(f"Error running harmonizer: {str(e)}")


# if __name__ == "__main__":
#     main()
