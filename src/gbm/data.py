"""
Centralised data loading and barn-interior masking for GBM.

All experiment scripts should eventually go through the functions here
instead of duplicating the barn_inside heuristic + CSV renaming logic.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Tuple


def load_barn_scenario(
    csv_path: str,
    gas: str = "CO2",
    lw_from_filename: bool = True,
) -> Tuple[pd.DataFrame, np.ndarray, float, int]:
    """
    Load a combined scenario CSV and return (nodes_df, barn_inside_mask, global_mean, lw_ratio).

    This is the single source of truth for the historic barn_inside heuristic.
    """
    df = pd.read_csv(csv_path)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    df.columns = [c.strip() for c in df.columns]

    # Column renaming (historic convention)
    rename_map = {
        "X [ m ]": "X",
        "Y [ m ]": "Y",
        "Z [ m ]": "Z",
    }
    if gas.upper() == "CO2":
        rename_map["Carbon Dioxide.Mass Fraction"] = "Carbon"
    else:
        rename_map["Ammonia Vapor.Mass Fraction"] = "Carbon"

    df = df.rename(columns=rename_map)
    df = df.sort_values(["Y", "Z", "X"], kind="mergesort").reset_index(drop=True)

    # LW ratio
    lw_ratio = 2
    if lw_from_filename:
        for token in csv_path.split("_"):
            if token.startswith("LW"):
                try:
                    lw_ratio = int(token[2:])
                except ValueError:
                    pass
                break

    n_total = len(df)
    W = 100 * lw_ratio
    H = 100
    n_y = n_total // (W * H)
    if n_total % (W * H) != 0:
        # fall back to unique Y count
        n_y = df["Y"].nunique()

    carbon_image = df["Carbon"].values.reshape((n_y, W, H))

    # --- Historic barn_inside heuristic (centralised here) --------------
    barn_inside = np.zeros((n_y, W, H), dtype=bool)
    barn_inside[: min(20, n_y), :, :] = True
    for j in range(min(20, n_y), n_y):
        x_sums = np.array([carbon_image[j, :, i].sum() for i in range(H)])
        for idx in range(1, 60):
            if (x_sums[-idx] - x_sums[-idx - 1]) < -200:
                barn_inside[j, :, (0 + idx) : (H - idx)] = True
                break

    inside_mask = barn_inside.flatten()
    global_mean = float(df.loc[inside_mask, "Carbon"].mean())

    return df, inside_mask, global_mean, lw_ratio
