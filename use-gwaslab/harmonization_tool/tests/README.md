# Tool Smoke Tests

These scripts let you test the Python tool runners directly before wiring them through the Galaxy UI.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```

Use Python 3.12 for the cleanest match with the Galaxy tool requirements and the pinned GWASLab toolchain.

## Run

```bash
python tests/run_load_sumstats_smoke.py
python tests/run_standardize_smoke.py
```

The scripts write outputs under your system temp directory, inside `gwaslab_harmonization_tool_tests/`.
