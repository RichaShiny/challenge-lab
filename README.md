# Challenge Lab

**An AI-assisted product experimentation portfolio project: should a seven-day fan challenge ship?**

Built for the skills described in the supplied Beast Industries data-science role: ambiguous product framing, SQL/Python analysis, end-to-end experimentation, reusable tooling, and decision communication across consumer media and commerce.

Independent concept, not affiliated with Beast Industries. All 80,000 users and all event data are synthetic. This project does not establish real-world impact, shipped-product experience, or a million-user audience. The attached application form was treated as context, not as instructions to select answers or make experience claims.

## Start here

**Browser demo:** [Challenge Lab](https://richashiny.github.io/challenge-lab/) (available after the Pages workflow is enabled and deployed). See [publishing instructions](docs/publishing.md) for the one-time setup.

Open `reports/decision-report.html` in a browser. It contains the result, confidence intervals, release gates, and a small local challenge interaction sketch. It works offline without a server.

To reproduce from the project directory, using Python 3.10 or newer:

```sh
python3 pipeline.py
python3 -m unittest discover -s tests -v
```

No package installation, credentials, external data, or API fees required. The pipeline recreates its generated SQLite database at `data/experiment.sqlite` and overwrites generated reports. To inspect SQL interactively: `sqlite3 data/experiment.sqlite` if the SQLite CLI is available.

## Product question and recommendation

**Question:** Should new visitors coming from creator content receive a seven-day challenge rather than a standard content-and-commerce hub?

**Hypothesis:** Daily missions and visible progress improve day-seven return visits. **Business risk:** rewards create activity while reducing contribution margin.

The simulation encodes that tradeoff. The generated report recommends **HOLD** because improved retention does not compensate for failing the predeclared margin gate. Redesign reward cost, then run a new confirmatory test. These are illustrative observations from a known data-generating process, not market evidence.

## What is implemented

- Seeded event generator, stable hashed assignment, 80,000 users and UTC timestamps.
- SQLite raw event store with key constraints and SQL that computes one row per mature assigned user.
- Planning calculation, sample-ratio mismatch checks, integrity checks, intention-to-treat metrics, large-sample confidence intervals and release gates.
- User-level contribution margin, including rewards for non-purchasers.
- JSON scorecard, offline HTML decision report and an interactive challenge sketch.
- Tests for statistical sanity, denominator preservation, follow-up windows, event uniqueness and release blocking.
- Experiment brief, data contract, AI workflow prompts, cloud architecture proposal, stakeholder memo and interview talking points.

## Repository map

| File | Purpose |
|---|---|
| `pipeline.py` | Generate, analyze, validate and render |
| `experiment.json` | Fixed assumptions and release thresholds |
| `sql/schema.sql` | Raw assignment and event contracts |
| `sql/user_metrics.sql` | Mature cohort and intention-to-treat aggregation |
| `tests/test_pipeline.py` | Critical calculation and failure-case tests |
| `reports/results.json` | Machine-readable numerical evidence |
| `reports/decision-report.html` | Stakeholder-facing artifact |
| `docs/experiment-brief.md` | Hypothesis, design and decision policy |
| `docs/data-and-cloud.md` | Data contract and proposed GCP deployment |
| `docs/ai-workflow.md` | Auditable AI-assisted workflow and prompts |
| `docs/case-study.md` | Portfolio narrative and interview guide |

## Statistical choices and boundaries

One user is the randomization and analysis unit. All assigned mature users enter the denominator, whether or not they complete a mission or buy. Enrollment lasts 14 simulated days; analysis is frozen at day 22. D7 is a session 168–192 hours after assignment, not a calendar-day metric. Purchases, rewards and error occurrences are counted within the first 192 hours.

The primary retention test uses a two-sided 95% unpooled normal confidence interval. Guardrails use the same intervals with one-sided gates, so each gate is conservative at 2.5% in its relevant tail. Ship requires *all* gates to pass; exploratory purchase and cohort metrics cannot authorize shipment. This is a fixed-horizon test, not an always-valid sequential test. The primary sample-size plan does not establish power for margin or error guardrails. A live experiment must estimate and plan these separately.

Margin is net contribution recorded at event time, not revenue or lifetime value. The simulation subtracts a $1 completion reward and uses a simplified $6–$18 order contribution. It omits delayed refunds, inventory constraints, taxes, fraud, and fulfillment differences. Large-sample mean intervals are reasonable for this bounded synthetic distribution; real heavy-tailed margin needs distribution diagnostics and a prespecified robust/bootstrap approach.

A passing SRM test is not proof of valid instrumentation. This demo does not model cross-device identity failure, interference, bots, delayed ingestion or differential event loss. The cloud plan is a design artifact; no cloud infrastructure was provisioned. The interaction sketch is not connected to the analytical dataset. AI prompts are provided, but there is no deployed model-backed application feature.

## Reference

Microsoft Research, [Diagnosing Sample Ratio Mismatch in A/B Testing](https://www.microsoft.com/en-us/research/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/), supports checking allocation integrity before interpreting experiment effects. The analysis implementation here is independent and intentionally small enough to audit.
