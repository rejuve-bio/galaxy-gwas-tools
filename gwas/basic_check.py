# import sys
# import gwaslab as gl
# import pandas as pd

# input_file = sys.argv[1]
# output_file = sys.argv[2]

# sumstats = gl.Sumstats(input_file, fmt="auto")
# # Ensure EA/NEA are strings
# sumstats.data["EA"] = sumstats.data["EA"].astype(str)
# sumstats.data["NEA"] = sumstats.data["NEA"].astype(str)

# sumstats.basic_check()
# sumstats.data.to_csv(output_file, sep="\t", index=False)




import sys
import gwaslab as gl
import pandas as pd

input_file = sys.argv[1]
output_file = sys.argv[2]

sumstats = gl.Sumstats(input_file, fmt="auto")

sumstats

# Fix: Drop duplicate columns
sumstats.data = sumstats.data.loc[:, ~sumstats.data.columns.duplicated()]

# Ensure EA/NEA are strings
sumstats.data["EA"] = sumstats.data["EA"].astype(str)
sumstats.data["NEA"] = sumstats.data["NEA"].astype(str)

sumstats.basic_check()
sumstats.data.to_csv(output_file, sep="\t", index=False)
