"""
Greedy baseline (forward selection).

This is a clean port of the original greedy implementation.
It is often one of the strongest simple baselines.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional, Tuple, List

from ..utils import sample_neighboring_points_2D_fast, sample_neighboring_points_3D_fast


def find_optimal_k_points_greedy_2D(
    nodes_df: pd.DataFrame,
    barn_inside_points: np.ndarray,
    k: int,
    in_CO2_avg: float,
    barn_section: float = 3.1500001,
    sampling_budget: int = 10000,
    neighborhood_numbers: int = 5,
    barn_LW_ratio: int = 2,
) -> Optional[Tuple[float, float, float, List[List[float]]]]:
    """Greedy forward selection in 2D."""
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

    # Greedy selection: track running sum for incremental mean
    selected = []
    selected_vals = []
    running_sum = 0.0
    remaining = np.arange(n_pts)

    for _ in range(k):
        best_loss = float("inf")
        best_idx = -1
        best_val = 0.0
        n_sel = len(selected) + 1

        for idx in remaining:
            new_sum = running_sum + carbon_vals[idx]
            new_mean = new_sum / n_sel
            loss = abs(new_mean - in_CO2_avg)
            if loss < best_loss:
                best_loss = loss
                best_idx = idx
                best_val = carbon_vals[idx]

        selected.append(best_idx)
        selected_vals.append(best_val)
        running_sum += best_val
        remaining = remaining[remaining != best_idx]

    min_locs = [[idx // H_2d, idx % H_2d] for idx in selected]
    loss = abs(np.mean(selected_vals) - in_CO2_avg)

    # Sensitivity
    combo_arr = sample_neighboring_points_2D_fast(
        min_locs, neighborhood_numbers, W, H_2d, sampling_budget
    )
    vals = carbon_2d[combo_arr[:, :, 0], combo_arr[:, :, 1]]
    means = vals.mean(axis=1)
    loss_array = np.abs(means - in_CO2_avg)
    min_pos = [[float(pos_X[ml[0], ml[1]]), float(pos_Z[ml[0], ml[1]])] for ml in min_locs]

    return loss, float(loss_array.mean()), float(loss_array.std()), min_pos


def find_optimal_k_points_greedy_3D(
    nodes_df: pd.DataFrame,
    barn_inside_points: np.ndarray,
    k: int,
    in_CO2_avg: float,
    sampling_budget: int = 10000,
    neighborhood_numbers: int = 5,
    barn_LW_ratio: int = 2,
) -> Optional[Tuple[float, float, float, List[List[float]]]]:
    """Greedy forward selection in 3D."""
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

    # Greedy selection
    selected_flat = []
    running_sum = 0.0
    remaining = np.arange(n_pts)

    for step in range(k):
        best_loss = float("inf")
        best_local = -1
        best_val = 0.0
        n_sel = len(selected_flat) + 1

        for local_idx in remaining:
            new_sum = running_sum + carbon_vals[local_idx]
            loss = abs(new_sum / n_sel - in_CO2_avg)
            if loss < best_loss:
                best_loss = loss
                best_local = local_idx
                best_val = carbon_vals[local_idx]

        selected_flat.append(best_local)
        running_sum += best_val
        remaining = remaining[remaining != best_local]

    # Map to 3D positions
    selected_global = interior_indices[selected_flat]
    min_locs = np.unravel_index(selected_global, (W, H_img, D))
    min_locs = list(zip(min_locs[0], min_locs[1], min_locs[2]))

    selected_vals = carbon_vals[selected_flat]
    loss = abs(float(np.mean(selected_vals)) - in_CO2_avg)

    # Sensitivity
    combo_arr = sample_neighboring_points_3D_fast(
        min_locs, neighborhood_numbers, W, H_img, D, sampling_budget
    )
    vals = C_arr[combo_arr[:, :, 0], combo_arr[:, :, 1], combo_arr[:, :, 2]]
    means = vals.mean(axis=1)
    loss_array = np.abs(means - in_CO2_avg)
    min_pos = [[float(X_arr[ml[0], ml[1], ml[2]]),
                float(Y_arr[ml[0], ml[1], ml[2]]),
                float(Z_arr[ml[0], ml[1], ml[2]])] for ml in min_locs]

    return loss, float(loss_array.mean()), float(loss_array.std()), min_pos
