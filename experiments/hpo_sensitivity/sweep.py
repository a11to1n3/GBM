#!/usr/bin/env python3
"""
HPO / Sensitivity Sweep Driver (clean port for the GBM repo).

Thin grid sweep over GBM hyperparameters (overlap, lr, epochs) on synthetic data.

This is the clean equivalent of the spirit of the original sensitivity_analysis.py and the grid part of hpo.py.
It uses only the modern GBM public API and the synthetic generator — no SMAC3, no old searchers.

Usage:
    python -m experiments.hpo_sensitivity.sweep \
        --dim 3D \
        --k 5,10 \
        --out results/aggregates/sensitivity_smoke.json

For full SMAC3 HPO on the real 242-scenario set, the historical scripts + Zenodo archives remain the reference for the published numbers.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Dict, List

import numpy as np
import pandas as pd

from gbm.core import find_optimal_k_points_gbm_3D, find_optimal_k_points_gbm_2D


def _make_synthetic(lw: int = 2, D: int = 12) -> tuple[pd.DataFrame, np.ndarray, float]:
    W, H = 100 * lw, 100
    x = np.linspace(-20 * lw, 20 * lw, W)
    y = np.linspace(0.4, 12, D)
    z = np.linspace(-70, 70, H)
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    C = 5e-6 + 4e-6 * np.exp(-((X)**2 + (Z)**2 + (Y - 6)**2) / 80)
    df = pd.DataFrame({"X": X.ravel(), "Y": Y.ravel(), "Z": Z.ravel(), "Carbon": C.ravel()})
    inside = np.ones(W * H * D, dtype=bool)
    return df, inside, float(C.mean())


def main() -> None:
    parser = argparse.ArgumentParser(description="GBM hyperparameter grid sweep (clean API)")
    parser.add_argument("--dim", default="3D", choices=["2D", "3D"])
    parser.add_argument("--k", default="5,10", help="Comma-separated k values")
    parser.add_argument("--out", default="results/aggregates/sensitivity_smoke.json")
    args = parser.parse_args()

    ks = [int(x) for x in args.k.split(",")]
    df, inside, gmean = _make_synthetic()

    sweeps: Dict[str, List] = {
        "overlap": [30, 50, 75, 85],
        "lr": [1e-7, 5e-7, 1e-6],
        "epochs": [5, 10, 20],
    }

    results: Dict[str, Dict] = {}

    for param, values in sweeps.items():
        print(f"\n--- {param} ---")
        pr = {}
        for val in values:
            losses = []
            for k in ks:
                kwargs = {"cross_section": "XZ" if args.dim == "3D" else "X",
                          "barn_LW_ratio": 2, "epochs": 8, "sampling_budget": 1500}
                if param == "overlap":
                    kwargs["overlap"] = val
                elif param == "lr":
                    kwargs["lr"] = val
                elif param == "epochs":
                    kwargs["epochs"] = val

                if args.dim == "3D":
                    res = find_optimal_k_points_gbm_3D(df, inside, k, gmean, **kwargs)
                else:
                    res = find_optimal_k_points_gbm_2D(df, inside, k, gmean, **kwargs)
                if res:
                    losses.append(res[1])  # mean sensitivity loss
            mean_loss = float(np.mean(losses)) if losses else None
            pr[str(val)] = {"mean_sens_loss": mean_loss, "n": len(losses)}
            print(f"  {param}={val}: mean_sens={mean_loss}")
        results[param] = pr

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump({"dim": args.dim, "k": ks, "sweeps": results}, f, indent=2)

    print(f"\nSaved sensitivity sweep to {args.out}")


if __name__ == "__main__":
    main()
