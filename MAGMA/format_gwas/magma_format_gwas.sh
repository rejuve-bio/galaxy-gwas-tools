#!/bin/bash
set -euo pipefail

GWAS_FILE="$1"
MODE="$2"
SPECIFIC_CHR="${3:-}"  # Default to empty if not provided

# Build filter
if [ "$MODE" = "specific" ] && [ -n "$SPECIFIC_CHR" ]; then
    FILTER="NR>1 && \$3==$SPECIFIC_CHR"
else
    FILTER="NR>1"
fi

# SNP location file
zcat "$GWAS_FILE" | awk -F' ' "$FILTER {print \$2, \$3, \$4}" > snp_loc.txt

# P-value file
zcat "$GWAS_FILE" | awk -F' ' "$FILTER {print \$2, \$15}" > pval.txt

echo "MAGMA formatting complete."
echo "  Mode: $MODE$( [ -n "$SPECIFIC_CHR" ] && echo " (chr$SPECIFIC_CHR)" || echo " (all)" )"
echo "  SNP loc lines: $(wc -l < snp_loc.txt)"
echo "  P-value lines: $(wc -l < pval.txt)"