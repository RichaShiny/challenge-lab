"""Reproducible synthetic experiment. Python 3.10+, no third-party dependencies."""
import argparse
import hashlib
import html
import json
import math
import random
import sqlite3
import statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DAY = 86400
START = int(datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp())

def assign(user_id):
    bucket = int.from_bytes(hashlib.sha256(f'fan_challenge_v1:{user_id}'.encode()).digest()[:8], 'big')
    return 'challenge' if bucket < 2**63 else 'control'

def sample_size(baseline, mde, alpha=.05, power=.8):
    """Normal-approximation two-sided binary test, equal groups, per-arm size."""
    p1, p2 = baseline, baseline + mde
    mean = (p1 + p2) / 2
    norm = statistics.NormalDist()
    return math.ceil(((norm.inv_cdf(1-alpha/2)*math.sqrt(2*mean*(1-mean)) +
                       norm.inv_cdf(power)*math.sqrt(p1*(1-p1)+p2*(1-p2))) / mde)**2)

def compare(control, treatment):
    """Independent user-level means, large-sample unpooled CI and normal test."""
    if min(len(control), len(treatment)) < 2:
        raise ValueError('Each arm needs at least two users')
    c, t = statistics.mean(control), statistics.mean(treatment)
    se = math.sqrt(statistics.variance(control)/len(control) + statistics.variance(treatment)/len(treatment))
    delta = t-c
    p = math.erfc(abs(delta/se)/math.sqrt(2)) if se else (1.0 if delta == 0 else 0.0)
    return dict(control=c, challenge=t, delta=delta, lower=delta-1.95996398454*se,
                upper=delta+1.95996398454*se, p=p)

def srm_p(control_n, treatment_n):
    total = control_n+treatment_n
    if not total:
        raise ValueError('Empty assignment table')
    chi2 = (control_n-treatment_n)**2/total
    return math.erfc(math.sqrt(chi2/2))

def decision(metrics, quality, cfg):
    if not quality['passed']:
        return 'INVALID', 'Resolve data-quality or maturity failures before interpreting effects.'
    if metrics['retained_d7']['lower'] <= 0:
        return 'HOLD', 'The primary retention metric has not demonstrated a positive effect.'
    if metrics['margin']['lower'] <= -cfg['margin_noninferiority_dollars']:
        return 'HOLD', 'Retention improved, but contribution margin did not pass the predeclared non-inferiority gate. Redesign reward cost and retest.'
    if metrics['had_error']['upper'] >= cfg['error_noninferiority_absolute']:
        return 'HOLD', 'The error-rate guardrail did not establish non-inferiority.'
    return 'STAGED ROLLOUT', 'All predeclared gates passed; begin a limited rollout with long-term monitoring.'

def generate(conn, cfg):
    rng = random.Random(cfg['seed'])
    conn.executescript((ROOT/'sql/schema.sql').read_text())
    assignments, events = [], []
    def event(uid, name, at, cents=0):
        events.append((f'e{len(events):09}', uid, name, at, cents))
    for i in range(cfg['users']):
        uid = f'u{i:07}'
        variant = assign(uid)
        treatment = variant == 'challenge'
        at = START+rng.randrange(cfg['enrollment_days']*DAY)
        channel = rng.choices(['video','organic','creator_link'], [0.6,0.25,0.15])[0]
        device = rng.choices(['mobile','desktop'], [.82,.18])[0]
        assignments.append((uid, variant, at, channel, device))
        # DGP deliberately encodes a retention/cost tradeoff, not an empirical finding.
        event(uid, 'session', at)
        if treatment and rng.random() < .48:
            event(uid, 'challenge_complete', at+rng.randrange(1,7*DAY))
            event(uid, 'reward', at+7*DAY, -100)
        if rng.random() < .20 + .027*treatment + .025*(channel=='organic'):
            event(uid, 'session', at+7*DAY+rng.randrange(DAY))
        if rng.random() < .075+.008*treatment:
            event(uid, 'purchase', at+rng.randrange(8*DAY), rng.choice([600,1000,1400,1800]))
        if rng.random() < .020+.001*treatment:
            event(uid, 'error', at+rng.randrange(8*DAY))
    conn.executemany('INSERT INTO assignments VALUES (?,?,?,?,?)', assignments)
    conn.executemany('INSERT INTO events VALUES (?,?,?,?,?)', events)
    conn.commit()

