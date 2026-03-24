from __future__ import annotations

from pathlib import Path
import json
from typing import Iterable


LOAD_ARG_NAMES = {
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
    "beta",
    "se",
    "chisq",
    "z",
    "p",
    "mlog10p",
    "info",
    "n",
    "direction",
    "ncontrol",
    "ncase",
    "maf",
    "status",
    "OR",
    "OR_95L",
    "OR_95U",
    "HR",
    "HR_95L",
    "HR_95U",
    "beta_95L",
    "beta_95U",
    "i2",
    "phet",
    "dof",
    "snpr2",
    "f",
}


def build_load_kwargs(arguments: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in arguments.items()
        if key in LOAD_ARG_NAMES and value not in (None, "")
    }


def detect_is_gzip(path: str | Path) -> bool:
    return str(path).endswith(".gz")


def write_dataframe(df, output_path: str | Path) -> None:
    path = Path(output_path)
    compression = "gzip" if detect_is_gzip(path) else None
    df.to_csv(path, sep="\t", index=False, compression=compression)


def write_metadata(metadata: dict[str, object], output_path: str | Path) -> None:
    path = Path(output_path)
    path.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")


def normalize_other_columns(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def read_chromosome_manifest(path: str | Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        identifier, file_path = raw_line.split("\t", 1)
        entries.append((identifier.strip(), file_path.strip()))
    return entries


def detect_collection_suffix(paths: Iterable[str]) -> str:
    path_list = list(paths)
    if not path_list:
        raise ValueError("Chromosome collection is empty.")
    all_gzip = all(str(path).endswith(".gz") for path in path_list)
    return ".tsv.gz" if all_gzip else ".tsv"
