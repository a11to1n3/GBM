# GBM — Gradient-Based Mapper

**Topology-constrained optimisation for gas sensor placement in naturally ventilated livestock buildings.**

GBM (Gradient-Based Mapper) is a practical, geometry-aware method for choosing a small fixed set of *k* sensor locations that reliably estimate the spatial mean of a scalar field (e.g. CO₂ or NH₃ concentration) across an entire barn volume or monitoring plane.

It combines **coordinate-projection Mapper covers** (overlapping strips in 2D or D−1 pillars in 3D) with a **projected value-subgradient refinement** heuristic and aggregates scenario-specific candidates into one deployable layout via *k*-means.

The same formulation works for any scalar field; the accompanying paper evaluates it on high-fidelity CFD data for both CO₂ (broad respiration plumes) and NH₃ (localised sources) under dozens of ventilation states.

## Key Features
- **2D** (horizontal monitoring plane) and **3D** (full volume, D−1 pillars) modes
- Gas-agnostic formulation but performance is **not** gas-invariant — CO₂ layouts do not transfer to NH₃
- Strong empirical results vs. 8 baselines (k-medoids + gradient, greedy, uniform grid, random, simulated annealing, PSO, genetic, Monte-Carlo) across LW2/3/4 barns
- Emphasis on **fixed deployable layouts** (one layout per geometry/gas/LW/*k*, not per-scenario optima)
- Built-in local sensitivity analysis and held-out robustness diagnostics
- Clean, installable Python package + full reproducibility materials for every figure and table in the paper

## Installation

```bash
# CPU-only (recommended for laptops and most clusters)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install gbm

# With extras
pip install "gbm[plotting,hpo,dev]"
```

See `docs/getting_started.md` for CUDA vs CPU wheel selection and cluster notes.

## Quickstart (synthetic data)

```python
import numpy as np
import pandas as pd
from gbm.core import find_optimal_k_points_gbm_2D

# Create a tiny synthetic 2D concentration field
W, H = 200, 100
x = np.linspace(-20, 20, W)
z = np.linspace(-10, 10, H)
X, Z = np.meshgrid(x, z, indexing="ij")
C = 5e-6 + 3e-6 * np.exp(-((X)**2 + (Z)**2) / 40)

df = pd.DataFrame({
    "X": X.ravel(), "Y": np.full(W*H, 3.15), "Z": Z.ravel(), "Carbon": C.ravel()
})
inside = np.ones(W*H, dtype=bool)
global_mean = float(C.mean())

loss, mean_sens, std_sens, positions = find_optimal_k_points_gbm_2D(
    df, inside, k=5, in_CO2_avg=global_mean,
    cross_section="Z", barn_LW_ratio=2, epochs=8
)

print(f"Best 5-point loss: {loss:.2e}")
print("Selected positions (x, z):", positions)
```

Full runnable notebooks live in `examples/`.

## Repository Layout

```
GBM/
├── src/gbm/                     # Installable package
│   ├── core/                    # GBM method (2D + 3D D-1)
│   ├── baselines/               # 8 real baseline implementations
│   └── ...
├── experiments/                 # Self-contained experiment families
│   ├── 2d_co2/
│   ├── 3d/
│   ├── nh3/
│   ├── deployable_layouts/      # Fixed-layout MAE, rankings, CD diagrams
│   └── ...
├── examples/                    # Runnable notebooks & scripts (synthetic data)
├── data/
│   ├── examples/                # Tiny real scenarios for smoke tests
│   └── synthetic/               # Generator for CI and quick starts
├── results/
│   └── aggregates/              # Final tables & figures for the paper
├── docs/
└── pyproject.toml
```

Each directory under `experiments/` is designed to feel (and be extractable) like its own small project, with its own README, seeds, and reproduction instructions.

## Reproducing the Paper

All numbers, tables, and figures in the companion paper can be regenerated from this repository plus the Zenodo archives.

1. Install the package: `pip install -e ".[torch,plotting]"`
2. Follow the instructions in the relevant `experiments/<family>/README.md` (e.g. `experiments/deployable_layouts/` for the main heatmaps and rankings).
3. Use the documented seeds (per-family `seeds.txt`) and exact commands provided.
4. Small synthetic examples in `examples/` and `data/synthetic/` let you validate changes without the full dataset.

See `docs/reproducibility.md` for a detailed reproducibility checklist and ready-to-paste text for the paper.

## Data & Code Availability

The high-fidelity CFD dataset is publicly available on Zenodo (cited as \citep{CFDdata} in the paper).  
Code, seeds, hyperparameters, minimal data subsets, and full experiment reproduction instructions are available at https://github.com/a11to1n3/GBM.  
Processed result tables and figure data will be archived with the accepted article.

## Citation

If you use this code, please cite the paper:

> Anh-Duy Pham et al. “Topology-constrained Optimisation for Gas Sensor Placement in a Naturally Ventilated Barn based on Computational Fluid Dynamics Simulations.” *Computers and Electronics in Agriculture* (under revision, COMPAG-D-26-02203).

A machine-readable `CITATION.cff` is included in the repository.

## License

Apache-2.0 (see `LICENSE`).

## Status

- Core GBM method (2D + 3D D-1) with real implementations
- All 8 baselines ported with actual code (most with 2D+3D)
- Comprehensive experiment families + runnable notebooks
- Strong reproducibility support (seeds, synthetic data, per-family instructions)

The repository is ready to support the paper revision and future open-science release.

## Links

- Paper (preprint / camera-ready when available): authors’ separate manuscript repository
- Full CFD data & results archives: Zenodo (DOIs listed in `data/README.md`)
- Issues & discussions: GitHub

---

**Authors (paper order):** Anh-Duy Pham, Sabrina Hempel, Ali Alaei, Abhijith Srinivas Bidaralli, David Janke, Thomas Amon, Martin Atzmueller, Tim Römer.

Maintained by the GBM team (2026).