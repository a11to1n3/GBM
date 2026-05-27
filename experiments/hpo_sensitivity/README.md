# HPO & Sensitivity Experiments

SMAC3 + grid sweeps over GBM hyperparameters (overlap percentage, learning rate, epochs) for both 2D and 3D.

## Status
This family is planned / empty. No driver has been ported yet.

The original HPO / sensitivity runs that appear in the paper (and the associated JSONs) were produced with the historical `hpo.py`, `sensitivity_analysis.py`, and SMAC3 configuration scripts from the BarnCSP checkout.

## Current practical path
- The sensitivity results used in the revision are archived in the Zenodo result sets (see `data/README.md`).
- For new work, the clean GBM Python API (`gbm.core.find_optimal_k_points_gbm_*`) plus the synthetic generator in `data/synthetic/` can be used to reproduce the spirit of the sweeps quickly.

## Seeds
Original runs used `np.random.seed(42)` + torch seeds (documented in the historical logs).

## Paper references
- Sensitivity analysis sections and supplementary figures in the COMPAG revision.
- Hyper-parameter robustness discussion.

A minimal driver matching the style of `deployable_layouts/run.py` will be added in a future increment.
