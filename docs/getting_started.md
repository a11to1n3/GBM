# Getting Started with GMB

## Installation

```bash
# CPU-only (recommended for most laptops and shared clusters)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install gbm

# With extras
pip install "gbm[plotting,hpo,dev]"
```

See `pyproject.toml` for the exact torch version requirement (hard dependency).

## Quick verification (no real data needed)

```bash
python -c "
from gbm.core import find_optimal_k_points_gbm_2D
from gbm.utils import factor_k_for_3D
print('GMB core import OK')
print('factor_k_for_3D(8,4)=', factor_k_for_3D(8, 4.0))
"
pytest tests/test_gbm_core.py -q
```

## Next steps for reproduction

1. Read the experiment family README that matches the figure/table you care about (e.g. `experiments/deployable_layouts/README.md`).
2. Use the small real examples in `data/examples/` or generate more with `data/synthetic/make_synthetic_scenario.py`.
3. Full 242-scenario data + all result JSONs are on Zenodo (DOIs in `data/README.md` and the family READMEs).

## Cluster / CUDA notes
Most heavy runs were performed with CUDA-enabled torch on SLURM nodes. The code itself is small — the data volume is the main resource consumer.

## Legacy barnCSP.py shim
During the transition you can still import the old modules from the original BarnCSP checkout if you need to reproduce an exact old result. New work should use the clean `gbm.*` API.
