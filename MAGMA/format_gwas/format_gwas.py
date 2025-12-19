#!/usr/bin/env python3
import argparse
import gzip

parser = argparse.ArgumentParser()
parser.add_argument("--gwas", required=True)
parser.add_argument("--chr", required=True, type=int)
parser.add_argument("--snp_loc", required=True)
parser.add_argument("--pval", required=True)
parser.add_argument("--p_is_log10", action="store_true")
parser.add_argument("--snp_col", type=int, required=True)
parser.add_argument("--chr_col", type=int, required=True)
parser.add_argument("--pos_col", type=int, required=True)
parser.add_argument("--p_col", type=int, required=True)

args = parser.parse_args()

open_func = gzip.open if args.gwas.endswith(".gz") else open

with open_func(args.gwas, "rt") as f, \
     open(args.snp_loc, "w") as snp_out, \
     open(args.pval, "w") as p_out:

    header = next(f)
    for line in f:
        cols = line.strip().split()
        if int(cols[args.chr_col - 1]) != args.chr:
            continue

        snp = cols[args.snp_col - 1]
        chr_ = cols[args.chr_col - 1]
        pos = cols[args.pos_col - 1]
        p = float(cols[args.p_col - 1])

        if args.p_is_log10:
            p = 10 ** (-p)

        snp_out.write(f"{snp}\t{chr_}\t{pos}\n")
        p_out.write(f"{snp}\t{p}\n")
