#!/usr/bin/env python3
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--bfile", required=True)
parser.add_argument("--pval", required=True)
parser.add_argument("--gene_annot", required=True)
parser.add_argument("--N", required=True)
parser.add_argument("--out", required=True)

args = parser.parse_args()

cmd = [
    "magma",
    "--bfile", args.bfile,
    "--pval", args.pval, f"N={args.N}",
    "--gene-annot", args.gene_annot,
    "--out", args.out
]

subprocess.run(cmd, check=True)
