# import sys
# import gwaslab as gl
# import matplotlib.pyplot as plt

# input_file = sys.argv[1]
# output_manhattan = sys.argv[2]
# output_qq = sys.argv[3]

# # Load summary statistics
# sumstats = gl.Sumstats(input_file, fmt="auto")

# # Drop duplicate columns if any
# sumstats.data = sumstats.data.loc[:, ~sumstats.data.columns.duplicated()]

# # Ensure EA/NEA are strings
# sumstats.data["EA"] = sumstats.data["EA"].astype(str)
# sumstats.data["NEA"] = sumstats.data["NEA"].astype(str)

# # Perform basic check to clean data before plotting
# sumstats.basic_check()

# # Generate and save Manhattan plot
# # manhattan_plot = sumstats.plot_manhattan(show=False)
# plot = sumstats.plot_mqq()

# plt.savefig(output_manhattan, dpi=300)
# plt.clf()  # Clear figure for the next plot

# # Generate and save Q-Q plot
# qq_plot = sumstats.plot_qq(show=False)
# plt.savefig(output_qq, dpi=300)
# plt.clf()






# import sys
# import gwaslab as gl
# import matplotlib.pyplot as plt

# input_file = sys.argv[1]
# output_qq = sys.argv[2]

# # Load and clean sumstats
# sumstats = gl.Sumstats(input_file, fmt="auto")
# sumstats.data = sumstats.data.loc[:, ~sumstats.data.columns.duplicated()]
# sumstats.data["EA"] = sumstats.data["EA"].astype(str)
# sumstats.data["NEA"] = sumstats.data["NEA"].astype(str)
# sumstats.basic_check()

# # Generate and save the MQQ plot
# # fig, ax = sumstats.plot_mqq()
# fig, ax = sumstats.plot_mqq(snpid="SNPID")
# fig.savefig(output_qq, dpi=300)
# plt.clf()



# import sys
# import gwaslab as gl
# import matplotlib.pyplot as plt

# input_file = sys.argv[1]
# output_qq = sys.argv[2]

# # Load and clean sumstats
# sumstats = gl.Sumstats(input_file, fmt="plink2")
# sumstats.data = sumstats.data.loc[:, ~sumstats.data.columns.duplicated()]
# sumstats.data["EA"] = sumstats.data["EA"].astype(str)
# sumstats.data["NEA"] = sumstats.data["NEA"].astype(str)
# sumstats.basic_check()

# # Print column names to confirm what's available
# print("Column names in input file:", sumstats.data.columns)

# # Confirm if SNP ID column is present
# if "SNPID" not in sumstats.data.columns:
#     raise ValueError("Expected SNPID column not found in input data. Available columns: " + ", ".join(sumstats.data.columns))

# sumstats.plot_mqq()
# fig, ax = sumstats.plot_mqq()
# fig.savefig(output_qq, dpi=300)
# plt.clf()



# import sys
# import gwaslab as gl
# import matplotlib.pyplot as plt
# import os

# input_file = sys.argv[1]
# output_qq = sys.argv[2]

# # Ensure output file has a valid image extension
# valid_exts = {".png", ".jpg", ".jpeg", ".svg", ".pdf", ".tiff", ".webp"}
# _, ext = os.path.splitext(output_qq)
# if ext.lower() not in valid_exts:
#     output_qq += ".png"  # Default to PNG if invalid or missing

# # Load and process summary statistics
# sumstats = gl.Sumstats(input_file, fmt="plink2")
# sumstats.data = sumstats.data.loc[:, ~sumstats.data.columns.duplicated()]
# sumstats.data["EA"] = sumstats.data["EA"].astype(str)
# sumstats.data["NEA"] = sumstats.data["NEA"].astype(str)
# sumstats.basic_check()

# # Plot and save
# # fig, ax = sumstats.plot_mqq()
# # fig.savefig(output_qq, dpi=300)
# # plt.clf()


# plot = sumstats.plot_mqq(
#     title="GWAS Manhattan and QQ Plot"
# )

