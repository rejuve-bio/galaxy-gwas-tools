from __future__ import annotations

import os
from pathlib import Path
import tempfile
import typing

import pandas as pd


def configure_runtime_environment() -> Path:
    """Set writable cache directories for local runs and Galaxy jobs."""

    runtime_tmp = Path(tempfile.gettempdir()) / "gwaslab_harmonization_tool"
    runtime_tmp.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(runtime_tmp / "mplconfig"))
    os.environ.setdefault("XDG_CACHE_HOME", str(runtime_tmp / "xdg-cache"))
    return runtime_tmp


def import_gwaslab_with_py310_compat():
    """Import gwaslab while tolerating the pd.NA typing bug on Python 3.10.

    GWASLab currently evaluates an annotation like `Union[str, pd.NA]` at import
    time. Python 3.10 rejects `pd.NA` there because it is an instance, not a
    type. We patch `typing._type_check` narrowly during import so the annotation
    is interpreted as `type(pd.NA)` instead. The runtime behavior of `pd.NA`
    remains unchanged elsewhere.
    """

    original_type_check = typing._type_check

    def patched_type_check(
        arg,
        msg,
        is_argument=True,
        module=None,
        *,
        allow_special_forms=False,
    ):
        if arg is pd.NA:
            return type(pd.NA)
        return original_type_check(
            arg,
            msg,
            is_argument=is_argument,
            module=module,
            allow_special_forms=allow_special_forms,
        )

    typing._type_check = patched_type_check
    try:
        import gwaslab as gl
    finally:
        typing._type_check = original_type_check
    return gl
