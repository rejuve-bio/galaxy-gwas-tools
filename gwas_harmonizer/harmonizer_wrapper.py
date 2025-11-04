#!/usr/bin/env python3
"""
GWAS Harmonizer - Galaxy wrapper for harmonizer.sh
"""

import argparse
import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_command(cmd, env=None):
    """Run a shell command and return output"""
    print(f"Running: {cmd}", flush=True)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
        print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        print(f"Command execution failed: {e}")
        return 1, "", str(e)

def prepare_output_files(workdir, input_file):
    """Prepare Galaxy output files from harmonizer outputs"""
    print("Preparing Galaxy outputs...")
    
    # Find SSF files (created by harmonizer.sh)
    ssf_files = list(workdir.glob("*.tsv.gz"))
    yaml_files = list(workdir.glob("*.yaml"))
    
    # Find harmonized output (look in logs directory for Nextflow outputs)
    log_dir = workdir / "logs"
    harmonized_files = []
    
    if log_dir.exists():
        # Look for any output files created by Nextflow
        for pattern in ['*harmonised*', '*harmonized*', '*final*']:
            harmonized_files.extend(log_dir.rglob(pattern))
    
    # Create a consolidated harmonized output
    harmonized_output = workdir / "harmonized_output.txt"
    
    if harmonized_files:
        # If we found harmonized files, combine them or use the first one
        primary_output = harmonized_files[0]
        if primary_output.suffix == '.gz':
            # Decompress if needed
            import gzip
            with gzip.open(primary_output, 'rt') as f_in:
                with open(harmonized_output, 'w') as f_out:
                    f_out.write(f_in.read())
        else:
            shutil.copy2(primary_output, harmonized_output)
        print(f"Primary harmonized output: {harmonized_output}")
    else:
        # Create a placeholder if no harmonized files found
        with open(harmonized_output, 'w') as f:
            f.write("Harmonization completed. Check individual output files.\n")
        print("No harmonized files found, created placeholder")
    
    # Report found files
    if ssf_files:
        print(f"SSF files: {[f.name for f in ssf_files]}")
    if yaml_files:
        print(f"YAML files: {[f.name for f in yaml_files]}")
    
    return harmonized_output

def main():
    parser = argparse.ArgumentParser(description='GWAS Harmonizer - Galaxy Wrapper')
    parser.add_argument('--input', required=True, help='Input GWAS summary statistics file')
    parser.add_argument('--build', required=True, choices=['GRCh37', 'GRCh38'], 
                       help='Genome build (GRCh37 or GRCh38)')
    parser.add_argument('--threshold', default='0.99', help='Palindromic SNP threshold')
    parser.add_argument('--ref-dir', required=True, help='Reference data directory')
    parser.add_argument('--code-repo', required=True, help='Harmonizer code repository path')
    parser.add_argument('--workdir', default='.', help='Working directory')
    parser.add_argument('--min-mac', help='Minimum minor allele count filter')
    parser.add_argument('--info-score', help='INFO score filter')
    
    args = parser.parse_args()
    
    workdir = Path(args.workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    
    print("=== GWAS Harmonizer ===")
    print(f"Working directory: {workdir}")
    print(f"Input file: {args.input}")
    print(f"Genome build: {args.build}")
    print(f"Threshold: {args.threshold}")
    print(f"Reference directory: {args.ref_dir}")
    print(f"Code repository: {args.code_repo}")
    
    # Verify paths exist
    code_repo_path = Path(args.code_repo)
    if not code_repo_path.exists():
        print(f"ERROR: Code repository not found: {args.code_repo}")
        sys.exit(1)
    
    ref_dir_path = Path(args.ref_dir)
    if not ref_dir_path.exists():
        print(f"ERROR: Reference directory not found: {args.ref_dir}")
        print("Please run the setup tool first")
        sys.exit(1)
    
    # Find the harmonizer script
    harmonizer_script = code_repo_path / "harmonizer.sh"
    if not harmonizer_script.exists():
        print(f"ERROR: Harmonizer script not found: {harmonizer_script}")
        sys.exit(1)
    
    # Make script executable
    harmonizer_script.chmod(0o755)
    
    # Set up environment
    env = os.environ.copy()
    env['PATH'] = f"{code_repo_path}:{env.get('PATH', '')}"
    
    # Build command for harmonizer.sh
    cmd_parts = [
        f"'{harmonizer_script}'",
        f"--input '{args.input}'",
        f"--build '{args.build}'",
        f"--threshold '{args.threshold}'",
        f"--ref '{args.ref_dir}'",
        f"--code-repo '{code_repo_path}'"
    ]
    
    # Add optional parameters
    if args.min_mac:
        cmd_parts.append(f"--min-mac '{args.min_mac}'")
    
    if args.info_score:
        cmd_parts.append(f"--info-score '{args.info_score}'")
    
    cmd = " ".join(cmd_parts)
    
    # Run the harmonizer script
    return_code, stdout, stderr = run_command(cmd, env=env)
    
    if return_code != 0:
        print(f"Harmonization failed with return code: {return_code}")
        sys.exit(return_code)
    
    # Prepare output files for Galaxy
    harmonized_output = prepare_output_files(workdir, args.input)
    
    print("✅ Harmonization completed successfully")
    print(f"Harmonized output: {harmonized_output}")

if __name__ == "__main__":
    main()