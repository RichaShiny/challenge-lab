# AI-assisted workflow with evidence boundaries

## What happened in this project

Codex was used to frame the consumer-product question, draft SQL and Python, implement deterministic analysis and write the stakeholder artifacts. The pipeline executes arithmetic locally; no LLM decides statistical significance or edits the metric values. The source and unit tests are reviewable. No live LLM API, warehouse connection or autonomous production analyst is deployed.

This is an example of AI-assisted project creation. No stopwatch benchmark or productivity improvement was measured, so do not claim a quantified speed-up. Review and understand the code before presenting it as your work.

## Reusable prompt 1: turn ambiguity into a contract

> You are a product analytics partner. The proposed feature is a seven-day fan challenge with a completion reward. Before writing SQL, define the product decision, eligible population, randomization unit, one primary metric, guardrails, exposure window and stopping rule. Separate stated facts from assumptions. Identify selection bias, interference and missing data risks. Do not invent a business-approved threshold.

Human review: approve the framing and operationalize every metric. Document why the recommendation matters for product strategy.

## Reusable prompt 2: audit SQL

> Review sql/user_metrics.sql against docs/experiment-brief.md and sql/schema.sql. Check zero-event users, maturity, time boundaries, post-treatment filtering, grain, reward costs and duplicate handling. Explain each proposed change. Give small counterexamples before changing production SQL.

Human review: compare against fixtures; require that the zero-event and boundary tests pass. Never send raw personal data to the model.

## Reusable prompt 3: write an evidence-bound memo

> Use only reports/results.json. Explicitly label the data synthetic. State the product decision first, then primary effect and confidence interval, margin guardrail, data-quality status, limitations and next experiment. Preserve the release decision in the JSON. Do not infer real customers, revenue impact, causality outside the simulated design or a 100M-user rollout. If a required field is absent, state that it is missing.

Validation: compare every number to the JSON, verify all intervals and units, and confirm that recommendation gates match the code. Any proposed strategy beyond measured outcomes must be labeled a hypothesis.

## Reusable prompt 4: adversarial review

> Argue against shipping this feature using the experiment brief and scorecard. Find ways the retention lift could mislead a product team. Distinguish demonstrated failures from plausible unmeasured risks. Suggest the smallest next test that resolves the main uncertainty.

## Evaluation rubric for future live AI integration

Maintain held-out scorecards with primary nulls, margin failures, error failures, SRM failures and missing metrics. Pass only if the generated memo has zero invented numbers, preserves every blocking gate and distinguishes synthetic/real evidence. Reject or fall back to a deterministic template when any check fails. Log prompt/model version and input hash. A live API integration and automated memo evaluator are proposed extensions, not included features.
