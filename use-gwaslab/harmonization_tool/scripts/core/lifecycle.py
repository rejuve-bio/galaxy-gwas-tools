from __future__ import annotations

PIPELINE_STEPS = (
    "load_sumstats",
    "standardize",
    "qc_check",
    "filtering",
    "reference_download",
    "liftover",
    "assign_rsid",
    "assign_chrpos",
    "harmonization",
    "status_report",
    "export",
)
