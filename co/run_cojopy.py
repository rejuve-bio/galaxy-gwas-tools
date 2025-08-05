import sys
import cojopy

gwas_file = sys.argv[1]
ld_path = sys.argv[2]       # this should be the precomputed LD matrix file
output_file = sys.argv[3]

cojo = cojopy.COJO()
cojo.load_sumstats(gwas_file, ld_path=ld_path)
cojo.window_size = 1000000
cojo.p_cutoff = 5e-8

cojo.run_conditional_analysis()

results = cojo.snps_selected

with open(output_file, 'w') as f:
    for snp in results:
        f.write(snp + '\n')
