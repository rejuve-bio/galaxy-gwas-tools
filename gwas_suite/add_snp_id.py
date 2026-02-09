#!/usr/bin/env python3
import argparse
import pandas as pd

def add_snp_identifier(input_path, output_path):
    """
    Reads a munged sumstats file, creates a CHR:BP:A2:A1 ID,
    and saves the new file.
    """
    print(f"Reading file: {input_path}")
    try:
        # MungeSumstats can produce columns with different capitalizations
        # so we read it in and then normalize the column names to uppercase
        df = pd.read_csv(input_path, sep='\t', low_memory=False)
        df.columns = [col.upper() for col in df.columns]

        print("Generating new 'ID' column...")
        # Ensure required columns exist
        required_cols = ['CHR', 'BP', 'A1', 'A2']
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            raise ValueError(f"Input file is missing required columns: {missing}")

        # Create the ID column by concatenating strings
        df['ID'] = df['CHR'].astype(str) + ':' + \
                   df['BP'].astype(str) + ':' + \
                   df['A2'].astype(str) + ':' + \
                   df['A1'].astype(str)

        print(f"Saving modified file to: {output_path}")
        df.to_csv(output_path, sep='\t', index=False)
        print("Done.")

    except Exception as e:
        # Exit with a clear error message if something goes wrong
        import sys
        sys.exit(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a SNP ID column to a summary statistics file.")
    parser.add_argument("--input", required=True, help="Path to the input summary statistics file.")
    parser.add_argument("--output", required=True, help="Path for the output file.")
    args = parser.parse_args()
    add_snp_identifier(args.input, args.output)