"""Random sampling baseline - actual port."""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional, Tuple, List

from ..utils import sample_neighboring_points_2D_fast


def find_optimal_k_points_random_search_2D(
    nodes_df: pd.DataFrame,
    barn_inside_points: np.ndarray,
    k: int,
    in_CO2_avg: float,
    barn_section: float = 3.1500001,
    epochs: int = 1000,
    sampling_budget: int = 10000,
    neighborhood_numbers: int = 5,
    barn_LW_ratio: int = 2,
) -> Optional[Tuple[float, float, float, List[List[float]]]]:
    """Pure random search baseline (2D)."""
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

    best_loss = float("inf")
    best_indices = None

    for _ in range(epochs):
        indices = np.random.choice(n_pts, k, replace=False)
        vals = carbon_vals[indices]
        loss = abs(vals.mean() - in_CO2_avg)
        if loss < best_loss:
            best_loss = loss
            best_indices = indices

    if best_indices is None:
        return None

    min_locs = [[idx // H_2d, idx % H_2d] for idx in best_indices]

    combo_arr = sample_neighboring_points_2D_fast(min_locs, neighborhood_numbers, W, H_2d, sampling_budget)
    vals = carbon_2d[combo_arr[:, :, 0], combo_arr[:, :, 1]]
    means = vals.mean(axis=1)
    loss_array = np.abs(means - in_CO2_avg)

    min_pos = [[float(pos_X[ml[0], ml[1]]), float(pos_Z[ml[0], ml[1]])] for ml in min_locs]
    return best_loss, float(loss_array.mean()), float(loss_array.std()), min_pos


def find_optimal_k_points_random_search_3D(
    nodes_df: pd.DataFrame,
    barn_inside_points: np.ndarray,
    k: int,
    in_CO2_avg: float,
    epochs: int = 1000,
    sampling_budget: int = 10000,
    neighborhood_numbers: int = 5,
    barn_LW_ratio: int = 2,
) -> Optional[Tuple[float, float, float, List[List[float]]]]:
    """Random search baseline (3D) - actual port."""
    nodes_df[~barn_inside_points.flatten().astype(bool)] = 1e9

    depth = len(nodes_df["Carbon"].values.flatten()) // (100 * barn_LW_ratio * 100)
    carbon_map = nodes_df["Carbon"].values.reshape(100 * barn_LW_ratio, 100, depth)
    position_map = nodes_df[["X", "Y", "Z"]].values.reshape(100 * barn_LW_ratio, 100, depth, -1)

    valid_indices = np.argwhere(barn_inside_points.reshape(100 * barn_LW_ratio, 100, depth))

    best_loss = float("inf")
    best_points = None
    best_positions = None

    for _ in range(epochs):
        selected_indices = valid_indices[np.random.choice(len(valid_indices), size=k, replace=False)]
        selected_points = carbon_map[selected_indices[:, 0], selected_indices[:, 1], selected_indices[:, 2]]
        selected_positions = position_map[selected_indices[:, 0], selected_indices[:, 1], selected_indices[:, 2]]

        loss = np.abs(np.mean(selected_points) - in_CO2_avg)

        if loss < best_loss:
            best_loss = loss
            best_points = selected_points
            best_positions = selected_positions

    # Sensitivity (note: original used last selected, not best - preserving behavior)
    image_width, image_height, image_depth = 100 * barn_LW_ratio, 100, depth
    best_locs = selected_indices.tolist()

    combinations = sample_neighboring_points_3D(best_locs, neighborhood_numbers, image_width, image_height, image_depth, sampling_budget)
    losses = []
    for combination in combinations:
        p_sum = sum(carbon_map[y, x, z] for y, x, z in combination)
        losses.append(np.abs(p_sum / k - in_CO2_avg))

    return best_loss, np.mean(losses), np.std(losses), best_positions
