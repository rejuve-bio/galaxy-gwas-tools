# Galaxy GWAS Harmonization Tools using GWASLab

This repository contains Galaxy tools for harmonizing GWAS summary statistics using the GWASLab library.

## Overview

GWAS harmonization is a critical step in preparing summary statistics for downstream analyses like polygenic risk score calculation. This tool suite provides automated harmonization workflows integrated into the Galaxy platform.

## Tools

### Harmonization Tool (`harmonization_tool/`)

A Galaxy tool that harmonizes GWAS summary statistics to a standard format (LDSC-compatible) using GWASLab v4.0.4.
See `harmonization_tool/README.md` for detailed usage and inputs.

**Features:**
- Auto-detection of input format
- Manual column specification
- Reference-based allele flipping and strand correction
- rsID annotation (optional)
- Multi-threaded processing for large datasets
- Output in LDSC format with HapMap3 SNPs, excluding HLA region

**Requirements:**
- GWASLab 4.0.4
- Python 3.12
- Reference genome FASTA
- Inference VCF with allele frequencies
- Optional: rsID mapping file

## Installation

1. Clone this repository into your Galaxy tools directory.
2. Install dependencies via Galaxy's tool requirements.
3. Restart Galaxy to load the tools.

## Usage

Upload your GWAS summary statistics and reference files to Galaxy, then run the harmonization tool with appropriate parameters.

## Repository Layout
- `harmonization_tool/`: Galaxy tool wrapper and Python entry point.
- `Notebooks/`: exploratory notebooks and examples.
- `gwaslab-sample-data/`: sample inputs for local testing.
