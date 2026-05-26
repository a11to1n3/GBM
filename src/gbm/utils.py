"""
GMB (Gradient-Based Mapper) — Shared utilities.

This module contains the low-level helpers used by the core GBM method
and the comparison baselines:

- Overlapping interval cover construction (Mapper-style coordinate projection)
- D-1 pillar factorisation for 3D (k_x × k_z ≈ k respecting L/W ratio)
- Fast vectorised neighbour sampling for local sensitivity analysis

References
----------
The mathematical background (D-1 coordinate Mapper cover, π_A projection,
projected value-subgradient heuristic) is given in the companion paper
(Section 3 and Appendix B).
"""

import numpy as np
from itertools import product
import random
from typing import List, Tuple, Sequence


def split_range_with_overlap_percentage(
    range_min: float,
    range_max: float,
    num_parts: int,
    overlap_percentage: float,
    verbose: bool = False,
) -> List[Tuple[float, float]]:
    """
    Split a 1D range into `num_parts` overlapping intervals.

    The overlap is expressed as a percentage of the non-overlapping part length.
    This produces the coordinate-projection "Mapper cover" used by GBM.

    Parameters
    ----------
    range_min, range_max
        Bounds of the axis (e.g. X or Z coordinates after filtering to the barn).
    num_parts
        Number of intervals (usually = k for 1-axis GBM or k_x / k_z for D-1).
    overlap_percentage
        e.g. 75 for 75 % overlap (the value used in the reported experiments).
    verbose
        Print debug info.

    Returns
    -------
    List of (lo, hi) tuples.
    """
    total_length = range_max - range_min
    part_length_without_overlap = total_length / num_parts
    overlap_length = part_length_without_overlap * overlap_percentage / 100.0

    if verbose:
        print(total_length, part_length_without_overlap, overlap_length)

    split_ranges = []
    for i in range(num_parts):
        if i != 0 and i != (num_parts - 1):
            split_ranges.append(
                (
                    range_min + part_length_without_overlap * i - overlap_length,
                    range_min + part_length_without_overlap * (i + 1) + overlap_length,
                )
            )
        elif i == 0:
            split_ranges.append(
                (
                    range_min,
                    range_min + part_length_without_overlap * (i + 1) + overlap_length,
                )
            )
        else:
            split_ranges.append(
                (
                    range_min + part_length_without_overlap * i - overlap_length,
                    range_max,
                )
            )
    return split_ranges


def factor_k_for_3D(k: int, lw_ratio: float) -> Tuple[int, int]:
    """
    Choose k_x, k_z such that k_x * k_z ≈ k and k_x / k_z ≈ lw_ratio.

    This is the core of the D-1 generalisation used in 3D GBM-XZ:
    the longer barn axis (X) receives more partitions than the shorter (Z),
    producing "pillars" whose horizontal cross-section respects the barn geometry.

    For prime k the routine falls back to (k, 1) — single-axis partitioning.

    Parameters
    ----------
    k
        Desired total number of pillars / sensors.
    lw_ratio
        Length-to-width ratio of the barn (parsed from filename, e.g. 4 for LW4).

    Returns
    -------
    (k_x, k_z)
    """
    best = (k, 1)
    best_diff = float("inf")
    for kx in range(1, int(k ** 0.5) + 1):
        if k % kx == 0:
            kz = k // kx
            # Try both orientations
            diff = abs(kx / kz - lw_ratio)
            if diff < best_diff:
                best_diff = diff
                best = (kx, kz)
            diff2 = abs(kz / kx - lw_ratio)
            if diff2 < best_diff:
                best_diff = diff2
                best = (kz, kx)
    return best


# ---------------------------------------------------------------------------
# Neighbour sampling (used for local sensitivity / robustness)
# ---------------------------------------------------------------------------

