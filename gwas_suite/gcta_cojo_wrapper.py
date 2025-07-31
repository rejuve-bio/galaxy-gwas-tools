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
        sumstats_df = pd.read_csv(sumstats_file, sep='\t', low_memory=False)

        # Normalize column names to lowercase for robust matching
        original_columns = list(sumstats_df.columns)
        sumstats_df.columns = [col.lower() for col in original_columns]
        
        # --- THIS IS THE FIX ---
        # Check if 'snp' column exists. If not, check for 'id'.
        if 'snp' in sumstats_df.columns:
            snp_col_name = 'snp'
            print("Found 'snp' column for SNP identifiers.")
        elif 'id' in sumstats_df.columns:
            snp_col_name = 'id'
            print("Found 'id' column for SNP identifiers.")
        else:
            raise ValueError("Could not find a 'SNP' or 'ID' column in the summary statistics file.")
        
        # Define required columns and check for their presence
        required_cols = ["a1", "a2", "frq", "beta", "se", "p", "n"]
        if not all(col in sumstats_df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in sumstats_df.columns]
            raise ValueError(f"Input summary statistics file is missing required columns: {missing}")

        # Select columns using their lowercase names
        cojo_df = sumstats_df[["a1", "a2", "frq", "beta", "se", "p", "n"]].copy()
        # Rename them to the uppercase versions GCTA expects
        cojo_df.rename(columns={"frq": "FRQ", "beta": "BETA", "se":"SE", "p": "P", "a1": "A1", "a2": "A2", "n": "N"}, inplace=True)
        
        # Use the correct column for the SNP identifier
        cojo_df["SNP"] = sumstats_df[snp_col_name]
        
        cojo_df = cojo_df[['SNP', 'A1', 'A2', 'FRQ', 'BETA', 'SE', 'P', 'N']]

        cojo_input_path = "cojo_sumstats.txt"
        cojo_df.to_csv(cojo_input_path, sep='\t', index=False)

        # --- 2. Run the GCTA-COJO Shell Script ---
        gcta_script_path = os.path.join(script_dir, "6_gcta_cojo_analysis.sh")
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

        process = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("--- GCTA Script Standard Output ---")
        print(process.stdout)
        print("--- GCTA Script Standard Error ---")
        print(process.stderr)

        # --- 3. Combine Results ---
        print("Combining COJO results from all chromosomes...")
        result_files = glob.glob(f"{gcta_out_dir}/*.jma.cojo")
        if not result_files:
            result_files = glob.glob(f"{gcta_out_dir}/*.cma.cojo")
        if not result_files:
            raise FileNotFoundError("No GCTA-COJO result files (.jma.cojo or .cma.cojo) were found.")

        all_results = []
        for f in result_files:
            df = pd.read_csv(f, sep='\t')
            all_results.append(df)

        combined_df = pd.concat(all_results, ignore_index=True)
        combined_df.to_csv(output_file, sep='\t', index=False)
        print(f"Successfully combined {len(result_files)} result files into final output.")

    except subprocess.CalledProcessError as e:
        print("ERROR: The GCTA shell script failed to execute.", file=sys.stderr)
        print("--- GCTA Script Standard Output ---", file=sys.stderr)
        print(e.stdout, file=sys.stderr)
        print("--- GCTA Script Standard Error ---", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        sys.exit(f"An error occurred during the GCTA-COJO workflow: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GCTA-COJO analysis wrapper for Galaxy.")
    parser.add_argument("--sumstats", required=True, help="Input summary statistics file.")
    parser.add_argument("--plink_ref_dir", required=True, help="Path to directory with PLINK reference files.")
    parser.add_argument("--maf", required=True, type=float, help="Minor Allele Frequency threshold.")
    parser.add_argument("--population", required=True, help="Reference population (e.g., EUR).")
    parser.add_argument("--output", required=True, help="Final combined output file.")
    parser.add_argument("--script_dir", required=True, help="Directory containing the bash script.")

    args = parser.parse_args()
    run_gcta_cojo(args.sumstats, args.plink_ref_dir, args.maf, args.population, args.output, args.script_dir)






# #!/usr/bin/env python3
# import argparse
# import pandas as pd
# import subprocess
# import os
# import sys
# import glob

# def run_gcta_cojo(sumstats_file, plink_ref_dir, maf, population, output_file, script_dir):
#     """
#     Prepares data for GCTA-COJO, runs the analysis for each chromosome via a shell script,
#     and combines the results.
#     """
#     try:
#         # --- 1. Prepare Input Data ---
#         print("Preparing summary statistics for COJO format...")
#         sumstats_df = pd.read_csv(sumstats_file, sep='\t')

#         # Normalize column names to lowercase for robust matching
#         sumstats_df.columns = [col.lower() for col in sumstats_df.columns]

#         # Define the required columns from MungeSumstats output, in lowercase
#         required_cols = ["a1", "a2", "frq", "beta", "se", "p", "n", "id"]
#         if not all(col in sumstats_df.columns for col in required_cols):
#             missing = [col for col in required_cols if col not in sumstats_df.columns]
#             raise ValueError(f"Input summary statistics file is missing required columns: {missing}")

#         # Select columns using their lowercase names
#         cojo_df = sumstats_df[["a1", "a2", "frq", "beta", "se", "p", "n"]].copy()
#         # Rename them to the uppercase versions GCTA expects
#         cojo_df.rename(columns={"frq": "FRQ", "beta": "BETA", "se":"SE", "p": "P", "a1": "A1", "a2": "A2", "n": "N"}, inplace=True)
#         cojo_df["SNP"] = sumstats_df["id"]
#         cojo_df = cojo_df[['SNP', 'A1', 'A2', 'FRQ', 'BETA', 'SE', 'P', 'N']]

#         cojo_input_path = "cojo_sumstats.txt"
#         cojo_df.to_csv(cojo_input_path, sep='\t', index=False)

#         # --- 2. Run the GCTA-COJO Shell Script ---
#         gcta_script_path = os.path.join(script_dir, "6_gcta_cojo_analysis.sh")
#         gcta_out_dir = "."

#         print("Running GCTA-COJO analysis script...")
#         cmd = [
#             "bash", gcta_script_path,
#             gcta_out_dir,
#             plink_ref_dir,
#             cojo_input_path,
#             str(maf),
#             population
#         ]

#         process = subprocess.run(cmd, capture_output=True, text=True, check=True)
#         print("--- GCTA Script Standard Output ---")
#         print(process.stdout)
#         print("--- GCTA Script Standard Error ---")
#         print(process.stderr)

#         # --- 3. Combine Results ---
#         print("Combining COJO results from all chromosomes...")
#         result_files = glob.glob(f"{gcta_out_dir}/*.jma.cojo")
#         if not result_files:
#             result_files = glob.glob(f"{gcta_out_dir}/*.cma.cojo")
#         if not result_files:
#             raise FileNotFoundError("No GCTA-COJO result files (.jma.cojo or .cma.cojo) were found.")

#         all_results = []
#         for f in result_files:
#             df = pd.read_csv(f, sep='\t')
#             all_results.append(df)

#         combined_df = pd.concat(all_results, ignore_index=True)
#         combined_df.to_csv(output_file, sep='\t', index=False)
#         print(f"Successfully combined {len(result_files)} result files into final output.")

#     except subprocess.CalledProcessError as e:
#         print("ERROR: The GCTA shell script failed to execute.", file=sys.stderr)
#         print("--- GCTA Script Standard Output ---", file=sys.stderr)
#         print(e.stdout, file=sys.stderr)
#         print("--- GCTA Script Standard Error ---", file=sys.stderr)
#         print(e.stderr, file=sys.stderr)
#         sys.exit(1)
#     except Exception as e:
#         sys.exit(f"An error occurred during the GCTA-COJO workflow: {e}")


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="GCTA-COJO analysis wrapper for Galaxy.")
#     parser.add_argument("--sumstats", required=True, help="Input summary statistics file.")
#     # The argument is now --plink_ref_dir
#     parser.add_argument("--plink_ref_dir", required=True, help="Path to directory with PLINK reference files.")
#     parser.add_argument("--maf", required=True, type=float, help="Minor Allele Frequency threshold.")
#     parser.add_argument("--population", required=True, help="Reference population (e.g., EUR).")
#     parser.add_argument("--output", required=True, help="Final combined output file.")
#     parser.add_argument("--script_dir", required=True, help="Directory containing the bash script.")

#     args = parser.parse_args()
#     run_gcta_cojo(args.sumstats, args.plink_ref_dir, args.maf, args.population, args.output, args.script_dir)