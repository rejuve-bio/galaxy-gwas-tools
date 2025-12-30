#!/usr/bin/env python3

import argparse
import pandas as pd

def filter_snps(input_file, output_file, pval_threshold=5e-8):
    # Load the munged file
    df = pd.read_csv(input_file, sep='\t')
    
    # Filter by p-value
    sig_df = df[df['P'] < pval_threshold]
    
    # Save to output
    sig_df.to_csv(output_file, sep='\t', index=False)
    print(f"Filtered {sig_df.shape[0]} rows with P < {pval_threshold}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter significant SNPs by P-value")
    parser.add_argument("-i", "--input", required=True, help="Path to input munged sumstats file")
    parser.add_argument("-o", "--output", required=True, help="Path to output filtered file")
    parser.add_argument("-p", "--pval", type=float, default=5e-8, help="P-value threshold")

    args = parser.parse_args()
    filter_snps(args.input, args.output, args.pval)
