#!/bin/bash
set -e

CODE_REPO="$1"
REF_DIR="$2"
CHROM_LIST="$3"

# Log everything
exec > >(tee -a "$REF_DIR/galaxy_job.log") 2>&1

echo "=== GALAXY JOB STARTED ==="
date
echo "Code repo: $CODE_REPO"
echo "Ref dir: $REF_DIR"
echo "Chrom list: $CHROM_LIST"

# Check if we can access nextflow
if [ ! -x "$CODE_REPO/nextflow" ]; then
    echo "ERROR: Nextflow not found or not executable at $CODE_REPO/nextflow"
    exit 1
fi

# Change to code directory
cd "$CODE_REPO" || {
    echo "ERROR: Cannot change to directory $CODE_REPO"
    exit 1
}

echo "Current directory: $(pwd)"

# Create reference directory
mkdir -p "$REF_DIR/logs"

echo "=== RUNNING NEXTFLOW ==="
# Run nextflow with full output
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
echo "Nextflow finished with exit code: $EXIT_CODE"
date
echo "=== GALAXY JOB COMPLETED ==="

exit $EXIT_CODE