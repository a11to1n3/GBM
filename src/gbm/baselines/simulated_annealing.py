"""Simulated Annealing baseline - actual port."""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional, Tuple, List

from ..utils import sample_neighboring_points_2D, sample_neighboring_points_3D


def find_optimal_k_points_simulated_annealing_2D(
    nodes_df: pd.DataFrame,
    barn_inside_points: np.ndarray,
    k: int,
    in_CO2_avg: float,
    barn_section: float = 3.1500001,
    initial_temperature: float = 100,
    cooling_rate: float = 0.995,
    epochs: int = 1000,
    sampling_budget: int = 10000,
    neighborhood_numbers: int = 5,
    barn_LW_ratio: int = 2,
) -> Optional[Tuple[float, float, float, List[List[float]]]]:
    """Simulated Annealing baseline (2D)."""
    nodes_at_height_df = nodes_df[barn_inside_points.flatten().astype(bool)][
        nodes_df[barn_inside_points.flatten().astype(bool)].Y == barn_section
    ]
    nodes_at_height_df = nodes_at_height_df.reset_index()

    carbon_map = nodes_at_height_df["Carbon"].values.reshape(100 * barn_LW_ratio, 100)
    position_map = nodes_at_height_df[["X", "Z"]].values.reshape(100 * barn_LW_ratio, 100, -1)

    valid_indices = np.argwhere(nodes_at_height_df.index.values.reshape(100 * barn_LW_ratio, 100))

    def get_random_solution():
        return valid_indices[np.random.choice(len(valid_indices), size=k, replace=False)]

    def get_neighbor_solution(solution):
        neighbor = solution.copy()
        index_to_change = np.random.randint(k)
        neighbor[index_to_change] = valid_indices[np.random.choice(len(valid_indices))]
        return neighbor

    def calculate_loss(solution):
        points = carbon_map[solution[:, 0], solution[:, 1]]
        return np.abs(np.mean(points) - in_CO2_avg)

    current_solution = get_random_solution()
    current_loss = calculate_loss(current_solution)
    best_solution = current_solution
    best_loss = current_loss

    temperature = initial_temperature

    for _ in range(epochs):
        neighbor_solution = get_neighbor_solution(current_solution)
        neighbor_loss = calculate_loss(neighbor_solution)

        if neighbor_loss < current_loss or np.random.random() < np.exp((current_loss - neighbor_loss) / temperature):
            current_solution = neighbor_solution
            current_loss = neighbor_loss

        if current_loss < best_loss:
            best_solution = current_solution
            best_loss = current_loss

        temperature *= cooling_rate

    best_points = carbon_map[best_solution[:, 0], best_solution[:, 1]]
    best_positions = position_map[best_solution[:, 0], best_solution[:, 1]]

    image_width, image_height = 100 * barn_LW_ratio, 100
    best_locs = [[int(pos[0]), int(pos[1])] for pos in best_positions]

    combinations = sample_neighboring_points_2D(best_locs, neighborhood_numbers, image_width, image_height, sampling_budget)
    losses = []
    for combination in combinations:
        p_sum = sum(carbon_map[y, x] for y, x in combination)
        losses.append(np.abs(p_sum / k - in_CO2_avg))

    return best_loss, np.mean(losses), np.std(losses), best_positions


def find_optimal_k_points_simulated_annealing_3D(
    nodes_df: pd.DataFrame,
    barn_inside_points: np.ndarray,
    k: int,
    in_CO2_avg: float,
    initial_temperature: float = 100,
    cooling_rate: float = 0.995,
    epochs: int = 1000,
    sampling_budget: int = 10000,
    neighborhood_numbers: int = 5,
    barn_LW_ratio: int = 2,
) -> Optional[Tuple[float, float, float, List[List[float]]]]:
    """Simulated Annealing baseline (3D) - actual port."""
    nodes_df[~barn_inside_points.flatten().astype(bool)] = 1e9

    depth = len(nodes_df["Carbon"].values.flatten()) // (100 * barn_LW_ratio * 100)
    carbon_map = nodes_df["Carbon"].values.reshape(100 * barn_LW_ratio, 100, depth)
    position_map = nodes_df[["X", "Y", "Z"]].values.reshape(100 * barn_LW_ratio, 100, depth, -1)

    valid_indices = np.argwhere(barn_inside_points.reshape(100 * barn_LW_ratio, 100, depth))

    def get_random_solution():
        return valid_indices[np.random.choice(len(valid_indices), size=k, replace=False)]

    def get_neighbor_solution(solution):
        neighbor = solution.copy()
        index_to_change = np.random.randint(k)
        neighbor[index_to_change] = valid_indices[np.random.choice(len(valid_indices))]
        return neighbor

    def calculate_loss(solution):
        points = carbon_map[solution[:, 0], solution[:, 1], solution[:, 2]]
        return np.abs(np.mean(points) - in_CO2_avg)

    current_solution = get_random_solution()
    current_loss = calculate_loss(current_solution)
    best_solution = current_solution
    best_loss = current_loss

    temperature = initial_temperature

    for _ in range(epochs):
        neighbor_solution = get_neighbor_solution(current_solution)
        neighbor_loss = calculate_loss(neighbor_solution)

        if neighbor_loss < current_loss or np.random.random() < np.exp((current_loss - neighbor_loss) / temperature):
            current_solution = neighbor_solution
            current_loss = neighbor_loss

        if current_loss < best_loss:
            best_solution = current_solution
            best_loss = current_loss

        temperature *= cooling_rate

    best_points = carbon_map[best_solution[:, 0], best_solution[:, 1], best_solution[:, 2]]
    best_positions = position_map[best_solution[:, 0], best_solution[:, 1], best_solution[:, 2]]

    image_width, image_height, image_depth = 100 * barn_LW_ratio, 100, depth
    best_locs = [[int(pos[0]), int(pos[1]), int(pos[2])] for pos in best_positions]

    combinations = sample_neighboring_points_3D(best_locs, neighborhood_numbers, image_width, image_height, image_depth, sampling_budget)
    losses = []
    for combination in combinations:
        p_sum = sum(carbon_map[y, x, z] for y, x, z in combination)
        losses.append(np.abs(p_sum / k - in_CO2_avg))

    return best_loss, np.mean(losses), np.std(losses), best_positions
