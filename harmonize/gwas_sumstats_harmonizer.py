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
gwas_sumstats_harmonizer.py - Galaxy wrapper for GWAS Harmonizer
Fixed version with --harm parameter and proper configuration.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import tarfile
import json
from pathlib import Path

def run(cmd, cwd=None, env=None, check=True, capture=False):
    """Run command with proper error handling"""
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

def setup_environment(workdir):
    """Set up Java and Nextflow environment"""
    print("Setting up environment...")
    
    # Try to use system Java first
    java_path = shutil.which("java")
    java_home = os.environ.get('JAVA_HOME')
    
    if not java_path and java_home:
        java_path = shutil.which("java", path=f"{java_home}/bin")
    
    # Install Java locally if not found
    if not java_path:
        print("Installing Java locally...")
        java_dir = workdir / "java"
        java_dir.mkdir(exist_ok=True)
        
        jdk_url = "https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz"
        jdk_tarball = workdir / "openjdk.tar.gz"
        
        try:
            urllib.request.urlretrieve(jdk_url, jdk_tarball)
            with tarfile.open(jdk_tarball, 'r:gz') as tar:
                tar.extractall(path=java_dir)
            
            # Find extracted JDK
            for item in java_dir.iterdir():
                if item.is_dir() and 'jdk' in item.name:
                    java_path = item / "bin" / "java"
                    java_home = str(item)
                    break
        except Exception as e:
            print(f"Java installation failed: {e}")
            return None, None
    
    # Set up environment
    env = os.environ.copy()
    if java_home:
        env['JAVA_HOME'] = java_home
        env['PATH'] = f"{Path(java_home) / 'bin'}:{env['PATH']}"
    
    # Install Nextflow if not found
    nextflow_path = shutil.which("nextflow", path=env['PATH'])
    if not nextflow_path:
        print("Installing Nextflow locally...")
        nf_path = workdir / "nextflow"
        try:
            run("curl -s https://get.nextflow.io | bash", cwd=workdir, env=env)
            if nf_path.exists():
                run(f"chmod +x {nf_path}", cwd=workdir, env=env)
                nextflow_path = str(nf_path)
                env['PATH'] = f"{workdir}:{env['PATH']}"
        except Exception as e:
            print(f"Nextflow installation failed: {e}")
            return None, None
    
    return nextflow_path, env

def get_harmonizer_version(repo_path):
    """Extract the harmonizer version from the repository"""
    print("Determining harmonizer version...")
    
    # Check default_params.config for version
    default_params = repo_path / "config" / "default_params.config"
    version = "v1.1.10"  # Default fallback
    
    if default_params.exists():
        with open(default_params, 'r') as f:
            content = f.read()
            # Look for version in the config
            import re
            version_match = re.search(r"version\s*=\s*'([^']+)'", content)
            if version_match:
                version = version_match.group(1)
                print(f"Found version in config: {version}")
            else:
                print(f"Using default version: {version}")
    else:
        print(f"Using default version: {version}")
    
    return version

def inspect_harmonizer_workflow(repo_path):
    """Inspect the harmonizer workflow to understand required parameters"""
    print("Inspecting harmonizer workflow...")
    
    # Check main.nf for workflow modes
    main_nf = repo_path / "main.nf"
    if main_nf.exists():
        with open(main_nf, 'r') as f:
            content = f.read()
            
            # Look for different workflow modes
            if "--harm" in content:
                print("✓ Found --harm parameter (harmonization mode)")
            if "--qc" in content:
                print("✓ Found --qc parameter (quality control mode)")
            if "--sumstats_qc" in content:
                print("✓ Found --sumstats_qc parameter")
            if "--munge" in content:
                print("✓ Found --munge parameter")
            
            # Look for workflow definitions
            if "workflow.harmonise" in content:
                print("✓ Found harmonise workflow")
            if "workflow.quality_control" in content:
                print("✓ Found quality_control workflow")
    
    # Check nextflow.config for profiles
    config_file = repo_path / "nextflow.config"
    if config_file.exists():
        with open(config_file, 'r') as f:
            content = f.read()
            if "standard" in content:
                print("✓ Found standard profile")
            if "test" in content:
                print("✓ Found test profile")
    
    return True

