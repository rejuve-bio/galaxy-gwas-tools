#!/usr/bin/env bash
set -euo pipefail

# ---------------------------
# GWAS Sumstats Harmoniser Setup Script
# ---------------------------

CHROMLIST="1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y,MT"

die() { echo "Error: $*" >&2; exit 2; }

usage() {
  cat << 'EOF'
Usage: harmonizer_setup.sh REF_DIR [CODE_REPO]

Positional Arguments:
  REF_DIR     Reference data directory (REQUIRED)
  CODE_REPO   Path to workflow scripts repo (default: current working directory)
EOF
}

# ---------------------------
# Positional arguments
# ---------------------------
REF_DIR="${1:-}"
CODE_REPO="${2:-$PWD}"

if [[ -z "$REF_DIR" ]]; then
  usage
  die "REF_DIR is required"
fi

# ---------------------------
# Validate directories
# ---------------------------
if [[ ! -d "$REF_DIR" ]]; then
  mkdir -p "$REF_DIR"
fi

if [[ ! -d "$CODE_REPO" ]]; then
  die "Code repository directory not found: $CODE_REPO"
fi

LOG_DIR="$REF_DIR/logs"
mkdir -p "$LOG_DIR"

# ---------------------------
# Detect Nextflow executable
# ---------------------------
if [[ -x "$CODE_REPO/nextflow" ]]; then
  NEXTFLOW="$CODE_REPO/nextflow"
elif command -v nextflow >/dev/null 2>&1; then
  NEXTFLOW="nextflow"
else
  die "Nextflow not found in PATH and not in CODE_REPO ($CODE_REPO/nextflow)"
fi

# Add CODE_REPO to PATH for workflow scripts
export PATH="$CODE_REPO:$PATH"

# ---------------------------
# Run Nextflow reference preparation
# ---------------------------
echo "==== PREPARE REFERENCES ===="
"$NEXTFLOW" run "$CODE_REPO" -profile standard \
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
