# GWASLab Harmonization Galaxy Tools

This directory contains the Galaxy-facing implementation for a modular GWAS summary statistics harmonization suite based on GWASLab.

## Current Layout
- `tool.xml` and `harmonize_gwas.py`: existing harmonization prototype
- `tools/`: modular Galaxy wrappers being added step by step
- `scripts/`: reusable Python helpers shared by wrappers
- `config/`: logging and workflow defaults
- `workflows/`: reserved for Galaxy workflow definitions
- `logs/`, `tmp/`, `outputs/`: local development artifacts only

## Next Tools In Progress
- `load_sumstats`
- `standardize`