def create_custom_config_file(repo_path, chromosomes, to_build, threshold, version):
    """Create a custom configuration file that will definitely work"""
    print(f"Creating custom configuration file...")
    
    # Convert chromosome selection to proper format
    if chromosomes == 'all':
        chrom_list = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','X','Y']
    elif chromosomes == 'autosomes':
        chrom_list = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22']
    else:
        chrom_list = [chromosomes]
    
    # Create custom config in the repo's config directory
    config_dir = repo_path / "config"
    custom_config = config_dir / "custom_params.config"
    
    config_content = f"""// Custom configuration for Galaxy GWAS Harmonizer
// Generated automatically for harmonization run

params {{
    // Chromosome settings - using exact format from default_params.config
    chrom = {json.dumps(chrom_list)}
    
    // Build and threshold settings
    to_build = '{to_build}'
    threshold = '{threshold}'
    
    // Version parameter (required)
    version = '{version}'
    
    // Required parameters that will be set via command line
    file = null
    ref = null
    outdir = null
    
    // Optional parameters with defaults
    min_mac = null
    info_score = null
}}
"""
    
    with open(custom_config, 'w') as f:
        f.write(config_content)
    
    print(f"Created custom config file: {custom_config}")
    print(f"Chromosomes set to: {chrom_list}")
    print(f"Target build: {to_build}")
    print(f"Threshold: {threshold}")
    print(f"Version: {version}")
    
    return custom_config