# # Save the plot to file for Galaxy output
# plt.savefig("gwas_mqq_plot.png", dpi=300, bbox_inches="tight")








#!/usr/bin/env python3

# import sys
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
# from scipy import stats
# import gwaslab as gl


# def create_manhattan_plot(df, output_file):
#     df['-log10p'] = -np.log10(df['P'])
#     df['ind'] = range(len(df))
#     df_grouped = df.groupby('CHR')

#     fig, ax = plt.subplots(figsize=(12, 6))
#     colors = ['#4E79A7', '#F28E2B']
#     x_labels = []
#     x_labels_pos = []

#     for i, (name, group) in enumerate(df_grouped):
#         group.plot(kind='scatter', x='ind', y='-log10p', color=colors[i % len(colors)], ax=ax, s=10)
#         x_labels.append(name)
#         x_labels_pos.append((group['ind'].iloc[-1] + group['ind'].iloc[0]) / 2)

#     ax.set_xticks(x_labels_pos)
#     ax.set_xticklabels(x_labels)
#     ax.set_xlabel('Chromosome')
#     ax.set_ylabel('-Log10(p-value)')
#     ax.set_title('Manhattan Plot')
#     plt.tight_layout()
#     plt.savefig(output_file)
#     plt.close()

# def create_qq_plot(p_values, output_file):
#     p_values = p_values.dropna()
#     p_values = p_values[p_values > 0]
#     observed = -np.log10(np.sort(p_values))
#     expected = -np.log10(np.linspace(1 / len(p_values), 1, len(p_values)))

#     fig, ax = plt.subplots(figsize=(6, 6))
#     ax.scatter(expected, observed, s=10, color='blue')
#     ax.plot([0, max(expected)], [0, max(expected)], color='red', linestyle='--')
#     ax.set_xlabel('Expected -Log10(p)')
#     ax.set_ylabel('Observed -Log10(p)')
#     ax.set_title('QQ Plot')
#     plt.tight_layout()
#     plt.savefig(output_file)
#     plt.close()

# def main():
#     input_file = sys.argv[1]
#     manhattan_output = sys.argv[2]
#     qq_output = sys.argv[3]

#     # df = pd.read_csv(input_file, sep="\t")
#     sumstats = gl.Sumstats(input_file, fmt="plink2")
#     df = sumstats.data

#     # Ensure required columns exist
#     # required_columns = {'CHR', 'BP', 'P'}
#     # if not required_columns.issubset(df.columns):
#     #     sys.exit("Error: Input file must contain CHR, BP, and P columns.")

#     create_manhattan_plot(df, manhattan_output)
#     create_qq_plot(df['P'], qq_output)

# if __name__ == "__main__":
#     main()




# import sys
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
# import gwaslab as gl


# def create_manhattan_plot(df, output_file):
#     df['-log10p'] = -np.log10(df['P'])
#     df['ind'] = range(len(df))
#     df_grouped = df.groupby('CHR')

#     fig, ax = plt.subplots(figsize=(12, 6))
#     colors = ['#4E79A7', '#F28E2B']
#     x_labels = []
#     x_labels_pos = []

#     for i, (name, group) in enumerate(df_grouped):
#         group.plot(kind='scatter', x='ind', y='-log10p', color=colors[i % len(colors)], ax=ax, s=10)
#         x_labels.append(str(name))
#         x_labels_pos.append((group['ind'].iloc[-1] + group['ind'].iloc[0]) / 2)

#     ax.set_xticks(x_labels_pos)
#     ax.set_xticklabels(x_labels)
#     ax.set_xlabel('Chromosome')
#     ax.set_ylabel('-Log10(p-value)')
#     ax.set_title('Manhattan Plot')
#     plt.tight_layout()
#     plt.savefig(output_file)
#     plt.close()

# def create_qq_plot(p_values, output_file):
#     p_values = p_values.dropna()
#     p_values = p_values[p_values > 0]
#     observed = -np.log10(np.sort(p_values))
#     expected = -np.log10(np.linspace(1 / len(p_values), 1, len(p_values)))

