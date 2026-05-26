.PHONY: install test smoke clean

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -q

smoke:
	python -c "from gbm.core import find_optimal_k_points_gbm_2D; print('GMB core OK')"
	pytest tests/test_gbm_core.py -q

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
