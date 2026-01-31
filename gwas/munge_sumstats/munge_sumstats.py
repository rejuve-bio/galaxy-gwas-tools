#!/usr/bin/env python3

import argparse
import os
import sys

import pandas as pmunge_sumstatsd
from rpy2.robjects import pandas2ri, r
from rpy2.robjects.conversion import localconverter
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.rinterface_lib.embedded import RRuntimeError

# Import R packages
base = importr("base")
utils = importr("utils")

try:
    mungesumstats = importr("MungeSumstats")
except RRuntimeError as e:
    print(f"Error: Could not import MungeSumstats: {e}", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Run MungeSumstats formatting on a GWAS summary statistics file.")
    parser.add_argument("--input", required=True, help="Path to raw GWAS summary statistics (.tsv or .tsv.bgz)")
    parser.add_argument("--output", required=True, help="Path to save munged output file")
    parser.add_argument("--ref_genome", default="GRCh37", help="Reference genome version")
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    ref_genome = args.ref_genome

    try:
        formatted_file_path_r = mungesumstats.format_sumstats(
            path=input_path,
            ref_genome=ref_genome,
            save_path=output_path,
            drop_indels=True,
            nThread=4,
            log_folder=os.path.join(os.path.dirname(output_path), "logs"),
            log_mungesumstats_msgs=True,
            save_format="LDSC",
        )

        # Convert the R object (a list) to a Python path string
        with localconverter(ro.default_converter + pandas2ri.converter):
            formatted_path = str(formatted_file_path_r[0])

        print(f"Munged file saved to: {formatted_path}")
    except Exception as e:
        print(f"Error during MungeSumstats formatting: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()






# import os
# import argparse
# from rpy2 import robjects
# from rpy2.robjects.packages import importr
# from rpy2.robjects.vectors import StrVector

# # Set up MungeSumstats
# utils = importr("utils")
# MungeSumstats = importr("MungeSumstats")

# def main():
#     parser = argparse.ArgumentParser(description="Format summary statistics using MungeSumstats")
#     parser.add_argument("--input", required=True, help="Input summary statistics file")
#     parser.add_argument("--output", required=True, help="Output file path")
#     args = parser.parse_args()

#     input_path = args.input
#     output_path = args.output

#     print(f"Formatting input file: {input_path}")
#     print(f"Saving formatted file to: {output_path}")

#     try:
#         MungeSumstats.format_sumstats(
#             path=input_path,
#             save_path=output_path,
#             validate_ref_genome=False,
#             check_dups=False,
#             dbSNP=robjects.NA_Character,
#             ref_genome=robjects.NA_Character
#         )
#         print("Formatting complete.")
#     except Exception as e:
#         print(f"Error during MungeSumstats formatting: {e}")

# if __name__ == "__main__":
#     main()
