#!/usr/bin/env python3

import sys
import pandas as pd
import gwaslab as gl

def main():
    input_file = sys.argv[1]
    chr_value = sys.argv[2]
    start_pos = int(sys.argv[3])
    end_pos = int(sys.argv[4])
    output_file = sys.argv[5]

    # Load the input using gwaslab
    sumstats = gl.Sumstats(input_file, fmt="auto")
    
    # Filter by chromosome and position
    query = f"CHR=={chr_value} & POS>{start_pos} & POS<{end_pos}"
    locus = sumstats.filter_value(query)

    # Export filtered data
    locus.data.to_csv(output_file, sep="\t", index=False)

if __name__ == "__main__":
    main()
