#!/usr/bin/env python3
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--snp_loc", required=True)
parser.add_argument("--gene_loc", required=True)
parser.add_argument("--out", required=True)
parser.add_argument("--window", default=None)

args = parser.parse_args()

cmd = [
    "magma",
    "--annotate",
    "--snp-loc", args.snp_loc,
    "--gene-loc", args.gene_loc,
    "--out", args.out
]

if args.window:
    cmd.insert(2, f"window={args.window}")

subprocess.run(cmd, check=True)