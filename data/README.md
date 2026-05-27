# GBM Data

## What lives here (git-tracked)
- `examples/` — A small number of representative real combined scenario CSVs (LW4 priority for the paper’s motivation and figure examples). Sufficient for smoke tests, CI, and quick development.
- `synthetic/` — Generator script that produces valid CSV files with the historic column names, correct grid dimensions, and plausible CO₂/NH₃ fields. Used by examples, smoke tests, and CI.

## Full data (outside this repo)
The complete set of 242 combined CFD scenarios (LW2/3/4, all ventilation states) comes from the BeLuVa project and is archived on Zenodo.

- Raw per-Y-plane data and the original 7z archive.
- Combined 3D scenario CSVs used by all GBM experiments.
- DOIs and record URLs are listed in the paper’s Data Availability statement and in the experiment-family READMEs.

A small helper script (`download_full.sh` or `python -m gbm.data.download`) will be added once the final Zenodo record IDs are confirmed. In the meantime the DOIs and direct links are listed in the paper Data Availability statement and in every experiment-family README.

## Results
All raw per-scenario JSON outputs and the aggregated files needed for the paper (`deploy_results_all.json`, ranking tables, etc.) are published on Zenodo.

Only the final aggregates and a few illustrative samples live in `results/aggregates/` and `results/samples/`.

## Reproducibility
The synthetic generator + the small real examples + the documented seeds per experiment family allow every number, plot, and table in the paper to be regenerated from this repository + the Zenodo datasets.

See the top-level `README.md` and `docs/reproducibility.md` for the exact Data Availability paragraph suitable for the paper.
