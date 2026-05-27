# GBM Experiments

One self-contained "experiment family" per major axis of the paper.

Each subdirectory is designed to feel (and be extractable) like its own small repository:
- `README.md` with exact reproduction commands, seeds, data requirements, and expected outputs
- `seeds.txt` (or inline documentation)
- Minimal `run.sh` or Python entry points
- Pointers to the full 242-scenario CFD data and result archives on Zenodo

## Families

| Family | Status | What it produces |
|--------|--------|------------------|
| `2d_co2/` | Minimal README + seeds | 2D monitoring-plane CO₂ results (LW2/3/4) |
| `3d/` | Minimal README + seeds | Full 3D volume (D-1 pillars / GBM-XZ) + all baselines |
| `nh3/` | Minimal README + seeds | NH₃ (2D + 3D) — gas-dependent behaviour |
| `deployable_layouts/` | Full driver (`run.py`, `plot_results.py`) | Fixed-layout MAE heatmaps, rankings, CD diagrams (core paper results) |
| `statistical_analysis/` | Core driver (`compute.py`) | Wilcoxon, Cliff’s delta, Nemenyi rankings, tables |
| `hpo_sensitivity/` | Planned (empty) | SMAC3 + grid sweeps (overlap / lr / epochs) |
| `robustness/` | Planned (empty) | 80/20 held-out splits (20 seeds) |
| `runtime_benchmark/` | Planned (empty) | Wall-time measurements |
| `ablation/` | Planned (empty) | Exploratory ablation (mapper-only vs. full GBM) |
| `deprecated/` | Historical only | Old DBSCAN / mapper-topology prototypes (not used in revision) |

## How to reproduce a family

1. From the repo root: `pip install -e ".[torch,plotting]"`
2. `cd experiments/<family>`
3. Follow that family’s `README.md` (and `run.sh` or the Python driver if present)
4. Use the documented seeds

Full per-scenario JSONs and figures live in the Zenodo archives (see `../data/README.md`). Only small examples and the synthetic generator are committed here.

## Seeds & reproducibility

All stochastic components use documented seeds (per-family `seeds.txt`).  
KMeans aggregation uses `random_state=0` (or 42 in noted variants).

## Relation to the paper

Every figure and table in the COMPAG revision was produced from one or more of these families plus the aggregates in `../results/aggregates/`.

See the top-level `README.md` and `docs/reproducibility.md` for the Data Availability statement and ready-to-paste LaTeX block.

## Adding a new family

Create a subdirectory with at minimum:
- `README.md`
- `seeds.txt`
- `run.sh` or a Python entry point (or clear note that the family is planned)

Keep large outputs out of git. This structure lets each major claim live as its own mini-project while sharing the clean `gbm` library.
