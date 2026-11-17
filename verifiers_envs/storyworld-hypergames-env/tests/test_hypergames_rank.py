"""HG-05 CPU harness boundary, rank, leakage and paired padding controls."""
from __future__ import annotations
import unittest
from fractions import Fraction as Q
from spiral_ln.evaluation_hypergames_rank import deficiency, rank
from spiral_ln.hypergames_rank import (
    COHORTS, TRAIN_SIZES, N_CAL, N_TEST, N_RANDOM, MASK_TEST, candidate_library,
    evaluate_condition, fit_basis, goal_masks, predict, random_bases, report, run,
    sample_vectors, score_signed, signatures, spec,
)


class HG05Harness(unittest.TestCase):
    def test_registered_full_rank(self):
        for cohort in COHORTS:
            d, _ = spec(cohort)
            for k in (1, 2, 4, 8, 16):
                self.assertEqual(rank(goal_masks(2026111700, cohort, k), d), k)

    def test_padded_samples_are_nested(self):
        seed=2026111701
        xs=sample_vectors(seed,140)
        a=sample_vectors(seed,512)
        b=sample_vectors(seed,1024)
        self.assertEqual(xs, tuple(y & ((1<<140)-1) for y in a))
        self.assertEqual(xs, tuple(y & ((1<<140)-1) for y in b))
        self.assertEqual(len(xs),16+N_CAL+N_TEST)

    def test_pool_preserves_core_features_when_fixed(self):
        for k in (1,2,8,16):
            base=goal_masks(2026111701,'core_140',k)
            self.assertEqual(base,goal_masks(2026111701,'padded_512',k))
            self.assertEqual(base,goal_masks(2026111701,'padded_1024',k))
            for d in ('padded_512','padded_1024'):
                self.assertEqual(candidate_library(2026111701,'core_140',k,'fixed'),
                                 candidate_library(2026111701,d,k,'fixed'))

    def test_dictionary_size_and_no_gold(self):
        for cohort,k in [('core_140',1),('native_512',4),('native_1024',16)]:
            for pool in ('fixed','ambient'):
                dict1=candidate_library(2026111700,cohort,k,pool)
                dict0=candidate_library(2026111700,cohort,k,pool,False)
                expected=k+(4*k if pool=='fixed' else max(4*k,spec(cohort)[0]//8))
                self.assertEqual(len(dict1),expected)
                self.assertEqual(len(dict0),expected)
                self.assertTrue(set(goal_masks(2026111700,cohort,k)).issubset(set(dict1)))
                self.assertFalse(set(goal_masks(2026111700,cohort,k))&set(dict0))
                self.assertTrue(all(x.bit_count()==6 for x in dict1+dict0))

    def test_random_basis_rank_and_repeated_draws_allowed(self):
        k=1; d=140; seed=2026111700
        lib=candidate_library(seed,'core_140',k,'fixed')
        bases=tuple(random_bases(lib,k,d,seed,'core_140','fixed'))
        self.assertEqual(len(bases),100)
        self.assertTrue(all(rank(b,d)==k for b in bases))
        self.assertLessEqual(len(set(bases)),len(lib))

    def test_full_public_observer_rank_grid(self):
        for seed in (2026111700,2026111701):
            for cohort in ('core_140','padded_512','native_512'):
                for k in (1,4,16):
                    rows=evaluate_condition(seed,cohort,k,'fixed')
                    self.assertEqual(len(rows),12)
                    self.assertTrue(all(r['basis_rank']==k for r in rows))
                    self.assertTrue(all(Q(r['random_rank_based_p']).denominator in (1,101) for r in rows))
                    self.assertTrue(all(0<=r['test_correct']<=N_TEST for r in rows))

    def test_frozen_pair_invariance(self):
        for k in (1,2,4,8,16):
            rows=[evaluate_condition(2026111700,cohort,k,'fixed')
                  for cohort in ('core_140','padded_512','padded_1024')]
            for j in range(12):
                for b in rows[1:]:
                    for field in ('test_correct','test_bit_correct','cal_correct','release',
                                  'true_utility','deficiency'):
                        self.assertEqual(rows[0][j][field],b[j][field])

    def test_training_only_fitter_ignores_test_labels(self):
        seed=2026111701; cohort='core_140'; k=4; d=140
        goals=goal_masks(seed,cohort,k)
        lib=candidate_library(seed,cohort,k,'fixed')
        xs=sample_vectors(seed,d)
        sig=signatures(tuple(set(lib+goals)),xs)
        gold={m:sig[m] for m in goals}
        fitted=fit_basis(lib,sig,goals,gold,8,seed)
        # Arbitrarily alter all heldout bits; feature basis cannot change.
        modified={m:(val ^ (MASK_TEST << (16+N_CAL))) for m,val in sig.items()}
        gold_mod={m:modified[m] for m in goals}
        self.assertEqual(fitted,fit_basis(lib,modified,goals,gold_mod,8,seed))
        self.assertEqual(predict(fitted,sig,goals,gold,8)['cal_correct'],
                         predict(fitted,modified,goals,gold_mod,8)['cal_correct'])

    def test_oracle_ceiling(self):
        rows=evaluate_condition(2026111700,'native_1024',16,'ambient')
        for r in rows:
            if r['arm']=='oracle_task':
                self.assertEqual((r['deficiency'],r['test_correct'],r['false_accept']), (0,64,0))
                self.assertEqual(r['true_utility'],'10')

    def test_signed_training_tie_rule(self):
        self.assertEqual(score_signed(0,0,4),(0,0))
        self.assertEqual(score_signed(0,15,4),(0,1))
        self.assertEqual(score_signed(0,3,4),(2,0))

    def test_toy_summary_provides_seed_level_and_padding_checks(self):
        rows=run(seeds=(2026111700,),cohorts=('core_140','padded_512','padded_1024'),ranks=(1,),pools=('fixed',))
        summary=report(rows)
        self.assertEqual(summary['counts']['seed_arm_rows'],36)
        self.assertEqual(summary['counts']['matched_padding_comparisons'],6)
        self.assertTrue(summary['gates']['fixed_pool_padding_invariance'])

    def test_reject_malformed(self):
        with self.assertRaises(ValueError):spec('missing')
        with self.assertRaises(ValueError):goal_masks(1,'core_140',0)
        with self.assertRaises(ValueError):candidate_library(1,'core_140',1,'wrong')
        with self.assertRaises(ValueError):sample_vectors(True,33)


if __name__=='__main__': unittest.main()
