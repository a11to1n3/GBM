#!/usr/bin/env python3
"""
Statistical Analysis Driver (clean port for GMB repo).

Core logic for Wilcoxon signed-rank tests, Cliff's delta, and basic ranking
on the deployable-layout results.

This is a focused, self-contained version of the original statistical_analysis.py
and accuracy_table.py, adapted for the clean repo structure.

Usage:
    python -m experiments.statistical_analysis.compute \
        --deploy-json results/aggregates/deploy_results_all.json \
        --out results/aggregates/ranking_tables.tex
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import wilcoxon

# Method order (matches paper)
METHODS_3D = ["GBM-XZ", "KMC+GBO", "Greedy", "PSO", "SA", "Uniform", "Random"]
METHODS_2D = ["GBM-X", "GBM-Z", "KMC+GBO", "Greedy", "PSO", "SA", "Uniform", "Random"]


def load_deploy_matrix(path: str, gas_key: str, dim: str, k_key: str) -> Tuple[List[str], np.ndarray]:
    data = json.load(open(path))
    key = f"{dim} {gas_key}"
    if key not in data or k_key not in data[key]:
        raise ValueError(f"No data for {key} / {k_key}")
    raw = data[key][k_key]          # dict lw -> list of [name, mae, count]
    lws = sorted(raw.keys())
    methods = METHODS_3D if dim == "3D" else METHODS_2D
    m2i = {m: i for i, m in enumerate(methods)}
    mat = np.full((len(methods), len(lws)), np.nan)
    for j, lw in enumerate(lws):
        for name, mae, _ in raw[lw]:
            if name in m2i:
                mat[m2i[name], j] = mae
    return methods, mat


def cliff_delta(x: np.ndarray, y: np.ndarray) -> float:
    """Simple Cliff's delta (effect size)."""
    nx, ny = len(x), len(y)
    more = sum(xi > yj for xi in x for yj in y)
    less = sum(xi < yj for xi in x for yj in y)
    return (more - less) / (nx * ny)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--deploy-json", default="results/aggregates/deploy_results_all.json")
    parser.add_argument("--out", default="results/aggregates/ranking_tables.tex")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    lines = []
    lines.append("\\begin{table}[htbp]")
    lines.append("\\centering")
    lines.append("\\caption{Basic ranking summary from deployable MAE (example).}")
    lines.append("\\begin{tabular}{lrrrr}")
    lines.append("Method & Mean Rank (3D CO2) & Mean Rank (2D CO2) & ... \\\\")
    lines.append("\\hline")

    # Very simplified example (real version would do full Wilcoxon + CD)
    for dim, gas in [("3D", "CO2"), ("2D", "CO2")]:
        try:
            methods, mat = load_deploy_matrix(args.deploy_json, gas, dim, "k=10")
            ranks = np.nanmean(np.argsort(np.argsort(mat, axis=0), axis=0) + 1, axis=1)
            for m, r in zip(methods, ranks):
                lines.append(f"{m} & {r:.2f} & ... \\\\")
        except Exception as e:
            lines.append(f"% Skipped {dim} {gas}: {e}")

    lines.append("\\end{tabular}")
    lines.append("\\end{table}")

    with open(args.out, "w") as f:
        f.write("\n".join(lines))
    print(f"Saved example ranking table to {args.out}")
    print("For full Wilcoxon, Cliff's delta, and Nemenyi CD diagrams, see the original statistical_analysis.py and accuracy_table.py (ported logic can be added here).")


if __name__ == "__main__":
    main()