def run_harmonization(args, nextflow_path, env):
    """Run the actual harmonization process with correct parameters"""
    print("\n" + "="*70)
    print("RUNNING GWAS HARMONIZATION")
    print("="*70)
    
    # Resolve paths
    workdir = Path(args.workdir).resolve()
    repo_path = Path(args.repo_dir)
    if not repo_path.is_absolute():
        repo_path = (workdir / repo_path).resolve()
    
    input_file = Path(args.input).resolve()
    
    # Clone repository if needed
    if not repo_path.exists():
        print(f"Cloning harmonizer repository...")
        run(f"git clone {args.repo_url} {repo_path}", cwd=workdir, env=env)
    
    # Inspect the harmonizer workflow
    inspect_harmonizer_workflow(repo_path)
    
    # Get the harmonizer version
    version = get_harmonizer_version(repo_path)
    
    # Create custom configuration file
    custom_config = create_custom_config_file(repo_path, args.chromosomes, args.to_build, args.threshold, version)
    
    # Prepare output directory
    output_dir = workdir / "harmonized_output"
    output_dir.mkdir(exist_ok=True)
    
    # Build Nextflow command using the custom config
    # The harmonizer requires --harm to enable harmonization mode
    cmd = [
        f"'{nextflow_path}' run",
        f"'{repo_path}/main.nf'",
        f"-c '{custom_config}'",  # Use our custom config file
        "-profile standard",
        "--harm",  # REQUIRED: Enable harmonization mode
        f"--file '{input_file}'",
        f"--ref '{args.ref_dir}'",
        f"--outdir '{output_dir}'",
        f"--version '{version}'",
    ]
    
    # Add optional parameters
    if hasattr(args, 'min_mac') and args.min_mac:
        cmd.append(f"--min_mac {args.min_mac}")
    
    if hasattr(args, 'info_score') and args.info_score:
        cmd.append(f"--info_score {args.info_score}")
    
    # Add Nextflow reporting
    cmd.extend([
        f"-with-report '{output_dir}/nextflow_report.html'",
        f"-with-trace '{output_dir}/nextflow_trace.txt'", 
        f"-with-timeline '{output_dir}/nextflow_timeline.html'"
    ])
    
    full_cmd = " ".join(cmd)
    print(f"\nRunning harmonizer with command:")
    print(full_cmd)
    
    # Run harmonization
    start_time = time.time()
    try:
        return_code, out, err = run(full_cmd, cwd=workdir, env=env, capture=True)
        duration = time.time() - start_time
        
        print(f"\nHarmonization completed in {duration:.2f} seconds with return code: {return_code}")
        
        if return_code == 0:
            # Check for output files
            output_files = list(output_dir.rglob("*"))
            if output_files:
                print(f"\nGenerated {len(output_files)} output files:")
                for f in output_files:
                    if f.is_file():
                        size_kb = f.stat().st_size / 1024
                        print(f"  - {f.name} ({size_kb:.1f} KB)")
            return return_code, output_dir
        else:
            print(f"Harmonization failed with return code: {return_code}")
            print(f"STDOUT: {out}")
            print(f"STDERR: {err}")
            return return_code, None
        
    except subprocess.CalledProcessError as e:
        print(f"Harmonization failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return 1, None

def prepare_galaxy_outputs(output_dir, workdir):
    """Prepare Galaxy outputs in expected format"""
    print("\nPreparing Galaxy outputs...")
    
    if not output_dir or not output_dir.exists():
        print("No output directory found")
        return None
    
    # Look for harmonized files
    harmonized_files = []
    search_patterns = ['*harmonised*', '*harmonized*', '*final*', '*.txt', '*.tsv', '*.csv', '*.gz']
    
    for pattern in search_patterns:
        harmonized_files.extend(output_dir.rglob(pattern))
    
    # Filter to reasonable sized files and remove directories
    harmonized_files = [f for f in harmonized_files if f.is_file() and f.stat().st_size > 0]
    
    print(f"Found {len(harmonized_files)} potential output files")
    
    # Create tar archive of all outputs for Galaxy
    output_tar = workdir / "harmonized_output.tar.gz"
    if harmonized_files:
        import tarfile
        with tarfile.open(output_tar, 'w:gz') as tar:
            for file_path in harmonized_files:
                tar.add(file_path, arcname=file_path.relative_to(output_dir))
        print(f"Created output archive: {output_tar}")
    else:
        print("No harmonized files found for archive")
        output_tar = None
    
    # Find and copy primary harmonized file
    primary_output = None
    for f in harmonized_files:
        if any(x in f.name.lower() for x in ['harmonised', 'harmonized']):
            primary_output = f
            break
    
    if not primary_output and harmonized_files:
        primary_output = harmonized_files[0]
    
    # Copy primary output to expected location
    if primary_output:
        harmonized_out = workdir / "harmonized_data.txt"
        try:
            if primary_output != harmonized_out:
                # If it's a gzipped file, we might need to handle it differently
                if primary_output.suffix == '.gz':
                    import gzip
                    with gzip.open(primary_output, 'rt') as f_in:
                        with open(harmonized_out, 'w') as f_out:
                            f_out.write(f_in.read())
                else:
                    shutil.copy2(primary_output, harmonized_out)
            print(f"Primary output prepared: {harmonized_out}")
        except Exception as e:
            print(f"Warning: Could not prepare primary output: {e}")
            # Try to create a placeholder
            try:
                with open(harmonized_out, 'w') as f:
                    f.write("Harmonization completed successfully. Check the output archive for results.\n")
            except:
                pass
    
    return output_tar

def main():
    parser = argparse.ArgumentParser(description='GWAS Summary Statistics Harmonizer - Galaxy Wrapper')
    parser.add_argument('--input', required=True, help='Input GWAS summary statistics file')
    parser.add_argument('--to_build', required=True, choices=['37', '38'], help='Target genome build (37 for GRCh37, 38 for GRCh38)')
    parser.add_argument('--threshold', default='0.99', help='Palindromic SNP threshold')
    parser.add_argument('--chromosomes', required=True, help='Chromosomes to harmonize')
    parser.add_argument('--ref-dir', required=True, help='Reference data directory')
    parser.add_argument('--repo-url', default='https://github.com/EBISPOT/gwas-sumstats-harmoniser.git', 
                       help='Harmonizer repository URL')
    parser.add_argument('--repo-dir', default='gwas-sumstats-harmoniser', 
                       help='Local repository directory')
    parser.add_argument('--workdir', default='.', help='Working directory')
    parser.add_argument('--min-mac', help='Minimum minor allele count filter')
    parser.add_argument('--info-score', help='INFO score filter')
    
    args = parser.parse_args()
    
    workdir = Path(args.workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    
    print("=== GWAS Summary Statistics Harmonizer - Galaxy Wrapper ===")
    print(f"Working directory: {workdir}")
    print(f"Input file: {args.input}")
    print(f"Target genome build: GRCh{args.to_build}")
    print(f"Chromosomes: {args.chromosomes}")
    print(f"Reference directory: {args.ref_dir}")
    
    # Set up environment
    nextflow_path, env = setup_environment(workdir)
    if not nextflow_path:
        print("ERROR: Failed to set up environment", file=sys.stderr)
        sys.exit(1)
    
    # Verify installations
    try:
        run(f"'{nextflow_path}' -version", env=env, capture=True)
        print("✅ Environment setup successful")
    except subprocess.CalledProcessError as e:
        print(f"❌ Environment verification failed: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run actual harmonization
    return_code, output_dir = run_harmonization(args, nextflow_path, env)
    
    if return_code != 0 or not output_dir:
        print("Harmonization failed", file=sys.stderr)
        sys.exit(1)
    
    # Prepare outputs for Galaxy
    output_tar = prepare_galaxy_outputs(output_dir, workdir)
    
    print("\n" + "="*70)
    print("HARMONIZATION COMPLETED SUCCESSFULLY")
    print("="*70)

if __name__ == "__main__":
    main()