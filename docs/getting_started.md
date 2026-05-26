# Getting Started with GMB

## Installation (detailed)

```bash
# CPU-only (most common on laptops / shared clusters)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install gbm

# CUDA 12.1 example
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install gbm
```

## Synthetic smoke test (verifies your install)

```bash
python -c "
from gbm.core import find_optimal_k_points_gbm_2D
import pandas as pd, numpy as np
print('GMB import OK')
# (the test_gbm_core.py suite exercises a full synthetic run)
"
pytest tests/test_gbm_core.py -q --tb=line
```

## Next steps

- Browse `experiments/2d_co2/README.md` for the exact commands that reproduced the 2D CO₂ tables/figures.
- See `data/synthetic/` for the generator used by CI.
- Full 242-scenario BeLuVa dataset + all result JSONs: Zenodo (DOI listed in `data/README.md` — to be wired after user confirms the exact record).
