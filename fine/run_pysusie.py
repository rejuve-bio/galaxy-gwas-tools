#!/usr/bin/env python3

import argparse
import sys
import pandas as pd
import numpy as np
import gzip
from pysusie import susie  # adjust import based on your PySuSiE installation

def load_sumstats(file_path):
    """Load summary statistics, skip duplicate headers if present."""
    try:
        sumstats = pd.read_csv(file_path, sep=None, engine='python')
        # Detect actual header row if there are duplicates
        if sumstats.iloc[0,0] == 'SNP':
            sumstats = sumstats[1:]  # remove duplicated header row
        sumstats = sumstats.reset_index(drop=True)
        return sumstats
    except Exception as e:
        print(f"Error loading sumstats: {e}", file=sys.stderr)
        sys.exit(1)

def load_snp_list(file_path):
    """Load SNP list and detect first column automatically."""
    try:
        snp_df = pd.read_csv(file_path, sep=None, engine='python', header=None)
        snp_df.columns = ['SNP']  # assume first column contains SNPs
        return snp_df
    except Exception as e:
        print(f"Error loading SNP list: {e}", file=sys.stderr)
        sys.exit(1)

def load_ld_matrix(file_path):
    """Load LD matrix as a numpy array. Supports plain text or gzipped files."""
    try:
        if file_path.endswith('.gz'):
            with gzip.open(file_path, 'rt') as f:
                return np.loadtxt(f)
        else:
            return np.loadtxt(file_path)
    except Exception as e:
        print(f"Error loading LD matrix: {e}", file=sys.stderr)
        sys.exit(1)

def run_susier_analysis(sumstats_file, ld_matrix_file, snp_list_file, n, output_creds, output_pips):
    print("--- Step 1: Loading input data ---")
    sumstats = load_sumstats(sumstats_file)
    snp_list = load_snp_list(snp_list_file)
    ld_matrix = load_ld_matrix(ld_matrix_file)

    # Filter sumstats to SNPs in the list
    filtered_sumstats = sumstats[sumstats['SNP'].isin(snp_list['SNP'])]
    if filtered_sumstats.empty:
        print("No SNPs matched between sumstats and SNP list.", file=sys.stderr)
        sys.exit(1)

    # Extract effect sizes and standard errors
    beta = filtered_sumstats['BETA'].astype(float).to_numpy()
    se = filtered_sumstats['SE'].astype(float).to_numpy()

    # Run SuSiE
    print("--- Step 2: Running SuSiE ---")
    try:
        susie_res = susie(bhat=beta, shat=se, R=ld_matrix, n=n)
    except Exception as e:
        print(f"Error running SuSiE: {e}", file=sys.stderr)
        sys.exit(1)

    # Save credible sets
    print("--- Step 3: Saving outputs ---")
    try:
        pd.DataFrame(susie_res['sets']['cs']).to_csv(output_creds, index=False)
        pd.DataFrame(susie_res['pip'], columns=['PIP']).to_csv(output_pips, index=False)
    except Exception as e:
        print(f"Error saving outputs: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run PySuSiE fine-mapping")
    parser.add_argument("--sumstats", required=True)
    parser.add_argument("--ld_matrix", required=True)
    parser.add_argument("--snp_list", required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--output_creds", required=True)
    parser.add_argument("--output_pips", required=True)
    args = parser.parse_args()

    run_susier_analysis(
        args.sumstats,
        args.ld_matrix,
        args.snp_list,
        args.n,
        args.output_creds,
        args.output_pips
    )
