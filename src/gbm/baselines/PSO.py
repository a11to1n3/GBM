"""PSO baseline - actual port (with original quirks preserved for fidelity)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional, Tuple, List

from ..utils import sample_neighboring_points_2D, sample_neighboring_points_3D


def find_optimal_k_points_pso_2D(
    nodes_df: pd.DataFrame,
    barn_inside_points: np.ndarray,
    k: int,
    in_CO2_avg: float,
    barn_section: float = 3.1500001,
    epochs: int = 100,
    c1: float = 1.5,
    c2: float = 1.5,
    w: float = 0.7,
    sampling_budget: int = 10000,
    neighborhood_numbers: int = 5,
    barn_LW_ratio: int = 2,
) -> Optional[Tuple[float, float, float, List[List[float]]]]:
    """Particle Swarm Optimization baseline (2D)."""
    nodes_at_height_df = nodes_df[barn_inside_points.flatten().astype(bool)][
        nodes_df[barn_inside_points.flatten().astype(bool)].Y == barn_section
    ]
    nodes_at_height_df = nodes_at_height_df.reset_index()

    carbon_map = nodes_at_height_df["Carbon"].values.reshape(100 * barn_LW_ratio, 100)
    position_map = nodes_at_height_df[["X", "Z"]].values.reshape(100 * barn_LW_ratio, 100, -1)

    valid_indices = np.argwhere(nodes_at_height_df.index.values.reshape(100 * barn_LW_ratio, 100))

    def initialize_particle():
        return valid_indices[np.random.choice(len(valid_indices), size=k, replace=False)]

    def calculate_fitness(particle):
        points = carbon_map[particle[:, 0], particle[:, 1]]
        return np.abs(np.mean(points) - in_CO2_avg)

    # Note: original used k particles instead of configured num_particles
    particles = [initialize_particle() for _ in range(k)]
    velocities = [np.zeros_like(particle) for particle in particles]
    personal_best_positions = particles.copy()
    personal_best_fitness = [calculate_fitness(p) for p in particles]

    global_best_index = np.argmin(personal_best_fitness)
    global_best_position = personal_best_positions[global_best_index].copy()
    global_best_fitness = personal_best_fitness[global_best_index]

    for _ in range(epochs):
        for i in range(k):
            r1, r2 = np.random.rand(2)
            velocities[i] = (w * velocities[i] +
                             c1 * r1 * (personal_best_positions[i] - particles[i]) +
                             c2 * r2 * (global_best_position - particles[i]))

            particles[i] = particles[i] + velocities[i]
            particles[i] = np.clip(particles[i], [0, 0], [100 * barn_LW_ratio - 1, 99])
            particles[i] = particles[i].astype(int)

            fitness = calculate_fitness(particles[i])

            if fitness < personal_best_fitness[i]:
                personal_best_fitness[i] = fitness
                personal_best_positions[i] = particles[i].copy()

            if fitness < global_best_fitness:
                global_best_fitness = fitness
                global_best_position = particles[i].copy()

    best_points = carbon_map[global_best_position[:, 0], global_best_position[:, 1]]
    best_positions = position_map[global_best_position[:, 0], global_best_position[:, 1]]

    image_width, image_height = 100 * barn_LW_ratio, 100
    best_locs = [[int(pos[0]), int(pos[1])] for pos in best_positions]

    combinations = sample_neighboring_points_2D(best_locs, neighborhood_numbers, image_width, image_height, sampling_budget)
    losses = []
    for combination in combinations:
        p_sum = sum(carbon_map[y, x] for y, x in combination)
        losses.append(np.abs(p_sum / k - in_CO2_avg))

    return global_best_fitness, np.mean(losses), np.std(losses), best_positions


def find_optimal_k_points_pso_3D(
    nodes_df: pd.DataFrame,
    barn_inside_points: np.ndarray,
    k: int,
    in_CO2_avg: float,
    epochs: int = 100,
    c1: float = 1.5,
    c2: float = 1.5,
    w: float = 0.7,
    sampling_budget: int = 10000,
    neighborhood_numbers: int = 5,
    barn_LW_ratio: int = 2,
) -> Optional[Tuple[float, float, float, List[List[float]]]]:
    """PSO baseline (3D) - actual port."""
    nodes_df[~barn_inside_points.flatten().astype(bool)] = 1e9

    depth = len(nodes_df["Carbon"].values.flatten()) // (100 * barn_LW_ratio * 100)
    carbon_map = nodes_df["Carbon"].values.reshape(100 * barn_LW_ratio, 100, depth)
    position_map = nodes_df[["X", "Y", "Z"]].values.reshape(100 * barn_LW_ratio, 100, depth, -1)

    valid_indices = np.argwhere(barn_inside_points.reshape(100 * barn_LW_ratio, 100, depth))

    def initialize_particle():
        return valid_indices[np.random.choice(len(valid_indices), size=k, replace=False)]

    def calculate_fitness(particle):
        points = carbon_map[particle[:, 0], particle[:, 1], particle[:, 2]]
        return np.abs(np.mean(points) - in_CO2_avg)

    particles = [initialize_particle() for _ in range(k)]
    velocities = [np.zeros_like(particle) for particle in particles]
    personal_best_positions = particles.copy()
    personal_best_fitness = [calculate_fitness(p) for p in particles]

    global_best_index = np.argmin(personal_best_fitness)
    global_best_position = personal_best_positions[global_best_index].copy()
    global_best_fitness = personal_best_fitness[global_best_index]

    for _ in range(epochs):
        for i in range(k):
            r1, r2 = np.random.rand(2)
            velocities[i] = (w * velocities[i] +
                             c1 * r1 * (personal_best_positions[i] - particles[i]) +
                             c2 * r2 * (global_best_position - particles[i]))

            particles[i] = particles[i] + velocities[i]
            particles[i] = np.clip(particles[i], [0, 0, 0], [100 * barn_LW_ratio - 1, 99, depth - 1])
            particles[i] = particles[i].astype(int)

            fitness = calculate_fitness(particles[i])

            if fitness < personal_best_fitness[i]:
                personal_best_fitness[i] = fitness
                personal_best_positions[i] = particles[i].copy()

            if fitness < global_best_fitness:
                global_best_fitness = fitness
                global_best_position = particles[i].copy()

    best_points = carbon_map[global_best_position[:, 0], global_best_position[:, 1], global_best_position[:, 2]]
    best_positions = position_map[global_best_position[:, 0], global_best_position[:, 1], global_best_position[:, 2]]

    image_width, image_height, image_depth = 100 * barn_LW_ratio, 100, depth
    best_locs = [[int(pos[0]), int(pos[1]), int(pos[2])] for pos in best_positions]

    combinations = sample_neighboring_points_3D(best_locs, neighborhood_numbers, image_width, image_height, image_depth, sampling_budget)
    losses = []
    for combination in combinations:
        p_sum = sum(carbon_map[y, x, z] for y, x, z in combination)
        losses.append(np.abs(p_sum / k - in_CO2_avg))

    return global_best_fitness, np.mean(losses), np.std(losses), best_positions
