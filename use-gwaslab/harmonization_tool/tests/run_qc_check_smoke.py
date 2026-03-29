#!/usr/bin/env python3
"""Smoke-test the qc_check runner before using the Galaxy UI.

What this does:
- runs the Python entry point directly against a small shared fixture
- uses the shared gwaslab-sample-data directory instead of repo-local test data
- writes outputs under your system temp directory
- checks the JSON QC report so duplicate counting/regression issues fail fast

How to run:
    python tests/run_qc_check_smoke.py
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER = PROJECT_ROOT / 'tools' / 'qc_check' / 'run_qc_check.py'
SAMPLE = PROJECT_ROOT.parent / 'gwaslab-sample-data' / 'standardize_case.tsv'
OUTPUT_ROOT = Path(tempfile.gettempdir()) / 'gwaslab_harmonization_tool_tests' / 'qc_check'


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
    case_dir = OUTPUT_ROOT / 'duplicate_fixture'
    case_dir.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        str(RUNNER),
        '--input',
        str(SAMPLE),
        '--input-format',
        'gwaslab',
        '--remove-dup',
        '--threads',
        '1',
        '--output-tsv',
        str(case_dir / 'output.tsv'),
        '--output-report',
        str(case_dir / 'report.json'),
        '--log',
        str(case_dir / 'run.log'),
    ]
    subprocess.run(command, check=True, cwd=PROJECT_ROOT)

    report = json.loads((case_dir / 'report.json').read_text(encoding='utf-8'))
    if report['mode'] != 'qc_check':
        raise AssertionError(f'Expected mode qc_check, got {report["mode"]}')
    if report['input_qc']['duplicate_variant_rows'] != 1:
        raise AssertionError('Expected one duplicate row in the shared QC fixture')
    if report['output_qc']['rows'] != 1:
        raise AssertionError('Expected duplicate removal to leave one output row')
    if report['duplicate_rows_removed'] != 1:
        raise AssertionError('Expected one duplicate row to be removed')

    print(f'qc_check outputs written under: {OUTPUT_ROOT}')
    print('qc_check smoke test passed')


if __name__ == '__main__':
    ensure_runtime_dependencies()
    main()
