from __future__ import annotations

import argparse
import csv
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.io.logging_utils import configure_logging, get_logger
from scripts.io.sumstats_io import write_metadata
from scripts.utils.gwaslab_runtime import (
    configure_runtime_environment,
    import_gwaslab_with_py310_compat,
)

RUNTIME_TMP = configure_runtime_environment()
gl = import_gwaslab_with_py310_compat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download or package GWASLab reference resources.")
    parser.add_argument("--mode", choices=("preset", "keywords", "local"), required=True)
    parser.add_argument("--preset-name")
    parser.add_argument("--build", choices=("19", "38"))
    parser.add_argument("--population", choices=("eas", "eur", "afr", "amr", "sas", "pan"), default="pan")
    parser.add_argument("--dbsnp-version", choices=("151", "157"), default="157")
    parser.add_argument("--keywords")
    parser.add_argument("--local-primary")
    parser.add_argument("--local-primary-label")
    parser.add_argument("--local-secondary")
    parser.add_argument("--local-secondary-label")
    parser.add_argument("--local-tertiary")
    parser.add_argument("--local-tertiary-label")
    parser.add_argument("--local-quaternary")
    parser.add_argument("--local-quaternary-label")
    parser.add_argument("--output-bundle", required=True)
    parser.add_argument("--output-manifest", required=True)
    parser.add_argument("--output-inventory", required=True)
    parser.add_argument("--log", required=True)
    return parser.parse_args()


def parse_keywords(raw_keywords: str | None) -> list[str]:
    if not raw_keywords:
        return []
    return [keyword.strip() for keyword in raw_keywords.split(",") if keyword.strip()]


def resolve_preset_keywords(args: argparse.Namespace) -> list[str]:
    if not args.preset_name or not args.build:
        raise ValueError("--preset-name and --build are required for preset mode.")

    build = args.build
    population = args.population
    dbsnp_version = args.dbsnp_version

    presets = {
        "harmonization": [f"ucsc_genome_hg{build}", f"1kg_{population}_hg{build}"],
        "assign_rsid_light": [f"1kg_dbsnp151_hg{build}_auto"],
        "assign_rsid_full": [f"1kg_dbsnp151_hg{build}_auto", f"dbsnp_v{dbsnp_version}_hg{build}"],
        "full_light": [
            f"ucsc_genome_hg{build}",
            f"1kg_{population}_hg{build}",
            f"1kg_dbsnp151_hg{build}_auto",
        ],
        "full_full": [
            f"ucsc_genome_hg{build}",
            f"1kg_{population}_hg{build}",
            f"1kg_dbsnp151_hg{build}_auto",
            f"dbsnp_v{dbsnp_version}_hg{build}",
        ],
    }
    if args.preset_name not in presets:
        raise ValueError(f"Unsupported preset: {args.preset_name}")
    return presets[args.preset_name]


def infer_reference_role(keyword: str) -> str:
    if keyword.startswith("ucsc_genome_"):
        return "harmonization_ref_seq"
    if keyword.startswith("1kg_") and keyword.endswith(("_hg19", "_hg38")):
        return "harmonization_ref_infer_vcf"
    if keyword.startswith("1kg_dbsnp151_") and keyword.endswith("_auto"):
        return "assign_rsid_tsv"
    if keyword.startswith("dbsnp_v"):
        return "assign_rsid_vcf"
    return "reference"


def copy_into_staging(staging_root: Path, source_path: Path, label: str) -> Path:
    target_dir = staging_root / label
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / source_path.name
    shutil.copy2(source_path, target_path)
    return target_path


def require_nonempty_file(path_value: str | Path | bool, label: str) -> Path:
    if not path_value or path_value is False:
        raise FileNotFoundError(f"{label} was not produced or could not be resolved by GWASLab.")

    path = Path(path_value)
    if not path.exists():
        raise FileNotFoundError(f"{label} does not exist at expected path: {path}")
    if path.stat().st_size <= 0:
        raise ValueError(f"{label} exists but is empty: {path}")
    return path


def set_gwaslab_download_directory(directory: Path) -> None:
    """Set the active GWASLab download directory across supported versions."""

    if hasattr(gl, "set_default_directory"):
        gl.set_default_directory(str(directory))
        return

    try:
        from gwaslab.bd.bd_download import set_default_directory as set_directory_impl

        set_directory_impl(str(directory))
        return
    except Exception:
        pass

    if hasattr(gl, "options") and hasattr(gl.options, "set_option"):
        gl.options.set_option("data_directory", str(directory))
        return

    raise AttributeError(
        "The installed GWASLab version does not expose a supported way to set the download directory."
    )


