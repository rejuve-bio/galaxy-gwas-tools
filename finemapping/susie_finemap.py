#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np
import pysusie

def main():
    parser = argparse.ArgumentParser(description="Run SuSiE fine-mapping using GWAS sumstats and LD matrix")
    parser.add_argument("--sumstats", required=True, help="GWAS summary statistics TSV file")
    parser.add_argument("--ld_matrix", required=True, help="LD matrix TSV file")
    parser.add_argument("--snp_list", required=True, help="SNP list TSV file")
    parser.add_argument("--L", type=int, default=-1, help="Number of SuSiE components")
    parser.add_argument("--coverage", type=float, default=0.95, help="Credible set coverage")
    parser.add_argument("--credible_sets_out", required=True, help="Output file for credible sets")
    parser.add_argument("--pips_out", required=True, help="Output file for PIPs")

    args = parser.parse_args()

    # Load sumstats
    sumstats = pd.read_csv(args.sumstats, sep="\t")
    
    # Load LD matrix
    ld_matrix = pd.read_csv(args.ld_matrix, sep="\t", index_col=0)

    # Load SNP list and reorder sumstats to match LD matrix
    snp_list = pd.read_csv(args.snp_list, sep="\t", header=None, names=["SNP"])
    sumstats = sumstats.set_index("SNP").loc[snp_list["SNP"]].reset_index()

    # Run SuSiE
    susie_res = pysusie.susie(
        sumstats['beta'].values,
        ld_matrix.values,
        L=args.L,
        coverage=args.coverage
    )

    # Save outputs
    susie_res.credible_sets.to_csv(args.credible_sets_out, sep="\t", index=False)
    susie_res.pips.to_csv(args.pips_out, sep="\t", index=False)

if __name__ == "__main__":
    main()
