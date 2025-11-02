# #!/usr/bin/env python3
# """
# gwas_sumstats_harmonizer.py
# Version with improved error handling for reference preparation.
# """

# import argparse
# import os
# import shutil
# import subprocess
# import sys
# import time
# import urllib.request
# import tarfile
# from pathlib import Path

# def run(cmd, cwd=None, env=None, check=True, capture=False):
#     print(f"> {cmd}", flush=True)
#     res = subprocess.run(cmd, shell=True, cwd=cwd, env=env, text=True,
#                          stdout=subprocess.PIPE if capture else None,
#                          stderr=subprocess.PIPE if capture else None)
#     if capture:
#         out = res.stdout or ""
#         err = res.stderr or ""
#     else:
#         out, err = "", ""
#     if check and res.returncode != 0:
#         print(f"Command failed (rc={res.returncode}). STDOUT:\n{out}\nSTDERR:\n{err}", file=sys.stderr, flush=True)
#         raise subprocess.CalledProcessError(res.returncode, cmd, output=out, stderr=err)
#     return res.returncode, out, err

# def install_java_locally(workdir):
#     """Install OpenJDK locally in the job directory"""
#     java_dir = workdir / "java"
#     java_dir.mkdir(exist_ok=True)
    
#     print("Attempting to install Java locally...", flush=True)
    
#     # Download portable JDK
#     jdk_url = "https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz"
#     jdk_tarball = workdir / "openjdk-17.tar.gz"
    
#     try:
#         print(f"Downloading OpenJDK from {jdk_url}...", flush=True)
#         urllib.request.urlretrieve(jdk_url, jdk_tarball)
        
#         print("Extracting OpenJDK...", flush=True)
#         with tarfile.open(jdk_tarball, 'r:gz') as tar:
#             tar.extractall(path=java_dir)
        
#         # Find the extracted JDK directory
#         jdk_path = None
#         for item in java_dir.iterdir():
#             if item.is_dir() and 'jdk' in item.name:
#                 jdk_path = item
#                 break
        
#         if jdk_path:
#             java_bin = jdk_path / "bin" / "java"
#             if java_bin.exists():
#                 print(f"✓ Portable OpenJDK installed: {java_bin}", flush=True)
#                 return str(java_bin), str(jdk_path)
#     except Exception as e:
#         print(f"Portable JDK installation failed: {e}", flush=True)
    
#     return None, None

# def install_nextflow_locally(workdir, java_home):
#     """Install Nextflow locally with proper Java environment"""
#     nf_path = workdir / "nextflow"
    
#     print("Installing Nextflow locally...", flush=True)
    
#     # Set up environment with Java
#     env = os.environ.copy()
#     if java_home:
#         env['JAVA_HOME'] = java_home
#         env['PATH'] = f"{Path(java_home) / 'bin'}:{env['PATH']}"
#         print(f"Setting JAVA_HOME to: {java_home}", flush=True)
    
#     try:
#         run("curl -s https://get.nextflow.io | bash", cwd=workdir, env=env, check=True)
        
#         if nf_path.exists():
#             run(f"chmod +x {nf_path}", cwd=workdir, env=env, check=True)
#             print(f"✓ Nextflow installed: {nf_path}", flush=True)
#             return str(nf_path)
#     except Exception as e:
#         print(f"Nextflow installation failed: {e}", flush=True)
    
#     return None

# def read_log_file(log_path, max_lines=50):
#     """Read and display the last few lines of a log file"""
#     if not log_path.exists():
#         return "Log file not found"
    
#     try:
#         with open(log_path, 'r') as f:
#             lines = f.readlines()
#             if len(lines) > max_lines:
#                 return "..." + "\n".join(lines[-max_lines:])
#             else:
#                 return "".join(lines)
#     except Exception as e:
#         return f"Error reading log file: {e}"

# def main():
#     print("=== GWAS Harmonizer - Local Installation Mode ===", flush=True)
    
