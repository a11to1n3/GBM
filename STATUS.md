# GMB Repository Status (for Paper Revision COMPAG-D-26-02203)

**Last updated:** 2026-05-26

## Core Deliverables
- Full GBM method implementation (2D + 3D D-1 pillars) in `src/gbm/core/`
- All 8 baselines with real code (most with 2D + 3D versions)
- Complete experiment family structure under `experiments/` (self-contained "mini-repos")
- Runnable examples in `examples/` (7 notebooks + scripts, strong 3D coverage)

## Reproducibility
- Seeds documented per experiment family
- Synthetic data generator + minimal real examples included
- Full reproduction instructions in per-family READMEs
- Data Availability text ready in `docs/paper_data_availability.tex`

## Paper Alignment
- Terminology standardized to "GBM" / "Gradient-Based Mapper" as used in the manuscript
- Data & Code Availability section matches paper claims
- Ready-to-paste LaTeX paragraph available

## Known Open Items (local)
- kmedoids_3D function has been appended to the baselines file
- Push to GitHub successful (https://github.com/a11to1n3/GBM)
- Add final Zenodo DOIs for full results when available

## Next for Paper Submission
1. Paste the paragraph from `docs/paper_data_availability.tex` into the manuscript / response letter
2. Add the final GitHub URL + any result DOIs
3. (Optional) Add a short "Code Availability" sentence in the main text if the journal requests it
