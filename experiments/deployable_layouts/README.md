# Deployable Layouts (Fixed Sensor Placement)

This family produces the main result tables and heatmaps of the paper:
"Deployable-layout MAE for CO₂ and NH₃ at k=5,10,20 across LW ratios."

## What it does
1. For each method, collect the best k-point positions from every scenario (per LW, dim, gas).
2. Pool them and run KMeans (fixed random_state=0) → one set of centroids = the single fixed deployable layout.
3. For every scenario, evaluate the layout (nearest-grid lookup + mean) vs. the true barn mean.
4. NH₃ additionally reports plume-only MAE (plume = values > 1% of max concentration in the scenario).
5. Produces `deploy_results_all.json`, ranking tables, critical difference diagrams, etc.

## Key outputs
- `results/aggregates/deploy_results_all.json`
- `results/aggregates/ranking_tables.tex`
- Main heatmaps (`deployable_co2_heatmap.pdf`, `deployable_nh3_heatmap.pdf`)
- CD diagrams and other figures (via plotting code)

## Usage

### Compute fixed layouts
```bash
python -m experiments.deployable_layouts.run \
    --results-root results \
    --k 5,10,20 \
    --out results/aggregates/deploy_results_all.json
```

### Regenerate the main heatmaps
```bash
python -m experiments.deployable_layouts.plot_results \
    --deploy-json results/aggregates/deploy_results_all.json \
    --outdir results/figures
```

The scripts are self-contained and work with either the full Zenodo result archive or a small development subset.

## Data requirements
- Per-scenario JSON position files under `results/<method_dir>/`.
- Scenario CSVs under `data/scenarios/` (only needed for MAE evaluation).

See the top-level `data/README.md` for how to obtain the full BeLuVa dataset and result archives.
