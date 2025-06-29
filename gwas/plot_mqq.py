import sys
import gwaslab as gl
import matplotlib.pyplot as plt

input_file = sys.argv[1]
output_manhattan = sys.argv[2]
output_qq = sys.argv[3]

# Load summary statistics
sumstats = gl.Sumstats(input_file, fmt="auto")

# Drop duplicate columns if any
sumstats.data = sumstats.data.loc[:, ~sumstats.data.columns.duplicated()]

# Ensure EA/NEA are strings
sumstats.data["EA"] = sumstats.data["EA"].astype(str)
sumstats.data["NEA"] = sumstats.data["NEA"].astype(str)

# Perform basic check to clean data before plotting
sumstats.basic_check()

# Generate and save Manhattan plot
manhattan_plot = sumstats.plot_manhattan(show=False)
plt.savefig(output_manhattan, dpi=300)
plt.clf()  # Clear figure for the next plot

# Generate and save Q-Q plot
qq_plot = sumstats.plot_qq(show=False)
plt.savefig(output_qq, dpi=300)
plt.clf()
