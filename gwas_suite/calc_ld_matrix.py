#!/usr/bin/env python3
import argparse
import pandas as pd
import subprocess
import os
import sys
import shutil

def calculate_ld_matrix(sumstats_file, plink_ref_dir, chromosome, lead_variant, window_kb, population, output_ld_path, output_snps_path):
    """
    Calculates an LD matrix for a given genomic region using PLINK.
    """
    try:
        # --- 1. Find the PLINK executable ---
        plink_exec = shutil.which("plink")
        if not plink_exec:
            sys.exit("ERROR: 'plink' executable not found. The Conda environment is not activated correctly.")
        print(f"Found PLINK executable at: {plink_exec}")

        # --- 2. Identify SNPs in the target window ---
        print("Reading summary statistics to identify region...")
        df = pd.read_csv(sumstats_file, sep='\t', low_memory=False)
        df.columns = [col.upper() for col in df.columns]

        # Robustly find the SNP identifier column
        if 'SNP' in df.columns:
            snp_col_name = 'SNP'
        elif 'ID' in df.columns:
            snp_col_name = 'ID'
        else:
            raise ValueError("Could not find a 'SNP' or 'ID' column in the summary statistics file.")
        
        # Case-insensitive search for the lead variant
        df['id_lower'] = df[snp_col_name].str.lower()
        lead_variant_lower = lead_variant.lower()

        lead_variant_row = df[df['id_lower'] == lead_variant_lower]
        if lead_variant_row.empty:
            raise ValueError(f"Lead variant '{lead_variant}' not found in the '{snp_col_name}' column.")

        lead_info = lead_variant_row.iloc[0]
        # The chromosome from the data must match the user's input for safety
        if str(lead_info['CHR']) != str(chromosome):
             raise ValueError(f"Lead variant '{lead_variant}' is on CHR {lead_info['CHR']}, but you provided a reference for CHR {chromosome}.")
        
        position = lead_info['BP']

        window_bp = window_kb * 1000
        start_pos = max(0, position - window_bp)
        end_pos = position + window_bp
        print(f"Defining window on CHR {chromosome} from {start_pos} to {end_pos} ({window_kb}kb around {lead_variant}).")

        region_df = df[(df['CHR'] == chromosome) & (df['BP'] >= start_pos) & (df['BP'] <= end_pos)]
        snps_in_region = region_df[snp_col_name].unique().tolist()

        if not snps_in_region:
            raise ValueError("No SNPs found in the specified window.")

        extract_snps_file = "snps_to_extract.txt"
        with open(extract_snps_file, 'w') as f:
            for snp_id in snps_in_region:
                f.write(f"{snp_id}\n")
        print(f"Found {len(snps_in_region)} SNPs in the window. Wrote list to {extract_snps_file}.")

        # --- 3. Run PLINK to calculate LD matrix ---
        plink_prefix = os.path.join(plink_ref_dir, f"{population}.{chromosome}")
        output_prefix = "ld_matrix_plink"

        print(f"Running PLINK with reference: {plink_prefix}")
        cmd = [
            plink_exec,
            "--bfile", plink_prefix,
            "--r", "square", "gz",
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
            if "No variants remain" in process.stderr or "No variants remain" in process.stdout:
                 sys.exit("PLINK Error: None of the SNPs from your file were found in the reference panel.")
            sys.exit("PLINK execution failed.")

        # --- 4. Prepare final output files ---
        plink_output_file = f"{output_prefix}.ld.gz"
        if not os.path.exists(plink_output_file):
            raise FileNotFoundError(f"PLINK did not generate the expected output file: {plink_output_file}")

        os.rename(plink_output_file, output_ld_path)
        # We output the list of SNPs that were actually used by PLINK, which is in the .log file
        # This is more accurate than the requested list.
        plink_snp_list = f"{output_prefix}.log"
        os.rename(plink_snp_list, output_snps_path)
        print("Successfully generated LD matrix and SNP list from PLINK log.")

    except Exception as e:
        sys.exit(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate LD Matrix for a genomic region using PLINK.")
    parser.add_argument("--sumstats", required=True)
    parser.add_argument("--plink_ref_dir", required=True)
    parser.add_argument("--chromosome", required=True, type=int)
    parser.add_argument("--lead_variant", required=True)
    parser.add_argument("--window", required=True, type=int)
    parser.add_argument("--population", required=True)
    parser.add_argument("--output_ld", required=True)
    parser.add_argument("--output_snps", required=True)
    
    args = parser.parse_args()
    calculate_ld_matrix(
        args.sumstats,
        args.plink_ref_dir,
        args.chromosome,
        args.lead_variant,
        args.window,
        args.population,
        args.output_ld,
        args.output_snps
    )
