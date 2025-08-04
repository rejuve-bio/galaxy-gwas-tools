#!/usr/bin/env python3
import argparse
import pandas as pd
import subprocess
import os
import sys
import glob
import shutil
import traceback

DEBUG_LOG = "cojo_debug.log"

def log(msg):
    print(f"[INFO] {msg}")
    with open(DEBUG_LOG, 'a') as log_file:
        log_file.write(f"[INFO] {msg}\n")
    sys.stdout.flush()

def error(msg, exc=None):
    print(f"[ERROR] {msg}")
    with open(DEBUG_LOG, 'a') as log_file:
        log_file.write(f"[ERROR] {msg}\n")
        if exc:
            traceback.print_exc(file=log_file)
    sys.stdout.flush()

def run_gcta_cojo(sumstats_file, bed_file, bim_file, fam_file, chromosome, maf, population, output_file, conda_prefix):
    try:
        log("Starting GCTA-COJO wrapper script.")

        # 1. Validate input files
        log("Checking input files...")
        for f in [sumstats_file, bed_file, bim_file, fam_file]:
            if not os.path.exists(f):
                raise FileNotFoundError(f"Missing input file: {f}")
        log("All input files found.")

        # 2. Locate GCTA binary
        gcta_exec = os.path.join(conda_prefix, "bin", "gcta")
        if not os.path.exists(gcta_exec):
            raise FileNotFoundError(f"GCTA not found at: {gcta_exec}")
        log(f"Using GCTA binary: {gcta_exec}")

        # 3. Copy PLINK files
        log("Copying PLINK files...")
        plink_dir = "plink_ref"
        os.makedirs(plink_dir, exist_ok=True)
        for ext, src in zip(["bed", "bim", "fam"], [bed_file, bim_file, fam_file]):
            dst = os.path.join(plink_dir, f"{population}.{chromosome}.{ext}")
            shutil.copyfile(src, dst)
        log("PLINK reference files copied successfully.")

        # 4. Parse and validate summary stats
        log("Reading summary statistics...")
        df = pd.read_csv(sumstats_file, sep='\t', low_memory=False)
        df.columns = [c.lower() for c in df.columns]

        snp_col = next((c for c in ['snp', 'id', 'rsid'] if c in df.columns), None)
        if not snp_col:
            raise ValueError("Summary stats must contain 'snp', 'id', or 'rsid' column.")

        required = ['a1', 'a2', 'frq', 'beta', 'se', 'p', 'n']
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        df["SNP"] = df[snp_col]
        df.rename(columns={"a1": "A1", "a2": "A2", "frq": "FRQ", "beta": "BETA",
                           "se": "SE", "p": "P", "n": "N"}, inplace=True)
        cojo_df = df[["SNP", "A1", "A2", "FRQ", "BETA", "SE", "P", "N"]]
        cojo_input = "cojo_sumstats.txt"
        cojo_df.to_csv(cojo_input, sep='\t', index=False)
        log("Summary statistics prepared for GCTA.")

        # 5. Build GCTA command
        bfile = os.path.join(plink_dir, f"{population}.{chromosome}")
        cmd = [
            gcta_exec,
            "--bfile", bfile,
            "--chr", str(chromosome),
            "--cojo-file", cojo_input,
            "--cojo-slct",
            "--maf", str(maf),
            "--out", f"{population}.{chromosome}.cojo"
        ]
        log(f"Running GCTA-COJO: {' '.join(cmd)}")

        # 6. Run GCTA
        result = subprocess.run(cmd, capture_output=True, text=True)
        log("--- GCTA STDOUT ---\n" + result.stdout.strip())
        log("--- GCTA STDERR ---\n" + result.stderr.strip())
        result.check_returncode()
        log("GCTA-COJO finished successfully.")

        # 7. Handle output
        output_path = f"{population}.{chromosome}.cojo.jma.cojo"
        if os.path.exists(output_path):
            shutil.move(output_path, output_file)
            log(f"Results written to: {output_file}")
        else:
            log("No signals found. Writing empty result file.")
            with open(output_file, 'w') as f:
                f.write("Chr\tSNP\tbp\trefA\tn_refA\tfreq_refA\teff_refA\tbeta\tse\tp\tn\tfreq_geno\tbJ\tbJ_se\tpJ\tLD_r\n")
    except subprocess.CalledProcessError as e:
        error("GCTA command failed.", e)
        raise
    except Exception as e:
        error("An unexpected error occurred.", e)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sumstats", required=True)
    parser.add_argument("--bed", required=True)
    parser.add_argument("--bim", required=True)
    parser.add_argument("--fam", required=True)
    parser.add_argument("--chromosome", type=int, required=True)
    parser.add_argument("--maf", type=float, required=True)
    parser.add_argument("--population", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--conda-prefix", required=True)
    args = parser.parse_args()

    try:
        run_gcta_cojo(
            args.sumstats, args.bed, args.bim, args.fam,
            args.chromosome, args.maf, args.population,
            args.output, args.conda_prefix
        )
    except Exception:
        log("Fatal error occurred — see log above.")
        sys.exit(1)
