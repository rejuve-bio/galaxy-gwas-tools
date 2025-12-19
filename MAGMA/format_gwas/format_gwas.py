#!/usr/bin/env python3
import argparse
import gzip
import sys

def auto_detect_columns(header_line):
    """Detect column indices based on common GWAS header names."""
    header = header_line.strip().split()
    header_lower = [h.lower().replace('_', '').replace('-', '').replace('#', '') for h in header]

    col_map = {}

    # Common variants for each column
    snp_names = ['snp', 'rsid', 'rs', 'marker', 'markername', 'variant', 'variantid', 'id']
    chr_names = ['chr', 'chrom', 'chromosome', 'chrm']
    pos_names = ['pos', 'bp', 'position', 'basepair', 'start', 'end']
    p_names = ['p', 'pval', 'pvalue', 'p_val', 'p_bolt', 'p_lmm', 'log10p', 'minuslog10p']

    for i, h in enumerate(header_lower):
        if any(name in h for name in snp_names):
            col_map['snp'] = i
        if any(name in h for name in chr_names):
            col_map['chr'] = i
        if any(name in h for name in pos_names):
            col_map['pos'] = i
        if any(name in h for name in p_names):
            col_map['p'] = i

    return col_map, header  # return original header too for error messages


def is_log10_p(p_values):
    """Heuristic: if most p-values > 20, assume they are -log10(p)"""
    large_count = sum(1 for p in p_values if p > 20)
    return large_count > len(p_values) * 0.5  # majority rule


parser = argparse.ArgumentParser(description="Format GWAS for MAGMA")
parser.add_argument("--gwas", required=True, help="Input GWAS summary statistics file")
parser.add_argument("--chr", type=int, required=True, help="Chromosome to extract")
parser.add_argument("--snp_loc", required=True, help="Output SNP location file")
parser.add_argument("--pval", required=True, help="Output p-value file")

# Optional manual overrides (only used if provided)
parser.add_argument("--snp_col", type=int, help="SNP column index (1-based)")
parser.add_argument("--chr_col", type=int, help="CHR column index (1-based)")
parser.add_argument("--pos_col", type=int, help="Position column index (1-based)")
parser.add_argument("--p_col", type=int, help="P-value column index (1-based)")
parser.add_argument("--p_is_log10", action="store_true", help="Force treat p-column as -log10(p)")

args = parser.parse_args()

# Determine file opener
open_func = gzip.open if str(args.gwas).endswith(".gz") else open

try:
    with open_func(args.gwas, "rt") as f:
        header_line = next(f)
except Exception as e:
    sys.exit(f"Error reading GWAS file: {e}")

# Auto-detect columns
detected, original_header = auto_detect_columns(header_line)

# Use manual overrides only if provided
snp_idx = (args.snp_col - 1) if args.snp_col else detected.get('snp')
chr_idx = (args.chr_col - 1) if args.chr_col else detected.get('chr')
pos_idx = (args.pos_col - 1) if args.pos_col else detected.get('pos')
p_idx   = (args.p_col - 1)   if args.p_col   else detected.get('p')

missing = []
if snp_idx is None: missing.append("SNP (rsid/marker)")
if chr_idx is None: missing.append("CHR (chromosome)")
if pos_idx is None: missing.append("POS (position/bp)")
if p_idx is None:   missing.append("P-value")

if missing:
    sys.exit(
        f"Error: Could not auto-detect required columns: {', '.join(missing)}\n"
        f"Header line was: {header_line.strip()}\n"
        "Please use Advanced Options to manually specify column indices."
    )

# Determine if p-values are -log10 (only auto-detect if user didn't force it)
force_log10 = args.p_is_log10
auto_log10_guess = False

if not force_log10:
    # Sample first 1000 p-values to guess
    p_sample = []
    try:
        with open_func(args.gwas, "rt") as f:
            next(f)  # skip header
            for i, line in enumerate(f):
                if i >= 1000:
                    break
                cols = line.strip().split()
                if len(cols) <= p_idx:
                    continue
                try:
                    p_val = float(cols[p_idx])
                    if p_val > 0:  # ignore 0 or negative
                        p_sample.append(p_val)
                except:
                    pass
        if p_sample:
            auto_log10_guess = is_log10_p(p_sample)
    except:
        pass  # fall back to assuming raw p-values

use_log10 = force_log10 or auto_log10_guess

# Now process the file
with open_func(args.gwas, "rt") as f, \
     open(args.snp_loc, "w") as snp_out, \
     open(args.pval, "w") as p_out:

    next(f)  # skip header

    for line in f:
        cols = line.strip().split()
        if len(cols) < max(snp_idx, chr_idx, pos_idx, p_idx) + 1:
            continue  # malformed line

        try:
            line_chr = int(cols[chr_idx])
        except ValueError:
            continue  # non-numeric chromosome

        if line_chr != args.chr:
            continue

        snp = cols[snp_idx]
        pos = cols[pos_idx]
        try:
            p = float(cols[p_idx])
        except ValueError:
            continue  # invalid p-value

        if use_log10:
            if p <= 0:
                continue  # avoid log(0)
            p = 10 ** (-p)

        # Write outputs in MAGMA format
        snp_out.write(f"{snp}\t{line_chr}\t{pos}\n")
        p_out.write(f"{snp}\t{p:.10g}\n")  # scientific notation, clean output

print("Formatting complete.")
if not force_log10:
    print(f"P-values treated as {'-log10(p)' if use_log10 else 'raw p-values'} "
          f"(auto-detected: {'yes' if auto_log10_guess else 'no'})")