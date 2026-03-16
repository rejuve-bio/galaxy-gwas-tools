# GWASLab Harmonization Galaxy Tool

This folder contains the Galaxy wrapper and the Python driver script used to
harmonize GWAS summary statistics with GWASLab.

## What It Does
- Detects or accepts a known input format.
- Optionally uses manual column mappings.
- Runs GWASLab `basic_check` and harmonization against reference files.
- Writes LDSC-ready output with HapMap3 SNPs and HLA exclusion.
- Produces a structured log for provenance.

## Files
- `harmonize_gwas.py`: Galaxy-invoked Python entry point.
- `tool.xml`: Galaxy tool definition and UI parameters.

## Inputs (Galaxy UI)
- GWAS summary stats: `txt`, `tsv`, `csv`, or `gz`.
- Reference FASTA: required.
- Inference VCF with `AF` in INFO: required.
- rsID TSV: optional.

## Outputs
- Harmonized LDSC format (gz).
- Log file (txt).

## Local Smoke Test (Optional)
```bash
python harmonize_gwas.py \
  --input example.tsv.gz \
  --format auto \
  --ref_seq ucsc_genome_hg19.fasta.gz \
  --ref_infer 1kg_pan_hg19.vcf.gz \
  --output harmonized.sumstats.gz \
  --log harmonize.log
```

## Notes
- The script expects Galaxy to supply a writable output path.
- The tool uses GWASLab v4.0.4 as declared in `tool.xml`.
