# NH₃ Experiments (Gas-Dependent Behaviour)

NH₃ is the harder case in the study: localised, sharp plumes from point sources (e.g. under slats) rather than the broad, well-mixed respiration plumes of CO₂.

## Purpose of this family
- Demonstrate that GBM is gas-agnostic in formulation but **not** gas-invariant in performance.
- Highlight the cells (LW/k combinations) where uniform, random, greedy, or PSO baselines can outperform GBM on a fixed deployable layout.
- Provide the NH₃-specific deployable MAE heatmaps (Figure 4 in the paper) and the accompanying discussion.

## Cross-section variants (2D + 3D)
- 2D: X and Z strips at the monitoring height.
- 3D: XZ and ZX (D-1), plus experimental XYZ* variants with forced height diversity.

All variants are exercised here.

## Key finding (reported)
For NH₃, no single method dominates every LW/k cell. The paper deliberately calls this out with outlined cells in the heatmaps and balanced interpretation in the text and response letter.

## Reproduction
Same pattern as the 3D family, but with `--gas NH3`.

Plume-only evaluation is performed in the deployable-layout post-processing step (threshold > 1% of per-scenario max concentration).

## Data & results
- Full NH₃ per-scenario JSONs (with _NH3 suffix) live in the Zenodo results archive.
- A subset of the raw scenarios with strong NH₃ plumes are included in `../data/examples/`.

## Relation to revision
- Directly supports the "gas-agnostic but not gas-invariant" claim.
- Drives the discussion that practitioners should select/validate the layout per target gas rather than blindly transferring a CO₂ layout to NH₃ (and vice versa).

See also the top-level paper response letter for the reviewer points that prompted the clearer gas-specific analysis.
