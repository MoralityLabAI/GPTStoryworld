"""HG-09 independent finite source checks. Intentionally outside broad test_* discovery."""
from __future__ import annotations
import csv,json,random,sys,unittest,os
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from run_hg09_cpu import gf2_fit,parity_predictions,score_world
from verify_hg09_fsi01 import audit,unpack


class HG09Checks(unittest.TestCase):
    def test_gf2_solver_recovers_known_parity(self):
        for dim in (6,12,18):
            rng=random.Random(dim)
            true_support=sum(1<<i for i in rng.sample(range(dim),min(dim,6)))
            rows=[1<<i for i in range(dim)]
            rows.extend(rng.getrandbits(dim) for _ in range(dim))
            y=[(x&true_support).bit_count()%2 for x in rows]
            rank,recovered=gf2_fit(rows,y,dim)
            self.assertEqual((rank,recovered),(dim,true_support))

    def test_rank_deficient_abstains(self):
        rank,mask=gf2_fit([0,1,2,3],[0,0,1,1],8)
        self.assertLess(rank,8)
        self.assertIsNone(mask)

    def test_causal_scope_by_input_bit(self):
        mask=(1<<1)|(1<<3)|(1<<7)|(1<<9)|(1<<13)|(1<<17)
        xs=(0,3,141,2**19-1)
        pred=parity_predictions(xs,mask)
        target=parity_predictions([x^(1<<3) for x in xs],mask)
        irrelevant=parity_predictions([x^(1<<4) for x in xs],mask)
        self.assertTrue((pred!=target).all())
        self.assertTrue((pred==irrelevant).all())

    def test_pack_unpack_little_endian(self):
        from run_hg09_cpu import pack_bits
        import numpy as np
        bits=np.zeros(256,dtype=np.uint8)
        bits[[0,1,7,8,128,255]]=1
        self.assertEqual(unpack(pack_bits(bits)),bits.tolist())

    def test_single_preceding_development_smoke(self):
        reg=json.loads((ROOT/'Hypergames/single_player/hg09_registration_v1.json').read_text())
        # This unit-test world is disjoint from all 64 registered confirmation worlds.
        world,correct,select=score_world(2026113997,reg)
        self.assertEqual(world['GF2_rank'],140)
        self.assertEqual(world['arms']['sparse_gf2_compiled']['test_correct'],256)
        self.assertEqual(world['arms']['sparse_gf2_compiled']['causal_selectivity'],256)
        self.assertEqual(world['arms']['scrambled_six_support']['causal_selectivity'],0)

    def test_archived_world_roster_and_fsi(self):
        if not os.environ.get('EVALMATH_FSI_FILE'):
            self.skipTest('EvalMath pinned file available in dedicated CI')
        x=audit(ROOT/'Hypergames/single_player/hg09_registration_v1.json',ROOT/'output/evaluation_hypergames/hg09/hg09_paired_bits.csv',ROOT/'output/evaluation_hypergames/hg09/hg09_worlds.json')
        self.assertEqual(x['worlds'],64)
        self.assertEqual(x['H1']['verdict'],'confirmed')
        self.assertEqual(x['H2']['verdict'],'confirmed')
        self.assertEqual(x['totals']['sparse_gf2_compiled']['correct'],16384)
        self.assertEqual(x['totals']['loop_task']['correct'],8240)

if __name__=='__main__':unittest.main()