#     p = argparse.ArgumentParser()
#     p.add_argument("--input", required=True, help="Path to input GWAS sumstats file")
#     p.add_argument("--build", required=True, choices=["GRCh37","GRCh38"], help="Genome build")
#     p.add_argument("--threshold", default="0.99", help="Palindromic threshold")
#     p.add_argument("--ref-dir", required=True, help="Reference directory")
#     p.add_argument("--repo-url", default="https://github.com/EBISPOT/gwas-sumstats-harmoniser.git", help="Harmoniser repo URL")
#     p.add_argument("--repo-dir", default="gwas-sumstats-harmoniser", help="Local clone directory")
#     p.add_argument("--workdir", default=".", help="Working directory")
#     args = p.parse_args()

#     WORKDIR = Path(args.workdir).resolve()
#     WORKDIR.mkdir(parents=True, exist_ok=True)
#     os.chdir(WORKDIR)
#     print(f"Working directory: {WORKDIR}", flush=True)

#     # Check for Java
#     java_path = shutil.which("java")
#     java_home = None
    
#     if not java_path:
#         print("Java not found in PATH, attempting local installation...", flush=True)
#         java_path, java_home = install_java_locally(WORKDIR)
    
#     if not java_path:
#         print("ERROR: Could not install or find Java.", file=sys.stderr)
#         sys.exit(1)
    
#     print(f"Using Java: {java_path}", flush=True)
    
#     # If we installed Java locally, set up environment
#     env = os.environ.copy()
#     if java_home:
#         env['JAVA_HOME'] = java_home
#         env['PATH'] = f"{Path(java_home) / 'bin'}:{env['PATH']}"
#         print(f"Set JAVA_HOME to: {java_home}", flush=True)

#     # Check for Nextflow with the updated environment
#     nextflow_path = shutil.which("nextflow", path=env['PATH'])
#     if not nextflow_path:
#         print("Nextflow not found in PATH, attempting local installation...", flush=True)
#         nextflow_path = install_nextflow_locally(WORKDIR, java_home)
    
#     if not nextflow_path:
#         print("ERROR: Could not install or find Nextflow.", file=sys.stderr)
#         sys.exit(1)
    
#     print(f"Using Nextflow: {nextflow_path}", flush=True)
    
#     # Add local nextflow to PATH if it's in our workdir
#     if WORKDIR in Path(nextflow_path).parents:
#         env['PATH'] = f"{WORKDIR}:{env['PATH']}"
#         print(f"Added {WORKDIR} to PATH for Nextflow", flush=True)

#     # Verify installations
#     try:
#         # Test Java
#         rc, out, err = run(f"'{java_path}' -version", env=env, capture=True, check=True)
#         print("✓ Java verification successful", flush=True)
        
#         # Test Nextflow
#         rc, out, err = run(f"'{nextflow_path}' -version", env=env, capture=True, check=True)
#         print(f"✓ Nextflow verification successful: {out.strip()}", flush=True)
        
#     except subprocess.CalledProcessError as e:
#         print(f"Dependency verification failed: {e}", file=sys.stderr)
#         sys.exit(1)

#     # Rest of harmonizer logic
#     print("All dependencies installed and verified!", flush=True)
#     print("Proceeding with harmonization workflow...", flush=True)

#     # Resolve repo directory
#     repo_path = Path(args.repo_dir)
#     if not repo_path.is_absolute():
#         repo_path = (WORKDIR / repo_path).resolve()

#     # Verify input exists
#     input_path = Path(args.input)
#     if not input_path.exists():
#         print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
#         sys.exit(2)

#     # Create run directory
#     run_work = WORKDIR / "harmonizer_run_work"
#     if run_work.exists():
#         timestamp = int(time.time())
#         backup = WORKDIR / f"harmonizer_run_work_backup_{timestamp}"
#         print(f"run_work exists; moving to {backup}")
#         shutil.move(str(run_work), str(backup))
#     run_work.mkdir(parents=True, exist_ok=False)

#     # Copy input file
#     input_local = run_work / input_path.name
#     print(f"Copying input {input_path} -> {input_local}")
#     shutil.copy2(str(input_path), str(input_local))

