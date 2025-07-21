#!/bin/bash
set -e

OUTDIR=$1
INPUT="$OUTDIR/ALL.chr1.shapeit2_integrated_v1a.GRCh37.vcf.gz"
OUTPUT="$OUTDIR/chr1.norm.vcf.gz"

echo "Normalizing chr1 VCF using bcftools..."

bcftools norm -m -both -Oz -o "$OUTPUT" "$INPUT"

tabix -p vcf "$OUTPUT"

echo "Normalization complete."
