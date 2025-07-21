#!/bin/bash

# This script runs GCTA-COJO analysis for each chromosome from 1 to 22.
# It expects arguments from the Python wrapper script.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Script Arguments ---
# $1: GCTA_OUT_DIR - The directory where results will be saved.
# $2: PLINK_DIR - The directory containing the 1000G reference panel PLINK files.
# $3: SUMSTATS_FILE - The path to the formatted summary statistics file.
# $4: MAF - The Minor Allele Frequency threshold.
# $5: POPULATION - The population code (e.g., "EUR").

GCTA_OUT_DIR=$1
PLINK_DIR=$2
SUMSTATS_FILE=$3
MAF=$4
POPULATION=$5

echo "--- Starting GCTA-COJO Analysis Loop ---"
echo "Output Directory: ${GCTA_OUT_DIR}"
echo "Reference Panel Directory: ${PLINK_DIR}"
echo "MAF: ${MAF}"
echo "Population: ${POPULATION}"

# Loop through chromosomes 1 to 22
for i in $(seq 1 22); do
    echo "Processing Chromosome ${i}..."
    
    # Define the path to the reference panel for the current chromosome
    # NOTE: Your filenames might be different. Adjust this line if needed.
    BFILE_PATH="${PLINK_DIR}/${POPULATION}.${i}"

    # Check if the reference file exists before running
    if [ -f "${BFILE_PATH}.bed" ]; then
        gcta64 \
            --bfile ${BFILE_PATH} \
            --chr ${i} \
            --cojo-file ${SUMSTATS_FILE} \
            --cojo-slct \
            --maf ${MAF} \
            --out "${GCTA_OUT_DIR}/${POPULATION}.${i}.cojo"
    else
        echo "Warning: Reference file for chr${i} not found at ${BFILE_PATH}.bed. Skipping."
    fi
done

echo "--- GCTA-COJO Analysis Loop Finished ---"