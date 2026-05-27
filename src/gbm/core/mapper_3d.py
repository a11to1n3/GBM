"""
Gradient-Based Mapper (GBM) — 3D implementation (D-1 pillars / GBM-XZ).

This is the 3D generalisation of the method described in the companion paper
(Definition 2 + Theorem 1 + Appendix B).

Given a 3D volume inside a barn, GBM:
1. Uses `factor_k_for_3D` to choose k_x, k_z such that k_x * k_z ≈ k
   and k_x / k_z ≈ barn_LW_ratio (the D-1 construction). This produces
   vertical full-height pillars whose horizontal cross-section respects
   the barn geometry.
2. Builds overlapping interval covers on the chosen axes (X/Z or Z/X).
3. Assigns every valid grid point to its (first) covering pillar → regions.
4. For each pillar, maintains a "pool" of concentration values (1e9 sentinel
   outside the pillar).
5. Runs a short projected value-subgradient refinement (RMSprop on scalar
   targets with nearest-grid snapping and height-aware stratified
   percentile initialisation) to minimise |mean(selected) − global_mean|.
6. Returns the best k-point set together with a local sensitivity estimate
   obtained by sampling neighbours around each selected point using a
   26-neighbour stencil in 3D (via `sample_neighboring_points_3D_fast`).

The 2D version (single-axis coordinate projection) lives in mapper_2d.py.
"""

from __future__ import annotations

import torch
import numpy as np
import pandas as pd
from typing import Optional, Tuple, List

from ..utils import (
    split_range_with_overlap_percentage,
    factor_k_for_3D,
    sample_neighboring_points_3D_fast,
)


