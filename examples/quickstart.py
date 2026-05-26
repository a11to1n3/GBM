#!/usr/bin/env python3
"""
GMB Quickstart Example (Python script version)

Demonstrates the core Gradient-Based Mapper (GBM) API using only synthetic data.
No external CFD files required.
"""

import numpy as np
import pandas as pd

from gbm.core import find_optimal_k_points_gbm_2D
from gbm.utils import factor_k_for_3D


def main():
    print("GMB Quickstart — Synthetic 2D Example")
    print("=" * 50)

    # 1. Create a simple synthetic 2D concentration field
    lw = 2
    W, H = 100 * lw, 100

    x = np.linspace(-20, 20, W)
    z = np.linspace(-10, 10, H)
    X, Z = np.meshgrid(x, z, indexing="ij")

    # Plausible field: background + one Gaussian plume
    C = 5e-6 + 3e-6 * np.exp(-((X)**2 + (Z)**2) / 50)

    df = pd.DataFrame({
        "X": X.ravel(),
        "Y": np.full(W * H, 3.1500001),
        "Z": Z.ravel(),
        "Carbon": C.ravel(),
    })

    inside = np.ones(W * H, dtype=bool)
    global_mean = float(C.mean())

    print(f"Grid: {W} x {H}  (LW={lw})")
    print(f"Global mean concentration: {global_mean:.3e}")

    # 2. Run GBM
    loss, mean_sens, std_sens, positions = find_optimal_k_points_gbm_2D(
        df,
        inside,
        k=5,
        in_CO2_avg=global_mean,
        cross_section="Z",           # or "X"
        barn_LW_ratio=lw,
        epochs=10,
        sampling_budget=1000,
    )

    print(f"\nBest 5-point loss:          {loss:.3e}")
    print(f"Sensitivity (mean ± std):   {mean_sens:.3e} ± {std_sens:.3e}")
    print("\nSelected sensor positions (x, z):")
    for i, (px, pz) in enumerate(positions, 1):
        print(f"  {i}: ({px:8.3f}, {pz:8.3f})")

    print("\nDone! For 3D examples and real data, see the experiment families in ../experiments/")


if __name__ == "__main__":
    main()
