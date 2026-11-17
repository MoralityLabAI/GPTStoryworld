"""Source replay tests for the HG-08 frozen independent-world receipt."""
import importlib.util,os,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
@unittest.skipUnless(os.getenv('EVALMATH_FSI_FILE') and Path(os.environ.get('EVALMATH_FSI_FILE','')).is_file(),
                     'optional EvalMath path is exercised in the dedicated HG08 CI')
class HG08FSITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from verify_hg08_fsi01 import audit
        cls.receipt=audit()
    def test_32_independent_worlds(self):
        self.assertEqual(self.receipt['n_worlds'],32)
        self.assertEqual(self.receipt['n_case_rows_per_test'],8192)
    def test_preregistered_effects_and_bonferroni(self):
        h=self.receipt['fsi01']
        self.assertAlmostEqual(h['H1']['cluster_macro_effect'],44/8192)
        self.assertAlmostEqual(h['H2']['cluster_macro_effect'],49/8192)
        self.assertTrue(all(h[k]['p_bonferroni'] > .05 for k in ('H1','H2')))
        self.assertTrue(all(h[k]['verdict']!='confirmed' for k in ('H1','H2')))
    def test_accuracy_and_exact_gf2(self):
        w=self.receipt['worlds']
        self.assertEqual([sum(x['correct'][i] for x in w) for i in range(3)],[4063,4107,4156])
        self.assertEqual(len({x['seed'] for x in w}),32)
    def test_no_calibration_release(self):
        for w in self.receipt['worlds']:
            for c in w['calibration']:
                self.assertFalse((c+1)/258 > 3/5)
    def test_no_absent_private_data(self):
        self.assertIn('Public 32-world synthetic parity',self.receipt['scope'])
if __name__=='__main__':unittest.main()
