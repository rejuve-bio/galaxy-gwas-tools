#!/bin/bash
set -euo pipefail

# Arguments
GWAS_FILE="$1"
MODE="$2"
SPECIFIC_CHR="${3:-}"
SOURCE_TYPE="${4:-default}"
SNP_COL_NUM="${5:-2}"
CHR_COL_NUM="${6:-3}"
POS_COL_NUM="${7:-4}"
P_COL_NUM="${8:-15}"
P_TYPE="${9:-raw}"

# Strip whitespace from path
GWAS_FILE=$(echo "$GWAS_FILE" | xargs)

# Verify file exists
if [ ! -f "$GWAS_FILE" ]; then
    echo "ERROR: Input file not found: '$GWAS_FILE'" >&2
    exit 1
fi

# Preset column and P-type overrides (1-based)
case "$SOURCE_TYPE" in
    "plink")
        SNP_COL_NUM=2
        CHR_COL_NUM=1
        POS_COL_NUM=3
        P_COL_NUM=7
        P_TYPE="raw"
        ;;
    "ukbb")
        SNP_COL_NUM=1  # variant (chr:pos:ref:alt) - script will need to parse for CHR/POS if needed
        CHR_COL_NUM=1  # Derive CHR from variant
        POS_COL_NUM=1  # Derive POS from variant
        P_COL_NUM=5  # Assume example col for pval; adjust per actual
        P_TYPE="raw"
        ;;
    "saige")
        SNP_COL_NUM=3  # MarkerID
        CHR_COL_NUM=1
        POS_COL_NUM=2
        P_COL_NUM=8  # p.value
        P_TYPE="raw"
        ;;
    "regenie")
        SNP_COL_NUM=3  # ID
        CHR_COL_NUM=1
        POS_COL_NUM=2  # GENPOS
        P_COL_NUM=9  # LOG10P
        P_TYPE="log10"
        ;;
    "gwas_catalog")
        SNP_COL_NUM=3  # variant_id if present, else derive
        CHR_COL_NUM=1  # chromosome
        POS_COL_NUM=2  # base_pair_location
        P_COL_NUM=3  # p_value
        P_TYPE="raw"  # Default; user can override if -log10
        ;;
    "default" | "")
        # BBJ/BOLT-LMM default
        SNP_COL_NUM=2
        CHR_COL_NUM=3
        POS_COL_NUM=4
        P_COL_NUM=15
        P_TYPE="raw"
        ;;
esac

# Use gunzip -c for decompression
DECOMPRESS="gunzip -c"

# Build filter
if [ "$MODE" = "specific" ] && [ -n "$SPECIFIC_CHR" ]; then
    FILTER="NR>1 && \$$CHR_COL_NUM==$SPECIFIC_CHR"
else
    FILTER="NR>1"
fi

# P-value expression
if [ "$P_TYPE" = "log10" ]; then
    P_EXPR="10^(- \$$P_COL_NUM)"
else
    P_EXPR="\$$P_COL_NUM"
fi

# SNP location file: SNP CHR POS
$DECOMPRESS "$GWAS_FILE" | \
awk -F'\t' "$FILTER {print \$$SNP_COL_NUM, \$$CHR_COL_NUM, \$$POS_COL_NUM}" > snp_loc.txt

# P-value file: SNP P
$DECOMPRESS "$GWAS_FILE" | \
awk -F'\t' "$FILTER {print \$$SNP_COL_NUM, $P_EXPR}" > pval.txt

echo "Formatting complete."
echo "  Source: $SOURCE_TYPE"
echo "  Columns (1-based): SNP=$SNP_COL_NUM, CHR=$CHR_COL_NUM, POS=$POS_COL_NUM, P=$P_COL_NUM"
echo "  P-Type: $P_TYPE"
echo "  Lines: SNP loc=$(wc -l < snp_loc.txt), P-val=$(wc -l < pval.txt)"