"""
GMB command-line interface (stub — Phase 2/3 work in progress).

Future full version will dispatch to the unified runner for all methods (GBM + baselines)
and support the deploy / analysis commands.
"""

import argparse
import sys


KNOWN_METHODS = ["gbm", "tda-mapper", "kmedoids", "greedy", "uniform",
                 "random", "simulated-annealing", "PSO", "monte-carlo", "genetic"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gbm",
        description="Gradient-Based Mapper (GMB) — sensor placement for scalar fields",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Run one method on one scenario (stub)")
    p_run.add_argument("csv")
    p_run.add_argument("--method", "-c", default="gbm", choices=KNOWN_METHODS)
    p_run.add_argument("--dim", "-d", choices=["2D", "3D"], default="3D")
    p_run.add_argument("--gas", choices=["CO2", "NH3"], default="CO2")
    p_run.add_argument("--cross-section", default=None)
    p_run.add_argument("--k", default="5,10,20")
    p_run.add_argument("--force", action="store_true")

    p_deploy = sub.add_parser("deploy", help="Compute fixed deployable layouts (stub)")
    p_deploy.add_argument("--results-dir", default="results")
    p_deploy.add_argument("--k", default="5,10,20")

    args = parser.parse_args(argv)

    if args.cmd == "run":
        print(f"[stub] gbm run {args.csv} --method {args.method} --dim {args.dim} "
              f"--gas {args.gas} --k {args.k}")
        print("Full implementation coming in Phase 2. For now use the Python API or the legacy barnCSP.py shim.")
        return 0

    if args.cmd == "deploy":
        print(f"[stub] gbm deploy --results-dir {args.results_dir} --k {args.k}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
