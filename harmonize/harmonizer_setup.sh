#!/usr/bin/env bash
set -euo pipefail

# ---------------------------
# GWAS Sumstats Harmoniser Setup Script
# ---------------------------

CHROMLIST="1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y,MT"

die() { echo "Error: $*" >&2; exit 2; }

usage() {
  cat << 'EOF'
Usage: harmonizer_setup.sh --ref REFDIR [--code-repo CODEREPO]

Options:
  --ref           Reference data directory (REQUIRED)
  --code-repo     Path to workflow scripts repo (default: current working directory)
  -h, --help      Show this help
EOF
}

# ---------------------------
# Defaults
# ---------------------------
REF_DIR=""
CODE_REPO="$PWD"

# ---------------------------
# Parse arguments
# ---------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ref) REF_DIR="$2"; shift 2 ;;
    --ref=*) REF_DIR="${1#*=}"; shift ;;
    --code-repo) CODE_REPO="$2"; shift 2 ;;
    --code-repo=*) CODE_REPO="${1#*=}"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

# ---------------------------
# Validation
# ---------------------------
if [[ -z "$REF_DIR" ]]; then
  die "--ref is required (path to reference data directory)"
fi
if [[ ! -d "$REF_DIR" ]]; then
  mkdir -p "$REF_DIR"
fi

if [[ ! -d "$CODE_REPO" ]]; then
  die "Code repository directory not found: $CODE_REPO"
fi

LOG_DIR="$REF_DIR/logs"
mkdir -p "$LOG_DIR"

# ---------------------------
# Ensure Nextflow executable is available
# ---------------------------
if [[ -x "$CODE_REPO/nextflow" ]]; then
  NEXTFLOW="$CODE_REPO/nextflow"
elif command -v nextflow >/dev/null 2>&1; then
  NEXTFLOW="nextflow"
else
  die "Nextflow not found in PATH and not in CODE_REPO ($CODE_REPO/nextflow)"
fi

# Add CODE_REPO to PATH (optional, for workflow scripts)
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
