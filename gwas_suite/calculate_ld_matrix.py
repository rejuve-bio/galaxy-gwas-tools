#!/usr/bin/env python3
import argparse
import pandas as pd
import subprocess
import os
import sys

def calculate_ld_matrix(sumstats_file, plink_ref_dir, lead_variant, window_kb, population, output_ld_path, output_snps_path):
    """
    Calculates an LD matrix for a given genomic region using PLINK.
    """
    try:
        # --- 1. Identify SNPs in the target window ---
        print("Reading summary statistics to identify region...")
        df = pd.read_csv(sumstats_file, sep='\t', low_memory=False)
        df.columns = [col.lower() for col in df.columns]

        # Find the lead variant to define the center of the window
        lead_variant_row = df[df['id'] == lead_variant]
        if lead_variant_row.empty:
            lead_variant_row = df[df['snp'] == lead_variant] # Fallback to 'snp' column

        if lead_variant_row.empty:
            raise ValueError(f"Lead variant '{lead_variant}' not found in the 'id' or 'snp' column of the summary statistics file.")

        # Get chromosome and position from the first match
        lead_info = lead_variant_row.iloc[0]
        chrom = lead_info['chr']
        position = lead_info['bp']

        window_bp = window_kb * 1000
        start_pos = max(0, position - window_bp)
        end_pos = position + window_bp

        print(f"Defining window on CHR {chrom} from {start_pos} to {end_pos} ({window_kb}kb around {lead_variant}).")

        # Filter for SNPs within this window
        region_df = df[(df['chr'] == chrom) & (df['bp'] >= start_pos) & (df['bp'] <= end_pos)]
        snps_in_region = region_df['id'].unique().tolist()

        if not snps_in_region:
            raise ValueError("No SNPs found in the specified window.")

        # Write the list of SNPs to a temporary file for PLINK
        extract_snps_file = "snps_to_extract.txt"
        with open(extract_snps_file, 'w') as f:
            for snp_id in snps_in_region:
                f.write(f"{snp_id}\n")

        print(f"Found {len(snps_in_region)} SNPs in the window. Wrote list to {extract_snps_file}.")

        # --- 2. Run PLINK to calculate LD matrix ---
        plink_prefix = os.path.join(plink_ref_dir, f"{population}.{int(chrom)}")
        output_prefix = "ld_matrix_plink"

        print(f"Running PLINK with reference: {plink_prefix}")
        cmd = [
            "plink",
            "--bfile", plink_prefix,
            "--r", "square", "gz", # Output gzipped square matrix (r-squared values)
            "--extract", extract_snps_file,
            "--out", output_prefix
        ]

        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode != 0:
            print("ERROR: PLINK command failed.", file=sys.stderr)
            print("--- PLINK Standard Output ---", file=sys.stderr)
            print(process.stdout, file=sys.stderr)
            print("--- PLINK Standard Error ---", file=sys.stderr)
            print(process.stderr, file=sys.stderr)
            # Check for a common error: no variants remaining
            if "No variants remain" in process.stderr or "No variants remain" in process.stdout:
                 sys.exit("PLINK Error: None of the SNPs from the specified region were found in the reference panel.")
            sys.exit("PLINK execution failed.")

        # --- 3. Prepare final output files ---
        # PLINK outputs a file with the .ld.gz extension
        plink_output_file = f"{output_prefix}.ld.gz"
        if not os.path.exists(plink_output_file):
            raise FileNotFoundError(f"PLINK did not generate the expected output file: {plink_output_file}")

        # The list of SNPs actually used by PLINK is in the .log file or can be inferred.
        # For simplicity, we will provide the list of SNPs we requested.
        os.rename(plink_output_file, output_ld_path)
        os.rename(extract_snps_file, output_snps_path)

        print("Successfully generated LD matrix.")

    except Exception as e:
        sys.exit(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate LD Matrix for a genomic region using PLINK.")
    parser.add_argument("--sumstats", required=True, help="Input summary statistics file.")
    parser.add_argument("--plink_ref_dir", required=True, help="Directory containing PLINK reference files.")
    parser.add_argument("--lead_variant", required=True, help="ID of the lead variant to center the window on.")
    parser.add_argument("--window", required=True, type=int, help="Window size in kilobases (kb) around the lead variant.")
    parser.add_argument("--population", required=True, help="Population prefix of the PLINK files (e.g., EUR).")
    parser.add_argument("--output_ld", required=True, help="Path for the output LD matrix file.")
    parser.add_argument("--output_snps", required=True, help="Path for the output SNP list file.")

    args = parser.parse_args()
    calculate_ld_matrix(
        args.sumstats,
        args.plink_ref_dir,
        args.lead_variant,
        args.window,
        args.population,
        args.output_ld,
        args.output_snps
    )