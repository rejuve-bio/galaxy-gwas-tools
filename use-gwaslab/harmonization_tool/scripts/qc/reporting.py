from __future__ import annotations

from collections.abc import Iterable
import re

import pandas as pd


REQUIRED_QC_COLUMNS = (
    "SNPID",
    "CHR",
    "POS",
    "EA",
    "NEA",
    "BETA",
    "SE",
    "P",
)
ALLELE_COLUMNS = ("EA", "NEA")
VALID_ALLELE_RE = re.compile(r"^[ACGTN]+$", re.IGNORECASE)


def _present_columns(df: pd.DataFrame, columns: Iterable[str]) -> list[str]:
    return [column for column in columns if column in df.columns]


def count_missing_values(df: pd.DataFrame, columns: Iterable[str]) -> dict[str, int | None]:
    summary: dict[str, int | None] = {}
    for column in columns:
        summary[column] = int(df[column].isna().sum()) if column in df.columns else None
    return summary


def count_invalid_allele_rows(df: pd.DataFrame) -> int:
    present = _present_columns(df, ALLELE_COLUMNS)
    if not present:
        return 0

    invalid_mask = pd.Series(False, index=df.index)
    for column in present:
        normalized = df[column].astype("string").str.upper().str.strip()
        invalid_mask = invalid_mask | (
            normalized.notna()
            & normalized.ne("")
            & ~normalized.str.fullmatch(VALID_ALLELE_RE)
        )
    return int(invalid_mask.sum())


def count_duplicate_variant_rows(df: pd.DataFrame) -> int:
    if "SNPID" in df.columns:
        return int(df.duplicated(subset=["SNPID"]).sum())

    subset = _present_columns(df, ("CHR", "POS", "EA", "NEA"))
    if len(subset) >= 2:
        return int(df.duplicated(subset=subset).sum())
    return 0


def summarize_qc_table(df: pd.DataFrame) -> dict[str, object]:
    missing_values = count_missing_values(df, REQUIRED_QC_COLUMNS)
    available_columns = _present_columns(df, REQUIRED_QC_COLUMNS)
    rows_with_missing_required = (
        int(df[available_columns].isna().any(axis=1).sum()) if available_columns else 0
    )
    return {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "missing_values_by_column": missing_values,
        "rows_with_missing_required_values": rows_with_missing_required,
        "invalid_allele_rows": count_invalid_allele_rows(df),
        "duplicate_variant_rows": count_duplicate_variant_rows(df),
    }