def _flat_to_3d(flat_idx: int, shape: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Convert a flat index into a (i, j, k) index for a 3D array of given shape."""
    i0 = flat_idx // (shape[1] * shape[2])
    rem = flat_idx % (shape[1] * shape[2])
    i1 = rem // shape[2]
    i2 = rem % shape[2]
    return i0, i1, i2


def find_optimal_k_points_gbm_3D(
    nodes_df: pd.DataFrame,
    barn_inside_points: np.ndarray,
    k: int,
    in_CO2_avg: float,
    cross_section: str = "XZ",
    overlap: float = 75.0,
    lr: float = 5e-7,
    epochs: int = 20,
    sampling_budget: int = 10000,
    neighborhood_numbers: int = 5,
    barn_LW_ratio: int = 2,
) -> Optional[Tuple[float, float, float, List[List[float]]]]:
    """
    Run GBM on a 3D volume using the D-1 pillar construction.

    Parameters
    ----------
    nodes_df
        DataFrame with at least columns ["X", "Y", "Z", "Carbon"] (after renaming).
        The grid must be a regular Cartesian product with shape (W, H, D) where
        W = 100 * barn_LW_ratio, H = 100 (or the historic Y-count).
    barn_inside_points
        Boolean mask of the same flattened length as nodes_df indicating interior points.
    k
        Number of points / sensors to place. For 3D this is the target composite k;
        the actual number of pillars is determined by `factor_k_for_3D`.
    in_CO2_avg
        Target global mean (mean of "Carbon" over the interior mask).
    cross_section
        "XZ" or "ZX" (D-1 pillars). Experimental "XYZ*" variants with forced
        height diversity are also accepted but fall back to XZ when k is odd
        or too small.
    overlap, lr, epochs
        GBM hyperparameters (see paper Appendix C for the values used in the
        reported runs).
    sampling_budget, neighborhood_numbers
        Budget and stencil size for the post-hoc local sensitivity analysis
        (26-neighbour stencil in 3D).
    barn_LW_ratio
        Length-to-width ratio (2, 3 or 4) — used both for grid reshaping and
        for the D-1 factorisation.

    Returns
    -------
    (best_loss, mean_sensitivity_loss, std_sensitivity_loss, positions)
    or None on failure (empty volume, malformed grid, etc.).

    Notes
    -----
    The implementation follows the "reported" path: pure coordinate projection
    (D-1 pillars) + value-space subgradient (no DBSCAN, no outlier filtering).
    Height-aware stratified percentile initialisation spreads sensors across
    the vertical (Y) axis inside each pillar.
    """
    # ── Partitioning axes (D-1 or experimental 3-axis) ─────────────────
    if cross_section in ("X", "Z"):
        n_axes, axes, k_parts = 1, [cross_section], [k]
    elif cross_section in ("XZ", "ZX"):
        k_x, k_z = factor_k_for_3D(k, barn_LW_ratio)
        if cross_section == "XZ":
            axes, k_parts = ["X", "Z"], [k_x, k_z]
        else:
            axes, k_parts = ["Z", "X"], [k_z, k_x]
        k = k_x * k_z
        n_axes = 2
    elif cross_section in ("XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX"):
        # Experimental 3-axis partitioning with forced Y-diversity.
        # Try k_y=2 when k is even; otherwise fall back to XZ.
        if k >= 4 and k % 2 == 0:
            k_y = 2
            k_rem = k // 2
            k_x, k_z = factor_k_for_3D(k_rem, barn_LW_ratio)
            if k_z > 1 or k_rem >= 2:
                k_parts = [k_x, k_y, k_z]
                axes = ["X", "Y", "Z"]
                k = k_x * k_y * k_z
                n_axes = 3
            else:
                k_x2, k_z2 = factor_k_for_3D(k, barn_LW_ratio)
                axes, k_parts = ["X", "Z"], [k_x2, k_z2]
                k = k_x2 * k_z2
                n_axes = 2
        else:
            k_x, k_z = factor_k_for_3D(k, barn_LW_ratio)
            axes, k_parts = ["X", "Z"], [k_x, k_z]
            k = k_x * k_z
            n_axes = 2
    else:
        raise ValueError(f"cross_section='{cross_section}' invalid for 3D GBM.")

    # ── Work on arrays only (never mutate caller DataFrame) ────────────
    inside_flat = barn_inside_points.flatten().astype(bool)
    W, H_img = 100 * barn_LW_ratio, 100
    n_total = len(nodes_df)
    if n_total % (W * H_img) != 0:
        return None
    D = n_total // (W * H_img)

    # Mask exterior to a huge sentinel inside a working copy of the concentration field
    C_arr = nodes_df["Carbon"].values.copy()
    C_arr[~inside_flat] = 1e9

    X_arr = nodes_df["X"].values
    Y_arr = nodes_df["Y"].values
    Z_arr = nodes_df["Z"].values

    # ── Build interval covers ──────────────────────────────────────────
    split_ranges = []
    for ax_idx in range(n_axes):
        ax = axes[ax_idx]
        vals = nodes_df.loc[nodes_df[ax] < 1e8, ax].values
        split_ranges.append(
            split_range_with_overlap_percentage(
                float(vals.min()), float(vals.max()), k_parts[ax_idx], float(overlap)
            )
        )

    # ── Pillar map ─────────────────────────────────────────────────────
    if n_axes == 1:
        pillar_map = [(i,) for i in range(k)]
    elif n_axes == 2:
        pillar_map = [
            (i, j) for i in range(k_parts[0]) for j in range(k_parts[1])
        ]
    else:
        pillar_map = [
            (i, j, l)
            for i in range(k_parts[0])
            for j in range(k_parts[1])
            for l in range(k_parts[2])
        ]

    # ── Vectorised pillar assignment ───────────────────────────────────
    cluster_id = np.full(n_total, -1, dtype=np.int32)
    for p_idx, indices in enumerate(pillar_map):
        mask = np.ones(n_total, dtype=bool)
        for ax_idx, ax in enumerate(axes):
            lo, hi = split_ranges[ax_idx][indices[ax_idx]]
            if ax == "X":
                mask &= (X_arr >= lo) & (X_arr < hi)
            elif ax == "Y":
                mask &= (Y_arr >= lo) & (Y_arr < hi)
            else:
                mask &= (Z_arr >= lo) & (Z_arr < hi)
        mask &= cluster_id == -1
        cluster_id[mask] = p_idx

    # ── Build per-pillar concentration pools (masked arrays) ───────────
    carbon_3d = C_arr.reshape(W, H_img, D)
    pos_X = X_arr.reshape(W, H_img, D)
    pos_Y = Y_arr.reshape(W, H_img, D)
    pos_Z = Z_arr.reshape(W, H_img, D)

    cluster_mask = np.zeros((W, H_img, D, k), dtype=bool)
    for p_idx in range(k):
        pm = cluster_id == p_idx
        if pm.any():
            idx = np.unravel_index(np.where(pm)[0], (W, H_img, D))
            cluster_mask[idx[0], idx[1], idx[2], p_idx] = True

    cluster_pools = []
    for p_idx in range(k):
        pool = carbon_3d.copy()
        pool[~cluster_mask[:, :, :, p_idx]] = 1e9
        cluster_pools.append(pool)

    # ── Projected value-subgradient refinement (height-aware init) ─────
    p_list: List[torch.Tensor] = []
    min_indices = np.zeros(k, dtype=np.int64)
    min_locs: List[Tuple[int, int, int]] = []

    for ep in range(epochs):
        if ep == 0:
            # Height-aware stratified initialisation: different percentiles
            # per pillar spread sensors across Y inside each pillar.
            for j in range(k):
                vals = cluster_pools[j][cluster_pools[j] < 1e9]
                if len(vals) == 0:
                    init = 0.0
                else:
                    pct = 100.0 * j / max(k - 1, 1)
                    init = float(np.percentile(vals, pct))
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
                _flat_to_3d(int(min_indices[j]), cluster_pools[j].shape)
                for j in range(k)
            ]

            p_list = [
                torch.tensor(
                    float(cluster_pools[j][ml[0], ml[1], ml[2]]),
                    requires_grad=True,
                )
                for j, ml in enumerate(min_locs)
            ]
            opt = torch.optim.RMSprop(p_list, lr=lr)
            opt.zero_grad()

        s = torch.stack(p_list).sum()
        loss = torch.nn.functional.l1_loss(s / k, torch.tensor(float(in_CO2_avg)))
        loss.backward()
        opt.step()

    # ── Final sensor positions (real coordinates) ──────────────────────
    if not min_locs:
        # Fallback: pick median of each pool
        min_locs = []
        for j in range(k):
            vals = cluster_pools[j][cluster_pools[j] < 1e9]
            if len(vals) == 0:
                return None
            med = np.median(vals)
            flat_idx = np.argmin(np.abs(cluster_pools[j].ravel() - med))
            min_locs.append(_flat_to_3d(flat_idx, cluster_pools[j].shape))

    min_pos = [
        [float(pos_X[ml[0], ml[1], ml[2]]),
         float(pos_Y[ml[0], ml[1], ml[2]]),
         float(pos_Z[ml[0], ml[1], ml[2]])]
        for ml in min_locs
    ]

    # ── Local sensitivity via 26-neighbour sampling in 3D ──────────────
    combo_arr = sample_neighboring_points_3D_fast(
        min_locs, neighborhood_numbers, W, H_img, D, sampling_budget
    )  # (n_combos, k, 3) int32
    vals = carbon_3d[combo_arr[:, :, 0], combo_arr[:, :, 1], combo_arr[:, :, 2]]
    means = vals.mean(axis=1)
    loss_array = np.abs(means - in_CO2_avg)

    final_loss = float(loss.detach().cpu().numpy()) if "loss" in locals() else float("nan")
    return final_loss, float(loss_array.mean()), float(loss_array.std()), min_pos
