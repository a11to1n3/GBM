# GMB Release Checklist

Use this checklist before tagging a new release or paper submission snapshot.

## Code & Quality
- [ ] All 8 baselines have real, tested implementations (2D + 3D where applicable).
- [ ] Core GBM (2D + 3D) passes smoke tests on synthetic data.
- [ ] No remaining "stub", "Phase 2", or development TODOs in public-facing code/docs (except intentional lightweight CLI).
- [ ] `ruff check` and basic linting pass.

## Documentation
- [ ] Root README is accurate and professional.
- [ ] All experiment-family READMEs are up to date.
- [ ] `examples/README.md` lists current notebooks and scripts.
- [ ] `docs/reproducibility.md` and `docs/getting_started.md` are current.
- [ ] `CONTRIBUTING.md` exists and is reasonable.
- [ ] `CITATION.cff` is present and correct.
- [ ] `STATUS.md` (or equivalent) reflects the current state for the paper team.

## Reproducibility
- [ ] All experiment families have `seeds.txt`.
- [ ] Synthetic data generator works.
- [ ] `data/README.md` correctly describes Zenodo sources.
- [ ] Data Availability text in `docs/paper_data_availability.tex` is ready.

## Repository Hygiene
- [ ] `.gitignore` is up to date (nuclear policy for data/results/artifacts).
- [ ] No large binary files or results committed.
- [ ] Working tree is clean (`git status`).
- [ ] Recent commits have correct human authorship only.

## Release
- [ ] Bump version in `pyproject.toml` and `__init__.py` if needed.
- [ ] Create annotated tag: `git tag -a vX.Y.Z -m "Release notes..."`
- [ ] Push branch + tags.
- [ ] (Optional) Build and upload to PyPI: `python -m build && twine upload dist/*`

## Paper Submission
- [ ] Copy latest text from `docs/paper_data_availability.tex` into the manuscript.
- [ ] Insert final GitHub URL and Zenodo DOIs.
- [ ] Update `STATUS.md` with submission date if desired.
