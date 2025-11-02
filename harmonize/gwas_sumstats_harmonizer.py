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
Version that properly tests if harmonization is actually working.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import tarfile
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

def test_harmonizer_with_small_file(repo_path, nextflow_path, ref_dir, workdir, env):
    """Test the harmonizer with a small test file to see if it actually works"""
    print("\n" + "="*70)
    print("TESTING HARMONIZER WITH SMALL SAMPLE FILE")
    print("="*70)
    
    # Create a small test GWAS file
    test_input = workdir / "test_gwas_data.txt"
    test_content = """SNP\tCHR\tBP\tA1\tA2\tBETA\tSE\tP
rs12345\t1\t100000\tA\tT\t0.123\t0.045\t0.006
rs23456\t1\t200000\tC\tG\t-0.067\t0.032\t0.036
rs34567\t2\t150000\tT\tA\t0.089\t0.028\t0.001
rs45678\t2\t250000\tG\tC\t0.154\t0.067\t0.021
rs56789\t3\t300000\tA\tG\t-0.098\t0.041\t0.017
"""
    
    with open(test_input, 'w') as f:
        f.write(test_content)
    
    print(f"Created test input file: {test_input}")
    print("Test file content:")
    print(test_content)
    
    # Run harmonizer on test file
    test_output_dir = workdir / "test_run"
    test_output_dir.mkdir(exist_ok=True)
    
    cmd = (
        f"'{nextflow_path}' run {repo_path} -profile standard "
        f"--harm --ref '{ref_dir}' --file '{test_input}' "
        f"--to_build GRCh37 --threshold 0.99 "
        f"-with-report '{test_output_dir}/test-report.html' "
        f"-with-trace '{test_output_dir}/test-trace.txt' "
    )
    
    print(f"Running test: {cmd}")
    
    test_log = test_output_dir / "test_harmonizer.log"
    start_time = time.time()
    
    try:
        with open(test_log, 'w') as fh:
            proc = subprocess.Popen(cmd, shell=True, cwd=str(test_output_dir), env=env, 
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            # Read output in real-time
            for line in proc.stdout:
                print(line, end='', flush=True)
                fh.write(line)
                fh.flush()
            
            proc.wait()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\nTest completed in {duration:.2f} seconds with exit code: {proc.returncode}")
        
        # Check for output files
        output_files = list(test_output_dir.rglob("*"))
        data_files = [f for f in output_files if f.is_file() and f.stat().st_size > 100]
        
        print(f"\nFound {len(data_files)} output files in test:")
        for file_path in data_files:
            size_kb = file_path.stat().st_size / 1024
            print(f"  {file_path.relative_to(test_output_dir)} ({size_kb:.1f} KB)")
            
            # Try to read small files
            if size_kb < 10:  # Only read small files
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        print(f"    Content preview: {content[:200]}...")
                except:
                    pass
        
        return proc.returncode, duration, len(data_files) > 0
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        return 1, 0, False

def check_harmonizer_dependencies(repo_path):
    """Check if the harmonizer has all required dependencies"""
    print("\n" + "="*70)
    print("CHECKING HARMONIZER DEPENDENCIES")
    print("="*70)
    
    issues = []
    
    # Check for required files
    required_files = [
        repo_path / "main.nf",
        repo_path / "nextflow.config",
        repo_path / "environment.yml"
    ]
    
    for req_file in required_files:
        if req_file.exists():
            print(f"✓ Found: {req_file.name}")
        else:
            print(f"✗ Missing: {req_file.name}")
            issues.append(f"Missing required file: {req_file.name}")
    
    # Check for modules directory
    modules_dir = repo_path / "modules"
    if modules_dir.exists():
        module_files = list(modules_dir.rglob("*.nf"))
        print(f"✓ Found {len(module_files)} module files")
    else:
        print("✗ Missing modules directory")
        issues.append("Missing modules directory")
    
    # Check for processes
    processes_dir = repo_path / "processes"
    if processes_dir.exists():
        process_files = list(processes_dir.glob("*.nf"))
        print(f"✓ Found {len(process_files)} process files")
    else:
        print("✗ Missing processes directory")
        issues.append("Missing processes directory")
    
    # Check for harmonizer specific files
    harmonizer_files = list(repo_path.rglob("*harmon*"))
    if harmonizer_files:
        print(f"✓ Found {len(harmonizer_files)} harmonizer-related files")
        for f in harmonizer_files[:5]:
            print(f"  - {f.relative_to(repo_path)}")
    else:
        print("✗ No harmonizer-specific files found")
        issues.append("No harmonizer-specific files found")
    
    return issues

def create_minimal_harmonizer_test(repo_path, workdir):
    """Create a minimal test to verify the harmonizer can process data"""
    print("\n" + "="*70)
    print("CREATING MINIMAL HARMONIZER TEST")
    print("="*70)
    
    test_dir = workdir / "minimal_test"
    test_dir.mkdir(exist_ok=True)
    
    # Create a very simple test Nextflow script
    test_script = test_dir / "test_minimal.nf"
    test_content = """#!/usr/bin/env nextflow

params.input_file = "test_data.txt"
params.output_dir = "results"

workflow {
    // Simple test to see if Nextflow works
    channel.fromPath(params.input_file)
        | map { file -> 
            println "Processing file: ${file.name}"
            return file 
          }
        | collect
        | view { files -> "Found files: ${files}" }
}
"""
    
    with open(test_script, 'w') as f:
        f.write(test_content)
    
    # Create test data
    test_data = test_dir / "test_data.txt"
    with open(test_data, 'w') as f:
        f.write("test_line_1\\ntest_line_2\\n")
    
    print(f"Created minimal test in: {test_dir}")
    return test_dir

def main():
    print("=== GWAS Harmonizer - Validation & Testing ===")
    
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
    print(f"Working directory: {WORKDIR}")

    # Check for Java
    java_path = shutil.which("java")
    java_home = None
    
    if not java_path:
        print("Java not found in PATH, attempting local installation...")
        java_path, java_home = install_java_locally(WORKDIR)
    
    if not java_path:
        print("ERROR: Could not install or find Java.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Using Java: {java_path}")
    
    # If we installed Java locally, set up environment
    env = os.environ.copy()
    if java_home:
        env['JAVA_HOME'] = java_home
        env['PATH'] = f"{Path(java_home) / 'bin'}:{env['PATH']}"
        print(f"Set JAVA_HOME to: {java_home}")

    # Check for Nextflow with the updated environment
    nextflow_path = shutil.which("nextflow", path=env['PATH'])
    if not nextflow_path:
        print("Nextflow not found in PATH, attempting local installation...")
        nextflow_path = install_nextflow_locally(WORKDIR, java_home)
    
    if not nextflow_path:
        print("ERROR: Could not install or find Nextflow.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Using Nextflow: {nextflow_path}")
    
    # Add local nextflow to PATH if it's in our workdir
    if WORKDIR in Path(nextflow_path).parents:
        env['PATH'] = f"{WORKDIR}:{env['PATH']}"
        print(f"Added {WORKDIR} to PATH for Nextflow")

    # Verify installations
    try:
        # Test Java
        rc, out, err = run(f"'{java_path}' -version", env=env, capture=True, check=True)
        print("✅ Java verification successful")
        
        # Test Nextflow
        rc, out, err = run(f"'{nextflow_path}' -version", env=env, capture=True, check=True)
        print(f"✅ Nextflow verification successful: {out.strip()}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Dependency verification failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Resolve repo directory
    repo_path = Path(args.repo_dir)
    if not repo_path.is_absolute():
        repo_path = (WORKDIR / repo_path).resolve()

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

    # STEP 1: Check harmonizer dependencies
    dependency_issues = check_harmonizer_dependencies(repo_path)
    
    if dependency_issues:
        print(f"\n❌ Found {len(dependency_issues)} dependency issues:")
        for issue in dependency_issues:
            print(f"  - {issue}")
        print("\nThe harmonizer may not be properly installed or configured.")
    else:
        print(f"\n✅ All basic dependencies found")

    # STEP 2: Test with small file
    print("\n" + "="*70)
    print("MAIN VALIDATION TEST")
    print("="*70)
    
    return_code, duration, has_output = test_harmonizer_with_small_file(
        repo_path, nextflow_path, args.ref_dir, WORKDIR, env
    )
    
    # Analysis of test results
    print("\n" + "="*70)
    print("TEST RESULTS ANALYSIS")
    print("="*70)
    
    if return_code == 0:
        print("✅ Nextflow workflow completed successfully")
    else:
        print("❌ Nextflow workflow failed")
    
    print(f"⏱️  Execution time: {duration:.2f} seconds")
    
    if has_output:
        print("✅ Output files were generated")
    else:
        print("❌ No output files were generated")
    
    if duration < 10:
        print("⚠️  Very short execution time - harmonization may not have actually run")
    
    if not has_output:
        print("⚠️  No output files - harmonization likely failed silently")
    
    # Create diagnostic report
    report_file = WORKDIR / "harmonizer_validation_report.txt"
    with open(report_file, 'w') as f:
        f.write("GWAS Harmonizer Validation Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Repository: {args.repo_url}\n")
        f.write(f"Repository path: {repo_path}\n")
        f.write(f"Dependency issues: {len(dependency_issues)}\n")
        for issue in dependency_issues:
            f.write(f"  - {issue}\n")
        f.write(f"\\nTest execution time: {duration:.2f} seconds\n")
        f.write(f"Test exit code: {return_code}\n")
        f.write(f"Output files generated: {has_output}\n")
        
        if duration < 10 and not has_output:
            f.write("\n❌ CONCLUSION: Harmonizer is NOT working properly\n")
            f.write("   The workflow completes too quickly and produces no output\n")
            f.write("   This suggests the harmonization process is failing silently\n")
        elif has_output:
            f.write("\n✅ CONCLUSION: Harmonizer appears to be working\n")
        else:
            f.write("\n⚠️  CONCLUSION: Inconclusive - needs further investigation\n")
    
    print(f"\n📋 Validation report saved to: {report_file}")
    
    # Only proceed with real harmonization if the test was successful
    if has_output and duration > 10:  # Only if test produced output and took reasonable time
        print("\n" + "="*70)
        print("PROCEEDING WITH REAL HARMONIZATION")
        print("="*70)
        
        # ... rest of harmonization code would go here ...
        print("Real harmonization would run here...")
        
    else:
        print("\n" + "="*70)
        print("SKIPPING REAL HARMONIZATION")
        print("="*70)
        print("The harmonizer test failed, so real harmonization is skipped.")
        print("Check the validation report for details on what went wrong.")
    
    print("\n" + "="*70)
    print("VALIDATION COMPLETE")
    print("="*70)
    print("Check the validation report for detailed results.")
    sys.exit(0 if return_code == 0 else 1)

if __name__ == "__main__":
    main()