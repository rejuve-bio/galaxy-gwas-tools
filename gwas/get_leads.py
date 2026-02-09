import sys
import gwaslab as gl

input_file = sys.argv[1]
output_file = sys.argv[2]

sumstats = gl.Sumstats(input_file, fmt="auto")
leads = sumstats.get_lead()
leads.to_csv(output_file, sep="\t", index=False)
