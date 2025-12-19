#!/usr/bin/env python3
import argparse
import gzip
import sys
import os

def open_file(filename, mode="rt"):
    """Automatically handle .gz files"""
    return gzip.open(filename, mode) if str(filename).endswith(".gz") else open(filename, mode)

def detect_columns(header):
    """Detect column indices from header using common synonyms"""
    fields = header.strip().split()
    lower_fields = [f.lower().replace('_', '').replace('-', '').replace('#', '') for f in fields]
    
    col = {'snp': None, 'chr': None, 'pos': None, 'p': None, 'n': None}
    
    snp_synonyms = ['snp', 'rsid', 'rs', 'marker', 'markername', 'variant', 'variantid', 'id']
    chr_synonyms = ['chr', 'chrom', 'chromosome', 'chrm']
    pos_synonyms = ['pos', 'bp', 'position', 'basepair', 'start']
    p_synonyms = ['p', 'pval', 'pvalue', 'p_val', 'p_bolt_lmm', 'pval_bolt', 'log10p', 'minuslog10p']
    n_synonyms = ['n', 'neff', 'n_eff', 'ncase', 'ncases', 'ncontrol', 'ncontrols', 'samplesize', 'sample_size']

    for i, name in enumerate(lower_fields):
        if col['snp'] is None and any(s in name for s in snp_synonyms):
            col['snp'] = i
        if col['chr'] is None and any(s in name for s in chr_synonyms):
            col['chr'] = i
        if col['pos'] is None and any(s in name for s in pos_synonyms):
            col['pos'] = i
        if col['p'] is None and any(s in name for s in p_synonyms):
            col['p'] = i
        if col['n'] is None and any(s in name for s in n_synonyms):
            col['n'] = i

    return col, fields

def is_log10_p(p_values, sample_size=1000):
    """Guess if p-values are -log10 transformed"""
    valid_p = [p for p in p_values if p > 0]
    if len(valid_p) < 10:
        return False
    return sum(p > 10 for p in valid_p) > len(valid_p) * 0.7  # most values >10 → likely -log10

def main():
    parser = argparse.ArgumentParser(description="Auto-format GWAS for MAGMA")
    parser.add_argument("--gwas", required=True, help="Input GWAS file (txt or txt.gz)")
    parser.add_argument("--out_prefix", required=True, help="Prefix for output files")
    args = parser.parse_args()

    gwas_file = args.gwas
    prefix = args.out_prefix

    # Output filenames
    snp_loc_file = f"{prefix}.snp.chr.pos.txt"
    pval_file = f"{prefix}.pval.txt"
    meta_file = f"{prefix}.meta.txt"

    try:
        with open_file(gwas_file, "rt") as f:
            header_line = next(f)
    except Exception as e:
        sys.exit(f"Error: Cannot read GWAS file: {e}")

    # Detect columns
    col_indices, original_header = detect_columns(header_line)

    missing = [name for name, idx in col_indices.items() if idx is None and name != 'n']
    if missing:
        sys.exit(
            f"Error: Could not auto-detect required columns: {', '.join(missing)}\n"
            f"Header line: {header_line.strip()}\n"
            "Please ensure your file has recognizable headers for SNP, CHR, POS, and P-value."
        )

    # Sample p-values to detect -log10
    p_sample = []
    try:
        with open_file(gwas_file, "rt") as f:
            next(f)  # skip header
            for _ in range(2000):
                line = f.readline()
                if not line:
                    break
                parts = line.strip().split()
                if len(parts) <= col_indices['p']:
                    continue
                try:
                    p_val = float(parts[col_indices['p']])
                    if p_val > 0:
                        p_sample.append(p_val)
                except:
                    pass
    except:
        pass

    p_is_log10 = is_log10_p(p_sample)

    # Estimate N if not present (use median if available)
    estimated_n = "NA"
    if col_indices['n'] is not None:
        n_values = []
        try:
            with open_file(gwas_file, "rt") as f:
                next(f)
                for _ in range(1000):
                    line = f.readline()
                    if not line:
                        break
                    parts = line.strip().split()
                    if len(parts) > col_indices['n']:
                        try:
                            n_values.append(float(parts[col_indices['n']]))
                        except:
                            pass
            if n_values:
                estimated_n = f"{sum(n_values)/len(n_values):.1f} (from N column)"
        except:
            pass

    # Write metadata summary
    with open(meta_file, "w") as meta:
        meta.write("MAGMA GWAS Formatting Summary\n")
        meta.write(f"Input file: {os.path.basename(gwas_file)}\n")
        meta.write(f"Detected columns:\n")
        meta.write(f"  SNP column: {original_header[col_indices['snp']]} (index {col_indices['snp']+1})\n")
        meta.write(f"  CHR column: {original_header[col_indices['chr']]} (index {col_indices['chr']+1})\n")
        meta.write(f"  POS column: {original_header[col_indices['pos']]} (index {col_indices['pos']+1})\n")
        meta.write(f"  P column:   {original_header[col_indices['p']]} (index {col_indices['p']+1})\n")
        meta.write(f"  N column:   {'Detected' if col_indices['n'] else 'Not found'}\n")
        meta.write(f"P-value format: {'-log10(P)' if p_is_log10 else 'raw P'}\n")
        meta.write(f"Effective N: {estimated_n}\n")

    # Process and write output files
    with open_file(gwas_file, "rt") as f, \
         open(snp_loc_file, "w") as snp_out, \
         open(pval_file, "w") as p_out:

        next(f)  # skip header

        for line in f:
            parts = line.strip().split()
            if len(parts) < max(col_indices.values()) + 1:
                continue

            snp = parts[col_indices['snp']]
            try:
                chr_val = int(parts[col_indices['chr']])
                pos = int(parts[col_indices['pos']])
            except ValueError:
                continue

            try:
                p_raw = float(parts[col_indices['p']])
            except ValueError:
                continue

            if p_raw <= 0 and p_is_log10:
                continue  # avoid log(0)

            p_final = 10 ** (-p_raw) if p_is_log10 else p_raw
            if p_final <= 0 or p_final > 1:
                continue  # invalid p-value

            n_val = "NA"
            if col_indices['n'] is not None:
                try:
                    n_val = parts[col_indices['n']]
                except:
                    pass

            # MAGMA SNP location: SNP CHR POS
            snp_out.write(f"{snp}\t{chr_val}\t{pos}\n")

            # MAGMA p-value file: SNP N P
            p_out.write(f"{snp}\t{n_val}\t{p_final:.10g}\n")

    print("Formatting complete!")
    print(f"Outputs written with prefix: {prefix}")

if __name__ == "__main__":
    main()