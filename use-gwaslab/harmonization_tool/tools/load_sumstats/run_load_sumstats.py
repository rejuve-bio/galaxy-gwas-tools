from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import tempfile

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.io.logging_utils import configure_logging, get_logger
from scripts.io.sumstats_io import (
    build_load_kwargs,
    detect_collection_suffix,
    normalize_other_columns,
    read_chromosome_manifest,
    write_dataframe,
    write_metadata,
)
from scripts.utils.gwaslab_runtime import (
    configure_runtime_environment,
    import_gwaslab_with_py310_compat,
)

RUNTIME_TMP = configure_runtime_environment()
gl = import_gwaslab_with_py310_compat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load GWAS summary statistics into a standardized table.")
    parser.add_argument("--mode", required=True, choices=("columns", "format", "auto", "chromsplit"))
    parser.add_argument("--input", help="Single summary statistics input file.")
    parser.add_argument("--chrom-manifest", help="Tab-delimited file of chromosome identifiers and paths.")
    parser.add_argument("--format-name", help="GWASLab format keyword.")
    parser.add_argument("--chrom-format-mode", choices=("format", "auto", "columns"), default="format")
    parser.add_argument("--sep", default="\t")
    parser.add_argument("--skiprows", type=int, default=0)
    parser.add_argument("--nrows", type=int)
    parser.add_argument("--na-values", default="")
    parser.add_argument("--build", choices=("19", "38", "99"))
    parser.add_argument("--verbose", action="store_true")

    for name in (
        "snpid",
        "rsid",
        "chrom",
        "pos",
        "ea",
        "nea",
        "ref",
        "alt",
        "eaf",
        "neaf",
        "n",
        "beta",
        "se",
        "chisq",
        "z",
        "p",
        "mlog10p",
        "info",
        "direction",
        "ncontrol",
        "ncase",
        "maf",
        "status",
    ):
        parser.add_argument(f"--{name}")

    parser.add_argument("--or-column", dest="OR")
    parser.add_argument("--or-95l", dest="OR_95L")
    parser.add_argument("--or-95u", dest="OR_95U")
    parser.add_argument("--hr-column", dest="HR")
    parser.add_argument("--hr-95l", dest="HR_95L")
    parser.add_argument("--hr-95u", dest="HR_95U")
    parser.add_argument("--beta-95l", dest="beta_95L")
    parser.add_argument("--beta-95u", dest="beta_95U")
    parser.add_argument("--i2")
    parser.add_argument("--phet")
    parser.add_argument("--dof")
    parser.add_argument("--snpr2")
    parser.add_argument("--f")
    parser.add_argument("--other")

    parser.add_argument("--output-tsv", required=True)
    parser.add_argument("--output-meta", required=True)
    parser.add_argument("--log", required=True)
    return parser.parse_args()


def build_reader_kwargs(args: argparse.Namespace) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "sep": normalize_separator(args.sep),
        "skiprows": args.skiprows,
    }
    if args.nrows is not None:
        kwargs["nrows"] = args.nrows
    if args.na_values:
        kwargs["na_values"] = [value.strip() for value in args.na_values.split(",") if value.strip()]
    if args.build:
        kwargs["build"] = args.build
    if args.verbose:
        kwargs["verbose"] = True
    return kwargs


def normalize_separator(raw_value: str) -> str:
    """Normalize Galaxy/UI separator values to actual pandas separators."""

    normalized = raw_value.strip()
    separator_map = {
        r"\t": "\t",
        "tab": "\t",
        "TAB": "\t",
        "&#009;": "\t",
        "&#x9;": "\t",
        r"\s+": r"\s+",
        "space": " ",
        "comma": ",",
        "semicolon": ";",
    }
    return separator_map.get(normalized, raw_value)


def build_sumstats_kwargs(args: argparse.Namespace) -> dict[str, object]:
    kwargs = build_load_kwargs(vars(args))
    other_columns = normalize_other_columns(args.other)
    if other_columns:
        kwargs["other"] = other_columns
    return kwargs


def collect_requested_columns(args: argparse.Namespace) -> list[str]:
    return [
        value
        for key, value in vars(args).items()
        if key in {"snpid", "rsid", "chrom", "pos", "ea", "nea", "ref", "alt", "eaf", "neaf", "n", "beta", "se", "chisq", "z", "p", "mlog10p", "info", "direction", "ncontrol", "ncase", "maf", "status"}
        and value
    ]


def read_header_columns(input_path: str, reader_kwargs: dict[str, object]) -> list[str]:
    return list(
        pd.read_table(
            input_path,
            sep=reader_kwargs["sep"],
            skiprows=reader_kwargs["skiprows"],
            nrows=0,
            engine="python",
        ).columns
    )


