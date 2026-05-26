# GBM Experiments

This directory contains one self-contained "experiment family" per major axis of the paper.

Each subdirectory is designed to feel (and be extractable) like its own small repository:

- Own `README.md` with exact reproduction commands, seeds, data requirements, and expected outputs.
- `seeds.txt` (or inline seeds documented).
- Minimal `run.sh` or Python entrypoints.
- Pointers to the full data and results on Zenodo (the 242 CFD scenarios and complete per-scenario JSONs live outside this repo).

## Families

- `2d_co2/` — 2D monitoring plane results for CO₂ across LW2/3/4.
- `3d/` — Full 3D volume (D-1 pillars / GBM-XZ) + all baselines.
- `nh3/` — NH₃ (2D + 3D, all cross-section variants). Highlights cases where some baselines win.
- `deployable_layouts/` — KMeans aggregation into fixed layouts. Produces the main heatmaps, tables, and rankings.
- `hpo_sensitivity/` — SMAC3 + grid sweeps (overlap / lr / epochs).
- `robustness/` — 80/20 held-out scenario splits (20 seeds).
- `ablation/` — Exploratory ablation (mapper-only vs full GBM vs uniform). Not used in reported results.
- `runtime_benchmark/` — Wall-time measurements.
- `statistical_analysis/` — Wilcoxon tests, Cliff’s delta, Nemenyi CD diagrams, ranking tables.
- `deprecated/` — Old DBSCAN / mapper-topology code (kept for archaeology only).

## How to reproduce a family

1. Install: `pip install -e ".[torch,plotting]"` from the repo root.
2. `cd experiments/<family>`
3. Follow the family’s `README.md` (or `run.sh`).
4. Use the documented seeds and commands.

Full per-scenario JSONs and figures live in the Zenodo archives (see `../data/README.md` for DOIs). Only small examples and synthetic generators are committed here.

## Seeds & reproducibility

All stochastic components use documented seeds (per-family `seeds.txt`).  
KMeans aggregation uses `random_state=0` (or 42 in noted variants) for exact reproducibility.

## Relation to the paper

Every figure and table in the COMPAG revision was produced from one or more of these families plus the aggregates in `../results/aggregates/`.

See the top-level `README.md` and `docs/reproducibility.md` for the Data Availability statement and ready-to-paste text for the paper.

## Adding a new family

Create a subdirectory containing:
- `README.md`
- `run.sh` (or Python entrypoint)
- `seeds.txt`
- `configs/`

Keep large outputs out of git (they belong on Zenodo or in `results/aggregates/`).

This design lets each major claim in the paper live as its own mini-project while sharing the core `gbm` library.
