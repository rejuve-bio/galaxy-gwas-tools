#!/bin/bash
set -e

OUTDIR=$1
VCF="$OUTDIR/chr1.norm.vcf.gz"
PLINK_PREFIX="$OUTDIR/chr1_plink"

echo "Converting VCF to PLINK format..."

plink2 \
  --vcf "$VCF" \
  --make-bed \
  --out "$PLINK_PREFIX" \
  --keep-allele-order \
  --allow-extra-chr

echo "PLINK files created: $PLINK_PREFIX.bed/.bim/.fam"
