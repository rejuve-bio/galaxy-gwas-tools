import os
import subprocess
import urllib.request
import zipfile
import stat

def download_and_prepare_gcta(download_dir):
    url = "http://cnsgenomics.com/software/gcta/gcta_1.93.2beta.zip"
    zip_path = os.path.join(download_dir, "gcta.zip")
    gcta_bin = os.path.join(download_dir, "gcta64")

    if os.path.exists(gcta_bin):
        return gcta_bin  # already downloaded

    print("Downloading GCTA...")
    urllib.request.urlretrieve(url, zip_path)

    print("Unzipping...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(download_dir)

    # Ensure executable
    st = os.stat(gcta_bin)
    os.chmod(gcta_bin, st.st_mode | stat.S_IEXEC)

    return gcta_bin

def main():
    temp_dir = os.getcwd()  # or use tempfile if needed
    gcta_path = download_and_prepare_gcta(temp_dir)

    subprocess.run([
        gcta_path,
        "--bfile", "plink_input",
        "--cojo-file", "cojo_input.dat",
        "--cojo-slct",
        "--out", "cojo_output"
    ], check=True)

if __name__ == "__main__":
    main()
    