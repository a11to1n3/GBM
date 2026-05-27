# GBM Repository Status (for Paper Revision COMPAG-D-26-02203)

**Last updated:** 2026-05-26

## Core Deliverables
- Full GBM method (2D + 3D D-1 pillars) in `src/gbm/core/`
- All 8 baselines with real, ported implementations (2D + 3D where applicable)
- Self-contained experiment families under `experiments/` (each with README, seeds, entry points)
- 8 runnable notebooks + scripts in `examples/` (strong 3D coverage, all synthetic)

## Reproducibility
- Seeds documented per family (`seeds.txt` + inline)
- Synthetic generator + small real scenarios for smoke tests / CI
- Full reproduction commands in every family README
- Data Availability + ready-to-paste LaTeX block in `docs/reproducibility.md`

## Paper Alignment
- Terminology: "GBM" / "Gradient-Based Mapper" throughout (matches manuscript)
- Data & Code Availability text ready for manuscript / response letter
- Deployable-layout drivers and statistical core already ported into the clean structure

## Known Open Items
- GitHub push is up to date.
- Final Zenodo DOIs for the complete result archives should be inserted when available.
- Four experiment families (`hpo_sensitivity/`, `robustness/`, `runtime_benchmark/`, `ablation/`) still lack full ported drivers (minimal honest READMEs present; see reproducibility doc).

## For Paper Submission
1. Copy the Data Availability block from `docs/reproducibility.md` (or the small `.tex` fragment in `docs/paper_data_availability.tex`) into the manuscript or response letter.
2. Insert the final GitHub URL + Zenodo DOIs once confirmed.
3. (Optional) Add a short "Code Availability" sentence in the main text if the journal style guide requires it.
