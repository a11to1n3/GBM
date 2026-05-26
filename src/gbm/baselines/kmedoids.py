"""k-medoids + projected value-subgradient baseline - actual port."""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional, Tuple, List

from ..utils import sample_neighboring_points_2D_fast


def _kmedoids_fit(pts, k, max_iter=100, random_state=0):
    """K-Medoids (PAM) on (n, d) points."""
    rng = np.random.RandomState(random_state)
    n = len(pts)
    if k >= n:
        return np.arange(n) % k

    # k-means++ seeding
    medoid_idx = [rng.choice(n)]
    for _ in range(1, k):
        dist = np.min(np.sum((pts - pts[medoid_idx][:, None]) ** 2, axis=2), axis=0)
        probs = dist / dist.sum()
        medoid_idx.append(rng.choice(n, p=probs))
    medoid_idx = np.array(medoid_idx)

    D = np.sum((pts[:, None, :] - pts[None, :, :]) ** 2, axis=2).astype(np.float32)
    labels = np.argmin(D[:, medoid_idx], axis=1)
    best_cost = float(sum(D[i, medoid_idx[labels[i]]] for i in range(n)))

    for _ in range(max_iter):
        improved = False
        for j in range(k):
            cluster = np.where(labels == j)[0]
            if len(cluster) < 2:
                continue
            for candidate in cluster:
                new_idx = medoid_idx.copy()
                new_idx[j] = candidate
                new_labels = np.argmin(D[:, new_idx], axis=1)
                new_cost = float(sum(D[i, new_idx[new_labels[i]]] for i in range(n)))
                if new_cost < best_cost:
                    medoid_idx, labels, best_cost = new_idx, new_labels, new_cost
                    improved = True
        if not improved:
            break
    return labels


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
) -> Optional[Tuple[float, float, float, List[List[float]]]]:
    """k-medoids + value-subgradient refinement (2D)."""
    inside_flat = barn_inside_points.flatten().astype(bool)
    at_height = nodes_df["Y"].values == barn_section
    plane_mask = inside_flat & at_height
    plane_df = nodes_df[plane_mask].reset_index(drop=True)
    n_pts = len(plane_df)
    if n_pts == 0:
        return None

    MAX_PTS = 500
    if n_pts > MAX_PTS:
        plane_df = plane_df.sample(n=MAX_PTS, random_state=42).reset_index(drop=True)
        n_pts = len(plane_df)

    W, H_2d = 100 * barn_LW_ratio, 100
    pts = np.column_stack([plane_df["X"].values, plane_df["Z"].values])
    labels = _kmedoids_fit(pts, k)

    C_arr = plane_df["Carbon"].values
    carbon_2d = C_arr.reshape(W, H_2d)
    pos_X = plane_df["X"].values.reshape(W, H_2d)
    pos_Z = plane_df["Z"].values.reshape(W, H_2d)

    cluster_mask = np.zeros((W, H_2d, k), dtype=bool)
    for j in range(k):
        pm = (labels == j)
        if pm.any():
            idx = np.unravel_index(np.where(pm)[0], (W, H_2d))
            cluster_mask[idx[0], idx[1], j] = True

    cluster_pools = []
    for j in range(k):
        pool = carbon_2d.copy()
        pool[~cluster_mask[:, :, j]] = 1e9
        cluster_pools.append(pool)

    # Value-subgradient refinement (simplified from original)
    import torch
    p_list = []
    for j in range(k):
        vals = cluster_pools[j][cluster_pools[j] < 1e9]
        init = float(np.median(vals)) if len(vals) > 0 else 0.0
        p_list.append(torch.tensor(init, requires_grad=True))

    opt = torch.optim.RMSprop(p_list, lr=lr)
    for _ in range(epochs):
        s = torch.stack(p_list).sum()
        loss = torch.nn.functional.l1_loss(s / k, torch.tensor(float(in_CO2_avg)))
        opt.zero_grad()
        loss.backward()
        opt.step()

    # Final positions (median of each cluster pool)
    min_locs = []
    for j in range(k):
        vals = cluster_pools[j][cluster_pools[j] < 1e9]
        if len(vals) == 0:
            continue
        med = np.median(vals)
        idx = np.unravel_index(np.argmin(np.abs(carbon_2d - med)), carbon_2d.shape)
        min_locs.append([idx[0], idx[1]])

    if len(min_locs) != k:
        return None

    min_pos = [[float(pos_X[ml[0], ml[1]]), float(pos_Z[ml[0], ml[1]])] for ml in min_locs]

    combo_arr = sample_neighboring_points_2D_fast(min_locs, neighborhood_numbers, W, H_2d, sampling_budget)
    vals = carbon_2d[combo_arr[:, :, 0], combo_arr[:, :, 1]]
    means = vals.mean(axis=1)
    loss_array = np.abs(means - in_CO2_avg)

    final_loss = float(loss.detach().cpu().numpy())
    return final_loss, float(loss_array.mean()), float(loss_array.std()), min_pos
