# Robustness Experiments

80/20 held-out scenario splits used to test whether the deployable (KMeans-aggregated) layouts generalise to unseen ventilation states.

## What it does (clean port)
- Performs N random 80/20 train/test splits over the provided scenarios.
- For each k and each split:
  - Runs GBM (and optionally selected baselines) on the train scenarios.
  - Pools all returned sensor positions.
  - Fits a single KMeans layout (`random_state=0`).
  - Evaluates the layout on the held-out test scenarios (full-barn MAE via nearest-grid lookup).
- Reports mean ± std test MAE across splits (per k).

This matches the spirit of the original `robustness_analysis.py` while using the clean GBM public API (`gbm.core` + `gbm.baselines`).

## Usage

### Smoke test (synthetic data, fast, no external files)
```bash
python -m experiments.robustness.run \
    --synthetic \
    --n-synthetic 8 \
    --dim 3D \
    --k 5,10 \
    --n-splits 3 \
    --out results/aggregates/robustness_smoke.json
```

### Real data (subset of Zenodo combined scenarios)
```bash
python -m experiments.robustness.run \
    --data-dir data/scenarios \
    --dim 3D \
    --k 5,10,20 \
    --n-splits 5 \
    --out results/aggregates/robustness_3d.json
```

The script writes a compact JSON:
```json
{
  "5":  {"mean_test_mae": 1.23e-7, "std_test_mae": 4.5e-9, "n_splits": 5},
  "10": {"mean_test_mae": ..., ...},
  ...
}
```

## Seeds & reproducibility
- Split RNG: `np.random.default_rng(42)` (deterministic across runs)
- KMeans: `random_state=0`
- GBM internal stochasticity: controlled by the documented seeds in the calling context (default `np.random.seed(42)` + torch seeds inside the optimisers)

## Data requirements
- Synthetic mode: zero external data.
- Real mode: a directory of combined scenario CSVs (the same format used by all other families). Full set is on Zenodo (see `../data/README.md`).

## Paper references
- Robustness section and associated figures/tables in the COMPAG revision.
- The published numbers were produced with the historical `robustness_analysis.py` + the full 242-scenario Zenodo set; the driver here lets you reproduce the methodology cleanly with the modern GBM package.

## Limitations of the current port
- Only GBM is exercised by default (easy to extend to baselines by adding a `--methods` flag).
- The original paper used 20 splits; the driver defaults to fewer for speed. Increase `--n-splits` for production runs.

This family is the first of the "next batch" of driver ports (following the style of `deployable_layouts/` and `statistical_analysis/`).
