# EDA plan: `application_train`

## Purpose and scope

This EDA will describe the labeled application sample, test whether the available
application-time fields contain credible repayment-risk signal, and identify data
quality, leakage, missingness, and fairness issues that must be resolved before
modeling.

The source is `data/raw/application_train.csv`, with one row per current loan
application, 307,511 rows, 122 columns, a unique `SK_ID_CURR`, and binary outcome
`TARGET`. The observed payment-difficulty rate is approximately 8.1%.

This is descriptive and diagnostic work. It will not select a production model,
claim that a variable causes payment difficulty, or recommend a lending cutoff.
The business target of reducing payment difficulty at a 90% approval rate and the
economic decision threshold require out-of-sample model scores and sponsor-supplied
cost assumptions.

## Analysis principles

- Preserve `data/raw/application_train.csv` unchanged.
- Treat `SK_ID_CURR` as an identifier, never as a predictor.
- Use counts and denominators with every rate. Show 95% confidence intervals for
  segment event rates and suppress or flag very small groups.
- Compare event rates with the 8.1% portfolio baseline using percentage-point
  difference and lift. Do not use p-values as the main measure of importance in a
  sample this large.
- Fit bin edges, rare-category groupings, and any later imputation rules on the
  training portion only after the model split is defined. The EDA may show full-sample
  descriptions, but it must not freeze preprocessing choices using validation or
  test outcomes.
- Treat missingness and undocumented placeholders as information to investigate,
  not values to fill automatically.
- Separate predictive relevance from legal or policy permissibility. Protected or
  sensitive attributes may be used for fairness audit even when excluded from the
  model.

## Stage 1: establish the data contract

### Q1. Does the file match its stated grain and key? `[added – standing check]`

- **Method:** Confirm row and column counts, exact column names, inferred types,
  `SK_ID_CURR` completeness and uniqueness, duplicate rows, and binary `TARGET`
  values. Reconcile these checks to `docs/data/data-map.md`.
- **Table:** `application_train`.
- **Output:** One compact data-contract table with expected, observed, and status;
  a short list of schema exceptions.
- **Dependency:** None. Stop if grain, key, or target validity fails.

### Q2. Could any field leak the outcome or be unavailable at decision time? `[added – standing check]`

- **Method:** Classify every column as identifier, outcome, application-time input,
  derived application-time input, uncertain timing, or prohibited/post-outcome.
  Review names and dictionary definitions for payment, delinquency, approval, or
  future-observation concepts. Document uncertainty instead of guessing.
- **Table:** `application_train`; data dictionary if available.
- **Output:** Feature-availability register with rationale and proposed action:
  retain, audit-only, exclude, or investigate.
- **Dependency:** Q1.
- **Limitation:** The CSV contains no full application timestamp or data-lineage
  metadata, so timing cannot be proven from values alone.

## Stage 2: understand the outcome and sample

### Q3. How imbalanced is `TARGET`? `[added – standing check]`

- **Method:** Count and percentage of `TARGET = 0` and `TARGET = 1`; calculate the
  portfolio event rate and a binomial 95% confidence interval.
- **Table:** `application_train`.
- **Output:** Two-row table and one restrained bar chart annotated with counts and
  percentages.
- **Dependency:** Q1.

### Q4. What does the sample represent, and what can it not support?

- **Method:** Compare the observed grain and available fields with the business
  problem statement. Record selection limits: approved applications only,
  anonymized market and currency, early payment difficulty rather than write-off,
  and no causal information about interventions.
- **Table:** `application_train`; business problem statement.
- **Output:** Scope-and-limitations table tying each limitation to the conclusions it
  prevents.
- **Dependency:** Q1–Q3.
- **Type:** This is a framing check, not an empirical risk-factor question.

## Stage 3: quantify missingness and invalid values

### Q5. Which variables and rows are incomplete? `[added – standing check]`

- **Method:** Calculate null count and share by column; number and share of missing
  fields per row; missingness by feature family. Show only ranked, readable views.
- **Table:** `application_train`.
- **Output:** Ranked missingness table; horizontal chart for columns above 5%
  missing; distribution of missing-field count per application; feature-family
  summary.
- **Dependency:** Q1–Q2.

### Q6. Is missingness associated with payment difficulty?

- **Method:** For each feature with missing values, compare `TARGET` rate for missing
  versus observed rows with counts, confidence intervals, percentage-point
  difference, and lift. Repeat for bands of total missing-field count. Examine
  common co-missingness patterns within related feature families rather than a
  122-column heatmap.
- **Table:** `application_train`.
- **Output:** Ranked missingness-risk table; target-rate plot by row-level missingness
  band; small co-missingness matrices for external scores, employment, property,
  and bureau-inquiry families.
- **Dependency:** Q3 and Q5.

### Q7. Which values are impossible, sentinel-coded, inconsistent, or extreme? `[added – standing check]`

