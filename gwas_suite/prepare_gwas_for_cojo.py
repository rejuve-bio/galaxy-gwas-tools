#!/usr/bin/env python3
import argparse
import pandas as pd
import sys

def format_gwas_for_cojo(gwas_file, output_file):
    """
    Reads a GWAS summary statistics file and formats it for GCTA-COJO.
    Selects and renames the required columns.
    """
    try:
        # Read the input GWAS file
        df = pd.read_csv(gwas_file, sep='\t', low_memory=False)

        # Normalize column names to uppercase for easier matching
        df.columns = [col.upper() for col in df.columns]

        # Define the columns we need and their final names for GCTA
        column_map = {
            'SNP': 'SNP',
            'A1': 'A1',
            'A2': 'A2',
            'FRQ': 'freq',
            'BETA': 'b',
            'SE': 'se',
            'P': 'p',
            'N': 'N'
        }

        # Select and rename the columns
        cojo_df = df[list(column_map.keys())].rename(columns=column_map)

        # Save the formatted file
        cojo_df.to_csv(output_file, sep='\t', index=False)
        print(f"Successfully formatted GWAS data for COJO and saved to {output_file}")

    except Exception as e:
        sys.exit(f"An error occurred during data formatting: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Format GWAS summary statistics for GCTA-COJO.")
    parser.add_argument("--gwas", required=True, help="Input GWAS summary statistics file.")
    parser.add_argument("--output", required=True, help="Path for the formatted output file.")
    args = parser.parse_args()
    format_gwas_for_cojo(args.gwas, args.output)
