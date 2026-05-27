# GBM Examples

This directory contains runnable examples demonstrating the Gradient-Based Mapper (GBM) method.

## Notebooks

- `01_quickstart_synthetic.ipynb` — Basic usage of GBM on synthetic 2D data. Good starting point.
- `02_gbm_vs_baselines.ipynb` — Quick comparison of GBM against selected baselines.
- `03_3d_gbm_quickstart.ipynb` — Basic 3D GBM (D-1 pillars) on synthetic volume data.
- `04_3d_baselines_comparison.ipynb` — GBM-3D vs several 3D baselines.
- `05_3d_full_baseline_sweep.ipynb` — Full side-by-side comparison of GBM-3D vs all currently available 3D baselines.
- `06_3d_runtime_benchmark.ipynb` — Wall-clock timing comparison across 3D methods.
- `07_kmedoids_3d_demo.ipynb` — Minimal demo of the kmedoids 3D implementation.

## Python Scripts

- `quickstart.py` — Plain Python equivalent of the first notebook (no Jupyter required).

## Running the Examples

```bash
pip install -e ".[dev]"     # or at minimum the core dependencies + jupyter
jupyter notebook            # or run the .py scripts directly
```

All examples use only synthetic data, so they run without any external CFD files.

## Purpose

These examples are intentionally minimal and self-contained. They let you understand the core GBM API and the newly ported 3D baselines quickly, without needing the full 242-scenario Zenodo dataset.

## New 3D Notebooks (added to exercise the newly ported 3D baselines)

- `03_3d_gbm_quickstart.ipynb` — Basic 3D GBM (D-1 pillars / GBM-XZ) on synthetic volume data.
- `04_3d_baselines_comparison.ipynb` — Side-by-side comparison of GBM 3D vs several 3D baselines (Greedy, Uniform, etc.) on the same synthetic field.

These notebooks demonstrate the new 3D baseline ports (greedy_3D, uniform_3D, PSO_3D, monte_carlo_3D, random_3D, simulated_annealing_3D, genetic_3D).

### New Comprehensive 3D Sweep Notebook
- `05_3d_full_baseline_sweep.ipynb` — Full side-by-side comparison of GBM-3D vs **all available 3D baselines** (Greedy 3D, Uniform 3D, PSO 3D, Monte Carlo 3D, Random 3D, SA 3D, Genetic 3D) on the same synthetic volume. Includes a summary table.

This is the most complete demonstration of the newly completed 3D baseline ports.

### New Runtime Benchmark Notebook
- `06_3d_runtime_benchmark.ipynb` — Wall-clock timing of GBM-3D vs multiple 3D baselines (Greedy, Uniform, PSO, Monte Carlo, Random) on synthetic data. Includes a simple summary table.

Useful for reproducing runtime claims and quick performance regression testing.

### New kmedoids 3D Demo Notebook
- `07_kmedoids_3d_demo.ipynb` — Minimal demo of the newly added `kmedoids_3D` (PAM + subgradient) compared to GBM 3D on synthetic volume data.

This notebook directly exercises the last 3D baseline piece.

### New 3D Sensitivity Analysis Notebook
- `08_3d_sensitivity.ipynb` — Sweeps overlap, lr, and epochs for GBM-3D on synthetic data and produces simple sensitivity plots (mean neighbor loss).

This directly addresses the request for a sensitivity analysis notebook in 3D.
