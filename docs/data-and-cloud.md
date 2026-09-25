# Data contract and cloud path

## Local implementation

`assignments`: one record per fictional user; primary-key user ID; variant in {control, challenge}; assigned_at in UTC epoch seconds; acquisition channel and device captured before treatment.

`events`: unique event ID; assignment foreign key; UTC occurrence timestamp; event name in {session, challenge_complete, purchase, reward, error}; integer contribution cents. Purchases carry positive contribution after modeled variable costs, rewards carry negative cost, other events carry zero. Amounts are USD only. The generator follows these rules; a production ingestion layer must validate event-type/amount consistency, schema version and required fields too.

The SQL left-joins events onto mature assignments, explicitly preserves zero-event users, caps the outcome window and aggregates at the randomization unit. Only the generated analytical rows are compared. Cohort labels are pre-treatment attributes. There is no personal data.

## Proposed GCP implementation — not deployed

```text
Client/server events → Pub/Sub → immutable GCS archive
                            ↓
                     BigQuery raw tables
                            ↓
              scheduled SQL / Dataform models
                            ↓
             user-level experiment outcome table
                            ↓
                  Cloud Run analysis job
                            ↓
                JSON scorecard + decision memo
```

This is a conceptual deployment path, not tested infrastructure or a claim of cloud operating experience. Event ingestion should add both event time and ingestion time, idempotency keys, schema versions, consent state and explicit experiment exposure. Partition raw tables by event date, cluster by experiment/user identifiers, and apply controlled retention. Separate assignment from rendering and verify exposure logging symmetrically.

A production model should reconcile enrollment counts with the assignment service, track latency and late-arrival completeness by arm, quarantine malformed events, monitor unexpected variant changes, and compare telemetry health to independent operational logs. Recompute after a fixed late-arrival grace period; record the frozen data version and query hash.

Access controls: least-privilege service accounts, pseudonymous analytical IDs, protected identity mapping, audit logging and deletion propagation. Use BigQuery dry runs/query budgets, partition pruning and scheduled materialization. Product events at a large audience size can be expensive; size from measured eligible event volume, not subscriber count.

## Suggested next implementation milestones

1. Replace synthetic input with a documented, consented pilot dataset and ingestion adapter.
2. Deploy assignment and telemetry with integration tests and an A/A experiment.
3. Validate user identity, logging parity, data latency and warehouse reconciliation.
4. Estimate real metric variances and guardrail power; approve thresholds before launch.
5. Add delayed refunds, fraud/reward abuse and long-term retention.

None of these milestones is claimed complete by the local demonstration.
