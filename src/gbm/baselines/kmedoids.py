"""
k-medoids + projected value-subgradient baseline (stub — Phase 2).

Original implementation: src/search_in_2D/kmedoids_k_points_searcher.py
(and the 3D counterpart).

TODO: port the PAM-style k-medoids + refinement logic here, expose
find_optimal_k_points_kmedoids_2D / _3D with the same signature as GBM.

For now this file exists only to document the intended public API.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Optional, Tuple, List


def find_optimal_k_points_kmedoids_2D(
    nodes_df: pd.DataFrame,
    barn_inside_points: np.ndarray,
    k: int,
    in_CO2_avg: float,
    barn_section: float = 3.1500001,
    lr: float = 5e-7,
    epochs: int = 20,
    sampling_budget: int = 10000,
    neighborhood_numbers: int = 5,
    barn_LW_ratio: int = 2,
    **kwargs,
) -> Optional[Tuple[float, float, float, List[List[float]]]]:
    """Stub — see docstring in the 2D GBM implementation for the expected contract."""
    raise NotImplementedError("kmedoids baseline port is Phase 2 work in progress. "
                              "Use the original searcher from the BarnCSP checkout for now.")
