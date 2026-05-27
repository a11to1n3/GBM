# Deprecated Code (DBSCAN / Mapper-Topology Era)

This directory contains the old prototype code that used CO₂-value filtering + spatial DBSCAN + greedy cluster selection before the revision.

## Status
**Not used for any reported results in the COMPAG-D-26-02203 revision.**

The revision explicitly removed DBSCAN / outlier filtering from the GBM pipeline. The reported method uses pure coordinate-projection Mapper covers + projected value-subgradient refinement (see `src/gbm/core/` and the paper Section 3 + Appendix B).

## Contents (historical)
- Old `mapper_topology_k_points_searcher.py` (2D and 3D versions)
- Related ablation utilities that compared "full GBM (with DBSCAN)" vs "mapper-only" vs uniform
- Pre-revision workflow diagrams and notes

## Why kept?
- For archaeology and reviewer questions ("what changed between the first submission and the revision?").
- The ablation JSONs and plots from the exploratory phase are still referenced in the response letter and some early figures.

## How to use (if you really must)
Do **not** use for new work. The modern entry points are `gbm.core.find_optimal_k_points_gbm_2D` / `..._3D`. 

The old ablation scripts are kept only for historical reference.

## Migration notes
- The barn_inside heuristic and grid handling were centralised in `gbm/data.py`.
- All stochastic seeds and hyper-parameters for the reported path are documented in the other experiment families and Appendix C of the paper.

This directory exists purely for transparency during the review process. New contributions should live in the clean core or the active experiment families.
