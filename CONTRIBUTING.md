# Contributing to GBM

Thank you for your interest in Gradient-Based Mapper!

## Quick Start for Contributors

1. Fork the repository and clone it locally.
2. Create a virtual environment and install in editable mode:
   ```bash
   pip install -e ".[dev]"
   ```
3. Make your changes.
4. Run the smoke tests:
   ```bash
   python -c "from gbm.core import find_optimal_k_points_gbm_2D"
   ```
5. Open a pull request with a clear description.

## Code Style

- We follow PEP 8 with a line length of 88 (enforced by Ruff).
- Keep public APIs stable and well-documented.
- New baselines or major features should come with a small example notebook when possible.

## Reporting Issues

Please use the GitHub issue tracker and include:
- A minimal reproducible example (synthetic data is preferred).
- Expected vs actual behavior.
- Your environment (Python version, OS).

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 License.
