#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import shutil
import tarfile
import urllib.request
from pathlib import Path

def ensure_java(repo_dir: Path):
    """Ensure Java 17 is available; download portable JDK if needed."""
    java_path = shutil.which("java")
    if java_path:
        print(f"✅ Java found: {java_path}")
        return java_path

    print("⚠️  Java not found. Installing portable OpenJDK 17...")

    java_dir = repo_dir / "java17"
    java_bin = java_dir / "bin" / "java"
    if java_bin.exists():
        os.environ["PATH"] = f"{java_dir}/bin:" + os.environ["PATH"]
        print(f"✅ Using existing local Java at {java_bin}")
        return str(java_bin)

    # Robust set of fallback URLs
    jdk_urls = [
        "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.13%2B11/OpenJDK17U-jdk_x64_linux_hotspot_17.0.13_11.tar.gz",
        "https://cdn.azul.com/zulu/bin/zulu17.46.19-ca-jdk17.0.9-linux_x64.tar.gz",
        "https://corretto.aws/downloads/latest/amazon-corretto-17-x64-linux-jdk.tar.gz"
    ]

    tar_path = repo_dir / "openjdk17.tar.gz"
    for url in jdk_urls:
        try:
            print(f"⬇️  Trying {url}")
            urllib.request.urlretrieve(url, tar_path)
            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(path=repo_dir)
            os.remove(tar_path)
            # Find extracted directory
            extracted_dirs = list(repo_dir.glob("jdk*")) + list(repo_dir.glob("zulu*")) + list(repo_dir.glob("amazon*"))
            if not extracted_dirs:
                raise FileNotFoundError("No extracted JDK folder found after unpacking.")
            extracted = extracted_dirs[0]
            extracted.rename(java_dir)
            os.environ["PATH"] = f"{java_dir}/bin:" + os.environ["PATH"]
            print(f"✅ Java installed locally at {java_dir}")
            return str(java_bin)
        except Exception as e:
            print(f"⚠️  Failed to install from {url}: {e}")
            continue

    sys.exit("❌ All Java download attempts failed. Please install Java 17 manually or provide JAVA_HOME.")


def ensure_nextflow(repo_dir: Path):
    """Ensure Nextflow is installed and executable."""
    nextflow_path = shutil.which("nextflow")
    if nextflow_path:
        print(f"✅ Nextflow found: {nextflow_path}")
        return nextflow_path

    local_nf = repo_dir / "nextflow"
    if local_nf.exists():
        print(f"✅ Using existing local Nextflow: {local_nf}")
        return str(local_nf)

    print("⚠️  Nextflow not found. Installing locally...")
    try:
        subprocess.run(
            ["curl", "-sL", "https://get.nextflow.io", "-o", "nextflow_installer.sh"],
            check=True
        )
        subprocess.run(["bash", "nextflow_installer.sh"], check=True)
        shutil.move("nextflow", str(local_nf))
        os.remove("nextflow_installer.sh")
        os.chmod(local_nf, 0o755)
        print(f"✅ Nextflow installed at {local_nf}")
        return str(local_nf)
    except subprocess.CalledProcessError as e:
        sys.exit(f"❌ Error installing Nextflow: {e}")

def main():
    parser = argparse.ArgumentParser(description="GWAS Harmonizer Setup Wrapper")
    parser.add_argument("--code-repo", required=True, help="Path to harmonizer code repository")
    parser.add_argument("--ref-dir", required=True, help="Reference data directory")
    parser.add_argument("--chromlist", default="1,2,3,...,22,X,Y,MT", help="Chromosome list")
    args = parser.parse_args()

    repo = Path(args.code_repo)
    ref_dir = Path(args.ref_dir)
    ref_dir.mkdir(parents=True, exist_ok=True)
    log_dir = ref_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    print(f"🧬 GWAS Harmonizer Setup")
    print(f"Repository: {repo}")
    print(f"Reference dir: {ref_dir}")
    print(f"Chromosomes: {args.chromlist}")
    print(f"Logs: {log_dir}")

    # Ensure dependencies
    ensure_java(repo)
    nextflow_bin = ensure_nextflow(repo)

    # Run Nextflow
    cmd = [
        nextflow_bin, "run", str(repo),
        "-profile", "standard",
        "--reference",
        "--ref", str(ref_dir),
        "--chromlist", args.chromlist,
        "-with-report", str(log_dir / "ref-report.html"),
        "-with-timeline", str(log_dir / "ref-timeline.html"),
        "-with-trace", str(log_dir / "ref-trace.txt"),
        "-with-dag", str(log_dir / "ref-dag.html")
    ]

    print(f"🚀 Running Nextflow pipeline...")
    with open(log_dir / "ref.log", "w") as log_f:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end="")
            log_f.write(line)
        process.wait()

    if process.returncode != 0:
        sys.exit(f"❌ Nextflow failed with exit code {process.returncode}")

    print("✅ Harmonizer setup completed successfully!")

    # Outputs for Galaxy
    with open("log_dir.txt", "w") as f:
        f.write(str(log_dir))
    shutil.copy2(log_dir / "ref-report.html", "report.html")
    shutil.copy2(log_dir / "ref-timeline.html", "timeline.html")

if __name__ == "__main__":
    main()
