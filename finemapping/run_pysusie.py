#!/usr/bin/env python3

import argparse
import pandas as pd
import numpy as np
import rpy2.robjects as ro
from rpy2.robjects import numpy2ri
from rpy2.robjects.conversion import localconverter

def main():
    parser = argparse.ArgumentParser(description="Run SuSiE fine-mapping using susieR via rpy2")
    parser.add_argument('--sumstats', required=True, help='Path to summary stats TSV file')
    parser.add_argument('--ld_matrix', required=True, help='Path to LD matrix file (tab-delimited)')
    parser.add_argument('--n', type=int, required=True, help='Sample size')
    parser.add_argument('--output_pips', required=True, help='Output file for PIPs')
    parser.add_argument('--output_creds', required=True, help='Output file for credible sets')

    args = parser.parse_args()

    # Load summary stats
    sumstats = pd.read_csv(args.sumstats, sep='\t')
    betas = sumstats['BETA'].values
    ses = sumstats['SE'].values

    # Load LD matrix
    R = np.loadtxt(args.ld_matrix)

    # Use rpy2 conversion context to convert numpy arrays to R objects
    with localconverter(ro.default_converter + numpy2ri.converter):
        ro.globalenv['bhat'] = betas
        ro.globalenv['shat'] = ses
        ro.globalenv['R'] = R
        ro.globalenv['n'] = args.n

        # Load susieR package and run susie_rss
        ro.r('library(susieR)')
        ro.r('fit <- susie_rss(bhat=bhat, shat=shat, R=R, n=n)')

        # Extract PIPs and credible sets
        pips = np.array(ro.r('fit$pip'))
        cs_list = ro.r('fit$sets$cs')

    # Write PIPs to file
    with open(args.output_pips, 'w') as f:
        f.write('SNP\tPIP\n')
        for snp, pip in zip(sumstats['SNP'], pips):
            f.write(f"{snp}\t{pip:.6f}\n")

    # Write credible sets to file
    with open(args.output_creds, 'w') as f:
        f.write('Credible_Set_ID\tSNPs\n')
        for i, cs in enumerate(cs_list):
            snp_indices = list(cs)
            snps_in_set = [sumstats['SNP'].iloc[idx-1] for idx in snp_indices]  # R is 1-based indexing
            f.write(f"{i+1}\t{','.join(snps_in_set)}\n")

    print("Done! PIPs and credible sets saved.")

if __name__ == "__main__":
    main()