#     fig, ax = plt.subplots(figsize=(6, 6))
#     ax.scatter(expected, observed, s=10, color='blue')
#     ax.plot([0, max(expected)], [0, max(expected)], color='red', linestyle='--')
#     ax.set_xlabel('Expected -Log10(p)')
#     ax.set_ylabel('Observed -Log10(p)')
#     ax.set_title('QQ Plot')
#     plt.tight_layout()
#     plt.savefig(output_file)
#     plt.close()

# def main():
#     input_file = sys.argv[1]
#     manhattan_output = sys.argv[2]
#     qq_output = sys.argv[3]

#     # df = pd.read_csv(input_file, sep="\t")
#     sumstats = gl.Sumstats(input_file, fmt="plink2")
#     df = sumstats.data

#     # Rename POS → BP to be consistent (optional)
#     if 'POS' in df.columns:
#         df.rename(columns={'POS': 'BP'}, inplace=True)

#     # Check required columns
#     required_columns = {'CHR', 'BP', 'P'}
#     if not required_columns.issubset(df.columns):
#         sys.exit("Error: Input file must contain CHR, BP (or POS), and P columns.")

#     create_manhattan_plot(df, manhattan_output)
#     create_qq_plot(df['P'], qq_output)

# if __name__ == "__main__":
#     main()



#!/usr/bin/env python3

import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def create_manhattan_plot(df, output_file):
    df['BP'] = pd.to_numeric(df['BP'], errors='coerce')
    df['CHR'] = pd.to_numeric(df['CHR'], errors='coerce')
    df = df.dropna(subset=['CHR', 'BP', 'P'])

    df['-log10p'] = -np.log10(df['P'])
    df['ind'] = range(len(df))
    df_grouped = df.groupby('CHR')

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['#4E79A7', '#F28E2B']
    x_labels = []
    x_labels_pos = []

    for i, (name, group) in enumerate(df_grouped):
        group.plot(kind='scatter', x='ind', y='-log10p', color=colors[i % len(colors)], ax=ax, s=10)
        x_labels.append(int(name))
        x_labels_pos.append((group['ind'].iloc[-1] + group['ind'].iloc[0]) / 2)

        # Add horizontal genome-wide significance line
    sig_threshold = -np.log10(5e-8)
    ax.axhline(y=sig_threshold, color='red', linestyle='--', linewidth=1)
    ax.text(df['ind'].max(), sig_threshold + 0.2, 'p = 5e-8', color='red', ha='right')

    ax.set_xticks(x_labels_pos)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel('Chromosome')
    ax.set_ylabel('-Log10(p-value)')
    ax.set_title('Manhattan Plot')
    plt.tight_layout()
    plt.savefig(output_file, format='png')  # <-- FORCES PNG FORMAT
    plt.close()


def create_qq_plot(p_values, output_file):
    p_values = p_values.dropna()
    p_values = p_values[p_values > 0]
    observed = -np.log10(np.sort(p_values))
    expected = -np.log10(np.linspace(1 / len(p_values), 1, len(p_values)))

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(expected, observed, s=10, color='blue')
    ax.plot([0, max(expected)], [0, max(expected)], color='red', linestyle='--')
    ax.set_xlabel('Expected -Log10(p)')
    ax.set_ylabel('Observed -Log10(p)')
    ax.set_title('QQ Plot')
    plt.tight_layout()
    plt.savefig(output_file, format='png')  # <-- FORCES PNG FORMAT
    plt.close()


def main():
    input_file = sys.argv[1]
    manhattan_output = sys.argv[2]
    qq_output = sys.argv[3]

    df = pd.read_csv(input_file, sep="\t")

    # Rename POS to BP if needed
    if 'POS' in df.columns and 'BP' not in df.columns:
        df.rename(columns={'POS': 'BP'}, inplace=True)

    required_columns = {'CHR', 'BP', 'P'}
    if not required_columns.issubset(df.columns):
        sys.exit("Error: Input file must contain CHR, BP (or POS), and P columns.")

    create_manhattan_plot(df, manhattan_output)
    create_qq_plot(df['P'], qq_output)


if __name__ == "__main__":
    main()
