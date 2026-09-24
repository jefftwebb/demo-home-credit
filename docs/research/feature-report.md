# Thin-file repayment-risk features available in this project

## Scope

This report includes only features that can be created from the two available applicant-level tables, `data/raw/application_train.csv` and `data/raw/application_test.csv`. Both have one row per current application and the same predictor columns; only the training table has `TARGET`. The tables are disjoint samples and should not be joined. Dictionary-described history tables are not present and are therefore outside scope. See the [data map](../data/data-map.md).

“Direct” means the source concept is represented by the available columns. “Partial/proxy” means a narrower or imperfect version can be built. No feature values, ratios, aggregates, or models were computed.

## Constructible features

| Feature | Why lenders use it | Availability | Exact tables and columns |
|---|---|---|---|
| External risk scores | Credit scores are disclosed underwriting inputs at Upstart, Enova, and LendingClub. [S1](#s1) [S2](#s2) [S3](#s3) | **Partial: opaque scores** | Both application tables: `EXT_SOURCE_1`, `EXT_SOURCE_2`, `EXT_SOURCE_3`. The sources, timing, and meaning of these normalized scores are undocumented, so they cannot be called FICO, VantageScore, or bureau scores. |
| Credit-bureau inquiry counts and velocity | LendingClub disclosed recent inquiries as an underwriting and loan-grading input. [S3](#s3) | **Direct** | Both tables: `AMT_REQ_CREDIT_BUREAU_HOUR`, `AMT_REQ_CREDIT_BUREAU_DAY`, `AMT_REQ_CREDIT_BUREAU_WEEK`, `AMT_REQ_CREDIT_BUREAU_MON`, `AMT_REQ_CREDIT_BUREAU_QRT`, `AMT_REQ_CREDIT_BUREAU_YEAR`. These support individual window counts and cross-window inquiry patterns. |
| Income amount and type | Upstart and Enova disclose income as an underwriting input. [S1](#s1) [S2](#s2) | **Direct, application-stated** | Both tables: `AMT_INCOME_TOTAL`, `NAME_INCOME_TYPE`. The data do not say whether income was verified. |
| Income-stability proxies | Regulators identify reliable income patterns over time as useful in cash-flow underwriting. [S4](#s4) | **Partial/proxy** | Both tables: `NAME_INCOME_TYPE`, `DAYS_EMPLOYED`, `OCCUPATION_TYPE`, `ORGANIZATION_TYPE`. These describe source and current employment, but not longitudinal income deposits or volatility. `DAYS_EMPLOYED = 365243` is an invalid sentinel documented in the [data map](../data/data-map.md) and must be treated as missing rather than tenure. |
| Employment tenure and job context | Upstart and Enova disclose employment history or tenure as underwriting inputs. [S1](#s1) [S2](#s2) | **Partial: current employment only** | Both tables: `DAYS_EMPLOYED`, `OCCUPATION_TYPE`, `ORGANIZATION_TYPE`, `NAME_INCOME_TYPE`, `FLAG_EMP_PHONE`. These do not provide prior employers, job changes, or unemployment spells. The `DAYS_EMPLOYED` sentinel and associated `ORGANIZATION_TYPE = XNA` require missing-value treatment. |
| Education level | The CFPB reported Upstart's use of education history; Upstart separately disclosed education among its model inputs. [S1](#s1) [S5](#s5) | **Direct but coarse** | Both tables: `NAME_EDUCATION_TYPE`. It represents highest education level, not school, field, grades, credential date, or full history. |
| Housing situation and residence-stability proxies | Enova discloses housing payment and duration of residence as underwriting inputs. [S2](#s2) | **Partial/proxy** | Both tables: `NAME_HOUSING_TYPE`, `FLAG_OWN_REALTY`, `DAYS_REGISTRATION`, `REG_REGION_NOT_LIVE_REGION`, `REG_REGION_NOT_WORK_REGION`, `LIVE_REGION_NOT_WORK_REGION`, `REG_CITY_NOT_LIVE_CITY`, `REG_CITY_NOT_WORK_CITY`, `LIVE_CITY_NOT_WORK_CITY`. `DAYS_REGISTRATION` is time since registration changed, not a documented move-in date; no rent or mortgage payment amount is available. |
| Requested-loan amount, payment burden, and product context | LendingClub disclosed requested amount in loan grading; regulators identify income and recurring obligations as established repayment-capacity inputs. [S3](#s3) [S4](#s4) | **Direct for available components** | Both tables: `AMT_CREDIT`, `AMT_ANNUITY`, `AMT_INCOME_TOTAL`, `AMT_GOODS_PRICE`, `NAME_CONTRACT_TYPE`. These support requested amount, annuity, loan-to-income, payment-to-income, and credit-to-goods-price features. There is no explicit current-loan term, APR, fee, or down-payment field. |
| Application timing | Peer-reviewed research finds application/checkout time predictive of consumer default, including among unscorable applicants. [S6](#s6) | **Direct but coarse** | Both tables: `HOUR_APPR_PROCESS_START`, `WEEKDAY_APPR_PROCESS_START`. There is no full timestamp, timezone, session duration, or event sequence. |
| Local cost-of-living proxies | Upstart disclosed cost of living among its model variables. [S5](#s5) | **Partial/proxy** | Both tables: `REGION_POPULATION_RELATIVE`, `REGION_RATING_CLIENT`, `REGION_RATING_CLIENT_W_CITY`, `NAME_HOUSING_TYPE`, and the building/property fields. These provide regional and housing context, not an explicit cost-of-living index. The proprietary regional ratings cannot be interpreted as cost of living without further documentation. |

## Important exclusions

`application_train.csv.TARGET` is the outcome label for the current loan, not a predictor for that same outcome. `application_test.csv` has no `TARGET`.

Availability does not establish legal permissibility. `CODE_GENDER` and `NAME_FAMILY_STATUS` should not be treated as ordinary risk features, and age has specific restrictions. Regulation B prohibits using a protected basis in evaluating creditworthiness, subject to narrow provisions and exceptions. Fine-grained regional, housing, and other proxy variables also require fair-lending review. [S7](#s7)

## Sources

<a id="s1"></a>**S1 — CFPB / lender practice disclosure.** Consumer Financial Protection Bureau, [*CFPB Announces First No-Action Letter to Upstart Network*](https://www.consumerfinance.gov/archive/newsroom/cfpb-announces-first-no-action-letter-upstart-network/), September 14, 2017. It reports Upstart's use of credit score, income, education, and employment history. The CFPB states that the letter does not endorse particular variables or techniques.

<a id="s2"></a>**S2 — Consumer-lender disclosure.** Enova International, Inc., [*2025 Annual Report*](https://www.sec.gov/Archives/edgar/data/0001529864/000119312526138939/enva_ars-2026.pdf), pp. 19–20. Enova discloses income, housing payment, employment history, external credit scores, debt, recurring expenditures, residence duration, disposable income, and prior performance as consumer-underwriting factors.

<a id="s3"></a>**S3 — Consumer-lending platform disclosure.** LendingClub Corporation, [*2008 Form 10-K*](https://www.sec.gov/Archives/edgar/data/1409970/000095012309014424/c86710e10vk.htm), filed June 29, 2009. Its disclosed criteria and grading inputs include FICO, debt-to-income, requested amount, inquiries, open accounts, utilization, and length of credit history.

<a id="s4"></a>**S4 — Federal banking-regulator guidance.** Federal Reserve, CFPB, FDIC, NCUA, and OCC, [*Interagency Statement on the Use of Alternative Data in Credit Underwriting*](https://www.occ.treas.gov/news-issuances/news-releases/2019/nr-ia-2019-142a.pdf), December 3, 2019. It discusses income and expense activity over time, reliable income patterns, recurring obligations, residual balances, and required compliance controls.

<a id="s5"></a>**S5 — Lending-platform SEC disclosure.** Upstart Holdings, Inc., [*Form 40 application / description of Upstart's AI models*](https://www.sec.gov/Archives/edgar/data/1647639/000119312520285907/d27815d40app.htm), November 5, 2020. Upstart disclosed employment, education history, and cost of living among more than 1,500 raw and combined variables used to assess risk and predict defaults.

<a id="s6"></a>**S6 — Peer-reviewed research.** Tobias Berg, Valentin Burg, Ana Gombović, and Manju Puri, [“On the Rise of FinTechs: Credit Scoring Using Digital Footprints,”](https://doi.org/10.1093/rfs/hhz099) *Review of Financial Studies* 33(7), 2020, 2845–2897.

<a id="s7"></a>**S7 — CFPB / current Regulation B.** Consumer Financial Protection Bureau, [12 C.F.R. § 1002.6, “Rules concerning evaluation of applications”](https://www.consumerfinance.gov/rules-policy/regulations/1002/6/).
