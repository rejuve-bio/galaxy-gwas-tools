# import os
# import subprocess
# import urllib.request
# import zipfile
# import stat

# def download_and_prepare_gcta(download_dir):
#     url = "http://cnsgenomics.com/software/gcta/gcta_1.93.2beta.zip"
#     zip_path = os.path.join(download_dir, "gcta.zip")
#     gcta_bin = os.path.join(download_dir, "gcta64")

#     if os.path.exists(gcta_bin):
#         return gcta_bin  # already downloaded

#     print("Downloading GCTA...")
#     urllib.request.urlretrieve(url, zip_path)

#     print("Unzipping...")
#     with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#         zip_ref.extractall(download_dir)

#     # Ensure executable
#     st = os.stat(gcta_bin)
#     os.chmod(gcta_bin, st.st_mode | stat.S_IEXEC)

#     return gcta_bin

# def main():
#     temp_dir = os.getcwd()  # or use tempfile if needed
#     gcta_path = download_and_prepare_gcta(temp_dir)

#     subprocess.run([
#         gcta_path,
#         "--bfile", "plink_input",
#         "--cojo-file", "cojo_input.dat",
#         "--cojo-slct",
#         "--out", "cojo_output"
#     ], check=True)

# if __name__ == "__main__":
#     main()
    
    
    
    


#!/usr/bin/env python3
import os
import subprocess
import urllib.request
import zipfile
import stat
import sys
import glob

# GCTA_URL = "http://cnsgenomics.com/software/gcta/gcta_1.93.2beta.zip"
GCTA_URL = "https://yanglab.westlake.edu.cn/software/gcta/bin/gcta-1.95.0-linux-kernel-3-x86_64.zip"


def download_and_prepare_gcta(download_dir):
    zip_path = os.path.join(download_dir, "gcta.zip")
    print("📥 Downloading GCTA from:", GCTA_URL)
    urllib.request.urlretrieve(GCTA_URL, zip_path)

    print("📦 Extracting GCTA...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(download_dir)

    # find the gcta64 binary inside the extracted directory
    candidates = glob.glob(os.path.join(download_dir, "**", "gcta64"), recursive=True)
    if not candidates:
        sys.exit("ERROR: Could not find gcta64 binary after extraction.")
    
    gcta_bin = candidates[0]
    print(f"✅ Found GCTA binary at: {gcta_bin}")

    # ensure executable permissions
    st = os.stat(gcta_bin)
    os.chmod(gcta_bin, st.st_mode | stat.S_IEXEC)
    return gcta_bin

def main():
    temp_dir = os.getcwd()
    gcta_path = download_and_prepare_gcta(temp_dir)

    cmd = [
        gcta_path,
        "--bfile", "plink_input",
        "--cojo-file", "cojo_input.dat",
        "--cojo-slct",
        "--out", "cojo_output"
    ]
    print("🚀 Running GCTA COJO...")
    try:
        subprocess.run(cmd, check=True)
        print("✅ GCTA COJO completed successfully.")
    except subprocess.CalledProcessError as e:
        print("❌ GCTA failed to run.", file=sys.stderr)
        print(f"Command: {' '.join(e.cmd)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
