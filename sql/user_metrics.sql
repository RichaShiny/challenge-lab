-- Intent-to-treat: retain every mature assigned user, including users with zero events.
-- Timestamps are UTC epoch seconds; :as_of is the frozen analysis cutoff.
-- D7 = at least one session in [assignment + 7 days, assignment + 8 days).
WITH mature AS (
 SELECT * FROM assignments WHERE assigned_at + 8 * 86400 <= :as_of
)
SELECT a.user_id, a.variant, a.channel, a.device,
 MAX(CASE WHEN e.event_name = 'session'
    AND e.occurred_at >= a.assigned_at + 7 * 86400 THEN 1 ELSE 0 END) AS retained_d7,
 MAX(CASE WHEN e.event_name = 'purchase' THEN 1 ELSE 0 END) AS purchased,
 MAX(CASE WHEN e.event_name = 'challenge_complete' THEN 1 ELSE 0 END) AS completed,
 MAX(CASE WHEN e.event_name = 'error' THEN 1 ELSE 0 END) AS had_error,
 COALESCE(SUM(e.contribution_cents), 0) / 100.0 AS margin
FROM mature a
LEFT JOIN events e ON a.user_id = e.user_id
 AND e.occurred_at >= a.assigned_at
 AND e.occurred_at < a.assigned_at + 8 * 86400
GROUP BY a.user_id, a.variant, a.channel, a.device;
