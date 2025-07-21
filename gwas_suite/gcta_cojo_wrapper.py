#!/usr/bin/env python3
import argparse
import pandas as pd
import subprocess
import os
import sys
import glob

def run_gcta_cojo(sumstats_file, plink_ref_dir, maf, population, output_file, script_dir):
    """
    Prepares data for GCTA-COJO, runs the analysis for each chromosome via a shell script,
    and combines the results.
    """
    try:
        # --- 1. Prepare Input Data ---
        print("Preparing summary statistics for COJO format...")
        sumstats_df = pd.read_csv(sumstats_file, sep='\t')

        # Select and rename columns for COJO
        cojo_df = sumstats_df[["A1", "A2", "freq", "b", "se", "p", "N"]].copy()
        cojo_df.rename(columns={"freq": "FRQ", "b": "BETA", "p": "P"}, inplace=True)
        cojo_df["SNP"] = sumstats_df["ID"] # Use the ID from the previous step
        cojo_df = cojo_df[['SNP', 'A1', 'A2', 'FRQ', 'BETA', 'SE', 'P', 'N']]

        # Save to a temporary file for the script to use
        cojo_input_path = "cojo_sumstats.txt"
        cojo_df.to_csv(cojo_input_path, sep='\t', index=False)

        # --- 2. Run the GCTA-COJO Shell Script ---
        gcta_script_path = os.path.join(script_dir, "6_gcta_cojo_analysis.sh")
        # The output directory will be the current working directory, which Galaxy provides.
        gcta_out_dir = "." 

        print("Running GCTA-COJO analysis script...")
        cmd = [
            "bash", gcta_script_path,
            gcta_out_dir,
            plink_ref_dir,
            cojo_input_path,
            str(maf),
            population
        ]

        # We run the script and check for errors
        subprocess.check_call(cmd)

        # --- 3. Combine Results ---
        print("Combining COJO results from all chromosomes...")
        # Use glob to find all result files created by the script
        result_files = glob.glob(f"{gcta_out_dir}/*.jma.cojo")
        if not result_files:
            raise FileNotFoundError("No GCTA-COJO result files (.jma.cojo) were found.")

        all_results = []
        for f in result_files:
            df = pd.read_csv(f, sep='\t')
            all_results.append(df)

        combined_df = pd.concat(all_results, ignore_index=True)
        combined_df.to_csv(output_file, sep='\t', index=False)
        print(f"Successfully combined {len(result_files)} result files into final output.")

    except Exception as e:
        sys.exit(f"An error occurred during the GCTA-COJO workflow: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GCTA-COJO analysis wrapper for Galaxy.")
    parser.add_argument("--sumstats", required=True, help="Input summary statistics file.")
    parser.add_argument("--plink_ref", required=True, help="Path to directory with PLINK reference files.")
    parser.add_argument("--maf", required=True, type=float, help="Minor Allele Frequency threshold.")
    parser.add_argument("--population", required=True, help="Reference population (e.g., EUR).")
    parser.add_argument("--output", required=True, help="Final combined output file.")
    # We need to tell the script where to find the other script
    parser.add_argument("--script_dir", required=True, help="Directory containing the bash script.")

    args = parser.parse_args()
    run_gcta_cojo(args.sumstats, args.plink_ref, args.maf, args.population, args.output, args.script_dir)