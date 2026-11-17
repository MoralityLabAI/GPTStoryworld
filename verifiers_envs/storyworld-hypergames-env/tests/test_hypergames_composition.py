"""Independent adversarial and exact finite controls for HG-06."""
import json
import unittest
from fractions import Fraction as Q
from itertools import combinations

from spiral_ln.evaluation_hypergames_composition import (
 fragment_weight_floor,exact_shortest_xor,short_fragment_certificate,parity_disagreement_probability,
 independent_parity_collision,spurious_fit_union_bound,exact_signed_candidates,
 posterior_joint_predictive_accuracy,certified_joint_goal_capacity)
from spiral_ln.hypergames_composition import (
 VERSION,SEED_START,COHORTS,RANKS,POOLS,TRAIN_SIZES,instance,samples,
 signatures,fit,_candidate_combinations,random_composite_bases,evaluate_condition,aggregate,run,N_TEST)
from spiral_ln.evaluation_hypergames_rank import rank,deficiency

class HG06MathTests(unittest.TestCase):
 def test_weight_barrier_for_every_d6_pair(self):
  target=(1<<6)-1
  pairs=tuple((1<<i)|(1<<j) for i,j in combinations(range(6),2))
  self.assertEqual(fragment_weight_floor(target,2),3)
  self.assertIsNone(exact_shortest_xor(target,pairs,6,2))
  self.assertIsNotNone(exact_shortest_xor(target,pairs,6,3))
  self.assertTrue(short_fragment_certificate(target,pairs,6,2)['weight_obstructed'])
  self.assertFalse(short_fragment_certificate(target,pairs,6,3)['weight_obstructed'])
 def test_exact_fibre_after_three_and_missing_one(self):
  target=63
  pairs=(3,12,48)
  self.assertEqual(certified_joint_goal_capacity(pairs,(target,),6)['optimal_joint_success'],Q(1))
  self.assertEqual(certified_joint_goal_capacity(pairs[:2],(target,),6)['optimal_joint_success'],Q(1,2))
 def test_independent_all_two_rows_small(self):
  count=0
  for d in range(1,5):
   for a in range(1<<d):
    for b in range(1<<d):
     for n in (0,1,2):
      self.assertEqual(parity_disagreement_probability(a,b,d,n),independent_parity_collision(a,b,d,n))
      count+=1
  self.assertEqual(count,3*sum(4**d for d in range(1,5)))
 def test_union_bound_capped_and_exact(self):
  self.assertEqual(spurious_fit_union_bound(1,1,4),Q(1,16))
  self.assertEqual(spurious_fit_union_bound(5,1,64),Q(9,1<<64))
  self.assertEqual(spurious_fit_union_bound(100,8,8),Q(1))
 def test_bayes_signed_posterior(self):
  support=exact_signed_candidates((1,2), (0,), (0,), 2)
  self.assertEqual(set(support),{(1,0),(2,0)})
  self.assertEqual(posterior_joint_predictive_accuracy(support,2),Q(3,4))
 def test_boundaries(self):
  with self.assertRaises(ValueError):fragment_weight_floor(-1,2)
  with self.assertRaises(ValueError):parity_disagreement_probability(4,0,2,3)
  with self.assertRaises(ValueError):spurious_fit_union_bound(2,-1,5)
  with self.assertRaises(ValueError):exact_signed_candidates((1,1),(0,),(0,),2)
  with self.assertRaises(ValueError):posterior_joint_predictive_accuracy((),2)

class HG06AppliedTests(unittest.TestCase):
 def test_registration_grid(self):
  self.assertEqual(VERSION,'HG-06/compositional-parity-v1')
  self.assertEqual((len(COHORTS),len(RANKS),len(POOLS),len(TRAIN_SIZES)),(5,4,2,4))
 def test_all_registered_pair_fragment_bases(self):
  for cohort in COHORTS:
   for k in RANKS:
    for pool in POOLS:
     d,t,frags,full,missing=instance(SEED_START,cohort,k,pool)
     self.assertEqual(len(full),len(missing))
     self.assertTrue(all(row.bit_count()==2 for row in full+missing))
     self.assertTrue(all(goal.bit_count()==6 for goal in t))
     self.assertEqual(len(set(t)),k)
     self.assertEqual(deficiency(full,t,d),0)
     self.assertEqual(deficiency(missing,t,d),k)
     self.assertEqual(rank(t,d),k)
 def test_fixed_pool_same_core_and_padded(self):
  for k in RANKS:
   a=instance(SEED_START,'core_140',k,'fixed')
   for cohort in ('padded_512','padded_1024'):
    b=instance(SEED_START,cohort,k,'fixed')
    self.assertEqual(a[1:],b[1:])
  data140=samples(SEED_START,140)
  data512=samples(SEED_START,512)
  self.assertEqual(data140,tuple(x & ((1<<140)-1) for x in data512))
 def test_no_target_row_in_dictionary(self):
  d,t,frags,full,missing=instance(SEED_START,'core_140',4,'ambient')
  self.assertTrue(set(t).isdisjoint(full))
 def test_triple_fit_train_oracle_n64(self):
  d,t,frags,full,missing=instance(SEED_START,'core_140',4,'fixed')
  ss=samples(SEED_START,d)
  fsign=signatures(full,ss)
  target=signatures(t,ss)
  candidates=_candidate_combinations(full,fsign,3)
  for ts in target:
   ids,mask,signature,invert=fit(candidates,ts,64)
   self.assertEqual(invert,0)
   self.assertEqual(mask, t[target.index(ts)])
 def test_random_rank_match_100(self):
  d,t,frags,full,missing=instance(SEED_START,'native_512',4,'ambient')
  sigs=signatures(full,samples(SEED_START,d))
  bases=tuple(random_composite_bases(full,sigs,d,4,SEED_START,'native_512:512','ambient'))
  self.assertEqual(len(bases),100)
  self.assertTrue(all(rank(tuple(row[1] for row in b),d)==4 for b in bases))
 def test_public_only(self):
  d,t,frags,full,missing=instance(SEED_START,'core_140',1,'fixed')
  self.assertNotIn('private_seed',json.dumps({'library':full,'targets':t}))
 def test_heldout_eval_small(self):
  rows=evaluate_condition(SEED_START,'core_140',1,'fixed')
  self.assertEqual(len(rows),24)
  o=next(r for r in rows if r['arm']=='privileged_goal_oracle' and r['train_n']==64)
  task=next(r for r in rows if r['arm']=='task_xor3' and r['train_n']==64)
  self.assertEqual((o['test_correct'],task['test_correct']),(N_TEST,N_TEST))
  self.assertTrue(all(r['deficiency']==1 for r in rows if r['arm']=='missing_component_xor3'))
 def test_one_seed_padding_invariance(self):
  rows=run(seeds=(SEED_START,),cohorts=('core_140','padded_512','padded_1024'),ranks=(1,),pools=('fixed',))
  # aggregate expects the complete grid; compare direct subsets here.
  m={(r['cohort'],r['arm'],r['train_n']):r for r in rows}
  for arm in ('task_xor1','task_xor2','task_xor3','missing_component_xor3','shuffled_label_xor3'):
   for n in TRAIN_SIZES:
    a=m['core_140',arm,n]
    for co in ('padded_512','padded_1024'):
     b=m[co,arm,n]
     self.assertEqual((a['test_correct'],a['release'],a['true_utility']),
                      (b['test_correct'],b['release'],b['true_utility']))

if __name__=='__main__':unittest.main()
