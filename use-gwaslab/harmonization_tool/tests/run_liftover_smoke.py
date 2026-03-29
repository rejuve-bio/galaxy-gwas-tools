#!/usr/bin/env python3
"""Smoke-test the liftover runner before using the Galaxy UI.

What this does:
- runs the Python entry point directly against a tiny hg19 fixture
- uses the built-in GWASLab chain files for hg19 -> hg38
- writes outputs under your system temp directory
- checks the metadata JSON so build conversion regressions are visible quickly

How to run:
    python tests/run_liftover_smoke.py
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER = PROJECT_ROOT / 'tools' / 'liftover' / 'run_liftover.py'
SAMPLE = PROJECT_ROOT.parent / 'gwaslab-sample-data' / 'liftover_case.tsv'
OUTPUT_ROOT = Path(tempfile.gettempdir()) / 'gwaslab_harmonization_tool_tests' / 'liftover'


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


def main() -> None:
    case_dir = OUTPUT_ROOT / 'builtin_hg19_to_hg38'
    case_dir.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        str(RUNNER),
        '--input',
        str(SAMPLE),
        '--input-format',
        'gwaslab',
        '--from-build',
        '19',
        '--to-build',
        '38',
        '--chain-source',
        'builtin',
        '--output-mapped',
        str(case_dir / 'mapped.tsv'),
        '--output-unmapped',
        str(case_dir / 'unmapped.tsv'),
        '--output-meta',
        str(case_dir / 'meta.json'),
        '--log',
        str(case_dir / 'run.log'),
    ]
    subprocess.run(command, check=True, cwd=PROJECT_ROOT)

    metadata = json.loads((case_dir / 'meta.json').read_text(encoding='utf-8'))
    if metadata['mode'] != 'liftover':
        raise AssertionError(f'Expected mode liftover, got {metadata["mode"]}')
    if metadata['from_build'] != '19' or metadata['to_build'] != '38':
        raise AssertionError('Expected hg19 -> hg38 metadata in liftover output')
    if metadata['mapped_rows'] <= 0:
        raise AssertionError('Expected at least one mapped row from the built-in chain file')

    print(f'liftover outputs written under: {OUTPUT_ROOT}')
    print('liftover smoke test passed')


if __name__ == '__main__':
    ensure_runtime_dependencies()
    main()
