# Galaxy Tools for GWAS Summary Statistics Processing and Fine-Mapping

This repository provides a suite of **Galaxy-compatible tools** for **genome-wide association study (GWAS)** data processing, analysis, and fine-mapping.
The tools integrate Python, R, and shell scripts to automate key workflows, including:

* Preprocessing and formatting GWAS summary statistics (`MungeSumstats`)
* Filtering genome-wide significant variants
* Downloading and preparing 1000 Genomes reference data
* Running **GCTA-COJO** conditional analysis
* LD-based regional fine-mapping with **SuSiE**

These components are modular, allowing them to be used independently as Galaxy tools or together as a pipeline.

---

## Features

* **Munge GWAS Summary Statistics**  
  Uses [MungeSumstats](https://bioconductor.org/packages/release/bioc/html/MungeSumstats.html) to harmonize, QC, and format GWAS input data for downstream analysis.

* **Significant Variant Extraction**  
  Filters variants below a genome-wide significance threshold (`p < 5e-8`).

* **1000 Genomes Reference Panel Preparation**  
  Automated scripts to:
  * Download VCFs (chr1–22)
  * Normalize and index files
  * Convert to PLINK binary format

* **GCTA-COJO Analysis**  
  Runs conditional and joint multiple-SNP analysis to identify independent signals.

* **Fine-Mapping with SuSiE**  
  Performs Bayesian fine-mapping using LD matrices from PLINK and the [susieR](https://github.com/stephenslab/susieR) package.  
  Includes optional hyperparameter optimization with Optuna.

---

## Requirements

### Python

* Python ≥ 3.8
* [marimo](https://github.com/marimo-team/marimo)
* pandas, numpy
* rpy2
* optuna

### R

* [MungeSumstats](https://bioconductor.org/packages/release/bioc/html/MungeSumstats.html)
* [susieR](https://github.com/stephenslab/susieR)
* BiocManager

### External Tools

* [PLINK 2.0](https://www.cog-genomics.org/plink/2.0/)
* [GCTA](https://yanglab.westlake.edu.cn/software/gcta/)
* Bash (for helper scripts)

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/rejuve-bio/galaxy-gwas-tools.git
   cd galaxy-gwas-tools
