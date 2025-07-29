#!/bin/bash
set -e

# --- Script Arguments ---
GCTA_OUT_DIR=$1
PLINK_DIR=$2
SUMSTATS_FILE=$3
MAF=$4
POPULATION=$5

# --- DEBUGGING STEP ---
# Print the contents of the reference directory to the log
echo "--- Directory Contents of ${PLINK_DIR} ---"
ls -l "${PLINK_DIR}"
echo "------------------------------------------"
# --- END DEBUGGING STEP ---

echo "--- Starting GCTA-COJO Analysis Loop ---"

# Loop through chromosomes 1 to 22
for i in $(seq 1 22); do
    echo "Processing Chromosome ${i}..."

    BFILE_PATH="${PLINK_DIR}/${POPULATION}.${i}"

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