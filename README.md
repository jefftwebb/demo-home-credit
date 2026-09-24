# Home Credit Risk Demo

This project analyzes Home Credit application data to estimate loan repayment
risk and translate model scores into business decision thresholds.

## Project layout

- `data/raw/`: immutable source data and the data dictionary
- `data/interim/`: cleaned and joined intermediate datasets
- `data/processed/`: model-ready datasets
- `docs/`: business context, data documentation, research, and analysis plans
- `notebooks/`: ordered exploratory and modeling notebooks
- `src/home_credit/`: reusable analysis and modeling code
- `reports/`: figures, tables, source documents, and final deliverables
- `models/`: fitted model artifacts and metadata
- `outputs/`: predictions and decision-policy tables
- `tests/`: automated checks for reusable code
- `config/`: data and modeling configuration

Data, model artifacts, generated outputs, and rendered Quarto files are kept
out of Git by default.

## Current analysis artifacts

- [`docs/data/data-map.md`](docs/data/data-map.md): source-table grain, keys,
  coverage, and dictionary conflicts
- [`docs/research/feature-report.md`](docs/research/feature-report.md):
  evidence-backed thin-file lending features available from the source data
- [`docs/planning/eda-plan.md`](docs/planning/eda-plan.md): staged exploratory
  analysis plan and review gates
- [`notebooks/01_eda.qmd`](notebooks/01_eda.qmd): executable exploratory
  analysis
- [`reports/slides/eda-with-ai.qmd`](reports/slides/eda-with-ai.qmd): source for
  the EDA workflow presentation

Render the analysis from the repository root with:

```sh
quarto render notebooks/01_eda.qmd --output-dir ../reports/_build
```

The notebook expects the ignored Home Credit CSV files in `data/raw/` and a
Python environment containing NumPy, pandas, Matplotlib, seaborn, SciPy, and
scikit-learn.