def analyze(conn, cfg):
    as_of = START+(cfg['enrollment_days']+cfg['followup_days'])*DAY
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute((ROOT/'sql/user_metrics.sql').read_text(), {'as_of':as_of})]
    groups = {v:[r for r in rows if r['variant']==v] for v in ['control','challenge']}
    counts = {v:len(g) for v,g in groups.items()}
    all_counts = dict(conn.execute('SELECT variant,COUNT(*) FROM assignments GROUP BY variant'))
    required = sample_size(cfg['baseline_d7'],cfg['mde_absolute'],cfg['alpha'],cfg['power'])
    quality = dict(assigned_counts=all_counts, mature_counts=counts,
        srm_p=srm_p(all_counts.get('control',0),all_counts.get('challenge',0)),
        mature_srm_p=srm_p(counts['control'],counts['challenge']),
        orphan_events=conn.execute('SELECT COUNT(*) FROM events e LEFT JOIN assignments a USING(user_id) WHERE a.user_id IS NULL').fetchone()[0],
        preassignment_events=conn.execute('SELECT COUNT(*) FROM events e JOIN assignments a USING(user_id) WHERE occurred_at < assigned_at').fetchone()[0],
        complete_followup=len(rows)==sum(all_counts.values()), required_per_arm=required)
    quality['passed'] = bool(quality['srm_p']>=cfg['srm_alpha'] and quality['mature_srm_p']>=cfg['srm_alpha']
        and quality['orphan_events']==quality['preassignment_events']==0 and quality['complete_followup'] and min(counts.values())>=required)
    metrics = {key:compare([r[key] for r in groups['control']], [r[key] for r in groups['challenge']])
               for key in ['retained_d7','margin','had_error','purchased']}
    status, rationale = decision(metrics,quality,cfg)
    segments = []
    for channel in sorted({r['channel'] for r in rows}):
        a = [r['retained_d7'] for r in groups['control'] if r['channel']==channel]
        b = [r['retained_d7'] for r in groups['challenge'] if r['channel']==channel]
        segments.append(dict(channel=channel, n=len(a)+len(b), **compare(a,b)))
    return dict(synthetic=True, experiment=cfg, as_of=as_of, quality=quality, metrics=metrics,
                decision=status, rationale=rationale, segments=segments,
                event_count=conn.execute('SELECT COUNT(*) FROM events').fetchone()[0])

def render(result):
    q,m = result['quality'],result['metrics']
    def fmt(x,key,delta=False):
        return f'${x:+.3f}' if key=='margin' else f'{x*100:+.2f} pp' if delta else f'{x*100:.2f}%'
    rows=''
    for key,label in [('retained_d7','D7 return rate · primary'),('margin','Contribution / assigned user · guardrail'),('had_error','Users with errors · guardrail'),('purchased','Purchase conversion · exploratory')]:
        v=m[key]
        rows += '<tr><td>'+label+'</td>'+''.join(f'<td>{fmt(v[k],key,k in ["delta","lower","upper"])}</td>' for k in ['control','challenge','delta'])+f'<td>{fmt(v["lower"],key,True)} to {fmt(v["upper"],key,True)}</td></tr>'
    seg=''.join(f'<tr><td>{html.escape(s["channel"])}</td><td>{s["n"]:,}</td><td>{s["delta"]*100:+.2f} pp</td><td>{s["lower"]*100:+.2f} to {s["upper"]*100:+.2f} pp</td></tr>' for s in result['segments'])
    template=(ROOT/'report_template.html').read_text()
    replacements = {'DECISION':result['decision'],'RATIONALE':result['rationale'],'ROWS':rows,'SEGMENTS':seg,
        'USERS':f'{sum(q["mature_counts"].values()):,}', 'EVENTS':f'{result["event_count"]:,}',
        'SRM':f'{q["srm_p"]:.3f}', 'SAMPLE':f'{q["required_per_arm"]:,}',
        'RETENTION':f'{m["retained_d7"]["delta"]*100:+.2f}', 'MARGIN':f'${m["margin"]["delta"]:+.3f}',
        'QUALITY':'PASS' if q['passed'] else 'FAIL'}
    for k,v in replacements.items(): template=template.replace('{{'+k+'}}',str(v))
    return template

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'data/experiment.sqlite')
    args=parser.parse_args()
    cfg=json.loads((ROOT/'experiment.json').read_text())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists(): args.output.unlink()
    with sqlite3.connect(args.output) as conn:
        generate(conn,cfg)
        result=analyze(conn,cfg)
    (ROOT/'reports/results.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'reports/decision-report.html').write_text(render(result))
    print(json.dumps({k:result[k] for k in ['decision','rationale','quality','metrics']},indent=2))

if __name__=='__main__': main()
