# Tool Directory Guide

This directory contains the Galaxy wrappers and Python entry points for the GWASLab harmonization workflow. Each tool is intentionally narrow so it can be used alone or composed into a Galaxy workflow.

## `load_sumstats`

Purpose:
- Load raw GWAS summary statistics into a standardized GWASLab-backed table.
- Support the four GWASLab loading modes exposed in the UI:
  - specify columns
  - specify a known format keyword
  - auto mode
  - chromosome-separated input files

Inputs:
- one summary statistics file, or a chromosome-split collection
- reader options such as separator, skipped rows, build hint, and NA values
- manual column mapping or a GWASLab format keyword depending on the selected mode

Outputs:
- standardized tabular dataset
- JSON metadata describing the load mode, columns, and row count
- GWASLab log file

## `standardize`

Purpose:
- Run GWASLab `basic_check()` as the main standardization step.
- Normalize identifiers, coordinates, alleles, and statistics into a cleaner intermediate table for downstream QC and harmonization.

Inputs:
- a summary statistics table
- input format hint
- optional build hint
- boolean flags controlling `basic_check()` and optional `fix_id()` pre-processing

Outputs:
- standardized tabular dataset
- JSON metadata summarizing rows before and after standardization
- GWASLab log file

## `qc_check`

Purpose:
- Run GWASLab QC-oriented checks after loading or standardization.
- Produce a compact QC report covering missing required values, invalid allele strings, and duplicate variants.

Inputs:
- a summary statistics table
- input format hint
- optional build hint
- optional duplicate removal flag

Outputs:
- QC-checked tabular dataset
- JSON QC report
- GWASLab log file

## `liftover`

Purpose:
- convert coordinates between genome builds such as `hg19 -> hg38` or `hg38 -> hg19`
- keep mapped and unmapped variants as separate Galaxy outputs so downstream workflow steps can decide what to do next

Inputs:
- a summary statistics table with genomic coordinates
- source and target genome builds
- either a built-in GWASLab chain file choice or a custom UCSC chain file
- optional STATUS-based filtering and coordinate-base settings

Outputs:
- mapped variants table
- unmapped variants table
- JSON metadata summarizing mapped and unmapped row counts
- GWASLab log file

## Testing

Galaxy wrapper tests:

```bash
planemo test tools/load_sumstats/tool.xml
planemo test tools/standardize/tool.xml
planemo test tools/qc_check/tool.xml
planemo test tools/liftover/tool.xml
```

Direct Python smoke tests:

```bash
python tests/run_load_sumstats_smoke.py
python tests/run_standardize_smoke.py
python tests/run_qc_check_smoke.py
python tests/run_liftover_smoke.py
```
