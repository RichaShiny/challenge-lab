import json
import sqlite3
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import ROOT, DAY, assign, compare, decision, sample_size, srm_p

class ExperimentTests(unittest.TestCase):
    def test_stable_assignment(self):
        self.assertEqual(assign('u42'), assign('u42'))
        self.assertEqual(set(assign(str(i)) for i in range(100)), {'control','challenge'})

    def test_srm(self):
        self.assertEqual(srm_p(1000,1000),1)
        self.assertLess(srm_p(900,1100),.001)

    def test_known_mean_difference(self):
        r=compare([0,1,0,1], [1,2,1,2])
        self.assertEqual(r['delta'],1)
        self.assertAlmostEqual(r['upper']-1,1-r['lower'])
        self.assertLess(r['p'],.05)
        self.assertEqual(compare([0,0],[0,0])['p'],1)

    def test_planning(self):
        n=sample_size(.20,.015)
        self.assertTrue(11000 < n < 12000)
        self.assertGreater(sample_size(.20,.01),n)

    def test_sql_boundaries_zero_users_and_immature_users(self):
        conn=sqlite3.connect(':memory:')
        conn.row_factory=sqlite3.Row
        conn.executescript((ROOT/'sql/schema.sql').read_text())
        conn.executemany('INSERT INTO assignments VALUES (?,?,?,?,?)',[
            ('zero','control',0,'video','mobile'),('active','challenge',0,'video','mobile'),
            ('immature','control',DAY,'video','mobile')])
        conn.executemany('INSERT INTO events VALUES (?,?,?,?,?)',[
            ('before','active','session',7*DAY-1,0),
            ('start','active','session',7*DAY,0),
            ('end','zero','session',8*DAY,0),
            ('purchase','active','purchase',DAY,1000),
            ('reward','active','reward',DAY,-100)])
        rows={r['user_id']:dict(r) for r in conn.execute((ROOT/'sql/user_metrics.sql').read_text(),{'as_of':8*DAY})}
        self.assertEqual(set(rows),{'zero','active'})
        self.assertEqual(rows['zero']['retained_d7'],0)
        self.assertEqual(rows['zero']['margin'],0)
        self.assertEqual(rows['active']['retained_d7'],1)
        self.assertEqual(rows['active']['margin'],9)
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO events VALUES ('start','active','session',1,0)")
        conn.close()

    def test_release_gates(self):
        cfg=json.loads((ROOT/'experiment.json').read_text())
        m={'retained_d7':{'lower':.01},'margin':{'lower':-.05},'had_error':{'upper':.002}}
        self.assertEqual(decision(m,{'passed':True},cfg)[0],'STAGED ROLLOUT')
        self.assertEqual(decision(m,{'passed':False},cfg)[0],'INVALID')
        m['margin']['lower']=-.11
        self.assertEqual(decision(m,{'passed':True},cfg)[0],'HOLD')
        m['margin']['lower']=-.05
        m['had_error']['upper']=.005
        self.assertEqual(decision(m,{'passed':True},cfg)[0],'HOLD')
        m['had_error']['upper']=.002
        m['retained_d7']['lower']=0
        self.assertEqual(decision(m,{'passed':True},cfg)[0],'HOLD')

if __name__=='__main__': unittest.main()
