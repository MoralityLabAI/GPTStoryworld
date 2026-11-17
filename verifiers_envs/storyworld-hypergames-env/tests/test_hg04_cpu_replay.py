"""Independent narrow HG-04 repo replay controls."""
import unittest
from fractions import Fraction as Q
from spiral_ln.hypergames_single_player import make_scenario, initial_state, observation, rollout, metric_greedy_action
from hg04_cpu_replay import sufficient, greedy, bucket_identifiable, noisy_episode, scenario, COHORTS

class HG04Replay(unittest.TestCase):
    def test_cohorts(self):
        self.assertEqual([scenario(17,c).dimension for c in COHORTS],[140,512,512,1024,1024])
    def test_sufficient_hidden_pair(self):
        for hidden in (0,1):
            s=make_scenario(17,140)
            self.assertEqual(rollout(s,hidden,sufficient,4)['grade']['true_utility'],'0')
            self.assertEqual(rollout(s,hidden,sufficient,5)['grade']['true_utility'],'9')
    def test_greedy_matches_exact_existing(self):
        s=make_scenario(41,140)
        o=observation(s,initial_state(0))
        self.assertEqual(greedy(s,o),metric_greedy_action(s,o))
    def test_hash_output_type(self):
        self.assertIs(type(bucket_identifiable(make_scenario(17),17,8)),bool)
    def test_noisy_audit_safety_threshold(self):
        s=make_scenario(17)
        self.assertEqual(noisy_episode(s,0,Q(1,2),17),(Q(0),'abstained'))
        self.assertEqual(noisy_episode(s,1,Q(1),17),(Q(9),'success'))

if __name__=='__main__': unittest.main()
