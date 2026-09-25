# Challenge Lab: portfolio case study

## One-minute pitch

I built an AI-assisted experimentation project for a creator-led consumer product. The product question was whether a seven-day fan challenge could turn one-time content visitors into returning users without undermining commerce economics. I translated that question into a fixed-horizon randomized experiment, built a raw-event-to-user SQL model, implemented statistical and quality gates in Python, and produced a decision report. In the synthetic scenario, retention improved but margin failed, so the recommendation was to redesign rewards rather than ship.

Use this pitch only after reviewing the implementation and being able to explain it. This is a local portfolio demonstration with synthetic data, not a deployed consumer product or evidence of previous employment.

## Evidence from the reproducible run

| Metric | Control | Challenge | Difference | 95% CI for difference |
|---|---:|---:|---:|---:|
| D7 return rate | 20.52% | 22.84% | +2.32 pp | +1.75 to +2.89 pp |
| Contribution per user | $0.895 | $0.536 | −$0.359 | −$0.407 to −$0.310 |
| Users with errors | 2.00% | 2.18% | +0.18 pp | −0.01 to +0.38 pp |
| Purchase conversion, exploratory | 7.49% | 8.37% | +0.89 pp | +0.51 to +1.26 pp |

80,000 synthetic users; 40,323 control and 39,677 treatment. The assignment SRM p-value is 0.0224, above the predeclared 0.001 blocking threshold. Full follow-up and tested integrity checks pass. Allocation is intentionally not forced to be exactly equal. Numeric source: `reports/results.json`.

## Decision memo

**Hold the current reward design.** The challenge improves D7 returns in the simulation, but it loses approximately $0.36 contribution per assigned user. The entire margin interval is below the allowed −$0.10 loss. Even a higher purchase rate does not offset the reward cost.

The next product iteration should test whether digital recognition or exclusive content can preserve the motivation mechanism at lower variable cost. That is a new hypothesis, not a finding from this experiment. Run a fresh test, plan guardrail power from real variance, and add longer-term retention and finalized margin before expansion.

## Why this aligns with the role

| Role requirement | Portfolio evidence |
|---|---|
| Frame ambiguous product questions | A precise release decision, population, metric contract and business tradeoff |
| Strong SQL and Python | Executable raw event schema, user aggregation and reusable analysis functions |
| Own A/B tests end to end | Planning, allocation, quality gates, intervals, non-inferiority gates and recommendation |
| Build repeatable tooling | One-command seeded reproduction, machine-readable scorecard and critical tests |
| AI-native workflow | AI-assisted implementation plus explicit review prompts and evidence checks |
| Product and engineering communication | Executive report, concrete release policy, data contract and follow-up plan |
| Consumer, media, gaming and commerce | Creator acquisition, gamified progression and reward-adjusted unit economics |
| Major cloud stack familiarity | Proposed GCP architecture; not a deployed cloud claim |

## What makes the analysis credible

Every mature assigned user stays in the denominator. Revenue is not substituted for margin. Reward cost is counted even when there is no purchase. A nonsignificant guardrail difference is not called safe; its confidence bound must pass a business-defined threshold. Cohort slices cannot be cherry-picked into a shipping decision. The synthetic result is reproducible and transparently encoded by the generator.

## Interview questions to prepare

1. Why does analyzing only challenge completers bias the estimate? Completion is affected by treatment and user motivation; conditioning on it breaks the randomized comparison.
2. Why is D7 measured 168–192 hours after assignment? It provides equal follow-up per user and avoids calendar-day ambiguity.
3. Why not stop when retention becomes significant? This is a fixed-horizon design; repeated significance-based stopping changes the error rate.
4. Why does conversion rise while margin falls? More purchases do not necessarily cover the reward paid to a broader set of participants.
5. What would change with real data? Identity, event loss, late arrivals, refunds, outliers, interference and guardrail power need explicit validation.
6. What did AI contribute? Framing, drafts, code and communication; deterministic code produced the results. No productivity uplift was measured.

## Honest portfolio description

“Built Challenge Lab, an AI-assisted Python/SQL experimentation project using 80,000 synthetic users. Implemented stable assignment, intention-to-treat metrics, quality checks, confidence intervals and contribution-margin guardrails; delivered a reproducible decision report identifying a retention-versus-cost tradeoff.”

Do not describe this as serving 80,000 real users, shipping to a million users, running a live Beast Industries experiment, or achieving business impact. The screenshot's application questions concern actual experience; this project alone does not establish those qualifications.
