# HPO & Sensitivity Experiments

Grid sweeps (and optionally SMAC3) over GBM hyperparameters (overlap, learning rate, epochs) on 2D and 3D synthetic or real data.

## Status
This family now contains a thin, clean grid-sweep driver (`sweep.py`) that uses only the modern GBM public API.

The full SMAC3 HPO runs and the exact sensitivity numbers that appear in the paper were produced with the historical `hpo.py` / `sensitivity_analysis.py` + the full Zenodo scenario set. Those scripts and the resulting JSONs live in the Zenodo archives and the original BarnCSP checkout.

## Usage

```bash
# Quick synthetic sensitivity sweep (no external data)
python -m experiments.hpo_sensitivity.sweep \
    --dim 3D \
    --k 5,10 \
    --out results/aggregates/sensitivity_smoke.json
```

The driver sweeps a small grid over overlap / lr / epochs and records mean neighbor sensitivity loss.

## Extending to SMAC3
If you have `smac` installed (`pip install "gbm[hpo]"`), you can add a small SMAC3 wrapper in this directory that calls the same clean `gbm.core` entry points. The original `hpo.py` can serve as a reference for the search space and in-process evaluation pattern.

## Paper references
- Sensitivity analysis sections and HPO discussion in the COMPAG revision.
- The published sensitivity / HPO JSONs are part of the Zenodo result archives.

This is the third driver of the "next batch" of clean ports.
