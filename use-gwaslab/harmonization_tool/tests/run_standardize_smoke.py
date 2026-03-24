#!/usr/bin/env python3
"""Smoke-test the standardize runner before using the Galaxy UI.

What this does:
- runs the Python standardize entry point directly
- uses the shared gwaslab-sample-data directory as the input source
- writes outputs under your system temp directory
- asserts that duplicate rows are removed and metadata matches the expectation

How to run:
    python tests/run_standardize_smoke.py
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER = PROJECT_ROOT / 'tools' / 'standardize' / 'run_standardize.py'
SAMPLE = PROJECT_ROOT.parent / 'gwaslab-sample-data' / 'standardize_case.tsv'
OUTPUT_ROOT = Path(tempfile.gettempdir()) / 'gwaslab_harmonization_tool_tests' / 'standardize'


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


if __name__ == '__main__':
    ensure_runtime_dependencies()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(RUNNER),
        '--input',
        str(SAMPLE),
        '--input-format',
        'gwaslab',
        '--remove-dup',
        '--output-tsv',
        str(OUTPUT_ROOT / 'output.tsv'),
        '--output-meta',
        str(OUTPUT_ROOT / 'meta.json'),
        '--log',
        str(OUTPUT_ROOT / 'run.log'),
    ]
    subprocess.run(command, check=True, cwd=PROJECT_ROOT)

    metadata = json.loads((OUTPUT_ROOT / 'meta.json').read_text(encoding='utf-8'))
    if metadata['mode'] != 'standardize':
        raise AssertionError('Expected standardize mode in metadata')
    if metadata['input_rows'] != 2:
        raise AssertionError(f'Expected 2 input rows, got {metadata["input_rows"]}')
    if metadata['output_rows'] != 1:
        raise AssertionError(f'Expected 1 output row, got {metadata["output_rows"]}')

    print('standardize smoke test passed')
