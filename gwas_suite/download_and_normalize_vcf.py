#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os

VCF_URL_TEMPLATE = "http://hgdownload.cse.ucsc.edu/gbdb/hg19/1000Genomes/phase3/ALL.chr{chr}.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz"

def download_and_normalize(chromosome, reference_fasta, output_vcf, output_tbi):
    """
    Downloads a 1000 Genomes VCF, renames chromosomes to add 'chr' prefix,
    normalizes it, and creates an index.
    """
    try:
        # --- 1. Download the VCF file ---
        vcf_url = VCF_URL_TEMPLATE.format(chr=chromosome)
        raw_vcf_path = "raw_chr{}.vcf.gz".format(chromosome)

        print(f"Downloading VCF for chr{chromosome} from: {vcf_url}")
        subprocess.run(["wget", "-O", raw_vcf_path, vcf_url], check=True)
        print("Download complete.")

        # --- 2. Create a chromosome name mapping file ---
        # This file tells bcftools how to rename chromosomes (e.g., '1' -> 'chr1')
        chrom_map_file = "chromosome_map.txt"
        with open(chrom_map_file, 'w') as f:
            for i in range(1, 23):
                f.write(f"{i}\tchr{i}\n")
            f.write("X\tchrX\n")
            f.write("Y\tchrY\n")
            f.write("MT\tchrM\n")
        print("Created chromosome name map file.")

        # --- 3. Rename chromosomes and Normalize in a single pipeline ---
        print(f"Renaming chromosomes and normalizing {raw_vcf_path}...")

        # We use a shell pipeline:
        # bcftools annotate ... | bcftools norm ...
        # This is efficient as it doesn't create an intermediate file.

        command_pipeline = (
            f"bcftools annotate --rename-chrs {chrom_map_file} {raw_vcf_path} | "
            f"bcftools norm -f {reference_fasta} -m -any -Oz -o {output_vcf}"
        )

        # Run the command pipeline through the shell
        process = subprocess.run(command_pipeline, shell=True, check=True, capture_output=True, text=True)

        print(f"Normalization complete. Output saved to {output_vcf}")
        if process.stderr:
            print("Normalization messages:\n", process.stderr)


        # --- 4. Index the normalized VCF ---
        print(f"Indexing the normalized VCF file: {output_vcf}")
        subprocess.run(["tabix", "-p", "vcf", output_vcf], check=True)
        print("Indexing complete.")

    except subprocess.CalledProcessError as e:
        print(f"ERROR: A command failed to execute.", file=sys.stderr)
        print(f"Command: {e.cmd}", file=sys.stderr)
        print(f"Return Code: {e.returncode}", file=sys.stderr)
        print(f"Stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        sys.exit(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and normalize a 1000 Genomes VCF file.")
    parser.add_argument("--chromosome", required=True, help="Chromosome number (e.g., 22).")
    parser.add_argument("--reference", required=True, help="Path to the indexed reference FASTA file.")
    parser.add_argument("--output_vcf", required=True, help="Path for the output normalized VCF.gz file.")
    parser.add_argument("--output_tbi", required=True, help="Path for the output VCF index (.tbi) file.")

    args = parser.parse_args()

    download_and_normalize(
        args.chromosome,
        args.reference,
        args.output_vcf,
        args.output_tbi
    )