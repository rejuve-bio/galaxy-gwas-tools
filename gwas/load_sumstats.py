import sys
import gwaslab as gl

input_file = sys.argv[1]
output_file = sys.argv[2]

sumstats = gl.Sumstats(input_file, fmt="plink2")
sumstats.data.to_csv(output_file, sep="\t", index=False)
