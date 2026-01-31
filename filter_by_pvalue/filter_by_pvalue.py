#!/usr/bin/env python3
import argparse
import pandas as pd
import sys

def filter_by_p_value(input_path, output_path, p_threshold):
    """
    Filters a summary statistics file based on a p-value threshold.
    """
    print(f"Reading file: {input_path}")
    try:
        df = pd.read_csv(input_path, sep='\t', low_memory=False)
        df.columns = [col.upper() for col in df.columns]

        # Ensure 'P' column exists
        if 'P' not in df.columns:
            raise ValueError("Input file is missing required column: 'P'")

        # Ensure P-value column is numeric, coercing errors to NaN
        df['P'] = pd.to_numeric(df['P'], errors='coerce')
        df.dropna(subset=['P'], inplace=True) # Drop rows where P is not a number

        print(f"Filtering rows where P < {p_threshold}")
        original_rows = len(df)

        # Perform the filtering
        filtered_df = df[df['P'] < p_threshold].copy()

        print(f"Kept {len(filtered_df)} of {original_rows} rows.")

        print(f"Saving filtered file to: {output_path}")
        filtered_df.to_csv(output_path, sep='\t', index=False)
        print("Done.")

    except Exception as e:
        sys.exit(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter a summary statistics file by P-value.")
    parser.add_argument("--input", required=True, help="Path to the input summary statistics file.")
    parser.add_argument("--output", required=True, help="Path for the output file.")
    parser.add_argument("--threshold", required=True, type=float, help="P-value threshold (e.g., 5e-8).")
    args = parser.parse_args()
    filter_by_p_value(args.input, args.output, args.threshold)