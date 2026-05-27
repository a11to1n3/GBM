#!/usr/bin/env python3
"""
Robustness Driver (clean port for the GBM repo).

Core logic adapted from the original robustness_analysis.py.

This script:
- Loads scenarios (real CSVs or synthetic on the fly for smoke tests).
- Performs N random 80/20 train/test splits.
- For each k and each split: runs GBM (and optionally selected baselines) on the train scenarios,
  pools the returned positions, and fits a single KMeans layout (random_state=0).
- Evaluates the resulting fixed layout on the held-out test scenarios (full-barn MAE).
- Aggregates mean/std test MAE across splits.

Usage (from the GBM repo root):
    # Smoke test on synthetic data (fast, no external files)
    python -m experiments.robustness.run --synthetic --n-splits 3 --k 5,10 --out results/aggregates/robustness_smoke.json

    # Real data (point at a directory containing a subset of the Zenodo combined scenario CSVs)
    python -m experiments.robustness.run \
        --data-dir data/scenarios \
        --dim 3D \
        --k 5,10,20 \
        --n-splits 5 \
        --out results/aggregates/robustness_3d.json

The script is designed to work with either the full Zenodo scenario set or a small development subset.
It uses the clean GBM public API (gbm.core + gbm.baselines).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

# --- Clean GBM imports -------------------------------------------------
from gbm.core import find_optimal_k_points_gbm_2D, find_optimal_k_points_gbm_3D
from gbm.data import load_barn_scenario


def _collect_positions(
    scenarios: List[Tuple[pd.DataFrame, np.ndarray, float, int]],
    dim: str,
    k: int,
    method: str = "gbm",
) -> List[List[float]]:
    """Run the chosen method on each scenario and return all selected positions."""
    positions: List[List[float]] = []
    for df, inside, co2_mean, lw in scenarios:
        if dim == "2D":
            fn = find_optimal_k_points_gbm_2D
            res = fn(df, inside, k, co2_mean, cross_section="X", barn_LW_ratio=lw, epochs=5)
        else:
            fn = find_optimal_k_points_gbm_3D
            res = fn(df, inside, k, co2_mean, cross_section="XZ", barn_LW_ratio=lw, epochs=5)
        if res is None:
            continue
        _, _, _, pts = res
        positions.extend(pts)
    return positions


def _evaluate_layout(
    centroids: np.ndarray,
    test_scenarios: List[Tuple[pd.DataFrame, np.ndarray, float, int]],
    dim: str,
) -> List[float]:
    """Nearest-grid MAE on each test scenario."""
    losses = []
    for df, inside, co2_mean, _ in test_scenarios:
        X = df["X"].values
        Y = df["Y"].values
        Z = df["Z"].values
        C = df["Carbon"].values
        inside_mask = inside.astype(bool)

        nearest = []
        for c in centroids:
            if dim == "3D":
                dist = (X - c[0])**2 + (Y - c[1])**2 + (Z - c[2])**2
            else:
                dist = (X - c[0])**2 + (Z - c[1])**2
            dist[~inside_mask] = 1e20
            idx = np.argmin(dist)
            nearest.append(float(C[idx]))
        losses.append(abs(np.mean(nearest) - co2_mean))
    return losses


def main() -> None:
    parser = argparse.ArgumentParser(description="Train/test robustness (clean port)")
    parser.add_argument("--data-dir", default=None, help="Directory with real scenario CSVs (optional)")
    parser.add_argument("--synthetic", action="store_true", help="Use synthetic scenarios instead of real data")
    parser.add_argument("--n-synthetic", type=int, default=8, help="Number of synthetic scenarios for smoke tests")
    parser.add_argument("--dim", default="3D", choices=["2D", "3D"])
    parser.add_argument("--k", default="5,10,20", help="Comma-separated k values")
    parser.add_argument("--n-splits", type=int, default=5, help="Number of 80/20 splits (20 in the paper)")
    parser.add_argument("--out", default="results/aggregates/robustness.json", help="Output JSON path")
    args = parser.parse_args()

    ks = [int(x) for x in args.k.split(",")]

    # --- Load or generate scenarios ------------------------------------
    scenarios: List[Tuple[pd.DataFrame, np.ndarray, float, int]] = []

    if args.synthetic:
        print(f"Generating {args.n_synthetic} synthetic scenarios (LW=2/3/4 mix)...")
        rng = np.random.default_rng(42)
        for i in range(args.n_synthetic):
            lw = rng.choice([2, 3, 4])
            # Tiny synthetic for speed
            W, H, D = 100 * lw, 100, 12
            x = np.linspace(-20 * lw, 20 * lw, W)
            y = np.linspace(0.4, 12, D)
            z = np.linspace(-70, 70, H)
            X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
            C = 5e-6 + 3e-6 * np.exp(-((X)**2 + (Z)**2 + (Y - 6)**2) / 80)
            C += rng.normal(0, 1e-8, C.shape)

            df = pd.DataFrame({
                "X": X.ravel(), "Y": Y.ravel(), "Z": Z.ravel(), "Carbon": C.ravel()
            })
            inside = np.ones(W * H * D, dtype=bool)
            co2_mean = float(C.mean())
            scenarios.append((df, inside, co2_mean, int(lw)))
    else:
        if not args.data_dir:
            print("ERROR: --data-dir is required when not using --synthetic", file=sys.stderr)
            sys.exit(1)
        print(f"Loading scenarios from {args.data_dir}...")
        for fn in sorted(os.listdir(args.data_dir)):
            if not fn.endswith(".csv"):
                continue
            path = os.path.join(args.data_dir, fn)
            try:
                df, inside, co2_mean, lw = load_barn_scenario(path, gas="CO2")
                scenarios.append((df, inside, co2_mean, lw))
            except Exception as e:
                print(f"  Skipped {fn}: {e}")
        print(f"Loaded {len(scenarios)} scenarios")

    if len(scenarios) < 4:
        print("ERROR: Need at least 4 scenarios for 80/20 splits", file=sys.stderr)
        sys.exit(1)

    results: Dict[str, Dict[str, List[float]]] = {str(k): {"test_mae": [], "test_std": []} for k in ks}

    n = len(scenarios)
    rng = np.random.default_rng(42)

    for split_i in range(args.n_splits):
        idx = rng.permutation(n)
        n_train = int(n * 0.8)
        train_idx = idx[:n_train]
        test_idx = idx[n_train:]

        train_sc = [scenarios[i] for i in train_idx]
        test_sc = [scenarios[i] for i in test_idx]

        for k in ks:
            pos = _collect_positions(train_sc, args.dim, k, method="gbm")
            if len(pos) < k:
                continue

            km = KMeans(n_clusters=k, random_state=0, n_init=3).fit(np.array(pos))
            centroids = km.cluster_centers_

            losses = _evaluate_layout(centroids, test_sc, args.dim)
            if losses:
                results[str(k)]["test_mae"].append(float(np.mean(losses)))
                results[str(k)]["test_std"].append(float(np.std(losses)))

        if (split_i + 1) % max(1, args.n_splits // 5) == 0:
            print(f"  Split {split_i+1}/{args.n_splits}")

    # Summarise
    summary = {}
    for k_str in results:
        maes = results[k_str]["test_mae"]
        if maes:
            summary[k_str] = {
                "mean_test_mae": float(np.mean(maes)),
                "std_test_mae": float(np.std(maes)),
                "n_splits": len(maes),
            }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nRobustness ({args.dim}, synthetic={args.synthetic}):")
    for k_str in sorted(summary.keys(), key=int):
        s = summary[k_str]
        print(f"  k={k_str:>3}: test_mae={s['mean_test_mae']:.2e} ± {s['std_test_mae']:.2e} ({s['n_splits']} splits)")
    print(f"Saved to {args.out}")


if __name__ == "__main__":
    main()
