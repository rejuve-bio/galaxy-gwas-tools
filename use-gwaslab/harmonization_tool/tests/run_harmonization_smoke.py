#!/usr/bin/env python3
"""Smoke-test the harmonization runner before using the Galaxy UI.

What this does:
- runs the Python entry point directly in both direct-reference mode and bundle mode
- uses the shared gwaslab-sample-data directory
- writes outputs under your system temp directory
- checks the metadata JSON so reference-resolution regressions fail fast

How to run:
    python tests/run_harmonization_smoke.py
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HARM_RUNNER = PROJECT_ROOT / 'tools' / 'harmonization' / 'run_harmonization.py'
REF_RUNNER = PROJECT_ROOT / 'tools' / 'reference_download' / 'run_reference_download.py'
SAMPLE_ROOT = PROJECT_ROOT.parent / 'gwaslab-sample-data'
OUTPUT_ROOT = Path(tempfile.gettempdir()) / 'gwaslab_harmonization_tool_tests' / 'harmonization'


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


def run_direct_mode(case_dir: Path) -> None:
    command = [
        sys.executable,
        str(HARM_RUNNER),
        '--input',
        str(SAMPLE_ROOT / 'harmonization_case.tsv'),
        '--build',
        '19',
        '--reference-mode',
        'direct',
        '--ref-seq',
        str(SAMPLE_ROOT / 'chr7.fasta.gz'),
        '--ref-infer',
        str(SAMPLE_ROOT / '1kg_eas_hg19.chr7_126253550_128253550.vcf.gz'),
        '--ref-alt-freq',
        'AF',
        '--ref-maf-threshold',
        '0.4',
        '--maf-threshold',
        '0.4',
        '--threads',
        '1',
        '--output-tsv',
        str(case_dir / 'direct_output.tsv'),
        '--output-meta',
        str(case_dir / 'direct_meta.json'),
        '--log',
        str(case_dir / 'direct.log'),
    ]
    subprocess.run(command, check=True, cwd=PROJECT_ROOT)

    metadata = json.loads((case_dir / 'direct_meta.json').read_text(encoding='utf-8'))
    if metadata['mode'] != 'harmonization':
        raise AssertionError('Expected harmonization mode metadata')
    if metadata['reference_mode'] != 'direct':
        raise AssertionError('Expected direct reference mode metadata')


def run_bundle_mode(case_dir: Path) -> None:
    bundle_dir = case_dir / 'bundle_inputs'
    bundle_dir.mkdir(parents=True, exist_ok=True)

    ref_command = [
        sys.executable,
        str(REF_RUNNER),
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
        str(bundle_dir / 'bundle.tar.gz'),
        '--output-manifest',
        str(bundle_dir / 'manifest.json'),
        '--output-inventory',
        str(bundle_dir / 'inventory.tsv'),
        '--log',
        str(bundle_dir / 'bundle.log'),
    ]
    subprocess.run(ref_command, check=True, cwd=PROJECT_ROOT)

    harm_command = [
        sys.executable,
        str(HARM_RUNNER),
        '--input',
        str(SAMPLE_ROOT / 'harmonization_case.tsv'),
        '--build',
        '19',
        '--reference-mode',
        'bundle',
        '--reference-bundle',
        str(bundle_dir / 'bundle.tar.gz'),
        '--reference-manifest',
        str(bundle_dir / 'manifest.json'),
        '--ref-alt-freq',
        'AF',
        '--ref-maf-threshold',
        '0.4',
        '--maf-threshold',
        '0.4',
        '--threads',
        '1',
        '--output-tsv',
        str(case_dir / 'bundle_output.tsv'),
        '--output-meta',
        str(case_dir / 'bundle_meta.json'),
        '--log',
        str(case_dir / 'bundle.log'),
    ]
    subprocess.run(harm_command, check=True, cwd=PROJECT_ROOT)

    metadata = json.loads((case_dir / 'bundle_meta.json').read_text(encoding='utf-8'))
    if metadata['reference_mode'] != 'bundle':
        raise AssertionError('Expected bundle reference mode metadata')
    if not metadata['references_used']['ref_seq']:
        raise AssertionError('Expected bundle mode to resolve a reference FASTA')


def main() -> None:
    case_dir = OUTPUT_ROOT / 'direct_and_bundle'
    case_dir.mkdir(parents=True, exist_ok=True)
    run_direct_mode(case_dir)
    run_bundle_mode(case_dir)
    print(f'harmonization outputs written under: {OUTPUT_ROOT}')
    print('harmonization smoke tests passed')


if __name__ == '__main__':
    ensure_runtime_dependencies()
    main()
