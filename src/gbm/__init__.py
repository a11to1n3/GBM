"""
GBM — Gradient-Based Mapper (public package root).

Quick import:
    from gbm.core import find_optimal_k_points_gbm_2D
    from gbm.utils import factor_k_for_3D
"""

__version__ = "0.1.0.dev"

from .core import find_optimal_k_points_gbm_2D  # noqa: F401

__all__ = ["find_optimal_k_points_gbm_2D", "__version__"]
