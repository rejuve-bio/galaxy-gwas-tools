#!/usr/bin/env python3
"""Smoke-test the reference_download runner before using the Galaxy UI.

What this does:
- runs the Python entry point directly in local packaging mode
- uses the shared gwaslab-sample-data directory so the test stays offline
- writes outputs under your system temp directory
- checks the manifest and bundle contents so packaging regressions fail fast

How to run:
    python tests/run_reference_download_smoke.py
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER = PROJECT_ROOT / 'tools' / 'reference_download' / 'run_reference_download.py'
SAMPLE_ROOT = PROJECT_ROOT.parent / 'gwaslab-sample-data'
OUTPUT_ROOT = Path(tempfile.gettempdir()) / 'gwaslab_harmonization_tool_tests' / 'reference_download'


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
    case_dir = OUTPUT_ROOT / 'local_bundle'
    case_dir.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        str(RUNNER),
        '--mode',
        'local',
        '--local-primary',
        str(SAMPLE_ROOT / 'chr7.fasta.gz'),
        '--local-primary-label',
        'ref_seq',
        '--local-secondary',
        str(SAMPLE_ROOT / '1kg_eas_hg19.chr7_126253550_128253550.vcf.gz'),
        '--local-secondary-label',
        'ref_infer_vcf',
        '--local-tertiary',
        str(SAMPLE_ROOT / '1kg_eas_hg19.chr7_126253550_128253550.vcf.gz.tbi'),
        '--local-tertiary-label',
        'ref_infer_vcf_tbi',
        '--output-bundle',
        str(case_dir / 'bundle.tar.gz'),
        '--output-manifest',
        str(case_dir / 'manifest.json'),
        '--output-inventory',
        str(case_dir / 'inventory.tsv'),
        '--log',
        str(case_dir / 'run.log'),
    ]
    subprocess.run(command, check=True, cwd=PROJECT_ROOT)

    manifest = json.loads((case_dir / 'manifest.json').read_text(encoding='utf-8'))
    if manifest['mode'] != 'local':
        raise AssertionError(f'Expected mode local, got {manifest["mode"]}')
    if len(manifest['resources']) != 3:
        raise AssertionError('Expected three packaged local reference resources')

    with tarfile.open(case_dir / 'bundle.tar.gz', 'r:gz') as archive:
        names = archive.getnames()
    if 'references/ref_seq/chr7.fasta.gz' not in names:
        raise AssertionError('Expected FASTA file in packaged bundle')
    if 'references/ref_infer_vcf/1kg_eas_hg19.chr7_126253550_128253550.vcf.gz' not in names:
        raise AssertionError('Expected VCF file in packaged bundle')

    print(f'reference_download outputs written under: {OUTPUT_ROOT}')
    print('reference_download smoke test passed')


if __name__ == '__main__':
    ensure_runtime_dependencies()
    main()
