# Data map

## Scope

This map covers the two business-data CSVs present in `data/raw/`: `application_train.csv` and `application_test.csv`. The only data dictionary found in the repository is `data/raw/HomeCredit_columns_description.csv`; there is no data-dictionary file under `docs/`.

The dictionary also describes six tables whose CSVs are not present: `bureau.csv`, `bureau_balance.csv`, `POS_CASH_balance.csv`, `credit_card_balance.csv`, `previous_application.csv`, and `installments_payments.csv`. Their row counts, key uniqueness, observed cardinalities, and applicant coverage therefore cannot be verified here.

Checks were limited to grain, row counts, keys, joins, applicant coverage, and values that conflict with explicit dictionary descriptions. No exploratory data analysis was performed.

## Summary

| Table | Grain | Rows | Primary key | Unique? | Foreign keys in available data | Share of `application_train` applicants with at least one row |
|---|---|---:|---|---|---|---:|
| `application_train.csv` | One labeled current loan application in the training sample | 307,511 | `SK_ID_CURR` | Yes: 307,511 distinct, 0 null, 0 duplicate | None | 100.0000% (307,511 / 307,511) |
| `application_test.csv` | One unlabeled current loan application in the test sample | 48,744 | `SK_ID_CURR` | Yes: 48,744 distinct, 0 null, 0 duplicate | None | 0.0000% (0 / 307,511) |

`application_train` and `application_test` are mutually exclusive sample partitions, not parent and child tables. Their `SK_ID_CURR` sets have no overlap, so `application_test.SK_ID_CURR` is not a foreign key to `application_train.SK_ID_CURR`.

## `application_train.csv`

### Grain and key

- **Grain:** one current loan application with its applicant/application attributes and observed target label.
- **Rows:** 307,511.
- **Primary key:** `SK_ID_CURR`.
- **Key check:** unique and complete: 307,511 distinct values, no nulls, and no duplicates.

### Foreign keys and cardinality

There are no outbound foreign keys to another available table. `SK_ID_CURR` is the table's primary key. In the wider schema described by the dictionary, this key would be referenced by auxiliary history tables in one-to-many relationships, but those CSVs are absent and the cardinalities cannot be measured.

### Coverage of training applicants

307,511 of 307,511 training applicants have a row in this table: **100.0000%**.

### Values that contradict the dictionary

| Column | Observed conflict | Affected rows |
|---|---|---:|
| `DAYS_EMPLOYED` | The dictionary says this is the number of days before the application that current employment started. The value `365243` is positive and represents about 1,000 years, so it cannot be a valid relative employment-start time. | 55,374 (18.0072%) |
| `FONDKAPREMONT_MODE` | Marked as normalized, but all non-null values are categorical strings: `not specified`, `org spec account`, `reg oper account`, or `reg oper spec account`. | 97,216 non-null rows |
| `HOUSETYPE_MODE` | Marked as normalized, but all non-null values are categorical strings: `block of flats`, `specific housing`, or `terraced house`. | 153,214 non-null rows |
| `WALLSMATERIAL_MODE` | Marked as normalized, but all non-null values are categorical strings such as `Panel`, `Stone, brick`, and `Wooden`. | 151,170 non-null rows |
| `EMERGENCYSTATE_MODE` | Marked as normalized, but its non-null values are the categories `Yes` and `No`. | 161,756 non-null rows |
| `CODE_GENDER` | The dictionary describes gender, but the undocumented placeholder `XNA` occurs in addition to `F` and `M`. | 4 (0.0013%) |
| `NAME_FAMILY_STATUS` | The dictionary describes family status, but the undocumented placeholder `Unknown` occurs. | 2 (0.0007%) |
| `ORGANIZATION_TYPE` | The dictionary describes an organization type, but the undocumented placeholder `XNA` occurs. It appears on exactly the same number of rows as the invalid `DAYS_EMPLOYED = 365243` sentinel. | 55,374 (18.0072%) |

All explicit binary flags contain only `0` and `1`; both regional-rating columns contain only `1`, `2`, and `3`; hours are within `0`–`23`; weekday labels are valid; and the numeric fields marked normalized are within `0`–`1` when present.

## `application_test.csv`

### Grain and key

