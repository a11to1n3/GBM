# 3D Experiments (D-1 Pillars / GBM-XZ)

This family contains the major new contribution of the revision: full 3D volume results using the D-1 generalisation (GBM-XZ pillars that respect barn L/W ratio, leaving height free for data-driven selection).

## Scope
- All 242 scenarios (LW2/3/4)
- GBM-XZ (and legacy single-axis X/Z for comparison)
- All 8 baselines (kmedoids, greedy, uniform, random, SA, PSO, genetic, Monte-Carlo)
- k up to 50 (composite k only for 3D to avoid prime-k collapse)
- Both CO₂ and NH₃

## D-1 principle (key implementation detail)
See `gbm/utils.py:factor_k_for_3D` and the paper (Definition 2 + Theorem 1).

For a target k and LW ratio we choose k_x, k_z such that k_x * k_z ≈ k and k_x/k_z ≈ LW. This produces vertical full-height pillars. Optimisation then selects one (X,Y,Z) location per pillar (Y is chosen freely from the data inside the pillar).

## Reproduction
See the family `run.sh` (or the port of the old `run_3d_pipeline.sh` / slurm scripts).

Typical command (via the unified CLI once Phase 2 is complete):
```bash
gbm run data/examples/LW4_....csv --method gbm --dim 3D --gas CO2 --cross-section XZ --k 5,10,20
```

## Key outputs
- Per-scenario JSONs under `results/tda-mapper/` (with 3dXZ / 3d etc. suffixes) and the corresponding baseline dirs.
- 3D-specific plots and tables (loss distributions, deployable MAE, runtime, etc.).

## Seeds
Documented in `seeds.txt` (to be added) + the individual searcher calls (np.random, torch, etc.).

## Data note
Full 3D runs are heavy. Use the small example scenarios in `../data/examples/` + the synthetic generator for development and CI. The complete result set is in the Zenodo archive.

## Paper references
- Method section (D-1 cover)
- All 3D figures and tables (especially the deployable-layout heatmaps and ranking results)
- Appendix on 3D factorisation and prime-k handling

This family demonstrates that GBM scales to true 3D and that the D-1 construction is both theoretically grounded and practically effective.
