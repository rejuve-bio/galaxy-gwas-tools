#!/usr/bin/env python3
import argparse
import gzip
import csv
import sys

def detect_delimiter(line):
    if '\t' in line:
        return '\t'
    elif ',' in line:
        return ','
    else:
        return None

def convert_gzip_to_tabular(input_path, output_path, output_format):
    try:
        with gzip.open(input_path, 'rt', encoding='utf-8', errors='replace') as gz_file:
            
            # Peek first line to detect input delimiter
            first_line = gz_file.readline()
            if not first_line:
                raise ValueError("Input GZIP file is empty.")

            input_delim = detect_delimiter(first_line)
            if not input_delim:
                raise ValueError("Could not detect delimiter in input file.")

            # Determine output delimiter
            output_delim = '\t' if output_format == "tsv" else ','

            # Rewind file after reading first line
            gz_file.seek(0)

            writer = csv.writer(open(output_path, 'w', newline=''), delimiter=output_delim)

            for line in gz_file:
                row = line.strip().split(input_delim)
                writer.writerow(row)

    except OSError:
        raise RuntimeError("Invalid GZIP file format or unsupported compression.")
    except Exception as e:
        raise RuntimeError(f"Error processing file: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Convert GZIP file to CSV/TSV")
    parser.add_argument("--input", required=True, help="Input .gz file")
    parser.add_argument("--output", required=True, help="Output tabular file")
    parser.add_argument("--format", required=True, choices=["csv", "tsv"],
                        help="Output format")

    args = parser.parse_args()

    try:
        convert_gzip_to_tabular(args.input, args.output, args.format)
    except Exception as e:
        sys.stderr.write(str(e) + "\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