- **Method:** Apply documented and domain-plausibility checks to relative-day fields,
  ages, employment tenure, household counts, amounts, ratios, normalized fields,
  regional ratings, hours, weekdays, and binary flags. Explicitly isolate
  `DAYS_EMPLOYED = 365243`, `ORGANIZATION_TYPE = XNA`, `CODE_GENDER = XNA`, and
  `NAME_FAMILY_STATUS = Unknown`. For numeric features, review min, p0.1, p1,
  median, p99, p99.9, and max, then inspect the rows behind material extremes.
- **Table:** `application_train`.
- **Output:** Validation-rule table with affected row count/share and proposed
  treatment; capped/log-scale distribution plots for material amount outliers.
- **Dependency:** Q1–Q2 and Q5.
- **Decision gate:** Approve the missing/sentinel treatment rules before derived
  features or modeling data are created.

## Stage 4: validate core underwriting concepts and derived features

### Q8. Are applicant income and requested-loan amounts believable?

- **Method:** Examine `AMT_INCOME_TOTAL`, `AMT_CREDIT`, `AMT_ANNUITY`, and
  `AMT_GOODS_PRICE` using quantiles, log-scale histograms, zero/negative checks,
  round-number concentration, and category-specific summaries. Inspect extreme
  values without dropping them automatically.
- **Table:** `application_train`.
- **Output:** Quantile table; four distribution plots; extreme-record review table
  with identifiers masked from the narrative.
- **Dependency:** Q7.

### Q9. Can repayment-capacity ratios be constructed reliably?

- **Method:** Create diagnostic versions of annual payment-to-income
  (`12 * AMT_ANNUITY / AMT_INCOME_TOTAL`), credit-to-income
  (`AMT_CREDIT / AMT_INCOME_TOTAL`), and credit-to-goods-price
  (`AMT_CREDIT / AMT_GOODS_PRICE`). Verify units and denominator validity, report
  missingness and implausible tails, and run sensitivity with the unannualized
  annuity ratio because the source dictionary does not explicitly state income and
  annuity periodicity.
- **Table:** `application_train`.
- **Output:** Ratio-definition table; coverage and quantile table; log-scale or
  clipped distributions; list of assumptions requiring confirmation.
- **Dependency:** Q7–Q8.
- **Limitation:** These are burden proxies, not a full debt-to-income measure because
  existing obligations, term, APR, and verified disposable income are absent.

### Q10. Are age, employment, residence, and registration tenures coherent?

- **Method:** Convert valid negative day counts to positive years; treat the
  employment sentinel as missing; compare tenure with age and flag impossible
  relationships. Cross-tab employment sentinel status with income type,
  organization type, occupation, and employment-phone flag.
- **Table:** `application_train`.
- **Output:** Validity and coverage table; age and tenure distributions; cross-tab of
  sentinel/missing employment states.
- **Dependency:** Q7.

## Stage 5: measure univariate risk separation

Use the same output convention in Q11–Q15: population count/share, bad count,
event rate, 95% confidence interval, percentage-point difference from portfolio,
and lift. Numeric variables use predeclared quantile bins plus explicit missing and
invalid groups. Categorical plots show only sufficiently populated levels and retain
an `Other/rare` group for completeness.

### Q11. How strongly do the external scores separate repayment risk?

- **Method:** For `EXT_SOURCE_1`, `EXT_SOURCE_2`, and `EXT_SOURCE_3`, show coverage,
  score distributions by target, event rate by decile, monotonicity, pairwise
  Spearman correlation, and missingness risk. Do not label them as conventional
  bureau scores.
- **Table:** `application_train`.
- **Output:** Coverage table; three decile risk plots; compact correlation matrix.
- **Dependency:** Q3, Q5–Q7.

### Q12. How do loan burden and amount features relate to payment difficulty?

- **Method:** Event rate across bins of income, credit, annuity, goods price, and the
  validated ratios from Q9; stratify the most useful relationships by contract type
  to check whether product mix explains them.
- **Table:** `application_train`.
- **Output:** Binned-risk plots and contract-type stratification table.
- **Dependency:** Q8–Q9.

### Q13. How do employment and income-stability proxies relate to risk?

- **Method:** Compare event rates across income type, occupation, organization type,
  valid employment-tenure bins, and employment-data availability. Keep the sentinel
  group explicit. Collapse rare organization types only for display, not in the raw
  analysis.
- **Table:** `application_train`.
- **Output:** Ranked categorical-risk tables and employment-tenure risk plot.
- **Dependency:** Q10.

### Q14. Do housing, household, regional, and mobility proxies separate risk?

- **Method:** Analyze housing type, home/car ownership, property-field availability,
  family size, children, regional ratings, population-relative measure, and
  live/work mismatch flags. Check whether property-related risk differences are
  largely missingness effects.
