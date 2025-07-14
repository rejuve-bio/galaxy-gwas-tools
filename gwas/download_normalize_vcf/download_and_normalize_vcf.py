#!/usr/bin/env python3

import argparse
import subprocess
import os

# VCF_URL_TEMPLATE = "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr{chr}.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz"
VCF_URL_TEMPLATE = "https://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr{chr}.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz"

def download_and_normalize(chr_num, output_prefix):
    url = VCF_URL_TEMPLATE.format(chr=chr_num)
    vcf_gz = f"{output_prefix}.vcf.gz"
    norm_vcf = f"{output_prefix}.normalized.vcf.gz"

    # Download
    subprocess.check_call(["wget", "-O", vcf_gz, url])

    # Index the raw VCF
    subprocess.check_call(["tabix", "-p", "vcf", vcf_gz])

    # Normalize using bcftools
    subprocess.check_call([
        "bcftools", "norm", 
        "-f", "/path/to/human_g1k_v37.fasta",  # You must have this reference locally
        "-Oz", "-o", norm_vcf, vcf_gz
    ])

    # Index the normalized VCF
    subprocess.check_call(["tabix", "-p", "vcf", norm_vcf])

    return norm_vcf

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and normalize 1000 Genomes VCF")
    parser.add_argument("--chr", required=True, help="Chromosome number (e.g., 22)")
    parser.add_argument("--output_prefix", required=True, help="Prefix for output files")

    args = parser.parse_args()
    download_and_normalize(args.chr, args.output_prefix)
