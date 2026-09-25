# Experiment brief: fan challenge v1

## Frame before querying

“Can we engage the audience?” is too broad. The decision is whether to replace the onboarding experience for newly eligible visitors with a seven-day challenge. Our measurable near-term target is return behavior after the first week; commerce margin and reliability constrain the decision. Audience size is not an experiment sample size: only eligible, randomized product visitors count.

For this demonstration, users are fictional first-time visitors, eligibility precedes assignment, and identity is stable. A live trial needs documented age/market eligibility, identity rules, bot exclusions defined before assignment, consent handling, and a server-side enrollment event emitted before variant rendering.

## Treatment and allocation

Control: standard content-and-commerce hub. Treatment: daily creative mission, seven-step progress and a completion reward. Stable SHA-256 hashing of experiment ID plus user ID provides 50/50 assignment in the demo. A real service should persist the assignment, use a server-side keyed hash and prevent rerandomization. Enrollment is 14 days followed by eight days for the last user to mature. No efficacy decisions are made before the frozen cutoff.

## Outcomes and predeclared decision policy

| Role | Definition | Required to ship |
|---|---|---|
| Primary | User has a session in [168,192) hours from assignment | Lower 95% CI of treatment − control > 0 |
| Margin guardrail | Sum of purchase contribution and reward costs in [0,192) hours / assigned user | Lower CI > −$0.10 per user |
| Error guardrail | Any error in [0,192) hours / assigned user | Upper CI < +0.005 absolute |
| Diagnostic | Purchase in [0,192) hours / assigned user | Exploratory, no shipping gate |

Thresholds are illustrative business assumptions, not company-approved values. A live experiment requires finance/product agreement on acceptable loss and a power plan for each gate. The 1.5 pp MDE is a planning effect size, not a minimum observed lift threshold.

Planning: baseline retention 20%, MDE 1.5 pp, two-sided alpha 5%, power 80%, equal groups. Formula uses the pooled mean under the alternative for the critical-value term and arm-specific Bernoulli variance for the power term. The generated scorecard reports the required per-arm count.

Quality blocking conditions: either SRM p < 0.001, orphan events, pre-assignment events, incomplete cohort maturation, or insufficient mature sample. Unique assignment/event constraints reject duplicates at ingestion. No treatment-on-the-treated analysis: restricting to completers would select a post-treatment variable.

## Interpretation and follow-up

No peeking-based efficacy stopping. Operational safety monitoring in a real trial is separate from formal efficacy inference. All gates must pass, so a nonsignificant margin difference is not enough: we need evidence that loss is below the accepted margin. There is one confirmatory efficacy metric. Purchase and channel slices are exploratory; do not select a winning cohort from them. A follow-up interaction hypothesis needs its own power and multiplicity plan.

If the gates pass, recommend a staged rollout rather than immediate full deployment. If margin fails, redesign rewards and rerandomize in a new experiment. Follow with D28 retention and finalized margin to distinguish a durable habit from short-term incentive response. Do not extrapolate the synthetic lift to a 100M-person audience.
