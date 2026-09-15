# Business Problem Statement: Home Credit Loan Repayment Risk

**Sponsor:** Home Credit, credit risk function (case sponsor) · **Analytics owner:** [team] · **Version:** 1.1 draft, 15 Sept 2026

## Business problem

Home Credit lends to consumers with little or no credit history, the people banks typically turn away. It does this at scale: after selling its India and Kazakhstan units in 2025, the group operates in the Czech Republic, Slovakia, and Vietnam with EUR 6.7 billion in net loans, and more than 60 percent of its European online purchase-finance transactions are approved with no human involvement.

The business rests on one decision, repeated hundreds of thousands of times a year: whether to approve an applicant without a conventional credit file. The errors are asymmetric. Approving someone who does not repay forfeits most of the principal on an unsecured loan. Declining someone who would have repaid forfeits the margin, the relationship, and the inclusion mission, and pushes that person toward predatory lenders.

Home Credit's portfolio is not in distress; its non-performing loan ratio fell to 5.1 percent in 2025. The opportunity is that every improvement in ranking risk among thin-file applicants converts directly into fewer losses at the same approval rate, or more approvals at the same loss rate. To size that opportunity, Home Credit released an anonymized sample of 307,511 approved loans with 122 application fields (income, employment, housing, bureau scores, telco and transactional signals) and six linked tables of prior credit and repayment history. About 8.1 percent (roughly 24,800 loans) developed payment difficulties. That is the baseline to beat.

## Benefit of a solution

A calibrated risk score lets the credit risk team act on each application according to its actual risk rather than applying one rule to everyone: decline, verify, or restructure the riskiest slice while leaving the rest untouched, and approve low-risk applicants near the current decline boundary. It also produces stated reasons per decision, which the revised EU Consumer Credit Directive will require for automated creditworthiness assessments from 20 November 2026.

The trade-off is economic, not statistical. Illustratively, if the net loss on a bad loan is five times the contribution on a good one, declining is worth it only when predicted risk exceeds about 17 percent, double the portfolio average. Most applicants should still be approved; the model's job is to isolate the tail. The actual ratio is Home Credit's to supply, and the recommended cut-off moves with it.

## Success metrics

Evaluated on loans the model did not see during development:

| Measure | Comparator | Target |
| --- | --- | --- |
| Payment-difficulty rate at a 90 percent approval rate | 8.1 percent (approve all) | At least 1.5 points lower |
| Net value per 1,000 applications, sponsor's margin and loss assumptions | Zero (approve all) | Positive, including with loss severity 50 percent higher |
| Good loans lost per bad loan avoided | Not measured today | Reported at every candidate cut-off |
| Calibration across risk bands | Not measured today | Predicted and observed rates within 1 point |
| Approval and error rates by gender and age band | Not measured today | Material gaps flagged before any recommendation |

Model gate, secondary: out-of-sample AUC of at least 0.75 (strongest public solutions reach about 0.80). Two models with the same AUC can differ substantially in portfolio value once the cut-off and costs are applied.

## Analytics approach

Estimate, at application time, the probability that a loan develops payment difficulties, using the application record and summarized prior credit history. Then convert probabilities into a decision table: for each cut-off, expected approval rate, losses avoided, good loans lost, and net value. The credit risk team picks the operating point. The work predicts; it does not explain why customers default or estimate the effect of any intervention.

## Scope

**Delivers:** scored file for the 48,744 held-out applications; the cut-off decision table; a decision memo with the recommended operating point and its sensitivity to assumptions; reason codes per high-risk application.

**Excludes:** amount, price, and term optimization; fraud; collections; inference about declined applicants (the sample holds only approved loans, so the value of added approvals is a projection, not a measurement); production deployment. Additions require an approved revision.

## Delivery details

[Analytics lead] owns the analysis; credit risk owns policy and use. Constraints: the data are historical and anonymized, with no stated currency or market, so results size the opportunity rather than a current profit figure; the label is early payment difficulty, not write-off, so loss severity must come from the sponsor; automated credit scoring is a high-risk use under the EU AI Act, with obligations from December 2027, so any production path needs governance beyond this project.

Milestones: assumptions confirmed [date]; interim review [date]; final delivery [date].

*Sources: PPF Financial Holdings Annual Report 2025 (audited); Home Credit Czech Republic 2025 results release; Directive (EU) 2023/2225; Regulation (EU) 2024/1689 as amended; Kaggle Home Credit Default Risk data documentation.*
