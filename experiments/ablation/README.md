# Ablation Experiments

Exploratory comparisons (mapper-only vs. full GBM vs. uniform grid, DBSCAN variants, etc.).

## Status
This family is planned / empty and was never part of the reported results in the COMPAG-D-26-02203 revision.

The ablation JSONs and plots from the early exploratory phase are still referenced in the response letter and some early figures. They live in the historical BarnCSP checkout (`ablation_study.py`, `results/ablation_*.json`, etc.).

## Important note
**These experiments are not used for any of the main claims or tables in the published revision.**

The revision explicitly removed DBSCAN / outlier filtering. The reported method is pure coordinate-projection Mapper covers + projected value-subgradient refinement.

## Paper references
- Early ablation discussion in the response letter and (where relevant) supplementary material.

Kept only for archaeology and reviewer questions. New contributions should live in the clean core or the active families.