def maybe_autodetect_tab_separator(
    args: argparse.Namespace,
    reader_kwargs: dict[str, object],
    requested_columns: list[str],
) -> tuple[dict[str, object], list[str]]:
    detected_columns = read_header_columns(args.input, reader_kwargs)
    if len(detected_columns) != 1 or "\t" not in detected_columns[0]:
        return reader_kwargs, detected_columns

    tab_reader_kwargs = dict(reader_kwargs)
    tab_reader_kwargs["sep"] = "\t"
    tab_detected_columns = read_header_columns(args.input, tab_reader_kwargs)
    missing_columns = [column for column in requested_columns if column not in tab_detected_columns]
    if missing_columns:
        return reader_kwargs, detected_columns
    return tab_reader_kwargs, tab_detected_columns


def validate_manual_columns_input(
    args: argparse.Namespace,
    reader_kwargs: dict[str, object],
) -> tuple[dict[str, object], list[str]]:
    """Validate the selected input/header before handing off to GWASLab.

    This gives a friendlier error than the raw pandas/usecols traceback when the
    user accidentally selects a log file or mismatched dataset in Galaxy.
    """

    requested_columns = collect_requested_columns(args)
    if not requested_columns:
        return reader_kwargs, []

    effective_reader_kwargs, detected_columns = maybe_autodetect_tab_separator(
        args,
        reader_kwargs,
        requested_columns,
    )
    missing_columns = [column for column in requested_columns if column not in detected_columns]
    if not missing_columns:
        return effective_reader_kwargs, detected_columns

    hint = ""
    joined_header = " | ".join(detected_columns[:3])
    if "Sumstats Object created." in joined_header or "GWASLab v" in joined_header:
        hint = (
            " The selected input looks like a GWASLab log/history text file, "
            "not a raw summary-statistics table."
        )

    raise ValueError(
        "The selected input file does not contain the requested manual columns. "
        f"Missing columns: {missing_columns}. "
        f"Detected header columns: {detected_columns[:20]}.{hint}"
    )


def create_pattern_from_collection(manifest_path: str) -> str:
    entries = read_chromosome_manifest(manifest_path)
    suffix = detect_collection_suffix(path for _, path in entries)
    temp_root = Path(tempfile.mkdtemp(prefix="gwaslab_chr_", dir=RUNTIME_TMP))
    for identifier, source_path in entries:
        normalized = identifier.replace("chr", "").replace("CHR", "")
        target_path = temp_root / f"sumstats.chr{normalized}{suffix}"
        os.symlink(source_path, target_path)
    return str(temp_root / f"sumstats.chr@{suffix}")


def load_sumstats(args: argparse.Namespace):
    reader_kwargs = build_reader_kwargs(args)
    load_kwargs = build_sumstats_kwargs(args)

    if args.mode == "columns":
        if not args.input:
            raise ValueError("--input is required for column-based loading.")
        effective_reader_kwargs, _ = validate_manual_columns_input(args, reader_kwargs)
        return gl.Sumstats(args.input, **effective_reader_kwargs, **load_kwargs)

    if args.mode == "format":
        if not args.input or not args.format_name:
            raise ValueError("--input and --format-name are required for format-based loading.")
        return gl.Sumstats(args.input, fmt=args.format_name, **reader_kwargs)

    if args.mode == "auto":
        if not args.input:
            raise ValueError("--input is required for auto loading.")
        return gl.Sumstats(args.input, fmt="auto", **reader_kwargs)

    if args.mode == "chromsplit":
        if not args.chrom_manifest:
            raise ValueError("--chrom-manifest is required for chromosome-separated loading.")
        pattern = create_pattern_from_collection(args.chrom_manifest)
        if args.chrom_format_mode == "auto":
            return gl.Sumstats(pattern, fmt="auto", **reader_kwargs)
        if args.chrom_format_mode == "columns":
            return gl.Sumstats(pattern, **reader_kwargs, **load_kwargs)
        if not args.format_name:
            raise ValueError("--format-name is required when chrom-format-mode is 'format'.")
        return gl.Sumstats(pattern, fmt=args.format_name, **reader_kwargs)

    raise ValueError(f"Unsupported mode: {args.mode}")


def summarize_sumstats(args: argparse.Namespace, ss) -> dict[str, object]:
    dataframe = ss.data
    meta = getattr(ss, "meta", {}) or {}
    return {
        "mode": args.mode,
        "format_name": args.format_name,
        "chrom_format_mode": args.chrom_format_mode if args.mode == "chromsplit" else None,
        "rows": int(len(dataframe)),
        "columns": list(dataframe.columns),
        "genome_build": meta.get("genome_build"),
        "gwaslab_meta_keys": sorted(meta.keys()),
        "source_uses_collection": args.mode == "chromsplit",
    }


def save_log(ss, log_path: str) -> None:
    if hasattr(ss, "log") and hasattr(ss.log, "save"):
        ss.log.save(log_path)
        return
    Path(log_path).write_text("GWASLab log object was not available.\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    configure_logging(PROJECT_ROOT / "config" / "logging.yaml")
    logger = get_logger("load_sumstats")

    logger.info("Loading GWAS summary statistics with mode=%s", args.mode)
    ss = load_sumstats(args)
    write_dataframe(ss.data, args.output_tsv)
    write_metadata(summarize_sumstats(args, ss), args.output_meta)
    save_log(ss, args.log)
    logger.info("Finished loading %s rows", len(ss.data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
