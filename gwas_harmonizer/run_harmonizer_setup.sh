#!/usr/bin/env bash
set -euo pipefail

# Get parameters from command line
HARMONIZER_REPO="$1"
REF_DIR="$2"
CHROMLIST="$3"

# Sanity checks
command -v nextflow >/dev/null || { echo "ERROR: nextflow not found in PATH"; exit 1; }

LOG_DIR="$REF_DIR/logs"
mkdir -p "$LOG_DIR"

# Add the code repo to the PATH so that Nextflow can find the workflow scripts
export PATH="$HARMONIZER_REPO:$PATH"

echo "==== PREPARE REFERENCES ===="
echo "Reference directory: $REF_DIR"
echo "Code repository: $HARMONIZER_REPO"
echo "Chromosome list: $CHROMLIST"

# Run nextflow directly (bypassing the complex argument parsing)
nextflow run "$HARMONIZER_REPO" -profile standard \
  --reference \
  --ref "$REF_DIR" \
  --chromlist "$CHROMLIST" \
  -with-report   "$LOG_DIR/ref-report.html" \
  -with-timeline "$LOG_DIR/ref-timeline.html" \
  -with-trace    "$LOG_DIR/ref-trace.txt" \
  |& tee -a "$LOG_DIR/ref.log"

echo "All done."
echo "Logs:      $LOG_DIR/"
echo "Outputs:   Look for a date-stamped folder created by Nextflow containing <basename>/final/"