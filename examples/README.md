# GBM Examples

Runnable notebooks and scripts demonstrating the Gradient-Based Mapper (GBM) method and all eight baselines.

All examples use only synthetic data generated on the fly. No external CFD files or Zenodo downloads are required.

## Notebooks (8 total)

| Notebook | Purpose |
|----------|---------|
| `01_quickstart_synthetic.ipynb` | Basic GBM usage on a tiny synthetic 2D field. Recommended starting point. |
| `02_gbm_vs_baselines.ipynb` | GBM vs. a subset of the 2D baselines on the same synthetic field. |
| `03_3d_gbm_quickstart.ipynb` | 3D GBM (D-1 pillars / GBM-XZ) on a synthetic volume. |
| `04_3d_baselines_comparison.ipynb` | GBM-3D vs. several 3D baselines (greedy, uniform, etc.). |
| `05_3d_full_baseline_sweep.ipynb` | Full side-by-side comparison of GBM-3D vs. all eight available 3D baselines on one synthetic volume, with a summary table. |
| `06_3d_runtime_benchmark.ipynb` | Wall-clock timing of GBM-3D vs. multiple 3D baselines (useful for regression checks and runtime claims). |
| `07_kmedoids_3d_demo.ipynb` | Minimal exercise of the newly ported `kmedoids_3D` (PAM + subgradient refinement). |
| `08_3d_sensitivity.ipynb` | Sensitivity sweep of GBM-3D hyperparameters (overlap, lr, epochs) on synthetic 3D data. |

## Python Scripts

- `quickstart.py` — Plain-Python equivalent of the first notebook (no Jupyter required).

## Running the Examples

```bash
# From the GBM repo root
pip install -e ".[dev]"          # or at minimum torch + jupyter
jupyter notebook examples/       # or run the .py scripts directly
```

## Scope and Limitations

These examples are intentionally minimal and self-contained. They let you verify that the core GBM API and all 3D baseline ports work correctly without the full 242-scenario Zenodo dataset.

For the actual paper results (full 242 scenarios, deployable-layout heatmaps, statistical tests, etc.) follow the instructions in the relevant `experiments/<family>/README.md` together with the Zenodo archives.
