"""Uniform grid baseline - actual port (cleaned, 2D + 3D)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional, Tuple, List

from ..utils import sample_neighboring_points_2D_fast, sample_neighboring_points_3D_fast


def find_optimal_k_points_uniform_grid_search_2D(
    nodes_df: pd.DataFrame,
    barn_inside_points: np.ndarray,
    k: int,
    in_CO2_avg: float,
    barn_section: float = 3.1500001,
    grid_size: int = 5,
    max_subset_evals: int = 5000,
    sampling_budget: int = 10000,
    neighborhood_numbers: int = 5,
    barn_LW_ratio: int = 2,
) -> Optional[Tuple[float, float, float, List[List[float]]]]:
    """Uniform coarse grid + random subset selection (2D)."""
    inside_flat = barn_inside_points.flatten().astype(bool)
    at_height = nodes_df["Y"].values == barn_section
    plane_mask = inside_flat & at_height
    plane_df = nodes_df[plane_mask].reset_index(drop=True)
    n_pts = len(plane_df)
    if n_pts == 0:
        return None

    W, H_2d = 100 * barn_LW_ratio, 100
    carbon_vals = plane_df["Carbon"].values.astype(np.float64)
    pos_X = plane_df["X"].values.reshape(W, H_2d)
    pos_Z = plane_df["Z"].values.reshape(W, H_2d)
    carbon_2d = carbon_vals.reshape(W, H_2d)

    step_x = max(1, W // grid_size)
    step_z = max(1, H_2d // grid_size)
    coarse_indices = []
    for i in range(0, W, step_x):
        for j in range(0, H_2d, step_z):
            flat = i * H_2d + j
            if flat < n_pts:
                coarse_indices.append(flat)

    if len(coarse_indices) < k:
        coarse_indices = list(range(n_pts))

    best_loss = float("inf")
    best_sel = None
    rng = np.random.default_rng(42)

    for _ in range(max_subset_evals):
        sel = rng.choice(coarse_indices, size=k, replace=False)
        loss = abs(carbon_vals[sel].mean() - in_CO2_avg)
        if loss < best_loss:
            best_loss = loss
            best_sel = sel

    if best_sel is None:
        return None

    min_locs = [[idx // H_2d, idx % H_2d] for idx in best_sel]
    combo_arr = sample_neighboring_points_2D_fast(min_locs, neighborhood_numbers, W, H_2d, sampling_budget)
    vals = carbon_2d[combo_arr[:, :, 0], combo_arr[:, :, 1]]
    means = vals.mean(axis=1)
    loss_array = np.abs(means - in_CO2_avg)
    min_pos = [[float(pos_X[ml[0], ml[1]]), float(pos_Z[ml[0], ml[1]])] for ml in min_locs]
    return best_loss, float(loss_array.mean()), float(loss_array.std()), min_pos


def find_optimal_k_points_uniform_grid_search_3D(
    nodes_df: pd.DataFrame,
    barn_inside_points: np.ndarray,
    k: int,
    in_CO2_avg: float,
    grid_size: int = 4,
    max_subset_evals: int = 2000,
    sampling_budget: int = 10000,
    neighborhood_numbers: int = 5,
    barn_LW_ratio: int = 2,
) -> Optional[Tuple[float, float, float, List[List[float]]]]:
    """Uniform coarse grid + random subset (3D) - simplified port."""
    nodes_df.loc[~barn_inside_points.flatten().astype(bool), :] = 1e9
    n_total = len(nodes_df)
    W, H_img = 100 * barn_LW_ratio, 100
    if n_total % (W * H_img) != 0:
        return None
    D = n_total // (W * H_img)

    interior_mask = nodes_df["X"] < 1e8
    carbon_vals = nodes_df.loc[interior_mask, "Carbon"].values.astype(np.float64)
    interior_indices = np.where(interior_mask)[0]
    n_pts = len(carbon_vals)
    if n_pts < k:
        return None

    C_arr = nodes_df["Carbon"].values.reshape(W, H_img, D)
    X_arr = nodes_df["X"].values.reshape(W, H_img, D)
    Y_arr = nodes_df["Y"].values.reshape(W, H_img, D)
    Z_arr = nodes_df["Z"].values.reshape(W, H_img, D)

    # Very coarse 3D grid
    step = max(1, int((n_pts ** (1/3)) / grid_size))
    coarse = list(range(0, n_pts, step))
    if len(coarse) < k:
        coarse = list(range(n_pts))

    best_loss = float("inf")
    best_sel = None
    rng = np.random.default_rng(42)

    for _ in range(max_subset_evals):
        sel_local = rng.choice(coarse, size=k, replace=False)
        sel_global = interior_indices[sel_local]
        loss = abs(carbon_vals[sel_local].mean() - in_CO2_avg)
        if loss < best_loss:
            best_loss = loss
            best_sel = sel_global

    if best_sel is None:
        return None

    min_locs = [tuple(np.unravel_index(idx, (W, H_img, D))) for idx in best_sel]
    combo_arr = sample_neighboring_points_3D_fast(min_locs, neighborhood_numbers, W, H_img, D, sampling_budget)
    vals = C_arr[combo_arr[:, :, 0], combo_arr[:, :, 1], combo_arr[:, :, 2]]
    means = vals.mean(axis=1)
    loss_array = np.abs(means - in_CO2_avg)
    min_pos = [[float(X_arr[ml[0], ml[1], ml[2]]), float(Y_arr[ml[0], ml[1], ml[2]]), float(Z_arr[ml[0], ml[1], ml[2]])] for ml in min_locs]
    return best_loss, float(loss_array.mean()), float(loss_array.std()), min_pos
