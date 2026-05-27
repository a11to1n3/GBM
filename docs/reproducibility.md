# Reproducibility

This document is the central reference for regenerating every number, table, and figure in the COMPAG revision (COMPAG-D-26-02203).

## Core claim
All results can be regenerated from:
- This GBM repository (code, minimal real scenarios, synthetic generator, experiment drivers)
- The full 242-scenario BeLuVa high-fidelity CFD dataset + complete per-scenario result JSON archives published on Zenodo (see `data/README.md` for DOIs and direct links)

Only small illustrative subsets and the synthetic generator are committed here. The heavy data and full result sets live on Zenodo.

## Exact reproduction steps per paper section
Each `experiments/<family>/README.md` documents:
- The exact commands or Python entry points used for that family
- The random seeds (also recorded in `seeds.txt`)
- Which Zenodo assets (raw scenarios or result archives) are required
- Expected outputs (JSONs, tables, figures)

Key families and what they produce:
- `deployable_layouts/` — fixed-layout MAE heatmaps, ranking tables, critical-difference diagrams (main results)
- `statistical_analysis/` — Wilcoxon signed-rank tests, Cliff's delta, Nemenyi rankings
- `3d/` and `nh3/` — all 3D (D-1 pillars) and gas-specific results
- `2d_co2/` — 2D monitoring-plane CO₂ results across LW ratios
- `hpo_sensitivity/`, `robustness/`, `runtime_benchmark/`, `ablation/` — planned / exploratory extensions (drivers not yet ported; see top-level reproducibility for current status)

## Key deterministic elements
- KMeans aggregation for deployable layouts: `random_state=0` (or 42 in documented variants)
- All stochastic components: `np.random.seed(42)`, `torch.manual_seed(42)` (or per-method equivalents documented in the family)
- All per-scenario optimizations were run once; the stored JSONs are the exact stochastic realizations used in the paper

## Recommended environment
- Python >= 3.11
- Core dependencies from `pyproject.toml` (hard `torch>=2.0`)
- For plotting / HPO extras: `pip install -e ".[torch,plotting,hpo,dev]"`

CPU-only torch wheels are recommended for laptops and most shared clusters:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e ".[torch,plotting]"
```

CUDA wheels are only needed for the heaviest full-suite runs; the code itself is small.

## Data Availability statement (ready to paste into the paper or response letter)
The high-fidelity CFD dataset analysed in this study is publicly available on Zenodo at \citep{CFDdata}. Code, seeds, hyperparameters, and minimal data subsets are available at https://github.com/a11to1n3/GBM. Processed result tables and figure data will be archived with the accepted article. Exact commands to regenerate every figure and table appear in the `experiments/` directory of this repository.

## Paper-ready LaTeX block (Data & Code Availability)
```latex
\section*{Data and Code Availability}
The high-fidelity CFD dataset analysed in this study is publicly available on Zenodo at \citep{CFDdata}.
Code, seeds, hyperparameters, and minimal data subsets are available at \url{https://github.com/a11to1n3/GBM}.
Processed result tables and figure data will be archived with the accepted article.
Exact commands to regenerate every figure and table appear in the \texttt{experiments/} directory of this repository.
```

See the individual family READMEs for the precise commands that produced each figure and table in the revision.
