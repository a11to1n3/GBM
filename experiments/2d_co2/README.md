# 2D CO₂ Experiments

2D monitoring-plane results for CO₂ across LW2/3/4 barns.

## Status
Minimal scaffolding present (seeds + run.sh). Full driver port from the original BarnCSP pipeline is planned but not yet completed.

For the actual 2D CO₂ deployable-layout results used in the paper, the historical scripts in the original BarnCSP checkout (or the full Zenodo result archives) remain the reference until the driver is ported into this family.

## Seeds
Documented in `seeds.txt` (`np.random.seed(42)`, KMeans `random_state=0`).

## Data
Full 242-scenario BeLuVa CFD data (combined 2D planes) + result JSONs are on Zenodo (see top-level `data/README.md`).

## Reproduction
See the top-level `docs/reproducibility.md` and the `deployable_layouts/` family (which already contains the ported aggregation driver) for the current practical path to the published 2D CO₂ heatmaps and rankings.

## Paper references
- All 2D CO₂ figures and tables in the COMPAG revision (especially the deployable-layout MAE heatmaps).
- Method section (coordinate-projection Mapper covers in 2D).

This family will eventually contain the clean, self-contained 2D CO₂ reproduction scripts matching the style of `deployable_layouts/`.
