#!/bin/bash
set -e

OUTDIR=$1
mkdir -p "$OUTDIR"

echo "Downloading chr1 VCF from 1000 Genomes..."

wget -O "$OUTDIR/ALL.chr1.shapeit2_integrated_v1a.GRCh37.vcf.gz" \
  ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr1.shapeit2_integrated_v1a.GRCh37.vcf.gz

wget -O "$OUTDIR/ALL.chr1.shapeit2_integrated_v1a.GRCh37.vcf.gz.tbi" \
  ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr1.shapeit2_integrated_v1a.GRCh37.vcf.gz.tbi

echo "Download complete."