#     # Clone or update repository
#     if not repo_path.exists():
#         print(f"Cloning harmoniser repo {args.repo_url} -> {repo_path}")
#         run(f"git clone {args.repo_url} {repo_path}", cwd=WORKDIR, env=env)
#     else:
#         print(f"Repo exists at {repo_path}; attempting update")
#         try:
#             run("git fetch --all --prune", cwd=repo_path, env=env)
#             run("git pull --ff-only", cwd=repo_path, env=env)
#         except subprocess.CalledProcessError:
#             print("Warning: git update failed; using existing repo", file=sys.stderr)

#     # Add repo to PATH
#     env["PATH"] = f"{repo_path}:{env.get('PATH','')}"

#     # Check if references need to be built
#     ref_dir = Path(args.ref_dir)
#     need_refs = not ref_dir.exists() or not any(ref_dir.iterdir())
    
#     if need_refs:
#         print(f"Reference directory {ref_dir} needs preparation")
#         if not ref_dir.exists():
#             ref_dir.mkdir(parents=True, exist_ok=True)
        
#         logs_dir = run_work / "logs"
#         logs_dir.mkdir(exist_ok=True)
#         setup_log = logs_dir / "harmonizer_setup.log"
        
#         print("Preparing references (this may take a while)...")
#         try:
#             # First, let's check if the harmonizer setup script exists
#             setup_script = repo_path / "harmonizer_setup.sh"
#             if setup_script.exists():
#                 print("Found harmonizer_setup.sh, using it for reference preparation...")
#                 run(f"chmod +x {setup_script}", env=env, check=True)
#                 cmd = f"'{setup_script}' --ref '{ref_dir}' --code-repo '{repo_path}'"
#             else:
#                 # Use Nextflow directly
#                 print("Using Nextflow directly for reference preparation...")
#                 cmd = f"'{nextflow_path}' run {repo_path} -profile standard --reference --ref '{ref_dir}' --chromlist 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y,MT"
            
#             print(f"Running: {cmd}")
#             with open(setup_log, "w") as fh:
#                 proc = subprocess.Popen(cmd, shell=True, cwd=str(run_work), env=env, stdout=fh, stderr=subprocess.STDOUT, text=True)
#                 proc.wait()
#                 if proc.returncode != 0:
#                     # Read and display the log for debugging
#                     log_content = read_log_file(setup_log)
#                     print(f"Reference preparation failed. Log content:\n{log_content}", file=sys.stderr)
#                     raise subprocess.CalledProcessError(proc.returncode, cmd)
#             print(f"Reference preparation completed; log: {setup_log}")
#         except subprocess.CalledProcessError as e:
#             print(f"Reference preparation failed with exit code {e.returncode}", file=sys.stderr)
#             print("This might be due to missing dependencies or network issues.", file=sys.stderr)
#             print("You can try preparing the reference directory manually or check the log above.", file=sys.stderr)
#             sys.exit(3)
#     else:
#         print(f"Reference directory {ref_dir} appears ready; skipping preparation")

#     # Run harmonization - try to proceed even if reference prep failed
#     run_log = run_work / "harmonizer_run.log"
#     print("Running harmonisation workflow...")
#     try:
#         cmd = (
#             f"'{nextflow_path}' run {repo_path} -profile standard "
#             f"--harm --ref '{ref_dir}' --file '{input_local}' "
#             f"--to_build {args.build} --threshold {args.threshold} "
#             f"-with-report '{run_work}/harm-report.html' "
#             f"-with-timeline '{run_work}/harm-timeline.html' "
#             f"-with-trace '{run_work}/harm-trace.txt' -resume"
#         )
#         print(f"Running harmonization: {cmd}")
#         with open(run_log, "w") as fh:
#             proc = subprocess.Popen(cmd, shell=True, cwd=str(run_work), env=env, stdout=fh, stderr=subprocess.STDOUT, text=True)
#             proc.wait()
#             if proc.returncode != 0:
#                 # Read and display the log for debugging
#                 log_content = read_log_file(run_log)
#                 print(f"Harmonization failed. Log content:\n{log_content}", file=sys.stderr)
#                 raise subprocess.CalledProcessError(proc.returncode, cmd)
#         print(f"Harmonisation completed; log: {run_log}")
#     except subprocess.CalledProcessError as e:
#         print("Harmonisation workflow failed.", file=sys.stderr)
#         print(f"Check detailed logs: {run_log}", file=sys.stderr)
#         sys.exit(4)

