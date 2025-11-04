#!/usr/bin/env python3

import sys
import pandas as pd
import gwaslab as gl

def main():
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Load as sumstats
    sumstats = gl.Sumstats(input_file, fmt="auto")

    # Fill in BETA values from OR
    sumstats.fill_data(to_fill=["BETA"])

    # Output final result
    sumstats.data.to_csv(output_file, sep="\t", index=False)

if __name__ == "__main__":
    main()
