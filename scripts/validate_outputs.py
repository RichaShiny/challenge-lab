"""Validate freshly generated outputs against the actual SQLite data."""
import json
import math
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    result = json.loads((root / 'reports/results.json').read_text())
    config = json.loads((root / 'experiment.json').read_text())
    report = (root / 'reports/decision-report.html').read_text()
    assert result['synthetic'] is True, 'Synthetic-data disclosure is missing'
    assert result['experiment'] == config, 'Scorecard configuration is stale'
    assert '{{' not in report, 'Unresolved template fields'
    assert 'synthetic' in report.lower(), 'Report must disclose synthetic data'
    assert result['decision'] in report, 'Decision missing from report'
    db_path = (root / 'data/experiment.sqlite').resolve()
    with sqlite3.connect(db_path.as_uri() + '?mode=ro', uri=True) as db:
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert not db.execute('PRAGMA foreign_key_check').fetchall()
        counts = dict(db.execute('SELECT variant, COUNT(*) FROM assignments GROUP BY variant'))
        assert sum(counts.values()) == config['users'], 'Incorrect population'
        assert counts == result['quality']['assigned_counts'], 'Assignment counts differ'
        assert counts == result['quality']['mature_counts'], 'Incomplete follow-up'
        assert db.execute('SELECT COUNT(*) FROM events').fetchone()[0] == result['event_count']
        # Independent raw-data reconciliation catches lost users or reward costs.
        raw_margin = dict(db.execute('''
            SELECT a.variant, SUM(e.contribution_cents) / 100.0
            FROM assignments a JOIN events e USING(user_id)
            WHERE e.occurred_at >= a.assigned_at
              AND e.occurred_at < a.assigned_at + 8 * 86400
            GROUP BY a.variant
        '''))
        for variant, n in counts.items():
            assert math.isclose(raw_margin[variant] / n,
                                result['metrics']['margin'][variant], abs_tol=1e-10)
    for name, metric in result['metrics'].items():
        assert all(math.isfinite(v) for v in metric.values()), name
        assert metric['lower'] <= metric['delta'] <= metric['upper'], name
        assert 0 <= metric['p'] <= 1, name
    print('Output checks passed: population, integrity, margin reconciliation, intervals and report.')


if __name__ == '__main__':
    validate()
