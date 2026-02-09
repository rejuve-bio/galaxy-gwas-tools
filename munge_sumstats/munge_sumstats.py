#!/usr/bin/env python3

import argparse
import os
import sys
from rpy2.robjects.packages import importr
import rpy2.robjects as ro


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Format GWAS summary statistics using the MungeSumstats R package"
    )
    parser.add_argument(
        '--input', required=True, help='Path to the input GWAS summary statistics file'
    )
    parser.add_argument(
        '--output', required=True, help='Path to the output file (TSV format expected by Galaxy)'
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    input_path = args.input
    output_path = args.output
    final_output_path = output_path

    # MungeSumstats appends ".tsv" even if you pass a name without it
    if not output_path.endswith(".tsv"):
        output_path += ".tsv"

    try:
        # Import MungeSumstats R package
        mungesumstats = importr("MungeSumstats")

        # Format the summary statistics
        mungesumstats.format_sumstats(
            path=input_path,
            ref_genome="GRCh37",
            save_path=output_path,
            drop_indels=True,
            save_format="LDSC",
            force_new=True
        )

        # Rename if MungeSumstats appended ".tsv"
        if output_path != final_output_path and os.path.exists(output_path):
            os.rename(output_path, final_output_path)

    except Exception as e:
        print(f"[ERROR] Failed to format summary statistics: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
