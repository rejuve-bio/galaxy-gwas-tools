#!/bin/bash
set -euo pipefail

# Arguments
GWAS_FILE="$1"
MODE="$2"
SPECIFIC_CHR="${3:-}"

# Strip leading/trailing whitespace from the path (critical for Galaxy)
GWAS_FILE=$(echo "$GWAS_FILE" | xargs)

# Verify file exists (debug + safety)
if [ ! -f "$GWAS_FILE" ]; then
    echo "ERROR: Input file not found or inaccessible: '$GWAS_FILE'" >&2
    exit 1
fi

# Build awk filter
if [ "$MODE" = "specific" ] && [ -n "$SPECIFIC_CHR" ]; then
    FILTER="NR>1 && \$3==$SPECIFIC_CHR"
else
    FILTER="NR>1"
fi

# Use gunzip -c: works for .gz files AND plain text files (decompresses if needed, copies if not)
gunzip -c "$GWAS_FILE" | \
awk -F' ' "$FILTER {print \$2, \$3, \$4}" > snp_loc.txt

gunzip -c "$GWAS_FILE" | \
awk -F' ' "$FILTER {print \$2, \$15}" > pval.txt

echo "MAGMA formatting successful!"
echo "  Input file: $GWAS_FILE"
echo "  Mode: $MODE$( [ -n "$SPECIFIC_CHR" ] && echo " (chr$SPECIFIC_CHR)" || echo " (all chromosomes)" )"
echo "  Output SNP loc lines: $(wc -l < snp_loc.txt)"
echo "  Output P-value lines: $(wc -l < pval.txt)"