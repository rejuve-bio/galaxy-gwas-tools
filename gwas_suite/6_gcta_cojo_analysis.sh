#!/bin/bash
# Exit immediately if a command fails.
set -e

# --- THIS IS THE FINAL FIX ---
# Find the absolute path to the gcta executable by searching upwards from the current
# directory to find the main 'database' directory, which is a parent to both the
# job working directory and the tool dependencies.

# Start in the current directory
SEARCH_PATH=$(pwd)
# Loop upwards until we find the 'database' directory or reach the root
while [[ "$SEARCH_PATH" != "" && ! -d "$SEARCH_PATH/dependencies" ]]; do
    SEARCH_PATH=$(dirname "$SEARCH_PATH")
done

# Check if we found the dependencies directory
if [ ! -d "$SEARCH_PATH/dependencies" ]; then
    echo "ERROR: Could not find the Galaxy 'dependencies' directory. The dependency may not be installed correctly." >&2
    exit 1
fi

# Now search for the gcta executable within the found dependencies directory
GCTA_EXEC=$(find "$SEARCH_PATH/dependencies" -type f -name gcta -path "*gcta=1.94.1*/bin/gcta" | head -n 1)

# Check if the executable was found. If not, exit with an error.
if [ -z "$GCTA_EXEC" ]; then
    echo "ERROR: Could not find the gcta executable within the dependencies directory. The dependency may not be installed correctly." >&2
    exit 1
fi

echo "Found GCTA executable at: $GCTA_EXEC"
# --- END FIX ---

# --- Script Arguments ---
GCTA_OUT_DIR=$1
PLINK_DIR=$2
SUMSTATS_FILE=$3
MAF=$4
POPULATION=$5
CHROMOSOME=$6

echo "--- Starting GCTA-COJO Analysis for Chromosome ${CHROMOSOME} ---"

BFILE_PATH="${PLINK_DIR}/${POPULATION}.${CHROMOSOME}"

# Call the gcta command using its full, absolute path
"$GCTA_EXEC" \
    --bfile "${BFILE_PATH}" \
    --chr "${CHROMOSOME}" \
    --cojo-file "${SUMSTATS_FILE}" \
    --cojo-slct \
    --maf "${MAF}" \
    --out "${GCTA_OUT_DIR}/${POPULATION}.${CHROMOSOME}.cojo"

echo "--- GCTA-COJO Analysis Finished ---"
