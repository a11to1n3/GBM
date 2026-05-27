#!/usr/bin/env python3
"""
Runtime Benchmark Driver (clean port for the GBM repo).

Thin, reproducible timing harness for GBM and selected baselines on synthetic 3D (and 2D) volumes.

Usage (from the GBM repo root):
    python -m experiments.runtime_benchmark.run \
        --dim 3D \
        --k 5,10,20 \
        --repeats 3 \
        --out results/aggregates/runtime_smoke.json

The script times the clean public API (`gbm.core.*` and `gbm.baselines.*`) on synthetic data.
It is intended for quick regression checks and for reproducing the spirit of the published timing tables.

For the exact numbers that appear in the paper, the historical `bench_runtime*.py` + full Zenodo scenarios remain the reference.
"""

from __future__ import annotations

import argparse
import json
import time
from typing import Dict, List

import numpy as np
import pandas as pd

from gbm.core import find_optimal_k_points_gbm_3D, find_optimal_k_points_gbm_2D
from gbm.baselines import (
    greedy,
    uniform,
    kmedoids,
    random as random_search,
    simulated_annealing,
)


def _make_synthetic(lw: int, D: int = 16) -> tuple[pd.DataFrame, np.ndarray, float]:
    W, H = 100 * lw, 100
    x = np.linspace(-20 * lw, 20 * lw, W)
    y = np.linspace(0.4, 12, D)
    z = np.linspace(-70, 70, H)
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    C = 5e-6 + 4e-6 * np.exp(-((X)**2 + (Z)**2 + (Y - 6)**2) / 80)
    df = pd.DataFrame({"X": X.ravel(), "Y": Y.ravel(), "Z": Z.ravel(), "Carbon": C.ravel()})
    inside = np.ones(W * H * D, dtype=bool)
    return df, inside, float(C.mean())


def _time_one(fn, *args, **kwargs) -> float:
    t0 = time.perf_counter()
    fn(*args, **kwargs)
    return time.perf_counter() - t0


def main() -> None:
    parser = argparse.ArgumentParser(description="Runtime benchmark (clean GBM API)")
    parser.add_argument("--dim", default="3D", choices=["2D", "3D"])
    parser.add_argument("--k", default="5,10,20", help="Comma-separated k values")
    parser.add_argument("--repeats", type=int, default=3, help="Repeats per (method,k) for median timing")
    parser.add_argument("--out", default="results/aggregates/runtime_smoke.json")
    args = parser.parse_args()

    ks = [int(x) for x in args.k.split(",")]
    lw = 2
    df, inside, gmean = _make_synthetic(lw, D=12 if args.dim == "3D" else 1)

    methods: Dict[str, callable] = {}
    if args.dim == "3D":
        methods["GBM-XZ"] = lambda k: find_optimal_k_points_gbm_3D(df, inside, k, gmean, cross_section="XZ", barn_LW_ratio=lw, epochs=5, sampling_budget=2000)
        methods["Greedy"] = lambda k: greedy.find_optimal_k_points_greedy_3D(df, inside, k, gmean, barn_LW_ratio=lw)
        methods["KMC+GBO"] = lambda k: kmedoids.find_optimal_k_points_kmedoids_3D(df, inside, k, gmean, barn_LW_ratio=lw, downsample=1500)
        methods["Uniform"] = lambda k: uniform.find_optimal_k_points_uniform_grid_search_3D(df, inside, k, gmean, barn_LW_ratio=lw)
    else:
        methods["GBM-X"] = lambda k: find_optimal_k_points_gbm_2D(df, inside, k, gmean, cross_section="X", barn_LW_ratio=lw, epochs=5)
        methods["Greedy"] = lambda k: greedy.find_optimal_k_points_greedy_2D(df, inside, k, gmean, barn_LW_ratio=lw)
        methods["KMC+GBO"] = lambda k: kmedoids.find_optimal_k_points_kmedoids_2D(df, inside, k, gmean, barn_LW_ratio=lw)
        methods["Uniform"] = lambda k: uniform.find_optimal_k_points_uniform_grid_search_2D(df, inside, k, gmean, barn_LW_ratio=lw)

    results: Dict[str, Dict[int, List[float]]] = {name: {k: [] for k in ks} for name in methods}

    for name, fn in methods.items():
        for k in ks:
            times = []
            for _ in range(args.repeats):
                t = _time_one(fn, k)
                times.append(t)
            results[name][k] = times
            med = float(np.median(times))
            print(f"{name:12s} k={k:2d}  median={med:.3f}s  (repeats={args.repeats})")

    # Compact output (median seconds)
    compact = {}
    for name, per_k in results.items():
        compact[name] = {str(k): float(np.median(v)) for k, v in per_k.items()}

    import os
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump({"dim": args.dim, "times_median_s": compact, "repeats": args.repeats}, f, indent=2)

    print(f"\nSaved timing table to {args.out}")


if __name__ == "__main__":
    main()
