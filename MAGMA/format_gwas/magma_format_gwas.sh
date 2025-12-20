#!/bin/bash
set -e  # Exit on error

GWAS_FILE=$1
CHROM=$2
SPECIFIC_CHR=$3  # Or "" if all

if [ "$CHROM" = "specific" ]; then
    FILTER="&& \$3==$SPECIFIC_CHR"
else
    FILTER=""
fi

# SNP loc file
zcat "$GWAS_FILE" | awk -F' ' "NR>1 $FILTER {print \$2, \$3, \$4}" > snp_loc.txt

# P-value file
zcat "$GWAS_FILE" | awk -F' ' "NR>1 $FILTER {print \$2, \$15}" > pval.txt