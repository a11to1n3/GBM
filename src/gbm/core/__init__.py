"""
GMB core — the Gradient-Based Mapper method.

Public API (stable):
    find_optimal_k_points_gbm_2D
    find_optimal_k_points_gbm_3D
"""

from .mapper_2d import find_optimal_k_points_gbm_2D  # type: ignore
# from .mapper_3d import find_optimal_k_points_gbm_3D  # TODO Phase 1 follow-up

__all__ = ["find_optimal_k_points_gbm_2D"]