def sample_neighboring_points_2D_fast(
    k_points: Sequence[Sequence[int]],
    n: int,
    image_width: int,
    image_height: int,
    budget: int = 2000,
) -> np.ndarray:
    """
    Fast vectorised 8-neighbour sampling around each of the k points.

    Returns a numpy array of shape (n_combos, k, 2) of integer grid indices.
    Used by GBM (and several baselines) to compute mean/std loss under small
    perturbations without enumerating the full combinatorial explosion.
    """
    offsets = np.array(
        [[dx, dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)],
        dtype=np.int32,
    )

    k = len(k_points)
    kpts = np.array(k_points, dtype=np.int32)
    all_candidates = kpts[:, None, :] + offsets[None, :, :]

    bounds = np.array([image_width, image_height], dtype=np.int32)
    valid = (
        (all_candidates[:, :, 0] >= 0)
        & (all_candidates[:, :, 0] < bounds[0])
        & (all_candidates[:, :, 1] >= 0)
        & (all_candidates[:, :, 1] < bounds[1])
    )

    neighbor_pools = []
    for j in range(k):
        v = all_candidates[j][valid[j]][:n]
        if len(v) == 0:
            v = kpts[j : j + 1]
        neighbor_pools.append(v)

    pool_sizes = [len(p) for p in neighbor_pools]
    total = int(np.prod(pool_sizes))

    if total <= budget and total > 0 and len(pool_sizes) <= 32:
        grids = np.meshgrid(*[np.arange(s) for s in pool_sizes], indexing="ij")
        all_indices = np.stack([g.ravel() for g in grids], axis=1)
    else:
        all_indices = np.stack(
            [np.random.randint(0, s, budget) for s in pool_sizes], axis=1
        )

    result = np.zeros((len(all_indices), k, 2), dtype=np.int32)
    for j in range(k):
        result[:, j, :] = neighbor_pools[j][all_indices[:, j]]
    return result


def sample_neighboring_points_3D_fast(
    k_points: Sequence[Sequence[int]],
    n: int,
    image_width: int,
    image_height: int,
    image_depth: int,
    budget: int = 2000,
) -> np.ndarray:
    """3D analogue of the above (26-neighbour stencil)."""
    offsets = np.array(
        [
            [dx, dy, dz]
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            for dz in (-1, 0, 1)
            if not (dx == 0 and dy == 0 and dz == 0)
        ],
        dtype=np.int32,
    )

    k = len(k_points)
    kpts = np.array(k_points, dtype=np.int32)
    all_candidates = kpts[:, None, :] + offsets[None, :, :]

    bounds = np.array([image_width, image_height, image_depth], dtype=np.int32)
    valid = (
        (all_candidates[:, :, 0] >= 0)
        & (all_candidates[:, :, 0] < bounds[0])
        & (all_candidates[:, :, 1] >= 0)
        & (all_candidates[:, :, 1] < bounds[1])
        & (all_candidates[:, :, 2] >= 0)
        & (all_candidates[:, :, 2] < bounds[2])
    )

    neighbor_pools = []
    for j in range(k):
        v = all_candidates[j][valid[j]][:n]
        if len(v) == 0:
            v = kpts[j : j + 1]
        neighbor_pools.append(v)

    pool_sizes = [len(p) for p in neighbor_pools]
    total = int(np.prod(pool_sizes))

    if total <= budget and total > 0 and len(pool_sizes) <= 32:
        grids = np.meshgrid(*[np.arange(s) for s in pool_sizes], indexing="ij")
        all_indices = np.stack([g.ravel() for g in grids], axis=1)
    else:
        all_indices = np.stack(
            [np.random.randint(0, s, budget) for s in pool_sizes], axis=1
        )

    result = np.zeros((len(all_indices), k, 3), dtype=np.int32)
    for j in range(k):
        result[:, j, :] = neighbor_pools[j][all_indices[:, j]]
    return result


# Legacy / convenience aliases (kept for back-compat during transition)
sample_neighboring_points_2D = sample_neighboring_points_2D_fast
sample_neighboring_points_3D = sample_neighboring_points_3D_fast
