"""
Gradient-Based Mapper (GBM) — 2D implementation (single-axis coordinate projection).

This is the core of the method described in the companion paper
(Section 3 + Algorithm 1 + Appendix B).

Given a 2D monitoring plane (fixed Y = barn_section) inside a barn,
GBM:

1. Builds an overlapping interval cover on one coordinate axis (X or Z)
   using `split_range_with_overlap_percentage`.
2. Assigns every valid grid point to its (first) covering interval → regions.
3. For each region, maintains a "pool" of concentration values (1e9 sentinel outside).
4. Runs a short projected value-subgradient refinement (RMSprop on scalar targets
   with nearest-grid snapping) to minimise |mean(selected) − global_mean|.
5. Returns the best k-point set together with a local sensitivity estimate
   obtained by sampling neighbours around each selected point.

The 3D generalisation (D-1 pillars, GBM-XZ) lives in mapper_3d.py.
"""

from __future__ import annotations

import torch
import numpy as np
import pandas as pd
from typing import Optional, Tuple, List, Any

from ..utils import split_range_with_overlap_percentage, sample_neighboring_points_2D_fast


def find_optimal_k_points_gbm_2D(
    nodes_df: pd.DataFrame,
    barn_inside_points: np.ndarray,
    k: int,
    in_CO2_avg: float,
    cross_section: str = "X",
    barn_section: float = 3.1500001,
    overlap: float = 75.0,
    lr: float = 5e-7,
    epochs: int = 20,
    sampling_budget: int = 10000,
    neighborhood_numbers: int = 5,
    barn_LW_ratio: int = 2,
) -> Optional[Tuple[float, float, float, List[List[float]]]]:
    """
    Run GBM on a 2D horizontal monitoring plane.

    Parameters
    ----------
    nodes_df
        DataFrame with at least columns ["X", "Y", "Z", "Carbon"] (after renaming).
    barn_inside_points
        Boolean mask of the same flattened length as nodes_df indicating interior points.
    k
        Number of points / sensors to place.
    in_CO2_avg
        Target global mean (mean of "Carbon" over the interior mask).
    cross_section
        "X" or "Z" — the axis along which the Mapper cover is built.
    barn_section
        Exact Y value used to slice the 2D plane (the historic 3.1500001 m).
    overlap, lr, epochs
        GBM hyperparameters (see paper Appendix C for the values used in the reported runs).
    sampling_budget, neighborhood_numbers
        Budget and stencil size for the post-hoc local sensitivity analysis.
    barn_LW_ratio
        Length-to-width ratio (2, 3 or 4) — used to reshape the grid.

    Returns
    -------
    (best_loss, mean_sensitivity_loss, std_sensitivity_loss, positions)
    or None on failure (empty plane, malformed grid, etc.).

    Notes
    -----
    The implementation follows the "reported" path: pure coordinate projection
    + value-space subgradient (no DBSCAN, no outlier filtering).
    """
    if cross_section not in ("X", "Z"):
        raise ValueError(f"cross_section='{cross_section}' invalid for 2D GBM.")

    # --- Filter to the monitoring plane ---------------------------------
    inside_flat = barn_inside_points.flatten().astype(bool)
    at_height = nodes_df["Y"].values == barn_section
    plane_mask = inside_flat & at_height
    plane_df = nodes_df[plane_mask].reset_index(drop=True)
    n_pts = len(plane_df)
    if n_pts == 0:
        return None

    W, H_2d = 100 * barn_LW_ratio, 100
    X_arr = plane_df["X"].values
    Z_arr = plane_df["Z"].values
    C_arr = plane_df["Carbon"].values

    # --- Build overlapping interval cover (Mapper-style) ----------------
    ax_arr = X_arr if cross_section == "X" else Z_arr
    split_ranges = split_range_with_overlap_percentage(
        float(ax_arr.min()), float(ax_arr.max()), k, float(overlap)
    )

    # Vectorised region assignment (first match wins)
    cluster_id = np.full(n_pts, -1, dtype=np.int32)
    for j in range(k):
        lo, hi = split_ranges[j]
        mask = (ax_arr >= lo) & (ax_arr < hi) & (cluster_id == -1)
        cluster_id[mask] = j

    # --- Per-region pools (sentinel = 1e9 outside region) ---------------
    carbon_2d = C_arr.reshape(W, H_2d)
    pos_X = plane_df["X"].values.reshape(W, H_2d)
    pos_Z = plane_df["Z"].values.reshape(W, H_2d)

    cluster_mask = np.zeros((W, H_2d, k), dtype=bool)
    for j in range(k):
        pm = cluster_id == j
        if pm.any():
            idx = np.unravel_index(np.where(pm)[0], (W, H_2d))
            cluster_mask[idx[0], idx[1], j] = True

    cluster_pools = []
    for j in range(k):
        pool = carbon_2d.copy()
        pool[~cluster_mask[:, :, j]] = 1e9
        cluster_pools.append(pool)

    # --- Projected value-subgradient refinement -------------------------
    p_list: List[torch.Tensor] = []
    min_indices = np.zeros(k, dtype=np.int64)
    min_locs: List[List[int]] = []

    for ep in range(epochs):
        if ep == 0:
            for j in range(k):
                vals = cluster_pools[j][cluster_pools[j] < 1e9]
                init = float(np.median(vals)) if len(vals) > 0 else 0.0
                p_list.append(torch.tensor(init, requires_grad=True))
            opt = torch.optim.RMSprop(p_list, lr=lr)
            opt.zero_grad()
        else:
            for j in range(k):
                if p_list[j].grad is not None:
                    p_list[j].grad.data.zero_()

            for j in range(k):
                cp = cluster_pools[j].ravel()
                valid = cp < 1e9
                if not valid.any():
                    return None
                vi = np.where(valid)[0]
                vv = cp[vi]
                tgt = p_list[j].detach().numpy()
                tgt_j = tgt + tgt * np.random.rand() * 1e-4
                min_indices[j] = vi[np.argmin(np.abs(vv - tgt_j))]

            min_locs = [
                [int(min_indices[j]) // H_2d, int(min_indices[j]) % H_2d]
                for j in range(k)
            ]

            p_list = [
                torch.tensor(float(cluster_pools[j][ml[0], ml[1]]), requires_grad=True)
                for j, ml in enumerate(min_locs)
            ]
            opt = torch.optim.RMSprop(p_list, lr=lr)
            opt.zero_grad()

        s = torch.stack(p_list).sum()
        loss = torch.nn.functional.l1_loss(s / k, torch.tensor(float(in_CO2_avg)))
        loss.backward()
        opt.step()

    # Final positions (real coordinates)
    if not min_locs:
        # fallback: pick median of each pool
        min_locs = []
        for j in range(k):
            vals = cluster_pools[j][cluster_pools[j] < 1e9]
            if len(vals) == 0:
                return None
            # crude median index
            med = np.median(vals)
            idx = np.unravel_index(np.argmin(np.abs(carbon_2d - med)), carbon_2d.shape)
            min_locs.append([idx[0], idx[1]])

    min_pos = [
        [float(pos_X[ml[0], ml[1]]), float(pos_Z[ml[0], ml[1]])] for ml in min_locs
    ]

    # --- Local sensitivity via neighbour sampling -----------------------
    combo_arr = sample_neighboring_points_2D_fast(
        min_locs, neighborhood_numbers, W, H_2d, sampling_budget
    )
    vals = carbon_2d[combo_arr[:, :, 0], combo_arr[:, :, 1]]
    means = vals.mean(axis=1)
    loss_array = np.abs(means - in_CO2_avg)

    final_loss = float(loss.detach().cpu().numpy()) if "loss" in locals() else float("nan")
    return final_loss, float(loss_array.mean()), float(loss_array.std()), min_pos
