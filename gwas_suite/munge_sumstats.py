#!/usr/bin/env python3
import argparse
import sys
from rpy2.robjects.packages import importr
from rpy2.rinterface_lib.callbacks import logger as rpy2_logger
import logging

# Set up logging to capture R messages
logging.basicConfig(level=logging.INFO)
rpy2_logger.setLevel(logging.INFO)

def munge_sumstats(sumstats_file, ref_genome, save_path, log_folder):
    """
    Uses the MungeSumstats R package via rpy2 to format a GWAS summary statistics file.
    """
    try:
        mungesumstats = importr('MungeSumstats')
        print(f"Successfully imported MungeSumstats.")
    except Exception as e:
        sys.exit(f"ERROR: Failed to import the MungeSumstats R package. Ensure it is installed in the tool's Conda environment. Details: {e}")

    print(f"Starting formatting for: {sumstats_file}")
    print(f"Reference Genome: {ref_genome}")
    print(f"Output Path: {save_path}")

    try:
        # Run the MungeSumstats formatting function
        mungesumstats.format_sumstats(
            path=sumstats_file,
            ref_genome=ref_genome,
            save_path=save_path,
            log_folder=log_folder,
            # Hard-coded for simplicity, but could be tool parameters
            drop_indels=True,
            save_format="LDSC",
            log_mungesumstats_msgs=True
        )
        print(f"MungeSumstats successfully formatted the file and saved it to {save_path}")
    except Exception as e:
        sys.exit(f"ERROR: MungeSumstats format_sumstats function failed. Details: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Galaxy tool wrapper for MungeSumstats::format_sumstats.")
    parser.add_argument("--sumstats", required=True, help="Path to the input summary statistics file.")
    parser.add_argument("--ref_genome", required=True, help="Reference genome build (e.g., GRCh37 or GRCh38).")
    parser.add_argument("--output", required=True, help="Path for the formatted output file.")
    parser.add_argument("--log_dir", required=True, help="Directory to save log files.")

    args = parser.parse_args()

    munge_sumstats(
        sumstats_file=args.sumstats,
        ref_genome=args.ref_genome,
        save_path=args.output,
        log_folder=args.log_dir
    )