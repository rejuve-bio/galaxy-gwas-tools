from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.io.logging_utils import configure_logging, get_logger
from scripts.io.sumstats_io import write_dataframe, write_metadata
from scripts.utils.gwaslab_runtime import (
    configure_runtime_environment,
    import_gwaslab_with_py310_compat,
)

RUNTIME_TMP = configure_runtime_environment()
gl = import_gwaslab_with_py310_compat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lift GWAS summary statistics between genome builds.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--input-format", default="gwaslab")
    parser.add_argument("--from-build", required=True, choices=("19", "38"))
    parser.add_argument("--to-build", required=True, choices=("19", "38"))
    parser.add_argument("--chain-source", choices=("builtin", "custom"), default="builtin")
    parser.add_argument("--chain-file")
    parser.add_argument("--filter-by-status", action="store_true")
    parser.add_argument("--one-based-input", action="store_true", default=True)
    parser.add_argument("--zero-based-input", action="store_true")
    parser.add_argument("--zero-based-output", action="store_true")
    parser.add_argument("--output-mapped", required=True)
    parser.add_argument("--output-unmapped", required=True)
    parser.add_argument("--output-meta", required=True)
    parser.add_argument("--log", required=True)
    return parser.parse_args()


def save_log(ss, log_path: str) -> None:
    if hasattr(ss, "log") and hasattr(ss.log, "save"):
        ss.log.save(log_path)
        return
    Path(log_path).write_text("GWASLab log object was not available.\n", encoding="utf-8")


def summarize(args: argparse.Namespace, input_rows: int, mapped_df: pd.DataFrame, unmapped_df: pd.DataFrame) -> dict[str, object]:
    return {
        "mode": "liftover",
        "input_format": args.input_format,
        "from_build": args.from_build,
        "to_build": args.to_build,
        "chain_source": args.chain_source,
        "chain_file": args.chain_file if args.chain_source == "custom" else None,
        "filter_by_status": args.filter_by_status,
        "input_rows": input_rows,
        "mapped_rows": int(len(mapped_df)),
        "unmapped_rows": int(len(unmapped_df)),
        "mapped_columns": list(mapped_df.columns),
        "unmapped_columns": list(unmapped_df.columns),
    }


def main() -> int:
    args = parse_args()
    if args.from_build == args.to_build:
        raise ValueError("from-build and to-build must be different for liftover.")
    if args.chain_source == "custom" and not args.chain_file:
        raise ValueError("--chain-file is required when --chain-source custom is used.")

    configure_logging(PROJECT_ROOT / "config" / "logging.yaml")
    logger = get_logger("liftover")

    reader_kwargs: dict[str, object] = {"fmt": args.input_format, "build": args.from_build}
    logger.info("Loading input for liftover from %s", args.input)
    ss = gl.Sumstats(args.input, **reader_kwargs)
    input_rows = int(len(ss.data))

    liftover_kwargs: dict[str, object] = {
        "from_build": args.from_build,
        "to_build": args.to_build,
        "remove": False,
        "filter_by_status": args.filter_by_status,
        "one_based_input": not args.zero_based_input,
        "one_based_output": not args.zero_based_output,
    }
    if args.chain_source == "custom":
        liftover_kwargs["chain_path"] = args.chain_file

    logger.info(
        "Running liftover from build %s to %s using %s chain source",
        args.from_build,
        args.to_build,
        args.chain_source,
    )
    ss.liftover(**liftover_kwargs)

    unmapped_mask = ss.data["CHR"].isna() | ss.data["POS"].isna()
    mapped_df = ss.data.loc[~unmapped_mask, :].copy()
    unmapped_df = ss.data.loc[unmapped_mask, :].copy()

    write_dataframe(mapped_df, args.output_mapped)
    write_dataframe(unmapped_df, args.output_unmapped)
    write_metadata(summarize(args, input_rows, mapped_df, unmapped_df), args.output_meta)
    save_log(ss, args.log)
    logger.info("Liftover complete: %s mapped, %s unmapped", len(mapped_df), len(unmapped_df))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
