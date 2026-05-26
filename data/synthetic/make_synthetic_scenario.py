#!/usr/bin/env python3
"""
Generate a minimal valid combined barn scenario CSV for testing / CI / examples.

Produces a file with the historic column names and a plausible concentration field
(smooth background + one or more localised plumes) on the correct grid for a given LW.

Usage:
    python -m data.synthetic.make_synthetic_scenario --lw 4 --gas CO2 --out /tmp/test_LW4.csv
"""

import argparse
import numpy as np
import pandas as pd


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--lw", type=int, default=4, choices=[2, 3, 4])
    p.add_argument("--gas", type=str.upper, default="CO2", choices=["CO2", "NH3"])
    p.add_argument("--ny", type=int, default=50)
    p.add_argument("--out", type=str, required=True)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    rng = np.random.default_rng(args.seed)
    W = 100 * args.lw
    H = 100

    # Coordinates (meters, roughly matching historic ranges)
    x = np.linspace(-20 * args.lw, 20 * args.lw, W)
    y = np.linspace(0.39, 11.66, args.ny)
    z = np.linspace(-70, 70, H)

    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")  # shape (W, ny, H) after transpose later
    # Actually build row-major like the real data (Y outer, then Z, X)
    # Simpler: create flat and reshape at end

    # Plausible background + plumes
    base = 4e-6 if args.gas == "CO2" else 1e-7
    C = np.full((args.ny, W, H), base, dtype=np.float64)

    # Add a few Gaussian plumes (different heights for 3D interest)
    for cx, cy, cz, amp, sx, sy, sz in [
        (5 * args.lw, 3.0, 10, 3e-6, 8, 2, 15),
        (-8 * args.lw, 6.5, -25, 2e-6, 6, 3, 12),
    ]:
        for j in range(args.ny):
            for i in range(W):
                for k in range(H):
                    dx = x[i] - cx
                    dy = y[j] - cy
                    dz = z[k] - cz
                    C[j, i, k] += amp * np.exp(-(dx**2 / (2*sx**2) + dy**2 / (2*sy**2) + dz**2 / (2*sz**2)))

    C += rng.normal(0, base * 0.01, C.shape)

    # Build DataFrame in the order the loaders expect (sorted Y, Z, X)
    rows = []
    for j in range(args.ny):
        for k in range(H):
            for i in range(W):
                rows.append({
                    "X [ m ]": float(x[i]),
                    "Y [ m ]": float(y[j]),
                    "Z [ m ]": float(z[k]),
                    "Carbon Dioxide.Mass Fraction": float(C[j, i, k]) if args.gas == "CO2" else base * 0.1 + rng.normal(0, 1e-9),
                    "Ammonia Vapor.Mass Fraction": float(C[j, i, k]) if args.gas == "NH3" else base * 0.05 + rng.normal(0, 1e-9),
                    "Velocity u [ m s^-1 ]": 0.5 + rng.normal(0, 0.1),
                })

    df = pd.DataFrame(rows)
    df = df.sort_values(["Y [ m ]", "Z [ m ]", "X [ m ]"], kind="mergesort").reset_index(drop=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote synthetic LW{args.lw} {args.gas} scenario with {len(df)} points to {args.out}")


if __name__ == "__main__":
    main()
