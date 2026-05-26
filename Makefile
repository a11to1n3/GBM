.PHONY: install smoke clean

install:
	pip install -e ".[dev]"

smoke:
	python -c "from gbm.core import find_optimal_k_points_gbm_2D; print('GMB core OK')"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
