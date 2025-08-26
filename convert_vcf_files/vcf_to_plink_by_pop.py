#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
import pandas as pd

PANEL_URL = "http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/integrated_call_samples_v3.20130502.ALL.panel"

def vcf_to_plink(input_vcf, population, output_prefix):
    """
    Filters a VCF for a specific population and converts it to PLINK format.
    """
    try:
        # --- 1. Download and process the population panel file ---
        panel_file = "1000G_panel.panel"
        print(f"Downloading 1000 Genomes population panel from: {PANEL_URL}")
        subprocess.run(["wget", "-O", panel_file, PANEL_URL], check=True)

        print(f"Filtering for samples in the '{population}' super-population...")
        df = pd.read_csv(panel_file, sep='\t')

        samples_in_pop = df[df['super_pop'] == population]['sample'].tolist()

        if not samples_in_pop:
            raise ValueError(f"No samples found for population '{population}'. Check the population code.")

        keep_file = "samples_to_keep.txt"
        with open(keep_file, 'w') as f:
            for sample_id in samples_in_pop:
                # --- THIS IS THE FIX ---
                # Write the sample ID twice for FID and IID columns
                f.write(f"{sample_id} {sample_id}\n")

        print(f"Found {len(samples_in_pop)} samples. Wrote list to {keep_file}.")

        # --- 2. Run PLINK to filter and convert ---
        print("Running PLINK to convert VCF to BED/BIM/FAM format...")

        cmd = [
            "plink",
            "--vcf", input_vcf,
            "--keep", keep_file,
            "--make-bed",
            "--allow-extra-chr",
            "--out", output_prefix
        ]

        subprocess.run(cmd, check=True)
        print(f"PLINK conversion complete. Files created with prefix: {output_prefix}")

    except subprocess.CalledProcessError as e:
        print(f"ERROR: A command failed to execute.", file=sys.stderr)
        print(f"Command: {' '.join(e.cmd)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        sys.exit(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter VCF by population and convert to PLINK format.")
    parser.add_argument("--vcf", required=True, help="Input normalized VCF.gz file.")
    parser.add_argument("--population", required=True, help="Super-population code (e.g., EUR, AFR, EAS, SAS, AMR).")
    parser.add_argument("--output_prefix", required=True, help="Prefix for the output PLINK files.")

    args = parser.parse_args()

    vcf_to_plink(
        args.vcf,
        args.population,
        args.output_prefix
    )