- **Grain:** one current loan application with applicant/application attributes but no observed target label.
- **Rows:** 48,744.
- **Primary key:** `SK_ID_CURR`.
- **Key check:** unique and complete: 48,744 distinct values, no nulls, and no duplicates.

### Foreign keys and cardinality

There are no outbound foreign keys to another available table. `SK_ID_CURR` is the table's primary key. It shares no keys with `application_train`, so the two files do not form a relational join.

### Coverage of training applicants

0 of 307,511 training applicants have a row in this table: **0.0000%**. This is expected for a disjoint test split and is not a referential-integrity failure.

### Values that contradict the dictionary

| Column | Observed conflict | Affected rows |
|---|---|---:|
| `DAYS_EMPLOYED` | The dictionary says this is the number of days before the application that current employment started. The value `365243` is positive and represents about 1,000 years, so it cannot be a valid relative employment-start time. | 9,274 (19.0259%) |
| `REGION_RATING_CLIENT_W_CITY` | The dictionary permits ratings `1`, `2`, and `3`, but the value `-1` occurs. | 1 (0.0021%) |
| `FONDKAPREMONT_MODE` | Marked as normalized, but all non-null values are categorical strings: `not specified`, `org spec account`, `reg oper account`, or `reg oper spec account`. | 15,947 non-null rows |
| `HOUSETYPE_MODE` | Marked as normalized, but all non-null values are categorical strings: `block of flats`, `specific housing`, or `terraced house`. | 25,125 non-null rows |
| `WALLSMATERIAL_MODE` | Marked as normalized, but all non-null values are categorical strings such as `Panel`, `Stone, brick`, and `Wooden`. | 24,851 non-null rows |
| `EMERGENCYSTATE_MODE` | Marked as normalized, but its non-null values are the categories `Yes` and `No`. | 26,535 non-null rows |
| `ORGANIZATION_TYPE` | The dictionary describes an organization type, but the undocumented placeholder `XNA` occurs. It appears on exactly the same number of rows as the invalid `DAYS_EMPLOYED = 365243` sentinel. | 9,274 (19.0259%) |

The dictionary labels its schema `application_{train|test}.csv` and includes `TARGET`, but `application_test.csv` does not contain that column. This is a schema-level discrepancy rather than a contradictory value and is consistent with the test table's unlabeled role.

All explicit binary flags contain only `0` and `1`; `REGION_RATING_CLIENT` contains only `1`, `2`, and `3`; hours are within `0`–`23`; weekday labels are valid; and the numeric fields marked normalized are within `0`–`1` when present.

## Dictionary metadata

`HomeCredit_columns_description.csv` contains 219 rows, each representing one column definition for a named source table. The natural metadata key (`Table`, `Row`) is unique. The file's `Unnamed: 0` column is also unique but appears to be an exported row index, not a business key. Because this is metadata rather than applicant-level data, foreign-key cardinality and training-applicant coverage are not applicable.

## Dictionary-declared relationships that could not be verified

The following relationships are inferred from shared identifier names and table grains in the dictionary. They are listed for schema context only because the child CSVs are absent.

| Child key | Referenced key | Expected cardinality |
|---|---|---|
| `bureau.SK_ID_CURR` | `application_{train|test}.SK_ID_CURR` | Many bureau credits to one current application |
| `previous_application.SK_ID_CURR` | `application_{train|test}.SK_ID_CURR` | Many previous applications to one current application |
| `credit_card_balance.SK_ID_CURR` | `application_{train|test}.SK_ID_CURR` | Many monthly balance rows to one current application |
| `POS_CASH_balance.SK_ID_CURR` | `application_{train|test}.SK_ID_CURR` | Many monthly balance rows to one current application |
| `installments_payments.SK_ID_CURR` | `application_{train|test}.SK_ID_CURR` | Many installment/payment rows to one current application |
| `bureau_balance.SK_ID_BUREAU` | `bureau.SK_ID_BUREAU` | Many monthly status rows to one bureau credit |
| `credit_card_balance.SK_ID_PREV` | `previous_application.SK_ID_PREV` | Many monthly balance rows to one previous application |
| `POS_CASH_balance.SK_ID_PREV` | `previous_application.SK_ID_PREV` | Many monthly balance rows to one previous application |
| `installments_payments.SK_ID_PREV` | `previous_application.SK_ID_PREV` | Many installment/payment rows to one previous application |
