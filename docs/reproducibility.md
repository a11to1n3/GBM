# Reproducibility

## Core claim
All numbers, tables, and figures in the COMPAG revision (COMPAG-D-26-02203) can be regenerated from:

- This GMB repository (code + minimal data + experiment scripts)
- The full 242-scenario BeLuVa CFD data + complete result JSONs published on Zenodo (see data/README.md for DOIs)

## Exact reproduction steps per paper section
See the individual `experiments/*/README.md` files. Each family documents:
- The exact commands / scripts used
- The random seeds (also in `seeds.txt`)
- Which Zenodo assets are required

## Key deterministic elements
- KMeans aggregation for deployable layouts: `random_state=0` (or 42 in noted variants)
- HPO / sensitivity / robustness: documented `np.random.seed(42)` + torch seeds
- All per-scenario optimizations were run once (single stored stochastic run)

## Data Availability statement (ready for paper / response letter)
The high-fidelity CFD dataset analysed in this study is publicly available on Zenodo at \citep{CFDdata}. Code, seeds, hyperparameters, and minimal data subsets are available at https://github.com/a11to1n3/GBM. Processed result tables and figure data will be archived with the accepted article. Exact commands to regenerate every figure and table appear in the `experiments/` directory of this repository.

## Environment
Python >= 3.11 + the dependencies in `pyproject.toml` (torch CPU/CUDA wheels documented in docs/getting_started.md).
