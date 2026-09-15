# Home Credit Risk Demo

This project analyzes Home Credit application data to estimate loan repayment
risk and translate model scores into business decision thresholds.

## Project layout

- `data/raw/`: immutable source data and the data dictionary
- `data/interim/`: cleaned and joined intermediate datasets
- `data/processed/`: model-ready datasets
- `docs/`: business context and research
- `notebooks/`: ordered exploratory and modeling notebooks
- `src/home_credit/`: reusable analysis and modeling code
- `reports/`: figures, tables, source documents, and final deliverables
- `models/`: fitted model artifacts and metadata
- `outputs/`: predictions and decision-policy tables
- `tests/`: automated checks for reusable code
- `config/`: data and modeling configuration

Data, model artifacts, generated outputs, and rendered Quarto files are kept
out of Git by default.