- **Table:** `application_train`.
- **Output:** Segment-risk tables; binned-risk plots; property-availability comparison.
- **Dependency:** Q5–Q7.

### Q15. Do inquiry counts, application timing, contact flags, or document flags add credible signal?

- **Method:** Analyze bureau inquiry windows individually and as recency summaries;
  compare weekday and hour bands; compare phone/email flags; report prevalence and
  event rate for each document flag. Flag very rare fields and avoid interpreting
  operational process correlations as causal customer risk.
- **Table:** `application_train`.
- **Output:** Inquiry-risk plots; weekday/hour heatmap with counts; prevalence-versus-
  lift plot for binary flags.
- **Dependency:** Q5–Q7.

## Stage 6: fairness, redundancy, and robustness

### Q16. Do observed outcome rates or data quality differ across protected or sensitive groups?

- **Method:** Audit `CODE_GENDER` and policy-defined age bands for population share,
  outcome rate, missingness burden, external-score coverage, and core burden ratios.
  Show confidence intervals and intersections only where sample sizes are adequate.
  Treat undocumented gender values separately. Do not infer discrimination or use
  these fields as ordinary predictive features.
- **Table:** `application_train`.
- **Output:** Fairness-audit table and gap chart; list of follow-up model evaluation
  metrics required after predictions exist.
- **Dependency:** Q3, Q5–Q12.
- **Limitation:** Error-rate and approval-rate gaps cannot be computed until a model
  and decision threshold exist.

### Q17. Which variables are duplicates, near-duplicates, or redundant representations?

- **Method:** Identify exact duplicate columns; compare `AVG`, `MODE`, and `MEDI`
  property families; calculate bounded Spearman correlations for numeric fields and
  association measures for categorical fields. Review regional ratings, social-circle
  pairs, and document/contact flags as families. Do not select features solely from
  correlation with `TARGET`.
- **Table:** `application_train`.
- **Output:** Exact/near-duplicate table; clustered correlation view limited to
  strongly related feature families; recommendation to retain, combine, or defer.
- **Dependency:** Q5–Q15.

### Q18. Are the main findings stable enough to guide preprocessing?

- **Method:** Repeat key binned event rates and missingness lifts on a fixed,
  stratified development/validation split, using development-derived bins. Compare
  direction, magnitude, category coverage, and confidence intervals. This is a
  robustness check, not model validation.
- **Table:** `application_train`.
- **Output:** Stability table for the short list of candidate concepts; warnings for
  unstable or sparse relationships.
- **Dependency:** Q11–Q17.

### Q19. Does the training sample align with the scoring population? `[added – standing check]`

- **Method:** Compare schema, missingness, numeric distributions, and category levels
  between train and the scoring sample; report population stability metrics only for
  variables whose meanings and cleaning rules are established.
- **Tables:** Requires `application_train` and `application_test`.
- **Output:** Train/test schema and distribution-shift report.
- **Dependency:** Q1–Q18.
- **Scope flag:** This cannot be answered from `application_train` alone. It should be
  a separate, approved extension using `application_test`; the files must be compared,
  not joined.

## Execution order and review gates

1. **Gate A — data contract:** Approve Q1–Q4, especially the availability/leakage
   register.
2. **Gate B — cleaning policy:** Approve Q5–Q7 and the handling of nulls,
   sentinels, undocumented categories, and extremes.
3. **Gate C — feature definitions:** Approve Q8–Q10, including units and ratio
   formulas.
4. **Gate D — descriptive risk results:** Review Q11–Q15 before combining or
   transforming predictors.
5. **Gate E — governance and robustness:** Review Q16–Q18. Add Q19 only if
   `application_test` is brought into scope.

If an earlier gate invalidates a field or definition, later questions that depend on
it will be revised rather than executed mechanically.

## Planned notebook structure

`notebooks/01_eda.qmd` should contain:

1. Scope, definitions, and reproducibility settings.
2. Standing checks: target; missingness; impossible values; key/grain; temporal
   direction; train/test consistency marked out of scope unless approved.
3. One section per question in the order above.
4. For each question: question, method, code, output, and one factual sentence
   stating what the output shows. Interpretation and business decisions remain for
   a separate review step.
5. A closing `What may still be missing?` section checked against the business
   problem statement, dictionary, standing checks, and values an underwriter would
   find implausible.

## Expected decision outputs from EDA

- Approved exclusion list for identifiers, leakage risks, and audit-only fields.
- Approved null, sentinel, rare-category, and extreme-value treatment rules.
- Validated definitions for application-time ratio features.
- Short list of credible risk concepts to test in modeling, with coverage and
  stability evidence.
- Fairness-audit requirements for model evaluation.
- Explicit unresolved data questions for the sponsor or data owner.

EDA will not produce an approval cutoff, economic value estimate, or reason codes;
those belong to modeling, calibration, and decision-policy stages.
