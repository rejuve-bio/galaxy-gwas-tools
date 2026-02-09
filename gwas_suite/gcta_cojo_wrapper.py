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
        print("Attempting to read GWAS summary statistics file...")
        df = pd.read_csv(gwas_file, sep='\t', low_memory=False)
        print(f"Successfully read {len(df)} rows.")

        # Normalize column names to uppercase for easier matching
        df.columns = [col.upper() for col in df.columns]
        print("Found columns:", list(df.columns))

        # Define the columns we need and their final names for GCTA
        # This map handles variations in input column names (e.g., FRQ or FREQ)
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
        
        # Check for alternative names
        if 'FREQ' in df.columns:
            column_map['FREQ'] = 'freq'
        
        # Find which columns are actually present in the dataframe
        present_columns = [col for col in column_map.keys() if col in df.columns]
        
        if len(present_columns) < 8:
            missing = set(column_map.keys()) - set(present_columns)
            raise ValueError(f"Input file is missing required columns. Could not find: {missing}")

        print(f"Using columns: {present_columns}")
        
        # Select and rename the columns
        cojo_df = df[present_columns].rename(columns=column_map)

        # Ensure final columns are in the correct order for GCTA
        final_order = ['SNP', 'A1', 'A2', 'freq', 'b', 'se', 'p', 'N']
        cojo_df = cojo_df[final_order]

        # Save the formatted file
        cojo_df.to_csv(output_file, sep='\t', index=False)
        print(f"Successfully formatted GWAS data for COJO and saved to {output_file}")

    except Exception as e:
        sys.exit(f"FATAL ERROR during data formatting: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Format GWAS summary statistics for GCTA-COJO.")
    parser.add_argument("--gwas", required=True, help="Input GWAS summary statistics file.")
    parser.add_argument("--output", required=True, help="Path for the formatted output file.")
    args = parser.parse_args()
    format_gwas_for_cojo(args.gwas, args.output)