#     # Package outputs
#     tarball = WORKDIR / "harmonizer_output.tar.gz"
#     print(f"Packaging outputs into {tarball}")
#     try:
#         run(f"tar -czf '{tarball}' -C '{run_work}' .", env=env, check=True)
#         print("Output packaging completed")
#     except Exception as e:
#         print(f"Failed to create output package: {e}", file=sys.stderr)
#         sys.exit(5)

#     # Copy main log for Galaxy
#     try:
#         top_run_log = WORKDIR / "harmonizer_run.log"
#         shutil.copy2(run_log, top_run_log)
#     except Exception:
#         pass

#     print("=== SUCCESS ===")
#     print(f"Output: {tarball}")
#     sys.exit(0)

# if __name__ == "__main__":
#     main()








#!/usr/bin/env python3
"""
gwas_sumstats_harmonizer.py
Comprehensive version that verifies harmonization and helps locate output files.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import tarfile
import gzip
import pandas as pd
from pathlib import Path

def run(cmd, cwd=None, env=None, check=True, capture=False):
    print(f"> {cmd}", flush=True)
    res = subprocess.run(cmd, shell=True, cwd=cwd, env=env, text=True,
                         stdout=subprocess.PIPE if capture else None,
                         stderr=subprocess.PIPE if capture else None)
    if capture:
        out = res.stdout or ""
        err = res.stderr or ""
    else:
        out, err = "", ""
    if check and res.returncode != 0:
        print(f"Command failed (rc={res.returncode}). STDOUT:\n{out}\nSTDERR:\n{err}", file=sys.stderr, flush=True)
        raise subprocess.CalledProcessError(res.returncode, cmd, output=out, stderr=err)
    return res.returncode, out, err

def install_java_locally(workdir):
    """Install OpenJDK locally in the job directory"""
    java_dir = workdir / "java"
    java_dir.mkdir(exist_ok=True)
    
    print("Attempting to install Java locally...", flush=True)
    
    # Download portable JDK
    jdk_url = "https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz"
    jdk_tarball = workdir / "openjdk-17.tar.gz"
    
    try:
        print(f"Downloading OpenJDK from {jdk_url}...", flush=True)
        urllib.request.urlretrieve(jdk_url, jdk_tarball)
        
        print("Extracting OpenJDK...", flush=True)
        with tarfile.open(jdk_tarball, 'r:gz') as tar:
            tar.extractall(path=java_dir)
        
        # Find the extracted JDK directory
        jdk_path = None
        for item in java_dir.iterdir():
            if item.is_dir() and 'jdk' in item.name:
                jdk_path = item
                break
        
        if jdk_path:
            java_bin = jdk_path / "bin" / "java"
            if java_bin.exists():
                print(f"✓ Portable OpenJDK installed: {java_bin}", flush=True)
                return str(java_bin), str(jdk_path)
    except Exception as e:
        print(f"Portable JDK installation failed: {e}", flush=True)
    
    return None, None

def install_nextflow_locally(workdir, java_home):
    """Install Nextflow locally with proper Java environment"""
    nf_path = workdir / "nextflow"
    
    print("Installing Nextflow locally...", flush=True)
    
    # Set up environment with Java
    env = os.environ.copy()
    if java_home:
        env['JAVA_HOME'] = java_home
        env['PATH'] = f"{Path(java_home) / 'bin'}:{env['PATH']}"
        print(f"Setting JAVA_HOME to: {java_home}", flush=True)
    
    try:
        run("curl -s https://get.nextflow.io | bash", cwd=workdir, env=env, check=True)
        
        if nf_path.exists():
            run(f"chmod +x {nf_path}", cwd=workdir, env=env, check=True)
            print(f"✓ Nextflow installed: {nf_path}", flush=True)
            return str(nf_path)
    except Exception as e:
        print(f"Nextflow installation failed: {e}", flush=True)
    
    return None

def analyze_output_structure(run_work_dir):
    """Analyze the output structure to understand where files are located"""
    print("\n" + "="*60, flush=True)
    print("ANALYZING OUTPUT STRUCTURE", flush=True)
    print("="*60, flush=True)
    
    # Create analysis report
    analysis_report = []
    analysis_report.append("GWAS Harmonizer Output Structure Analysis")
    analysis_report.append("=" * 50)
    
    # First, let's see what directories exist
    analysis_report.append("\n📁 DIRECTORY STRUCTURE:")
    all_items = list(run_work_dir.iterdir())
    
    for item in all_items:
        if item.is_dir():
            analysis_report.append(f"📁 {item.name}/")
            # Count files in directory
            file_count = len(list(item.rglob("*")))
            dir_count = len([d for d in item.rglob("*") if d.is_dir()])
            analysis_report.append(f"    Contains: {file_count} files, {dir_count} subdirectories")
            
            # Show largest files in this directory
            files_in_dir = [f for f in item.rglob("*") if f.is_file()]
            if files_in_dir:
                largest_files = sorted(files_in_dir, key=lambda x: x.stat().st_size, reverse=True)[:3]
                analysis_report.append("    Largest files:")
                for f in largest_files:
                    size_mb = f.stat().st_size / (1024*1024)
                    analysis_report.append(f"      {f.relative_to(item)} ({size_mb:.2f} MB)")
        else:
            size_mb = item.stat().st_size / (1024*1024)
            analysis_report.append(f"📄 {item.name} ({size_mb:.2f} MB)")
    
    # Look for Nextflow work directory specifically
    work_dir = run_work_dir / "work"
    if work_dir.exists():
        analysis_report.append(f"\n🔍 NEXTFLOW WORK DIRECTORY ANALYSIS:")
        work_subdirs = list(work_dir.iterdir())
        analysis_report.append(f"Found {len(work_subdirs)} work subdirectories")
        
        # Sample a few work directories to understand structure
        for work_subdir in work_subdirs[:3]:
            if work_subdir.is_dir():
                analysis_report.append(f"\n  Work subdirectory: {work_subdir.name}")
                # Look for output files
                output_files = list(work_subdir.rglob("*"))
                data_files = [f for f in output_files if f.is_file() and f.stat().st_size > 1000]
                
                if data_files:
                    analysis_report.append(f"  Found {len(data_files)} data files:")
                    for file_path in data_files[:5]:  # Show first 5
                        size_mb = file_path.stat().st_size / (1024*1024)
                        rel_path = file_path.relative_to(work_subdir)
                        analysis_report.append(f"    {rel_path} ({size_mb:.2f} MB)")
                        
                        # Try to identify file type
                        if any(x in str(rel_path).lower() for x in ['harmon', 'output', 'result', 'final']):
                            analysis_report.append(f"      ⚡ POTENTIAL HARMONIZED OUTPUT")
    
    # Look for any file that might be harmonized output
    analysis_report.append(f"\n🔎 SEARCHING FOR HARMONIZED DATA FILES:")
    
    # Search patterns for harmonized files
    search_patterns = [
        "*harmonised*", "*harmonized*", "*output*", "*result*", "*final*",
        "*.tsv", "*.txt", "*.csv", "*.gz", "*.bgz"
    ]
    
    potential_files = []
    for pattern in search_patterns:
        for file_path in run_work_dir.rglob(pattern):
            if (file_path.is_file() and 
                file_path.stat().st_size > 1000 and
                "trace" not in file_path.name.lower() and
                "report" not in file_path.name.lower() and
                "log" not in file_path.name.lower() and
                ".nextflow" not in str(file_path)):
                potential_files.append(file_path)
    
    # Remove duplicates and sort by size
    potential_files = list(set(potential_files))
    potential_files.sort(key=lambda x: x.stat().st_size, reverse=True)
    
    analysis_report.append(f"Found {len(potential_files)} potential harmonized data files:")
    
    for file_path in potential_files[:10]:  # Show top 10
        size_mb = file_path.stat().st_size / (1024*1024)
        rel_path = file_path.relative_to(run_work_dir)
        analysis_report.append(f"  📊 {rel_path} ({size_mb:.2f} MB)")
        
        # Try to read first line to identify content
        try:
            if file_path.suffix == '.gz':
                with gzip.open(file_path, 'rt') as f:
                    first_line = f.readline().strip()
            else:
                with open(file_path, 'r') as f:
                    first_line = f.readline().strip()
            
            # Check for GWAS-related content
            gwas_keywords = ['snp', 'rsid', 'chr', 'pos', 'bp', 'a1', 'a2', 'beta', 'se', 'p', 'pval', 'or', 'effect']
            if any(keyword in first_line.lower() for keyword in gwas_keywords):
                analysis_report.append(f"      ✅ CONTAINS GWAS DATA: {first_line[:100]}...")
            else:
                analysis_report.append(f"      📝 First line: {first_line[:100]}...")
        except Exception as e:
            analysis_report.append(f"      ❌ Cannot read file: {e}")
    
    # Write analysis report to file
    report_file = run_work_dir.parent / "output_analysis_report.txt"
    with open(report_file, 'w') as f:
        f.write("\n".join(analysis_report))
    
    print("\n".join(analysis_report), flush=True)
    print(f"\n📋 Full analysis report saved to: {report_file}", flush=True)
    
    return potential_files

def create_simple_tabular_output(potential_files, output_dir):
    """Create a simple tabular output from the most likely harmonized file"""
    if not potential_files:
        print("❌ No potential harmonized files found", flush=True)
        return None
    
    # Use the largest file as the most likely candidate
    main_file = potential_files[0]
    print(f"🎯 Attempting to use main file: {main_file}", flush=True)
    
    output_file = output_dir / "harmonized_gwas_data.tsv"
    
    try:
        # Try to read the file
        if main_file.suffix == '.gz':
            with gzip.open(main_file, 'rt') as f:
                first_lines = [f.readline() for _ in range(5)]
        else:
            with open(main_file, 'r') as f:
                first_lines = [f.readline() for _ in range(5)]
        
        print("📖 File preview:", flush=True)
        for i, line in enumerate(first_lines):
            if line.strip():
                print(f"  Line {i+1}: {line.strip()}", flush=True)
        
        # Try different separators
        separators = ['\t', ',', ' ', '|']
        best_sep = None
        best_cols = 0
        
        for sep in separators:
            try:
                if main_file.suffix == '.gz':
                    df_sample = pd.read_csv(main_file, compression='gzip', sep=sep, nrows=5, engine='python')
                else:
                    df_sample = pd.read_csv(main_file, sep=sep, nrows=5, engine='python')
                
                if len(df_sample.columns) > best_cols and len(df_sample.columns) > 1:
                    best_cols = len(df_sample.columns)
                    best_sep = sep
            except:
                continue
        
        if best_sep:
            print(f"🔧 Using separator: '{best_sep}' with {best_cols} columns", flush=True)
            
            # Read full file
            if main_file.suffix == '.gz':
                df = pd.read_csv(main_file, compression='gzip', sep=best_sep, engine='python')
            else:
                df = pd.read_csv(main_file, sep=best_sep, engine='python')
            
            # Save as TSV
            df.to_csv(output_file, sep='\t', index=False)
            print(f"✅ Created harmonized TSV: {output_file} ({len(df)} rows, {len(df.columns)} columns)", flush=True)
            
            print("📊 Column names:", flush=True)
            for col in df.columns:
                print(f"  - {col}", flush=True)
            
            return output_file
        else:
            print("❌ Could not detect file format", flush=True)
            return None
            
    except Exception as e:
        print(f"❌ Error processing file: {e}", flush=True)
        return None

def main():
    print("=== GWAS Harmonizer - Comprehensive Analysis ===", flush=True)
    
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Path to input GWAS sumstats file")
    p.add_argument("--build", required=True, choices=["GRCh37","GRCh38"], help="Genome build")
    p.add_argument("--threshold", default="0.99", help="Palindromic threshold")
    p.add_argument("--ref-dir", required=True, help="Reference directory")
    p.add_argument("--repo-url", default="https://github.com/EBISPOT/gwas-sumstats-harmoniser.git", help="Harmoniser repo URL")
    p.add_argument("--repo-dir", default="gwas-sumstats-harmoniser", help="Local clone directory")
    p.add_argument("--workdir", default=".", help="Working directory")
    args = p.parse_args()

    WORKDIR = Path(args.workdir).resolve()
    WORKDIR.mkdir(parents=True, exist_ok=True)
    os.chdir(WORKDIR)
    print(f"Working directory: {WORKDIR}", flush=True)

    # Check for Java
    java_path = shutil.which("java")
    java_home = None
    
    if not java_path:
        print("Java not found in PATH, attempting local installation...", flush=True)
        java_path, java_home = install_java_locally(WORKDIR)
    
    if not java_path:
        print("ERROR: Could not install or find Java.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Using Java: {java_path}", flush=True)
    
    # If we installed Java locally, set up environment
    env = os.environ.copy()
    if java_home:
        env['JAVA_HOME'] = java_home
        env['PATH'] = f"{Path(java_home) / 'bin'}:{env['PATH']}"
        print(f"Set JAVA_HOME to: {java_home}", flush=True)

    # Check for Nextflow with the updated environment
    nextflow_path = shutil.which("nextflow", path=env['PATH'])
    if not nextflow_path:
        print("Nextflow not found in PATH, attempting local installation...", flush=True)
        nextflow_path = install_nextflow_locally(WORKDIR, java_home)
    
    if not nextflow_path:
        print("ERROR: Could not install or find Nextflow.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Using Nextflow: {nextflow_path}", flush=True)
    
    # Add local nextflow to PATH if it's in our workdir
    if WORKDIR in Path(nextflow_path).parents:
        env['PATH'] = f"{WORKDIR}:{env['PATH']}"
        print(f"Added {WORKDIR} to PATH for Nextflow", flush=True)

    # Verify installations
    try:
        # Test Java
        rc, out, err = run(f"'{java_path}' -version", env=env, capture=True, check=True)
        print("✅ Java verification successful", flush=True)
        
        # Test Nextflow
        rc, out, err = run(f"'{nextflow_path}' -version", env=env, capture=True, check=True)
        print(f"✅ Nextflow verification successful: {out.strip()}", flush=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Dependency verification failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Rest of harmonizer logic
    print("All dependencies installed and verified!", flush=True)
    print("Proceeding with harmonization workflow...", flush=True)

    # Resolve repo directory
    repo_path = Path(args.repo_dir)
    if not repo_path.is_absolute():
        repo_path = (WORKDIR / repo_path).resolve()

    # Verify input exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        sys.exit(2)

    # Create run directory
    run_work = WORKDIR / "harmonizer_run_work"
    if run_work.exists():
        timestamp = int(time.time())
        backup = WORKDIR / f"harmonizer_run_work_backup_{timestamp}"
        print(f"run_work exists; moving to {backup}")
        shutil.move(str(run_work), str(backup))
    run_work.mkdir(parents=True, exist_ok=False)

    # Copy input file
    input_local = run_work / input_path.name
    print(f"Copying input {input_path} -> {input_local}")
    shutil.copy2(str(input_path), str(input_local))

    # Clone or update repository
    if not repo_path.exists():
        print(f"Cloning harmoniser repo {args.repo_url} -> {repo_path}")
        run(f"git clone {args.repo_url} {repo_path}", cwd=WORKDIR, env=env)
    else:
        print(f"Repo exists at {repo_path}; attempting update")
        try:
            run("git fetch --all --prune", cwd=repo_path, env=env)
            run("git pull --ff-only", cwd=repo_path, env=env)
        except subprocess.CalledProcessError:
            print("Warning: git update failed; using existing repo", file=sys.stderr)

    # Add repo to PATH
    env["PATH"] = f"{repo_path}:{env.get('PATH','')}"

    # Check if references need to be built
    ref_dir = Path(args.ref_dir)
    need_refs = not ref_dir.exists() or not any(ref_dir.iterdir())
    
    if need_refs:
        print(f"Reference directory {ref_dir} needs preparation")
        if not ref_dir.exists():
            ref_dir.mkdir(parents=True, exist_ok=True)
        
        logs_dir = run_work / "logs"
        logs_dir.mkdir(exist_ok=True)
        setup_log = logs_dir / "harmonizer_setup.log"
        
        print("Preparing references (this may take a while)...")
        try:
            # First, let's check if the harmonizer setup script exists
            setup_script = repo_path / "harmonizer_setup.sh"
            if setup_script.exists():
                print("Found harmonizer_setup.sh, using it for reference preparation...")
                run(f"chmod +x {setup_script}", env=env, check=True)
                cmd = f"'{setup_script}' --ref '{ref_dir}' --code-repo '{repo_path}'"
            else:
                # Use Nextflow directly
                print("Using Nextflow directly for reference preparation...")
                cmd = f"'{nextflow_path}' run {repo_path} -profile standard --reference --ref '{ref_dir}' --chromlist 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y,MT"
            
            print(f"Running: {cmd}")
            with open(setup_log, "w") as fh:
                proc = subprocess.Popen(cmd, shell=True, cwd=str(run_work), env=env, stdout=fh, stderr=subprocess.STDOUT, text=True)
                proc.wait()
                if proc.returncode != 0:
                    raise subprocess.CalledProcessError(proc.returncode, cmd)
            print(f"Reference preparation completed; log: {setup_log}")
        except subprocess.CalledProcessError as e:
            print(f"Reference preparation failed with exit code {e.returncode}", file=sys.stderr)
            sys.exit(3)
    else:
        print(f"Reference directory {ref_dir} appears ready; skipping preparation")

    # Run harmonization
    run_log = run_work / "harmonizer_run.log"
    print("Running harmonisation workflow...")
    try:
        cmd = (
            f"'{nextflow_path}' run {repo_path} -profile standard "
            f"--harm --ref '{ref_dir}' --file '{input_local}' "
            f"--to_build {args.build} --threshold {args.threshold} "
            f"-with-report '{run_work}/harm-report.html' "
            f"-with-timeline '{run_work}/harm-timeline.html' "
            f"-with-trace '{run_work}/harm-trace.txt' -resume"
        )
        print(f"Running harmonization: {cmd}")
        with open(run_log, "w") as fh:
            proc = subprocess.Popen(cmd, shell=True, cwd=str(run_work), env=env, stdout=fh, stderr=subprocess.STDOUT, text=True)
            proc.wait()
            if proc.returncode != 0:
                raise subprocess.CalledProcessError(proc.returncode, cmd)
        print(f"✅ Harmonisation completed; log: {run_log}")
    except subprocess.CalledProcessError as e:
        print("❌ Harmonisation workflow failed.", file=sys.stderr)
        sys.exit(4)

    # Analyze output structure to understand where files are
    print("\n" + "="*60, flush=True)
    print("SEARCHING FOR HARMONIZED OUTPUT FILES", flush=True)
    print("="*60, flush=True)
    
    potential_files = analyze_output_structure(run_work)

    # Try to create tabular output
    print("\n" + "="*60, flush=True)
    print("CREATING TABULAR OUTPUT", flush=True)
    print("="*60, flush=True)
    
    tabular_file = create_simple_tabular_output(potential_files, WORKDIR)

    # Package raw outputs
    tarball = WORKDIR / "harmonizer_output.tar.gz"
    print(f"\n📦 Packaging raw outputs into {tarball}")
    try:
        run(f"tar -czf '{tarball}' -C '{run_work}' .", env=env, check=True)
        print("✅ Raw output packaging completed")
    except Exception as e:
        print(f"❌ Failed to create raw output package: {e}", file=sys.stderr)
        sys.exit(5)

    # Copy main log for Galaxy
    try:
        top_run_log = WORKDIR / "harmonizer_run.log"
        shutil.copy2(run_log, top_run_log)
    except Exception:
        pass

    print("\n" + "="*60, flush=True)
    print("SUMMARY", flush=True)
    print("="*60, flush=True)
    print(f"📦 Raw output: {tarball}")
    print(f"📋 Analysis report: output_analysis_report.txt")
    if tabular_file:
        print(f"📊 Harmonized data: {tabular_file.name}")
    else:
        print(f"❌ No harmonized data extracted - check analysis report")
    print("✅ Harmonization workflow completed successfully!")
    sys.exit(0)

if __name__ == "__main__":
    main()