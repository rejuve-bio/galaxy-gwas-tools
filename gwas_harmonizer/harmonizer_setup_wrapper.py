#!/usr/bin/env python3
import os, sys, argparse, subprocess, shutil, tarfile, urllib.request
from pathlib import Path

def run(cmd, cwd=None, env=None, check=True):
    """Run shell command with clean output and error checking."""
    print(f"> {cmd}", flush=True)
    res = subprocess.run(cmd, shell=True, cwd=cwd, env=env)
    if check and res.returncode != 0:
        sys.exit(f"❌ Command failed: {cmd} (exit {res.returncode})")
    return res

# -------------------------------------------------------
#  Install Java 17 (portable)
# -------------------------------------------------------
def install_java(workdir):
    java_dir = Path(workdir) / "java17"
    java_bin = java_dir / "bin" / "java"

    if shutil.which("java"):
        java_path = shutil.which("java")
        print(f"✅ Java found: {java_path}")
        return str(java_path), None

    if java_bin.exists():
        print(f"✅ Using existing local Java at {java_bin}")
        return str(java_bin), str(java_dir)

    print("⚠️  Java not found. Installing portable OpenJDK 17...")

    java_dir.mkdir(parents=True, exist_ok=True)
    jdk_url = "https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz"
    tar_path = Path(workdir) / "openjdk17.tar.gz"

    try:
        urllib.request.urlretrieve(jdk_url, tar_path)
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=java_dir)
        os.remove(tar_path)
        extracted = [p for p in java_dir.iterdir() if p.is_dir() and "jdk" in p.name]
        if not extracted:
            raise RuntimeError("JDK not extracted properly")
        jdk_home = extracted[0]
        java_bin = jdk_home / "bin" / "java"
        if not java_bin.exists():
            raise FileNotFoundError("java binary not found after extraction")
        print(f"✅ Java installed: {java_bin}")
        return str(java_bin), str(jdk_home)
    except Exception as e:
        sys.exit(f"❌ Java installation failed: {e}")

# -------------------------------------------------------
#  Install Nextflow (portable)
# -------------------------------------------------------
def install_nextflow(workdir, java_home=None):
    nf_path = shutil.which("nextflow")
    if nf_path:
        print(f"✅ Nextflow found: {nf_path}")
        return nf_path

    nf_local = Path(workdir) / "nextflow"
    if nf_local.exists():
        print(f"✅ Using existing local Nextflow: {nf_local}")
        return str(nf_local)

    print("⚠️  Nextflow not found. Installing locally...")
    env = os.environ.copy()
    if java_home:
        env["JAVA_HOME"] = java_home
        env["PATH"] = f"{Path(java_home)/'bin'}:{env['PATH']}"

    try:
        run("curl -s https://get.nextflow.io | bash", cwd=workdir, env=env)
        if not nf_local.exists():
            raise FileNotFoundError("Nextflow binary missing after installation")
        nf_local.chmod(0o755)
        print(f"✅ Nextflow installed at {nf_local}")
        return str(nf_local)
    except Exception as e:
        sys.exit(f"❌ Nextflow installation failed: {e}")

# -------------------------------------------------------
#  Verify tools
# -------------------------------------------------------
def verify_tools(java_path, nf_path, env):
    print("🔍 Verifying environment...")
    run(f"'{java_path}' -version", env=env)
    run(f"'{nf_path}' -version", env=env)
    print("✅ Verification successful")

# -------------------------------------------------------
#  Main execution
# -------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="GWAS Harmonizer Setup Wrapper")
    parser.add_argument("--code-repo", required=True, help="Path to harmonizer code repository")
    parser.add_argument("--ref-dir", required=True, help="Reference data directory")
    parser.add_argument("--chromlist", required=True, help="Comma-separated chromosome list")
    args = parser.parse_args()

    repo = Path(args.code_repo).resolve()
    ref_dir = Path(args.ref_dir).resolve()
    log_dir = ref_dir / "logs"
    ref_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    print("🧬 GWAS Harmonizer Setup")
    print(f"Repository: {repo}")
    print(f"Reference dir: {ref_dir}")
    print(f"Chromosomes: {args.chromlist}")
    print(f"Logs: {log_dir}")

    # Install dependencies
    java_path, java_home = install_java(repo)
    nf_path = install_nextflow(repo, java_home)

    env = os.environ.copy()
    if java_home:
        env["JAVA_HOME"] = java_home
        env["PATH"] = f"{Path(java_home)/'bin'}:{env['PATH']}"
    env["PATH"] = f"{repo}:{env['PATH']}"

    verify_tools(java_path, nf_path, env)

    # Run Nextflow
    cmd = (
        f"'{nf_path}' run '{repo}' "
        f"-profile standard --reference "
        f"--ref '{ref_dir}' --chromlist '{args.chromlist}' "
        f"-with-report '{log_dir}/ref-report.html' "
        f"-with-timeline '{log_dir}/ref-timeline.html' "
        f"-with-trace '{log_dir}/ref-trace.txt' "
        f"-with-dag '{log_dir}/ref-dag.html'"
    )

    print("🚀 Running Nextflow pipeline...")
    with open(log_dir / "ref.log", "w") as log_f:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
        for line in process.stdout:
            print(line, end="")
            log_f.write(line)
        process.wait()

    if process.returncode != 0:
        sys.exit(f"❌ Nextflow failed with exit code {process.returncode}")

    print("✅ Harmonizer setup completed successfully!")

    # Galaxy outputs
    with open("log_dir.txt", "w") as f:
        f.write(str(log_dir))
    shutil.copy2(log_dir / "ref-report.html", "report.html")
    shutil.copy2(log_dir / "ref-timeline.html", "timeline.html")

if __name__ == "__main__":
    main()
