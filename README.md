# Home Credit Risk Demo

This project analyzes Home Credit application data to estimate loan repayment
risk and translate model scores into business decision thresholds.

## Data and analytical scope

The repository works with two ignored source files in `data/raw/`:

| Dataset | Rows | Columns | Role |
|---|---:|---:|---|
| `application_train.csv` | 307,511 | 122 | Labeled development population |
| `application_test.csv` | 48,744 | 121 | Unlabeled scoring population |

Each file has one row per current application and a complete, unique
`SK_ID_CURR`. The ID sets are disjoint, so the files are sample partitions and
must be compared rather than joined. Only the training file contains `TARGET`.
Payment difficulty occurs in 24,825 training applications, or 8.07%.

The available data describes approved applications. It cannot measure outcomes
for declined applicants, causal effects of lending decisions, loss severity, or
the economic value of an approval threshold.

## EDA findings

The exploratory analysis establishes the following modeling considerations:

- Missingness is concentrated in property fields, car age, occupation, and the
  external-score fields. Missingness is retained as information rather than
  assumed to be random.
- `DAYS_EMPLOYED = 365243` is an invalid employment-tenure sentinel. It occurs
  in 55,374 training rows (18.01%) and 9,274 test rows (19.03%), alongside
  `ORGANIZATION_TYPE = XNA`.
- Income, credit, annuity, and goods-price fields are strongly right-skewed.
  The EDA does not justify automatically deleting or capping their upper tails.
- Higher values of all three opaque external scores are associated with lower
  observed payment-difficulty rates, although their provenance and timing are
  undocumented.
- Loan amounts, repayment-burden ratios, employment information, property
  coverage, regional fields, inquiries, and operational flags show descriptive
  risk separation. These relationships are not causal conclusions.
- `CODE_GENDER`, `DAYS_BIRTH`, `NAME_FAMILY_STATUS`, and derived age fields
  require fairness and policy review before model use.
- Train/test population-shift analysis, model validation, calibration, and an
  economic decision threshold remain separate modeling tasks.

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

## Modeling preparation

The reusable rules derived from the EDA are implemented in
[`src/home_credit/features.py`](src/home_credit/features.py).

| Function | Purpose |
|---|---|
| `clean_application_data()` | Replaces the employment sentinel and unavailable organization type with missing values while retaining a sentinel flag |
| `create_application_features()` | Creates validity-guarded ratios, tenure fields, missingness indicators, coverage counts, and audit age bands |
| `prepare_application_data()` | Applies cleaning and feature creation in one call |

The combined function creates 13 fields:

- Burden ratios: `_ANNUAL_PAYMENT_TO_INCOME`,
  `_PAYMENT_TO_INCOME_UNANNUALIZED`, `_CREDIT_TO_INCOME`, and
  `_CREDIT_TO_GOODS`.
- Tenure fields: `_AGE_YEARS`, `_EMPLOYED_YEARS`,
  `_REGISTRATION_YEARS`, and `_ID_PUBLISH_YEARS`.
- Availability fields: `_EMPLOYED_SENTINEL`, `_MISSING_COUNT`,
  `_PROPERTY_MISSING_COUNT`, and `_EXT_SOURCES_OBSERVED`.
- Audit grouping: `_AGE_BAND`.

Ratios are created only from positive inputs. Derived age is limited to 18–100,
and employment tenure is set to missing when it implies employment before age
14. The annual payment-to-income ratio assumes monthly annuity and annual
income; the unannualized version is retained because those periods are not
documented in the source dictionary.

From the repository root, add `src/` to the Python path and prepare either
application file as follows:

```python
import pandas as pd

from home_credit import prepare_application_data

raw = pd.read_csv("data/raw/application_train.csv")
prepared = prepare_application_data(raw)
```

The functions copy their input by default and validate required columns and
numeric types. `AUDIT_ONLY_COLUMNS` identifies fields that should not enter a
model without policy review.

The EDA deliberately does not authorize these operations, so the preparation
module does not perform them:

- missing-value imputation;
- outlier removal, winsorization, or automatic capping;
- rare-category grouping;
- correlated-feature deletion;
- categorical encoding or numeric scaling; or
- automatic inclusion of sensitive or audit-only fields.

## Validation

Run the preparation tests with:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The current tests cover sentinel treatment, input immutability, idempotent
cleaning, ratio guards, tenure validity, missingness features, audit groups, and
schema validation. The preparation pipeline has also been executed successfully
against all 307,511 training rows and 48,744 test rows with matching derived
schemas and no infinite ratio or tenure values.
