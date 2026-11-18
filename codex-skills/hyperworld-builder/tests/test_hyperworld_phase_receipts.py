"""Cairo HGW-02 dynamic option and public trace regression guards."""
import sys
import unittest
from pathlib import Path
from fractions import Fraction as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from hyperworld_engine import CairoHyperworld
from hyperworld_phase import p2value
from build_hyperworld import secret_witnesses
from play_hyperworld import POLICIES, choose_scripted


class HyperworldIntegrationTests(unittest.TestCase):
    def test_all_secret_witnesses_are_live(self):
        scenarios=secret_witnesses()
        self.assertEqual(len(scenarios['witnesses']),4)
        for w in scenarios['witnesses']:
            self.assertEqual(w['ending'],w['final_ending'])
            self.assertTrue(all(step['public_unlock']['unlocked'] for step in w['steps']))
            self.assertTrue(all(0 <= step['support_after'] <= 8 for step in w['steps']))
            self.assertNotIn('private',repr(w))

    def test_public_nested_beliefs_match_mechanic(self):
        g=CairoHyperworld(1)
        for action in ('brief','appeal','appeal'):
            g.step(action)
        for belief in g.view()['first_order_and_second_order_beliefs']['second_order']:
            actual=p2value(g._moments,'char_nur',belief['believer'],belief['target'])
            self.assertAlmostEqual(belief['p2Value'],float(actual),places=5)

    def test_all_actions_have_a_public_fallback(self):
        for seed in range(4):
            for path in POLICIES.values():
                game=CairoHyperworld(seed)
                for target in path:
                    chosen=choose_scripted(game,target)
                    self.assertIn(chosen,game.legal_actions())
                    game.step(chosen)
                self.assertEqual(game.turn,7)
                self.assertIsNotNone(game.ending)

    def test_graph_is_belief_projection_only(self):
        g=CairoHyperworld(0)
        for action in ('charter','appeal','convene'):
            g.step(action)
        secret=g.grader_only()['private_binary_state']
        old=g._posterior
        weights=dict(g._edges)
        g.step('sever')
        self.assertEqual(g.grader_only()['private_binary_state'],secret)
        self.assertEqual(g._posterior,old)
        self.assertNotEqual(g._edges,weights)


if __name__=='__main__':unittest.main()
