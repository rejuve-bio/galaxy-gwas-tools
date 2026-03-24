from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_TMP = PROJECT_ROOT / "tmp"
RUNTIME_TMP.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(RUNTIME_TMP / "mplconfig"))
os.environ.setdefault("XDG_CACHE_HOME", str(RUNTIME_TMP / "xdg-cache"))

import gwaslab as gl

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.io.logging_utils import configure_logging, get_logger
from scripts.io.sumstats_io import write_dataframe, write_metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Standardize GWAS summary statistics with GWASLab.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--input-format", default="gwaslab")
    parser.add_argument("--build", choices=("19", "38", "99"))
    parser.add_argument("--remove-bad", action="store_true")
    parser.add_argument("--remove-dup", action="store_true")
    parser.add_argument("--normalize", action="store_true")
    parser.add_argument("--fixchrpos", action="store_true")
    parser.add_argument("--fixid", action="store_true")
    parser.add_argument("--fixsep", action="store_true")
    parser.add_argument("--forcefixid", action="store_true")
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--output-tsv", required=True)
    parser.add_argument("--output-meta", required=True)
    parser.add_argument("--log", required=True)
    return parser.parse_args()


def save_log(ss, log_path: str) -> None:
    if hasattr(ss, "log") and hasattr(ss.log, "save"):
        ss.log.save(log_path)
        return
    Path(log_path).write_text("GWASLab log object was not available.\n", encoding="utf-8")


def summarize(args: argparse.Namespace, ss, input_rows: int) -> dict[str, object]:
    output_rows = int(len(ss.data))
    return {
        "mode": "standardize",
        "input_rows": input_rows,
        "output_rows": output_rows,
        "removed_rows": input_rows - output_rows,
        "remove_bad": args.remove_bad,
        "remove_dup": args.remove_dup,
        "normalize": args.normalize,
        "status_column_present": "STATUS" in ss.data.columns,
        "columns": list(ss.data.columns),
    }


def main() -> int:
    args = parse_args()
    configure_logging(PROJECT_ROOT / "config" / "logging.yaml")
    logger = get_logger("standardize")

    reader_kwargs: dict[str, object] = {"fmt": args.input_format}
    if args.build:
        reader_kwargs["build"] = args.build

    logger.info("Loading input for standardization from %s", args.input)
    ss = gl.Sumstats(args.input, **reader_kwargs)
    input_rows = int(len(ss.data))

    if any((args.fixchrpos, args.fixid, args.fixsep, args.forcefixid)):
        logger.info("Running fix_id pre-step before basic_check")
        ss.fix_id(
            fixchrpos=args.fixchrpos,
            fixid=args.fixid,
            fixsep=args.fixsep,
            forcefixid=args.forcefixid,
        )

    logger.info(
        "Running basic_check(remove=%s, remove_dup=%s, normalize=%s, threads=%s)",
        args.remove_bad,
        args.remove_dup,
        args.normalize,
        args.threads,
    )
    ss.basic_check(
        remove=args.remove_bad,
        remove_dup=args.remove_dup,
        normalize=args.normalize,
        threads=args.threads,
    )

    write_dataframe(ss.data, args.output_tsv)
    write_metadata(summarize(args, ss, input_rows), args.output_meta)
    save_log(ss, args.log)
    logger.info("Standardization complete: %s -> %s rows", input_rows, len(ss.data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
