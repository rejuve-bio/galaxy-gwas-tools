from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.io.logging_utils import configure_logging, get_logger
from scripts.io.sumstats_io import write_dataframe, write_metadata
from scripts.qc.reporting import summarize_qc_table
from scripts.utils.gwaslab_runtime import (
    configure_runtime_environment,
    import_gwaslab_with_py310_compat,
)

RUNTIME_TMP = configure_runtime_environment()
gl = import_gwaslab_with_py310_compat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run GWASLab QC checks and emit a compact QC report.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--input-format", default="gwaslab")
    parser.add_argument("--build", choices=("19", "38", "99"))
    parser.add_argument("--remove-dup", action="store_true")
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--output-tsv", required=True)
    parser.add_argument("--output-report", required=True)
    parser.add_argument("--log", required=True)
    return parser.parse_args()


def save_log(ss, log_path: str) -> None:
    if hasattr(ss, "log") and hasattr(ss.log, "save"):
        ss.log.save(log_path)
        return
    Path(log_path).write_text("GWASLab log object was not available.\n", encoding="utf-8")


def summarize_report(args: argparse.Namespace, input_report: dict[str, object], ss) -> dict[str, object]:
    output_report = summarize_qc_table(ss.data)
    return {
        "mode": "qc_check",
        "input_format": args.input_format,
        "remove_dup": args.remove_dup,
        "threads": args.threads,
        "input_qc": input_report,
        "output_qc": output_report,
        "duplicate_rows_removed": input_report["duplicate_variant_rows"] - output_report["duplicate_variant_rows"],
        "status_column_present": "STATUS" in ss.data.columns,
        "qc_methods_run": ["check_sanity", "check_data_consistency"] + (["remove_dup"] if args.remove_dup else []),
    }


def main() -> int:
    args = parse_args()
    configure_logging(PROJECT_ROOT / "config" / "logging.yaml")
    logger = get_logger("qc_check")

    reader_kwargs: dict[str, object] = {"fmt": args.input_format}
    if args.build:
        reader_kwargs["build"] = args.build

    logger.info("Loading input for QC check from %s", args.input)
    ss = gl.Sumstats(args.input, **reader_kwargs)
    input_report = summarize_qc_table(ss.data)

    logger.info("Running GWASLab check_sanity()")
    ss.check_sanity()
    logger.info("Running GWASLab check_data_consistency()")
    ss.check_data_consistency()

    if args.remove_dup:
        logger.info("Removing duplicate variants after QC checks")
        ss.remove_dup()

    write_dataframe(ss.data, args.output_tsv)
    write_metadata(summarize_report(args, input_report, ss), args.output_report)
    save_log(ss, args.log)
    logger.info("QC check complete: %s input rows -> %s output rows", input_report["rows"], len(ss.data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
