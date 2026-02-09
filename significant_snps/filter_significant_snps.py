#!/usr/bin/env python3

import pandas as pd
import argparse

def filter_snps(input_file, output_file, pval_column, pval_threshold):
    # Load the summary statistics file
    df = pd.read_csv(input_file, sep=None, engine="python") 

    if pval_column not in df.columns:
        raise ValueError(f"Column '{pval_column}' not found in input file. Available columns: {', '.join(df.columns)}")

    # Filter based on p-value threshold
    filtered_df = df[df[pval_column] < pval_threshold]

    # Write filtered SNPs to output
    filtered_df.to_csv(output_file, sep="\t", index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter significant SNPs based on p-value threshold.")
    parser.add_argument("--input", required=True, help="Input summary statistics file (TSV/CSV)")
    parser.add_argument("--output", required=True, help="Output file for significant SNPs")
    parser.add_argument("--pval_column", default="P", help="Name of the p-value column (default: P)")
    parser.add_argument("--pval_threshold", type=float, default=5e-8, help="P-value threshold (default: 5e-8)")

    args = parser.parse_args()
    filter_snps(args.input, args.output, args.pval_column, args.pval_threshold)
