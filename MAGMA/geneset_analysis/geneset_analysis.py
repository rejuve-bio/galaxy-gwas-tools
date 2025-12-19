#!/usr/bin/env python3
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--gene_results", required=True)
parser.add_argument("--geneset", required=True)
parser.add_argument("--out", required=True)

args = parser.parse_args()

cmd = [
    "magma",
    "--gene-results", args.gene_results,
    "--set-annot", args.geneset,
    "--out", args.out
]

subprocess.run(cmd, check=True)
