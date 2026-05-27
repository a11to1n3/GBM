# Runtime Benchmark Experiments

Wall-clock timing of GBM and the eight baselines on representative 2D/3D synthetic volumes.

## Status
This family now contains a thin, clean driver (`run.py`) that exercises the modern GBM public API.

The numbers that appear in the published paper were produced with the historical `bench_runtime*.py` scripts + the full Zenodo scenario set. The driver here lets you reproduce the *methodology* quickly and reproducibly with the clean package (useful for regression testing and new timing claims).

## Usage

```bash
# 3D timing (default)
python -m experiments.runtime_benchmark.run \
    --dim 3D \
    --k 5,10,20 \
    --repeats 3 \
    --out results/aggregates/runtime_3d_smoke.json

# 2D timing
python -m experiments.runtime_benchmark.run \
    --dim 2D \
    --k 5,10 \
    --repeats 5 \
    --out results/aggregates/runtime_2d.json
```

Output is a compact JSON with median wall-clock seconds per (method, k).

## Methods timed (extendable)
- GBM (2D X or 3D XZ)
- Greedy, KMC+GBO (kmedoids), Uniform (others can be added in one line)

## Seeds / determinism
Synthetic data is generated deterministically inside the driver for the current run. The GBM / baseline calls use their documented default seeds.

## Relation to the paper
See the runtime claims and any timing tables/figures in the COMPAG revision (and the original `bench_runtime*.py` logs in the historical checkout).

This is the second driver of the "next batch" port (following `robustness/`).
