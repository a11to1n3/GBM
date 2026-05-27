# Statistical Analysis

This family contains the code that produces the ranking tables, Wilcoxon signed-rank tests, Cliff's delta effect sizes, and Nemenyi critical-difference diagrams used in the paper.

## Main outputs
- `ranking_tables.tex`
- Summary statistics (mean/median ranks, win counts, p-values, effect sizes)

## Usage
```bash
python -m experiments.statistical_analysis.compute \
    --deploy-json results/aggregates/deploy_results_all.json \
    --out results/aggregates/ranking_tables.tex
```

For the full set of tests and diagrams that appear in the paper (including sensitivity, ablation, and robustness), the original `statistical_analysis.py` and `accuracy_table.py` can be used as reference and gradually ported here.

## Data
Requires the compact deploy matrix produced by `experiments/deployable_layouts/run.py`.
