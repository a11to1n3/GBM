# GMB Experiments

This directory contains one self-contained "experiment family" per major axis of the paper.

Each sub-directory is designed to feel (and be extractable) like its own small repository:

- Own `README.md` with exact reproduction commands, seeds, data requirements, and expected outputs.
- `seeds.txt` (or inline seeds documented).
- Minimal `run.sh` / `Makefile` (or Python entrypoints).
- Pointers to the full data/results on Zenodo (the 242 CFD scenarios and complete per-scenario JSONs live outside this repo).

## Families (matching the paper)

- `2d_co2/` — 2D monitoring plane results for CO₂ across LW2/3/4.
- `3d/` — Full 3D volume (D-1 pillars / GBM-XZ) + all baselines.
- `nh3/` — NH₃ (2D + 3D, all cross-section variants X/Z/XZ/ZX). Includes the cases where some baselines win.
- `deployable_layouts/` — KMeans aggregation of per-scenario positions into one fixed layout per (gas, dim, LW, k). Produces the main heatmaps/tables.
- `hpo_sensitivity/` — SMAC3 + grid sweeps for overlap / lr / epochs.
- `robustness/` — 80/20 held-out scenario splits (20 seeds).
- `ablation/` — (Deprecated exploratory path; see paper notes — mapper-only vs full GBM vs uniform.)
- `runtime_benchmark/` — Wall-time measurements.
- `statistical_analysis/` — Wilcoxon, Cliff's delta, Nemenyi CD diagrams, ranking tables.
- `deprecated/` — Old DBSCAN / mapper-topology code (not used in reported results; kept for archaeology).

## How to reproduce a specific family

1. Install the package: `pip install -e ".[torch,plotting]"` from the GMB root.
2. `cd experiments/<family>`
3. Follow the family's `README.md` (usually `./run.sh` or `python reproduce.py`).
4. Full per-scenario JSONs + figures are in the Zenodo archives (DOIs below). Use `--data-dir` or the download script if you need the complete set.

## Data & results provenance

- Full 242 combined CFD scenarios (~50 GB) and all raw per-scenario result JSONs (968+ per method + variants): published on Zenodo by the authors (BeLuVa project data + GMB outputs).
- See `../data/README.md` for the exact DOIs and download instructions.
- Only tiny example subsets + synthetic generators live in this repo (for CI, smoke tests, and quick starts).

## Seeds & reproducibility

All stochastic components use documented seeds (see each family's `seeds.txt` or the family README).
KMeans aggregation in deploy scripts uses `random_state=0` (or 42 in some variants) for exact reproducibility.

When a family is ready, its README will list the exact Git commit / tag of the GMB core used.

## Relation to the paper

Every figure and table in the COMPAG revision was produced from one (or more) of these families + the aggregates in `../results/aggregates/`.

See the top-level `README.md` and `docs/reproducibility.md` (when added) for the Data Availability statement text suitable for the paper.

## Adding a new experiment family

Create a new subdirectory with:
- `README.md`
- `run.sh` (or equivalent)
- `seeds.txt`
- `configs/` (YAML or simple Python dicts)
- Any family-specific analysis scripts

Keep heavy outputs out of git (they belong on Zenodo or in `results/aggregates/`).

This structure lets collaborators (or future you) treat each major claim in the paper as its own mini-project while sharing the core `gbm` library.
