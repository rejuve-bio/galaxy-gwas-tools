#!/bin/bash
set -e

OUTDIR=$1

echo "Downloading sample panel info..."

wget -O "$OUTDIR/integrated_call_samples_v3.20130502.ALL.panel" \
  ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/phase3/integrated_call_samples_v3.20130502.ALL.panel

cut -f1,2 "$OUTDIR/integrated_call_samples_v3.20130502.ALL.panel" > "$OUTDIR/population_ids.txt"

echo "Population file created at $OUTDIR/population_ids.txt"
