from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.io.logging_utils import configure_logging, get_logger
from scripts.io.reference_bundle import resolve_reference_paths
from scripts.io.sumstats_io import write_dataframe, write_metadata
from scripts.utils.gwaslab_runtime import (
    configure_runtime_environment,
    import_gwaslab_with_py310_compat,
)

RUNTIME_TMP = configure_runtime_environment()
gl = import_gwaslab_with_py310_compat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Harmonize GWAS summary statistics using GWASLab references.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--input-format", default="gwaslab")
    parser.add_argument("--build", choices=("19", "38", "99"))
    parser.add_argument("--reference-mode", choices=("direct", "bundle"), required=True)
    parser.add_argument("--ref-seq")
    parser.add_argument("--ref-infer")
    parser.add_argument("--ref-rsid-tsv")
    parser.add_argument("--ref-rsid-vcf")
    parser.add_argument("--reference-bundle")
    parser.add_argument("--reference-manifest")
    parser.add_argument("--ref-alt-freq", default="AF")
    parser.add_argument("--ref-maf-threshold", type=float, default=0.4)
    parser.add_argument("--maf-threshold", type=float, default=0.4)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--remove", action="store_true")
    parser.add_argument("--output-tsv", required=True)
    parser.add_argument("--output-meta", required=True)
    parser.add_argument("--log", required=True)
    return parser.parse_args()


def save_log(ss, log_path: str) -> None:
    if hasattr(ss, "log") and hasattr(ss.log, "save"):
        ss.log.save(log_path)
        return
    Path(log_path).write_text("GWASLab log object was not available.\n", encoding="utf-8")


def resolve_references(args: argparse.Namespace) -> dict[str, str | None]:
    if args.reference_mode == "direct":
        return {
            "ref_seq": args.ref_seq,
            "ref_infer": args.ref_infer,
            "ref_rsid_tsv": args.ref_rsid_tsv,
            "ref_rsid_vcf": args.ref_rsid_vcf,
        }

    if not args.reference_bundle or not args.reference_manifest:
        raise ValueError("Bundle mode requires both --reference-bundle and --reference-manifest.")

    extract_root = Path(tempfile.mkdtemp(prefix="gwaslab_harm_refs_", dir=RUNTIME_TMP))
    resolved = resolve_reference_paths(args.reference_bundle, args.reference_manifest, extract_root)
    return {
        "ref_seq": resolved.get("harmonization_ref_seq"),
        "ref_infer": resolved.get("harmonization_ref_infer_vcf"),
        "ref_rsid_tsv": resolved.get("assign_rsid_tsv"),
        "ref_rsid_vcf": resolved.get("assign_rsid_vcf"),
    }


def summarize(args: argparse.Namespace, input_rows: int, ss, references: dict[str, str | None]) -> dict[str, object]:
    return {
        "mode": "harmonization",
        "reference_mode": args.reference_mode,
        "input_rows": input_rows,
        "output_rows": int(len(ss.data)),
        "removed_rows": input_rows - int(len(ss.data)),
        "columns": list(ss.data.columns),
        "status_column_present": "STATUS" in ss.data.columns,
        "references_used": {key: bool(value) for key, value in references.items()},
        "ref_alt_freq": args.ref_alt_freq,
        "ref_maf_threshold": args.ref_maf_threshold,
        "maf_threshold": args.maf_threshold,
    }


def main() -> int:
    args = parse_args()
    configure_logging(PROJECT_ROOT / "config" / "logging.yaml")
    logger = get_logger("harmonization")

    reader_kwargs: dict[str, object] = {"fmt": args.input_format}
    if args.build:
        reader_kwargs["build"] = args.build

    logger.info("Loading input for harmonization from %s", args.input)
    ss = gl.Sumstats(args.input, **reader_kwargs)
    input_rows = int(len(ss.data))

    references = resolve_references(args)
    if not any(references.values()):
        raise ValueError(
            "No usable harmonization references were provided. Supply direct references or a bundle/manifest with supported roles."
        )

    logger.info(
        "Running GWASLab harmonize with refs: ref_seq=%s ref_infer=%s ref_rsid_tsv=%s ref_rsid_vcf=%s",
        bool(references["ref_seq"]),
        bool(references["ref_infer"]),
        bool(references["ref_rsid_tsv"]),
        bool(references["ref_rsid_vcf"]),
    )
    ss.harmonize(
        ref_seq=references["ref_seq"],
        ref_infer=references["ref_infer"],
        ref_rsid_tsv=references["ref_rsid_tsv"],
        ref_rsid_vcf=references["ref_rsid_vcf"],
        ref_alt_freq=args.ref_alt_freq,
        ref_maf_threshold=args.ref_maf_threshold,
        maf_threshold=args.maf_threshold,
        threads=args.threads,
        remove=args.remove,
    )

    write_dataframe(ss.data, args.output_tsv)
    write_metadata(summarize(args, input_rows, ss, references), args.output_meta)
    save_log(ss, args.log)
    logger.info("Harmonization complete: %s -> %s rows", input_rows, len(ss.data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
