#!/usr/bin/env python3
"""
GWASLab-based harmonization wrapper for Galaxy.

This script is invoked by the Galaxy tool XML and writes outputs/logs to the
paths provided by Galaxy.
"""

from __future__ import annotations

import argparse
import logging
from typing import Dict

import gwaslab as gl


MANUAL_COLUMNS = ("snpid", "chrom", "pos", "ea", "nea", "eaf", "beta", "se", "p", "n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GWASLab Harmonization Tool")
    parser.add_argument("--input", required=True, help="GWAS summary statistics file")
    parser.add_argument("--format", default="auto", help="Format keyword or 'manual'")
    parser.add_argument("--snpid", default=None, help="SNPID column name")
    parser.add_argument("--chrom", default=None, help="CHR column name")
    parser.add_argument("--pos", default=None, help="POS column name")
    parser.add_argument("--ea", default=None, help="EA column name")
    parser.add_argument("--nea", default=None, help="NEA column name")
    parser.add_argument("--eaf", default=None, help="EAF column name")
    parser.add_argument("--beta", default=None, help="BETA column name")
    parser.add_argument("--se", default=None, help="SE column name")
    parser.add_argument("--p", default=None, help="P column name")
    parser.add_argument("--n", default=None, help="N column name")
    parser.add_argument("--ref_seq", required=True, help="Reference genome FASTA file (uploaded)")
    parser.add_argument("--ref_infer", required=True, help="Inference VCF file with AF (uploaded)")
    parser.add_argument("--ref_rsid_tsv", default=None, help="rsID TSV file (optional, uploaded)")
    parser.add_argument("--output", required=True, help="Output dataset path")
    parser.add_argument("--log", required=True, help="Log file")
    return parser.parse_args()


def configure_logging(log_path: str) -> None:
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def collect_manual_kwargs(args: argparse.Namespace) -> Dict[str, str]:
    return {key: value for key, value in vars(args).items() if key in MANUAL_COLUMNS and value}


def output_base(path: str) -> str:
    if path.endswith(".gz"):
        return path[:-3]
    return path


def main() -> None:
    args = parse_args()
    configure_logging(args.log)

    logging.info("GWASLab Harmonization Tool started")
    load_kwargs = collect_manual_kwargs(args)

    logging.info("Loading sumstats")
    ss = gl.Sumstats(args.input, fmt=args.format, **load_kwargs)

    ss.infer_build()
    build = ss.meta.get("genome_build", "unknown")
    logging.info("Build detected/inferred: %s", build)

    logging.info("Running basic_check")
    ss.basic_check(remove_dup=True, threads=4)

    if args.ref_rsid_tsv:
        logging.info("Annotating rsIDs")
        ss.assign_rsid2(path=args.ref_rsid_tsv, threads=4, overwrite="all")
    else:
        logging.info("Skipping rsID annotation")

    logging.info("Harmonizing")
    ss.harmonize(
        basic_check=False,
        ref_seq=args.ref_seq,
        ref_infer=args.ref_infer,
        ref_alt_freq="AF",
        ref_rsid_tsv=args.ref_rsid_tsv,
        threads=4,
        remove=False,
        sweep_mode=True,
    )
    ss.flip_allele_stats()

    logging.info("Saving harmonized output")
    ss.to_format(
        output_base(args.output),
        fmt="ldsc",
        hapmap3=True,
        exclude_hla=True,
        md5sum=True,
    )  # .gz handled by Galaxy

    logging.info("Finished successfully")


if __name__ == "__main__":
    main()
