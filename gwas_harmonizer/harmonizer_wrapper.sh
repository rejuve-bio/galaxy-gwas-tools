#!/bin/bash
set -e

# Debug info
echo "=== GALAXY WRAPPER DEBUG ==="
echo "User: $(whoami)"
echo "PWD: $(pwd)"
echo "Code repo: $1"
echo "Ref dir: $2"
echo "Chromlist: $3"

# Set environment
export CODE_REPO="$1"
export REF_DIR="$2"
export CHROM_LIST="$3"

# Check if we can access the files
echo "=== FILE ACCESS CHECK ==="
ls -la "$CODE_REPO/nextflow" || exit 1
ls -la "$CODE_REPO/main.nf" || exit 1

# Create directories
mkdir -p "$REF_DIR/logs"

# Change to code directory - THIS IS CRITICAL
cd "$CODE_REPO"
echo "Working in: $(pwd)"

# Run nextflow
echo "=== EXECUTING NEXTFLOW ==="
./nextflow run . \
    -profile standard \
    --reference \
    --ref "$REF_DIR" \
    --chromlist "$CHROM_LIST" \
    -with-report "$REF_DIR/logs/ref-report.html" \
    -with-timeline "$REF_DIR/logs/ref-timeline.html" \
    -with-trace "$REF_DIR/logs/ref-trace.txt" \
    -with-dag "$REF_DIR/logs/ref-dag.html"

EXIT_CODE=$?
echo "Nextflow completed with exit code: $EXIT_CODE"

# Create Galaxy outputs
echo "$REF_DIR/logs" > log_dir.txt
[ -f "$REF_DIR/logs/ref-report.html" ] && cp "$REF_DIR/logs/ref-report.html" report.html || touch report.html
[ -f "$REF_DIR/logs/ref-timeline.html" ] && cp "$REF_DIR/logs/ref-timeline.html" timeline.html || touch timeline.html

exit $EXIT_CODE