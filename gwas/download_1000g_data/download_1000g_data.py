#!/usr/bin/env python3

import argparse
import subprocess
import os

def run_scripts(scripts, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for script in scripts:
        print(f"Running script: {script}")
        result = subprocess.run(["bash", script, output_dir], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running {script}:\n{result.stderr}")
            exit(1)
        else:
            print(f"{script} output:\n{result.stdout}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", required=True, help="Output directory for 1000G data.")
    args = parser.parse_args()

    scripts = [
        os.path.join("scripts", "1000Genomes_phase3", "1_download_vcfs.sh"),
        os.path.join("scripts", "1000Genomes_phase3", "2_normalise_vcfs.sh"),
        os.path.join("scripts", "1000Genomes_phase3", "3_make_population_ids.sh"),
        os.path.join("scripts", "1000Genomes_phase3", "4_convert_to_plink.sh")
    ]

    run_scripts(scripts, args.output_dir)

if __name__ == "__main__":
    main()
