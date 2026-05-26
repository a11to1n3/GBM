"""
Minimal smoke tests for the extracted GMB core (no external CFD data required).
"""

import numpy as np
import pandas as pd
import pytest

from gbm.core import find_optimal_k_points_gbm_2D
from gbm.utils import factor_k_for_3D, split_range_with_overlap_percentage


def make_synthetic_2d_plane(lw: int = 2, noise: float = 1e-8) -> tuple:
    """Create a tiny plausible 2D concentration field on a regular grid."""
    W, H = 100 * lw, 100
    # Create a smooth gradient + a localised plume
    x = np.linspace(0, 10 * lw, W)
    z = np.linspace(0, 10, H)
    X, Z = np.meshgrid(x, z, indexing="ij")
    C = 5e-6 + 2e-6 * np.exp(-((X - 5 * lw) ** 2 + (Z - 5) ** 2) / 8)  # plume
    C = C + noise * np.random.randn(*C.shape)

    # Build DataFrame in the historic column order
    df = pd.DataFrame(
        {
            "X": X.ravel(),
            "Y": np.full(W * H, 3.1500001),
            "Z": Z.ravel(),
            "Carbon": C.ravel(),
        }
    )
    # All points considered "inside" for the synthetic test
    inside = np.ones(W * H, dtype=bool)
    global_mean = float(C.mean())
    return df, inside, global_mean, lw


def test_gbm_2d_runs_on_synthetic():
    df, inside, gmean, lw = make_synthetic_2d_plane(lw=2)
    res = find_optimal_k_points_gbm_2D(
        df,
        inside,
        k=3,
        in_CO2_avg=gmean,
        cross_section="Z",
        barn_LW_ratio=lw,
        epochs=5,           # short for speed
        sampling_budget=200,
    )
    assert res is not None
    loss, mean_sens, std_sens, pos = res
    assert len(pos) == 3
    assert all(len(p) == 2 for p in pos)
    assert 0 < mean_sens < 1e-3   # sanity: sensitivity loss is small on smooth field


def test_factor_k_for_3d():
    assert factor_k_for_3D(8, 4.0) in [(4, 2), (2, 4)]
    assert factor_k_for_3D(7, 2.0) == (7, 1)  # prime fallback


def test_split_cover():
    iv = split_range_with_overlap_percentage(0, 100, 4, 50)
    assert len(iv) == 4
    assert iv[0][0] == 0
    assert iv[-1][1] == 100
