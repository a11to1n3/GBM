# GMB — Gradient-Based Mapper

**Topology-constrained optimisation for gas sensor placement in naturally ventilated livestock buildings.**

GMB (Gradient-Based Mapper) is a practical, geometry-aware method for choosing a small fixed set of k sensor locations (or sampling points) that reliably estimate the spatial mean of a scalar field (e.g. CO₂ or NH₃ concentration) across an entire barn volume or monitoring plane. It combines **coordinate-projection Mapper covers** (overlapping strips or D−1 pillars) with a **projected value-subgradient refinement** heuristic and aggregates scenario-specific candidates into one deployable layout via k-means.

The same formulation works for any scalar field; the paper evaluates it on high-fidelity CFD data for both CO₂ (broad respiration plumes) and NH₃ (localised sources) under dozens of ventilation states.

## Key Features
- **2D (horizontal plane)** and **3D (full volume, D−1 pillars)** modes
- Gas-agnostic but performance is **not** gas-invariant — CO₂ layouts do not transfer to NH₃
- Strong empirical results vs. 8 baselines (k-medoids + gradient, greedy, uniform grid, random, SA, PSO, genetic, Monte-Carlo) across LW2/3/4 barns, k=1..50, 2D/3D, CO₂/NH₃
- Emphasis on **fixed deployable layouts** (one layout per geometry/gas/LW/k, not per-scenario optima)
- Built-in sensitivity (local neighbour perturbation) and held-out robustness diagnostics
- Clean, installable Python package + full reproducibility scripts for every figure/table in the paper

## Installation

```bash
# Recommended (includes torch for the subgradient refinement)
pip install gbm[torch]

# Or with uv (fast on clusters)
uv pip install gbm[torch,plotting,hpo]

# CPU-only torch wheel example (Linux)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install gbm
```

See `docs/getting_started.md` for CUDA vs CPU wheel selection and cluster notes.

## Quickstart (synthetic data)

```python
import numpy as np
from gbm.core import find_optimal_k_points_gbm_2D, find_optimal_k_points_gbm_3D

# TODO: load your scalar field (X, Y, Z, value) as a DataFrame or grid
# nodes_df, barn_inside_mask, global_mean = ...

# 2D example (monitoring plane at fixed height)
loss, mean_sens, std_sens, positions = find_optimal_k_points_gbm_2D(
    nodes_df, barn_inside_mask, k=5, in_CO2_avg=global_mean,
    cross_section="Z", barn_LW_ratio=4, overlap=75, epochs=20
)

print("Best 5-point loss:", loss)
print("Positions (x,z):", positions)
```

Full example notebooks and synthetic generators live in `data/synthetic/`.

## Repository Layout (Monorepo with Experiment Families)

```
GMB/
├── src/gbm/                  # The installable package (core + baselines)
│   ├── core/mapper_*.py      # The Gradient-Based Mapper (2D + 3D D-1)
│   ├── baselines/            # All 8 comparison methods (optional)
│   └── data.py               # Centralised loader + barn-inside heuristic
├── experiments/              # "Every experiment in its own (sub)repo"
│   ├── 2d_co2/               # 2D CO₂ results, plots, tables
│   ├── 3d/                   # 3D (D-1) + all baselines
│   ├── nh3/                  # NH₃ (2D/3D, X/Z/XZ/ZX cross-sections)
│   ├── deployable_layouts/   # KMeans fixed-layout MAE (main paper tables/figs)
│   ├── hpo_sensitivity/
│   ├── robustness/
│   ├── ablation/             # (Deprecated exploratory path — see paper)
│   └── ...
├── data/
│   ├── examples/             # 4–8 representative real scenarios (small, git-tracked)
│   ├── synthetic/            # Generator for examples, smoke tests & CI
│   └── download_full.sh      # Pulls the complete 242-scenario BeLuVa set from Zenodo
├── results/
│   ├── aggregates/           # deploy_results_all.json, ranking_tables.tex, sensitivity_*.json, ...
│   └── samples/              # Tiny illustrative JSONs
├── paper/                    # Minimal pointers (full manuscript lives in the authors' separate paper repo)
├── examples/                 # Runnable notebooks and scripts (synthetic data)
├── docs/
└── pyproject.toml
```

Each `experiments/<family>/` directory is self-contained (own README, `run.sh` / Makefile, `seeds.txt`, configs). Full per-scenario result JSONs and the complete CFD dataset are archived on Zenodo (see below).

## Reproducing the Paper

1. Install with `pip install -e ".[torch,plotting,hpo,dev]"`.
2. `cd experiments/3d && ./run.sh` (or the equivalent for your family).
3. All random seeds, HPO settings, and exact commands are documented per experiment family.
4. Figures/tables are regenerated from `results/aggregates/`.

**Data & full results:** The 242 combined CFD scenarios (~50 GB) and the complete set of per-scenario JSON outputs for all methods are published on Zenodo. See `data/README.md` and each experiment `README.md` for DOIs and download instructions.

## Citation

If you use GMB in academic work, please cite the companion paper:

> Anh-Duy Pham et al. "Topology-constrained Optimisation for Gas Sensor Placement in a Naturally Ventilated Barn based on Computational Fluid Dynamics Simulations." *Computers and Electronics in Agriculture* (under revision, COMPAG-D-26-02203).

A `CITATION.cff` file is provided for machine-readable citation.

## License

Apache-2.0 (see `LICENSE`).

## Status & Roadmap

- [x] Core GBM 2D + 3D (D-1) method extracted and packaged
- [ ] Full baseline re-exports + modern CLI
- [ ] Experiment families populated with run scripts + seeds
- [ ] Minimal real + synthetic data subsets
- [ ] CI smoke tests + docs

Contributions and issues are welcome (especially new scalar-field use cases outside livestock ventilation).

## Links

- Paper (preprint / camera-ready when available): [separate authors' paper repo]
- Full data & results: Zenodo (DOIs listed in `data/README.md`)
- Issues / discussions: GitHub

---

**Authors (paper order):** Anh-Duy Pham, Sabrina Hempel, Ali Alaei, Abhijith Srinivas Bidaralli, David Janke, Thomas Amon, Martin Atzmueller, Tim Römer.

Maintained by the GMB team (2026).

## Badges (add once repo is public)
<!-- [![CI](https://github.com/a11to1n3/GBM/actions/workflows/ci.yml/badge.svg)](https://github.com/a11to1n1/GBM/actions) -->
<!-- [![PyPI](https://img.shields.io/pypi/v/gbm.svg)](https://pypi.org/project/gbm) -->
<!-- [![Zenodo](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX) -->

## Quick links for the paper
- Data & full results: Zenodo (DOIs to be inserted in Data Availability paragraph)
- Paper repo: (authors' separate manuscript repository)
