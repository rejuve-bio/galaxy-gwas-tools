#!/usr/bin/env python3
import argparse
import pandas as pd
import subprocess
import os
import sys
import shutil

def calculate_ld_matrix(sumstats_file, plink_ref_dir, chromosome, lead_variant, window_kb, population, output_ld_path, output_snps_path):
    """
    Calculates an LD matrix and outputs a clean list of SNPs used.
    """
    try:
        # Find PLINK executable in system PATH
        plink_exec = shutil.which("plink")
        if plink_exec is None:
            # As a fallback for your specific setup, check the hardcoded path
            hardcoded_path = "/home/icog-bioai2/miniconda3/bin/plink"
            if os.path.exists(hardcoded_path):
                plink_exec = hardcoded_path
            else:
                sys.exit("ERROR: PLINK executable not found. Please install PLINK or ensure it is in your PATH.")
        print(f"Using PLINK executable at: {plink_exec}")

        # --- Identify SNPs in the target window ---
        print("Reading summary statistics to identify region...")
        df = pd.read_csv(sumstats_file, sep='\t', low_memory=False)
        df.columns = [col.upper() for col in df.columns]

        if 'SNP' in df.columns:
            snp_col_name = 'SNP'
        elif 'ID' in df.columns:
            snp_col_name = 'ID'
        else:
            raise ValueError("Could not find a 'SNP' or 'ID' column in the summary statistics file.")
        
        df['id_lower'] = df[snp_col_name].str.lower()
        lead_variant_lower = lead_variant.lower()
        lead_variant_row = df[df['id_lower'] == lead_variant_lower]
        if lead_variant_row.empty:
            raise ValueError(f"Lead variant '{lead_variant}' not found in the '{snp_col_name}' column.")

        lead_info = lead_variant_row.iloc[0]
        if str(lead_info['CHR']) != str(chromosome):
             raise ValueError(f"Lead variant '{lead_variant}' is on CHR {lead_info['CHR']}, but you provided a reference for CHR {chromosome}.")
        position = lead_info['BP']

        window_bp = window_kb * 1000
        start_pos = max(0, position - window_bp)
        end_pos = position + window_bp
        print(f"Defining window on CHR {chromosome} from {start_pos} to {end_pos}.")

        region_df = df[(df['CHR'] == int(chromosome)) & (df['BP'] >= start_pos) & (df['BP'] <= end_pos)]
        snps_in_region = region_df[snp_col_name].unique().tolist()

        if not snps_in_region:
            print("No SNPs from the summary statistics file were found in the specified window.")
            with open(output_ld_path, 'w') as f: f.write("")
            with open(output_snps_path, 'w') as f: f.write("# No SNPs found in window\n")
            sys.exit()

        extract_snps_file = "snps_to_extract.txt"
        with open(extract_snps_file, 'w') as f:
            for snp_id in snps_in_region:
                f.write(f"{snp_id}\n")
        print(f"Found {len(snps_in_region)} SNPs in the window.")

        # --- Run PLINK to calculate LD matrix ---
        plink_prefix = os.path.join(plink_ref_dir, f"{population}.{chromosome}")
        output_prefix = "ld_matrix_plink"

        print(f"Running PLINK with reference: {plink_prefix}")
        # Add --make-bed flag to create a new .bim file with only the extracted SNPs
        cmd = [
            plink_exec, "--bfile", plink_prefix, "--r", "square", "gz",
            "--extract", extract_snps_file, "--out", output_prefix, "--make-bed"
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True)
        if "No variants remain" in process.stdout or "No variants remain" in process.stderr:
            print("PLINK Warning: None of the SNPs from your file were found in the reference panel.")
            with open(output_ld_path, 'w') as f: f.write("")
            with open(output_snps_path, 'w') as f: f.write("# None of the requested SNPs were found in the reference panel.\n")
            sys.exit()

        if process.returncode != 0:
            print("ERROR: PLINK command failed.", file=sys.stderr)
            print("--- PLINK STDOUT ---", file=sys.stderr); print(process.stdout, file=sys.stderr)
            print("--- PLINK STDERR ---", file=sys.stderr); print(process.stderr, file=sys.stderr)
            sys.exit("PLINK execution failed.")

        # --- Prepare final output files ---
        plink_output_file = f"{output_prefix}.ld.gz"
        if not os.path.exists(plink_output_file):
            raise FileNotFoundError(f"PLINK did not generate the expected output file: {plink_output_file}")
        os.rename(plink_output_file, output_ld_path)
        
        # --- THIS IS THE NEW LOGIC ---
        # Read the .bim file that PLINK created, which contains only the SNPs it actually used.
        plink_bim_file = f"{output_prefix}.bim"
        if os.path.exists(plink_bim_file):
            final_snps_df = pd.read_csv(plink_bim_file, sep='\t', header=None, usecols=[1])
            final_snps_df.to_csv(output_snps_path, header=False, index=False)
            print(f"Successfully generated LD matrix and a clean SNP list with {len(final_snps_df)} SNPs.")
        else:
            raise FileNotFoundError(f"PLINK did not generate the filtered BIM file needed for the SNP list: {plink_bim_file}")

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
    parser.add_argument("--output_snps", required=True) # Changed from output_log
    
    args = parser.parse_args()
    calculate_ld_matrix(
        args.sumstats, args.plink_ref_dir, args.chromosome,
        args.lead_variant, args.window, args.population,
        args.output_ld, args.output_snps # Changed from output_log
    )
