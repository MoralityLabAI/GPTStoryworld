from fractions import Fraction as F
from copy import deepcopy
import unittest
from provenance_design_audit import Audit, north_quay


class DesignAuditTest(unittest.TestCase):
    def test_threshold_and_copy(self):
        a = Audit(list(north_quay())[0]); r = a.run()
        self.assertEqual(r['root_stop_value'], '1/26')
        self.assertEqual(r['root_q']['hear_reprint'], '1/26')
        self.assertEqual(r['root_q']['inspect_seals'], '5/26')
        self.assertEqual(r['policies']['full']['false'], '1/26')

    def test_instrumental_prerequisite(self):
        a = Audit(list(north_quay())[1]); r = a.run()
        self.assertEqual(r['minimal_optimal_horizon'], 2)
        self.assertEqual(r['policies']['one']['utility'], '1/26')
        self.assertEqual(r['policies']['macro']['utility'], '5/26')
        self.assertNotIn('inspect_seals',a.legal(frozenset(),2))

    def test_complementary_information(self):
        r = Audit(list(north_quay())[2]).run()
        self.assertEqual(r['lookahead_value'], ['0','0','11/64','15/64'])
        self.assertEqual(r['minimal_optimal_horizon'],3)
        self.assertEqual(r['policies']['macro']['utility'],'0')
        self.assertEqual(r['policies']['two']['utility'],'15/64')

    def test_order_invariance_and_dominance(self):
        for v in north_quay():
            r=Audit(v).run(); reverse=deepcopy(v)
            reverse['queries']=dict(reversed(list(v['queries'].items())))
            s=Audit(reverse).run()
            self.assertEqual(r['root_q'],s['root_q'])
            self.assertEqual(r['lookahead_value'],s['lookahead_value'])
            full=F(r['policies']['full']['utility'])
            self.assertTrue(all(full >= F(p['utility']) for p in r['policies'].values()))

    def test_invalid_sidecars(self):
        v=list(north_quay())[1]
        for key,value in [('budget',-1),('worlds',[])]:
            x=deepcopy(v); x[key]=value
            with self.assertRaises(ValueError): Audit(x)
        x=deepcopy(v); x['queries']['catalogue']['requires']=['inspect_seals']
        with self.assertRaises(ValueError): Audit(x)

if __name__ == '__main__': unittest.main()
