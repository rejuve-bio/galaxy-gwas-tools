#!/usr/bin/env python3
import argparse
import pandas as pd
import sys

def find_intersecting_snps(file1_path, col1, file2_path, col2, output_path):
    """
    Finds the intersection of SNP IDs from two files based on specified columns.
    """
    try:
        print(f"Reading SNP IDs from file 1: {file1_path}, column {col1}")
        # Adjust for 1-based column numbers from Galaxy to 0-based for pandas
        col1_index = col1 - 1
        df1 = pd.read_csv(file1_path, sep='\t', header=None, usecols=[col1_index], low_memory=False, skiprows=1)
        snps_file1 = set(df1.iloc[:, 0].dropna().astype(str))
        print(f"Found {len(snps_file1)} unique SNP IDs in file 1.")

        print(f"Reading SNP IDs from file 2: {file2_path}, column {col2}")
        col2_index = col2 - 1
        df2 = pd.read_csv(file2_path, sep='\t', header=None, usecols=[col2_index], low_memory=False)
        snps_file2 = set(df2.iloc[:, 0].dropna().astype(str))
        print(f"Found {len(snps_file2)} unique SNP IDs in file 2.")

        print("Finding intersection...")
        intersection = snps_file1.intersection(snps_file2)
        
        print(f"Found {len(intersection)} overlapping SNP IDs.")

        with open(output_path, 'w') as f:
            if intersection:
                for snp_id in sorted(list(intersection)):
                    f.write(f"{snp_id}\n")
            else:
                f.write("No overlapping SNPs found between the two files.\n")
        
        print("Done.")

    except Exception as e:
        sys.exit(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find intersecting SNPs between two files.")
    parser.add_argument("--file1", required=True, help="First input file (e.g., summary statistics).")
    parser.add_argument("--col1", required=True, type=int, help="1-based column number for SNP IDs in the first file.")
    parser.add_argument("--file2", required=True, help="Second input file (e.g., BIM file).")
    parser.add_argument("--col2", required=True, type=int, help="1-based column number for SNP IDs in the second file.")
    parser.add_argument("--output", required=True, help="Path for the output file with intersecting IDs.")
    
    args = parser.parse_args()
    find_intersecting_snps(args.file1, args.col1, args.file2, args.col2, args.output)