def bundle_downloaded_keywords(args: argparse.Namespace, logger) -> list[dict[str, object]]:
    download_dir = Path(tempfile.mkdtemp(prefix="gwaslab_refs_", dir=RUNTIME_TMP))
    logger.info("Using temporary GWASLab download directory %s", download_dir)
    set_gwaslab_download_directory(download_dir)

    available_refs = gl.check_available_ref(show_all=True, verbose=False)
    keywords = (
        resolve_preset_keywords(args)
        if args.mode == "preset"
        else parse_keywords(args.keywords)
    )
    if not keywords:
        raise ValueError("No reference keywords were provided.")

    staging_root = Path(tempfile.mkdtemp(prefix="gwaslab_ref_bundle_", dir=RUNTIME_TMP))
    manifest_entries: list[dict[str, object]] = []

    for keyword in keywords:
        if keyword not in available_refs:
            raise ValueError(f"Unknown GWASLab reference keyword: {keyword}")

        logger.info("Downloading reference keyword %s", keyword)
        gl.download_ref(keyword, directory=str(download_dir))
        local_path = require_nonempty_file(gl.get_path(keyword, verbose=False), f"Reference {keyword}")
        staged_main = copy_into_staging(staging_root, local_path, keyword)

        entry = {
            "name": keyword,
            "source": "download",
            "role": infer_reference_role(keyword),
            "description": available_refs[keyword].get("description", ""),
            "suggested_use": available_refs[keyword].get("suggested_use", ""),
            "bundle_path": str(staged_main.relative_to(staging_root)),
            "original_filename": local_path.name,
            "_staged_path": str(staged_main),
        }

        tbi_path = Path(f"{local_path}.tbi")
        if tbi_path.exists():
            require_nonempty_file(tbi_path, f"Index for {keyword}")
            staged_tbi = copy_into_staging(staging_root, tbi_path, keyword)
            entry["index_bundle_path"] = str(staged_tbi.relative_to(staging_root))
            entry["_index_staged_path"] = str(staged_tbi)

        manifest_entries.append(entry)

    return manifest_entries


def bundle_local_references(args: argparse.Namespace) -> list[dict[str, object]]:
    pairs = [
        (args.local_primary_label, args.local_primary),
        (args.local_secondary_label, args.local_secondary),
        (args.local_tertiary_label, args.local_tertiary),
        (args.local_quaternary_label, args.local_quaternary),
    ]
    provided_pairs = [(label, path) for label, path in pairs if label and path]
    if not provided_pairs:
        raise ValueError("At least one local reference file must be provided in local mode.")

    staging_root = Path(tempfile.mkdtemp(prefix="gwaslab_ref_bundle_", dir=RUNTIME_TMP))
    manifest_entries: list[dict[str, object]] = []
    for label, raw_path in provided_pairs:
        source_path = require_nonempty_file(raw_path, f"Local reference {label}")
        staged_path = copy_into_staging(staging_root, source_path, label)
        manifest_entries.append(
            {
                "name": label,
                "source": "local",
                "role": "custom_reference",
                "description": "User-provided reference file packaged for Galaxy",
                "suggested_use": "Custom reference input",
                "bundle_path": str(staged_path.relative_to(staging_root)),
                "original_filename": source_path.name,
                "_staged_path": str(staged_path),
            }
        )
    return manifest_entries


def write_inventory(entries: list[dict[str, object]], output_path: str) -> None:
    with Path(output_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "name",
                "source",
                "role",
                "description",
                "suggested_use",
                "bundle_path",
                "index_bundle_path",
                "original_filename",
            ],
            delimiter="\t",
        )
        writer.writeheader()
        for entry in entries:
            writer.writerow({key: value for key, value in entry.items() if not key.startswith("_")})


def write_bundle(entries: list[dict[str, object]], output_path: str) -> None:
    with tarfile.open(output_path, "w:gz") as archive:
        for entry in entries:
            bundle_path = Path(entry["bundle_path"])
            source_path = Path(entry["_staged_path"])
            archive.add(source_path, arcname=str(Path("references") / bundle_path))

            index_bundle_path = entry.get("index_bundle_path")
            index_staged_path = entry.get("_index_staged_path")
            if index_bundle_path and index_staged_path:
                index_rel = Path(index_bundle_path)
                index_source = Path(index_staged_path)
                archive.add(index_source, arcname=str(Path("references") / index_rel))


def save_log_text(log_path: str, message: str) -> None:
    Path(log_path).write_text(message, encoding="utf-8")


def validate_final_outputs(output_paths: list[tuple[str, str]]) -> None:
    for label, output_path in output_paths:
        require_nonempty_file(output_path, label)


def main() -> int:
    args = parse_args()
    configure_logging(PROJECT_ROOT / "config" / "logging.yaml")
    logger = get_logger("reference_download")

    if args.mode == "preset":
        entries = bundle_downloaded_keywords(args, logger)
    elif args.mode == "keywords":
        entries = bundle_downloaded_keywords(args, logger)
    else:
        entries = bundle_local_references(args)

    manifest = {
        "mode": args.mode,
        "preset_name": args.preset_name,
        "build": args.build,
        "population": args.population,
        "dbsnp_version": args.dbsnp_version,
        "keywords": [entry["name"] for entry in entries],
        "resources": [
            {key: value for key, value in entry.items() if not key.startswith("_")}
            for entry in entries
        ],
        "bundle_format": "tar.gz",
    }
    write_metadata(manifest, args.output_manifest)
    write_inventory(entries, args.output_inventory)
    write_bundle(entries, args.output_bundle)
    save_log_text(
        args.log,
        "Reference bundle prepared successfully.\n"
        f"Mode: {args.mode}\n"
        f"Resources: {', '.join(entry['name'] for entry in entries)}\n",
    )
    validate_final_outputs(
        [
            ("reference bundle", args.output_bundle),
            ("manifest", args.output_manifest),
            ("inventory", args.output_inventory),
            ("log", args.log),
        ]
    )
    logger.info("Prepared reference bundle with %s resource(s)", len(entries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
