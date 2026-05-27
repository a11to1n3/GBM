#!/usr/bin/env python3
"""
Deployable Layouts Driver (clean port for the GBM repo).

Core logic extracted and adapted from the original deploy_fixed_layout.py
and related scripts.

This script:
- Loads per-scenario position results for methods.
- Pools positions per (method, k, LW, gas, dim).
- Runs KMeans to produce one fixed layout per cell.
- Evaluates full-barn MAE (and plume-only for NH3).
- Produces a compact deploy_results matrix suitable for plotting/tables.

Usage (from the GMB repo root):
    python -m experiments.deployable_layouts.run \
        --results-root results \
        --k 5,10,20 \
        --out results/aggregates/deploy_results_all.json

The script is designed to work with either the full Zenodo result archive
or a small subset for development.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

# --- Configuration (can be moved to config/ later) ----------------------

K_VALUES = [5, 10, 20]

# Method name -> (directory in results/, suffix pattern)
# This mapping can be extended or made configurable.
M3D = [
    ("GBM-XZ", "tda-mapper", "3dXZ"),
    ("KMC+GBO", "kmedoids", "3d"),
    ("PSO", "PSO", "3d"),
    ("Greedy", "greedy", "3d"),
    ("Uniform", "uniform", "3d"),
    ("Random", "random", "3d"),
    ("SA", "simulated_annealing", "3d"),
    ("Genetic", "genetic", "3d"),
    ("MC", "Monte-Carlo", "3d"),
]

M2D = [
    ("GBM-X", "tda-mapper", "2dX"),
    ("GBM-Z", "tda-mapper", "2dZ"),
    ("KMC+GBO", "kmedoids", "2d"),
    ("PSO", "PSO", "2d"),
    ("Greedy", "greedy", "2d"),
    ("Uniform", "uniform", "2d"),
    ("Random", "random", "2d"),
    ("SA", "simulated_annealing", "2d"),
    ("Genetic", "genetic", "2d"),
    ("MC", "Monte-Carlo", "2d"),
]

TWO_D_HEIGHT = 3.1500001

# -----------------------------------------------------------------------


def load_positions(results_root: str, method_dir: str, suffix: str, k: int) -> Dict[str, List[List[float]]]:
    """Load k-point positions for one (method, suffix) from JSON files."""
    pattern = os.path.join(results_root, method_dir, f"*_{suffix}.json")
    data = {}
    for path in glob.glob(pattern):
        bn = os.path.basename(path).replace(".json", "")
        if bn.endswith(f"_{suffix}"):
            bn = bn[: -(len(suffix) + 1)]
        try:
            with open(path) as f:
                d = json.load(f)
            key = f"{k}-point"
            if key not in d:
                continue
            for kkey in d[key]:
                if "Point" in kkey and "Position" in kkey:
                    pts = d[key][kkey]
                    if pts and len(pts) >= k:
                        data[bn] = pts
                    break
        except Exception:
            pass
    return data


def load_scenario(csv_path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Optional[np.ndarray]]:
    """Minimal loader for evaluation (returns grids + concentration volumes)."""
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        "X [ m ]": "X",
        "Y [ m ]": "Y",
        "Z [ m ]": "Z",
        "Carbon Dioxide.Mass Fraction": "Carbon",
        "Ammonia Vapor.Mass Fraction": "Ammonia",
    })
    xs = np.sort(df["X"].unique()).astype(np.float32)
    ys = np.sort(df["Y"].unique()).astype(np.float32)
    zs = np.sort(df["Z"].unique()).astype(np.float32)
    df = df.sort_values(["Y", "Z", "X"], kind="mergesort")
    shape = (len(ys), len(zs), len(xs))
    C = df["Carbon"].values.astype(np.float32).reshape(shape)
    A = df["Ammonia"].values.astype(np.float32).reshape(shape) if "Ammonia" in df.columns else None
    return xs, ys, zs, C, A


def evaluate(
    positions: np.ndarray,
    scenario_names: List[str],
    scenarios: Dict[str, Tuple],
    target_idx: int,   # 3=CO2, 4=NH3
    is_3d: bool,
    plane_y: Optional[float] = None,
) -> Tuple[float, Optional[float]]:
    """Return (full_barn_MAE, plume_MAE or None)."""
    losses_full = []
    losses_plume = []

    for bn in scenario_names:
        if bn not in scenarios:
            continue
        xs, ys, zs, C, A = scenarios[bn]
        Cv = C if target_idx == 3 else A
        if Cv is None:
            continue

        t_full = float(np.mean(Cv))

        if target_idx == 4:  # NH3 plume
            thresh = np.max(Cv) * 0.01
            plume_mask = Cv > thresh
            t_plume = float(np.mean(Cv[plume_mask])) if plume_mask.sum() > 0 else t_full
        else:
            t_plume = None

        nearest = []
        plane_idx = int(np.abs(ys - plane_y).argmin()) if (not is_3d and plane_y is not None) else None

        for p in positions:
            if is_3d:
                ix = int(np.abs(xs - p[0]).argmin())
                iy = int(np.abs(ys - p[1]).argmin())
                iz = int(np.abs(zs - p[2]).argmin())
            else:
                ix = int(np.abs(xs - p[0]).argmin())
                iy = plane_idx
                iz = int(np.abs(zs - p[1]).argmin())
            nearest.append(float(Cv[iy, iz, ix]))

        pred = np.mean(nearest)
        losses_full.append(abs(pred - t_full))
        if t_plume is not None:
            losses_plume.append(abs(pred - t_plume))

    mae_full = float(np.mean(losses_full)) if losses_full else float("nan")
    mae_plume = float(np.mean(losses_plume)) if losses_plume else None
    return mae_full, mae_plume


def redistribute_y(centroids: np.ndarray, y_min: float, y_max: float) -> np.ndarray:
    """Spread Y coordinates evenly for NH3 3D plume coverage."""
    k = len(centroids)
    new = centroids.copy()
    order = np.argsort(centroids[:, 1])
    new_Y = np.linspace(y_min, y_max, k)
    for i, idx in enumerate(order):
        new[idx, 1] = new_Y[i]
    return new


def main():
    parser = argparse.ArgumentParser(description="Compute fixed deployable layouts (clean port)")
    parser.add_argument("--results-root", default="results", help="Directory containing method subdirs with JSONs")
    parser.add_argument("--k", default="5,10,20", help="Comma-separated k values")
    parser.add_argument("--out", default="results/aggregates/deploy_results_all.json", help="Output JSON")
    parser.add_argument("--scenarios", default="data/scenarios", help="Directory with scenario CSVs (for evaluation)")
    args = parser.parse_args()

    ks = [int(x) for x in args.k.split(",")]
    results_root = args.results_root
    scenarios_dir = args.scenarios

    print("Pre-loading scenario data for evaluation...", flush=True)
    scenarios = {}
    for cf in sorted(glob.glob(os.path.join(scenarios_dir, "*.csv"))):
        bn = os.path.basename(cf).replace(".csv", "")
        scenarios[bn] = load_scenario(cf)
    print(f"Loaded {len(scenarios)} scenarios", flush=True)

    print("Loading position data from results...", flush=True)
    all_pos: Dict[Tuple[str, str, int], Dict[str, List[List[float]]]] = {}

    for method_dir, sfx, k in [
        (m[1], m[2], kk) for m in (M3D + M2D) for kk in ks
    ]:
        key = (method_dir, sfx, k)
        if key not in all_pos:
            all_pos[key] = load_positions(results_root, method_dir, sfx, k)

    print("Computing deployable layouts...", flush=True)
    deploy: Dict[str, Dict[str, Dict[str, List]]] = {}

    for gas, target_idx, gas_label in [("CO2", 3, "CO2"), ("NH3", 4, "NH3")]:
        for dim_label, methods, is_3d in [("3D", M3D, True), ("2D", M2D, False)]:
            key = f"{dim_label} {gas_label}"
            deploy[key] = {}
            plane_y = None if is_3d else TWO_D_HEIGHT

            for k_val in ks:
                kkey = f"k={k_val}"
                deploy[key][kkey] = {}
                print(f"\n{'='*50} {key} k={k_val}", flush=True)

                gbm_sfx = "3dXZ" if is_3d else "2dX"
                if gas == "NH3":
                    gbm_sfx = gbm_sfx + "_NH3" if not gbm_sfx.endswith("_NH3") else gbm_sfx

                gbm_pos = all_pos.get(("tda-mapper", gbm_sfx, k_val), {})
                if not is_3d:
                    gbm_z = all_pos.get(("tda-mapper", "2dZ_NH3" if gas=="NH3" else "2dZ", k_val), {})
                    all_gbm = set(gbm_pos) | set(gbm_z)
                else:
                    all_gbm = set(gbm_pos)

                for lw in ["2", "3", "4"]:
                    bases = sorted([b for b in all_gbm if f"LW{lw}" in b and b in scenarios])
                    MIN_N = 3 if lw == "4" else 5
                    if len(bases) < MIN_N:
                        continue

                    cell_results = []
                    for name, md, msfx in methods:
                        method_sfx = msfx + "_NH3" if gas == "NH3" else msfx
                        pos_data = all_pos.get((md, method_sfx, k_val), {})

                        avail = sorted([b for b in bases if b in pos_data])
                        if len(avail) < MIN_N:
                            continue

                        all_pts = np.array([p for b in avail for p in pos_data[b]], dtype=np.float32)
                        km = KMeans(n_clusters=k_val, random_state=0, n_init=3).fit(all_pts)
                        centroids = km.cluster_centers_

                        # NH3 3D special handling
                        if target_idx == 4 and is_3d:
                            all_Y = []
                            for b in avail:
                                _, Y, _, _, A = scenarios[b]
                                if A is None:
                                    continue
                                thresh = np.max(A) * 0.01
                                y_mask = np.any(A > thresh, axis=(1, 2))
                                if y_mask.sum() > 0:
                                    all_Y.extend([Y[y_mask].min(), Y[y_mask].max()])
                            if all_Y:
                                y_min, y_max = min(all_Y), max(all_Y)
                                centroids = redistribute_y(centroids.copy(), y_min, y_max)

                        mae_full, mae_plume = evaluate(centroids, avail, scenarios, target_idx, is_3d, plane_y)
                        cell_results.append((name, mae_full, mae_plume, len(avail)))

                    if len(cell_results) < 2:
                        continue

                    cell_results.sort(key=lambda x: x[1])
                    deploy[key][kkey][lw] = [[n, mf, mp, c] for n, mf, mp, c in cell_results]

                    items = ", ".join(f"{n}={mf:.2e}" for n, mf, _, _ in cell_results[:3])
                    print(f"  LW{lw}: {items}", flush=True)

    # Save compact version
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    compact = {}
    for key, kvs in deploy.items():
        compact[key] = {}
        for kk, lws in kvs.items():
            compact[key][kk] = {}
            for lw, entries in lws.items():
                compact[key][kk][lw] = [[e[0], e[1], e[3]] for e in entries]  # name, full_mae, count

    with open(args.out, "w") as f:
        json.dump(compact, f, indent=2)

    print(f"\nSaved: {args.out}")
    print("Done.")


if __name__ == "__main__":
    main()
