from copy import deepcopy
from fractions import Fraction as F
import unittest
from reaction_sensitivity_audit import parse_expr, evaluate, parse_swmd, audit, apply_effects
from verify_reaction_sensitivity import ROOT, spec, run, B, T, A


class SensitivityTests(unittest.TestCase):
    def test_exact_parser(self):
        self.assertEqual(evaluate(parse_expr('DIV(ADD(C(1/3),MUL(P(a.b[c]),0.25)),C(2))'),{'a.b[c]':F(2,3)}),F(1,4))
        for bad in ('UNKNOWN(C(0))','ADD(C(1))','C(1) C(2)','P(a)','DIV(C(1),C(2),C(3))'):
            with self.assertRaises(ValueError):parse_expr(bad)

    def test_unsupported_or_missing_consequence(self):
        for raw in ('ORX x/y ->  | O:hi | E:SET none = C(0) | D:C(0)',
                    'ORX x/y -> missing | O:hi | E:SET none = C(0) | D:C(0)'):
            with self.assertRaises(ValueError):parse_swmd('# SWMD-0-MIN\nENC root turn=0..1\n'+raw)

    def test_sequential_and_clipping(self):
        r={'effects':[('a.b','+=',parse_expr('C(2)')),('a.c','=',parse_expr('P(a.b)'))]}
        s,rows=apply_effects(r,{'a.b':F(1,2),'a.c':F(0)})
        self.assertEqual(s,{'a.b':F(1),'a.c':F(1)})
        self.assertEqual(rows[0],('a.b',F(2),F(1,2),True))

    def test_regression_and_repair(self):
        r=run();self.assertTrue(all(r['checks'].values()))
        self.assertEqual(r['factual_ledgers'],26)

    def test_missing_state_rejected(self):
        s=spec(False);del s['initial_states'][0][B]
        with self.assertRaises(ValueError):audit((ROOT/'north_quay_reaction_bad.swmd.min.md').read_text(),s)

    def test_horizon_censoring(self):
        s=spec(True);s['horizon']=0
        r=audit((ROOT/'north_quay_reaction_calibrated.swmd.min.md').read_text(),s)
        self.assertGreater(r['horizon_cuts'],0)
        self.assertEqual(r['endings']['end_archive']['incoming_attempts'],0)

    def test_multistep_and_ties(self):
        text = """# SWMD-0-MIN
ENC start turn=0..0
ORX prepare/first -> hub | O:prepare | E:SET a.b += 0.25 | D:C(0)
ORX prepare/second -> end | O:prepare | E:SET none = C(0) | D:C(0)
ENC hub turn=1..1
ORX open/yes -> end | O:open | E:SET a.b += 0.25 | D:C(0)
ENC end turn=1..2
"""
        s={'entry':'start','horizon':2,'max_effect':'1/4','initial_states':[{'a.b':'0'}],
           'perturbations':{},'guards':{'end':[['a.b','>=','1/2']]}}
        r=audit(text,s)
        self.assertEqual(r['options']['start/prepare']['ties'],1)
        self.assertEqual(r['endings']['end']['witness'],['start/prepare/first','hub/open/yes'])
        s['max_states']=2
        with self.assertRaisesRegex(ValueError,'state cap'):audit(text,s)

    def test_unprobed_variable_is_not_inert(self):
        s=spec(False);del s['perturbations'][T]
        r=audit((ROOT/'north_quay_reaction_bad.swmd.min.md').read_text(),s)
        self.assertEqual(r['options']['hearing/verdict']['variables'][T]['status'],'UNTESTED')


if __name__=='__main__':unittest.main()
