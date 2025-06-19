import sys
import gwaslab as gl
import pandas as pd

input_file = sys.argv[1]
output_file = sys.argv[2]

sumstats = gl.Sumstats(input_file, fmt="auto")
sumstats.basic_check()
sumstats.df.to_csv(output_file, sep="\t", index=False)
