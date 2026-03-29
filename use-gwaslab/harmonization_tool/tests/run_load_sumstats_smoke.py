#!/usr/bin/env python3
"""Smoke-test the load_sumstats runner before using the Galaxy UI.

What this does:
- runs the Python entry point directly in format mode and manual-column mode
- uses the shared gwaslab-sample-data directory as the input source
- writes outputs under your system temp directory
- checks the metadata JSON so failures are easier to spot quickly

How to run:
    python tests/run_load_sumstats_smoke.py
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER = PROJECT_ROOT / 'tools' / 'load_sumstats' / 'run_load_sumstats.py'
SAMPLE = PROJECT_ROOT.parent / 'gwaslab-sample-data' / 'bbj_t2d_hm3_chr7_variants.txt.gz'
OUTPUT_ROOT = Path(tempfile.gettempdir()) / 'gwaslab_harmonization_tool_tests' / 'load_sumstats'


def ensure_runtime_dependencies() -> None:
    """Fail early with a clear message when the test environment is not ready."""

    if importlib.util.find_spec('gwaslab') is None:
        raise SystemExit(
            'gwaslab is not installed for this Python interpreter.\n'
            'Create a project environment and install requirements first:\n'
            '  python -m venv .venv\n'
            '  source .venv/bin/activate\n'
            '  pip install -r requirements-dev.txt'
        )


def run_case(name: str, extra_args: list[str], expected_mode: str) -> None:
    case_dir = OUTPUT_ROOT / name
    case_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(RUNNER),
        '--input',
        str(SAMPLE),
        '--output-tsv',
        str(case_dir / 'output.tsv'),
        '--output-meta',
        str(case_dir / 'meta.json'),
        '--log',
        str(case_dir / 'run.log'),
        *extra_args,
    ]
    subprocess.run(command, check=True, cwd=PROJECT_ROOT)

    metadata = json.loads((case_dir / 'meta.json').read_text(encoding='utf-8'))
    if metadata['mode'] != expected_mode:
        raise AssertionError(f'Expected mode {expected_mode}, got {metadata["mode"]}')
    if metadata['rows'] <= 0:
        raise AssertionError('Expected at least one loaded row')


if __name__ == '__main__':
    ensure_runtime_dependencies()
    run_case(
        name='format_mode',
        expected_mode='format',
        extra_args=['--mode', 'format', '--format-name', 'gwaslab'],
    )
    run_case(
        name='manual_columns_mode',
        expected_mode='columns',
        extra_args=[
            '--mode', 'columns',
            '--snpid', 'SNPID',
            '--chrom', 'CHR',
            '--pos', 'POS',
            '--ea', 'EA',
            '--nea', 'NEA',
            '--eaf', 'EAF',
            '--beta', 'BETA',
            '--se', 'SE',
            '--p', 'P',
            '--n', 'N',
        ],
    )
    print(f'load_sumstats outputs written under: {OUTPUT_ROOT}')
    print('load_sumstats smoke tests passed')
