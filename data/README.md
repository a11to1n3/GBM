# GMB Data

## What lives here (in-repo, git-tracked)
- `examples/` — A small number of representative real combined scenario CSVs (LW4 priority for the motivation and figure examples in the paper). These are sufficient for smoke tests, CI, and quick development.
- `synthetic/` — Generator script(s) that produce valid CSV files with the historic column names, correct grid dimensions for a given LW ratio, and plausible CO₂/NH₃ concentration fields (smooth background + localised plumes). Used by examples, smoke tests, and CI.

## Full data (outside this repo)
The complete set of 242 combined CFD scenarios (LW2/3/4, all ventilation states, both gases) comes from the BeLuVa project (DFG-funded) and is archived on Zenodo.

- Raw per-Y-plane data + the 7z archive from the original Zenodo record.
- The combined 3D scenario CSVs used by all GMB experiments.
- DOIs and exact record URLs: see the paper Data Availability statement and the experiment-family READMEs.

**Download script**: `download_full.sh` (or `python -m gbm.data.download`) will be provided once the precise Zenodo record IDs are confirmed.

## Results (per-scenario JSONs + aggregates)
All raw outputs (one JSON per scenario + method + dim + gas + cross-section variant) plus the aggregated `deploy_results_all.json`, sensitivity/robustness/hpo JSONs, etc. are also published on Zenodo.

Only a few sample JSONs + the final aggregates needed to regenerate the paper figures/tables are committed here (under `results/aggregates/` and `results/samples/`).

## Reproducibility note
With the synthetic generator + the example scenarios + the published full archives on Zenodo + the exact seeds documented per experiment family, every number, plot, and table in the paper can be regenerated from this repository + the Zenodo datasets.

See the top-level README and `docs/reproducibility.md` (when populated) for the exact paragraph suitable for the paper's Data Availability section.
