"""
GBM command-line interface (lightweight).

This CLI is intentionally minimal. For full features and all experiment
drivers use the Python API directly (see experiments/*/README.md and the
notebooks in examples/).
"""

import argparse
import sys


KNOWN_METHODS = ["gbm", "tda-mapper", "kmedoids", "greedy", "uniform",
                 "random", "simulated-annealing", "PSO", "monte-carlo", "genetic"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gbm",
        description="Gradient-Based Mapper (GBM) — sensor placement for scalar fields",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Run one method on one scenario (lightweight CLI)")
    p_run.add_argument("csv")
    p_run.add_argument("--method", "-c", default="gbm", choices=KNOWN_METHODS)
    p_run.add_argument("--dim", "-d", choices=["2D", "3D"], default="3D")
    p_run.add_argument("--gas", choices=["CO2", "NH3"], default="CO2")
    p_run.add_argument("--cross-section", default=None)
    p_run.add_argument("--k", default="5,10,20")
    p_run.add_argument("--force", action="store_true")

    p_deploy = sub.add_parser("deploy", help="Compute fixed deployable layouts (lightweight CLI)")
    p_deploy.add_argument("--results-dir", default="results")
    p_deploy.add_argument("--k", default="5,10,20")

    args = parser.parse_args(argv)

    if args.cmd == "run":
        print(f"[lightweight] gbm run {args.csv} --method {args.method} --dim {args.dim} "
              f"--gas {args.gas} --k {args.k}")
        print("For full features, use the Python API directly.")
        return 0

    if args.cmd == "deploy":
        print(f"[lightweight] gbm deploy --results-dir {args.results_dir} --k {args.k}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
