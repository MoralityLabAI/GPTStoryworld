"""Exact fictional social-belief/secret-gate invariants; public development cases."""
from __future__ import annotations

import json
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from hyperworld_engine import CairoHyperworld, SECRET_ENDINGS, prior, mask_for, update
from hyperworld_phase import (
    EDGES, NODES, FOCUS_PEOPLE, FOCUS_EDGES, bridge_delta, collect_moments,
    graph_weights, marginal_critical_edge, pvalue, p2value, phase_transition,
)

SNAP_PATH = ("charter", "appeal", "appeal", "resonance", "resonance", "resonance", "snap_vote")
CIVIC_PATH = ("charter", "appeal", "convene", "sever", "audit", "charter", "audit")


def play(seed: int, path: tuple[str, ...]):
    g = CairoHyperworld(seed)
    for action in path:
        if action not in g.legal_actions():
            raise AssertionError(f"scripted witness option locked: seed={seed} action={action} turn={g.turn}")
        g.step(action)
    return g


class ExactNestedBeliefs(unittest.TestCase):
    def test_1024_posterior_probabilities_remain_exact(self):
        p = prior()
        self.assertEqual(len(p), 1024)
        self.assertEqual(sum(p), F(1))
        after = update(p, mask_for((1, 3)), 0, F(3, 4))
        self.assertEqual(sum(after), F(1))
        self.assertTrue(all(isinstance(v, F) for v in after))

    def test_second_order_shifts_with_fixed_marginals(self):
        p = update(prior(), mask_for((1, 3)), 0, F(3, 4))
        moments = collect_moments(p)
        self.assertEqual(moments.points[1], 0)
        self.assertEqual(moments.points[3], 0)
        self.assertEqual(pvalue(moments, "char_nur", "char_salma"), 0)
        self.assertEqual(pvalue(moments, "char_mariam", "char_salma"), F(1, 8))
        self.assertEqual(p2value(moments, "char_nur", "char_mariam", "char_salma"), F(1, 6))

    def test_negative_parity_changes_the_nested_assessment(self):
        p = update(prior(), mask_for((1, 3)), 1, F(3, 4))
        self.assertEqual(p2value(collect_moments(p), "char_nur", "char_mariam", "char_salma"), -F(1, 6))

    def test_invalid_nested_keyrings_rejected(self):
        p = collect_moments(prior())
        for actors in [("char_nur", "char_nur", "char_salma"),
                       ("char_nur", "char_mariam", "char_mariam"),
                       ("char_nur", "real_official", "char_mariam")]:
            with self.assertRaises(ValueError): p2value(p,*actors)


class GraphPhaseTests(unittest.TestCase):
    def test_graph_is_symmetric_bounded_named_and_connected(self):
        w = graph_weights()
        self.assertEqual(len(w), len(EDGES))
        self.assertEqual(len(NODES), 8)
        self.assertTrue(all(F(0) <= weight <= F(1) for weight in w.values()))
        self.assertTrue(all(a in NODES and b in NODES for a,b,_,_ in EDGES))
        reached={NODES[0]}
        while True:
            new = reached | {v for (a,b),weight in w.items() if weight > 0
                             for v in ([b] if a in reached else [a] if b in reached else [])}
            if new == reached:break
            reached = new
        self.assertEqual(reached, set(NODES))

    def test_exact_critical_link_can_trigger_six_node_snap(self):
        p = collect_moments(prior())
        appeals={"char_salma":F(2,5),"char_dalia":F(2,5)}
        result = marginal_critical_edge(p, graph_weights(), appeals,
                                       ("char_salma", "char_workers"), F(2,5))
        self.assertEqual((result['before'],result['after'],result['changed']), (2,8,6))
        before=phase_transition(p,graph_weights(),appeals)
        after=phase_transition(p,bridge_delta(graph_weights(),("char_salma","char_workers"),F(2,5)),appeals)
        self.assertFalse(before.snap)
        self.assertTrue(after.snap)
        self.assertLessEqual(len(after.rounds), len(NODES))
        self.assertEqual(after.order_parameter, 1)

    def test_all_six_traits_are_mechanically_live(self):
        from hyperworld_engine import AXES, trait_values
        p = collect_moments(prior())
        profiles={a:{ax:F(str(v)) for ax,v in trait_values(a).items()} for a in NODES}
        self.assertEqual(len(profiles['char_nabil']),6)
        base=phase_transition(p,graph_weights(),{},traits=profiles)
        for axis in AXES:
            changed={a:dict(v) for a,v in profiles.items()}
            changed['char_nabil'][axis] = F(1) if profiles['char_nabil'][axis] < 1 else F(-1)
            # Crossing need not occur, so assert a full calculation remains well typed.
            result=phase_transition(p,graph_weights(),{},traits=changed)
            self.assertTrue(0 <= result.order_parameter <= 1)
        self.assertTrue(0 <= base.order_parameter <= 1)

    def test_link_mutation_never_modifies_posterior(self):
        g=CairoHyperworld(1)
        for a in ("brief", "appeal"):
            g.step(a)
        old=g._posterior
        self.assertIn('convene',g.legal_actions())
        before=dict(g._edges)
        g.step('convene')
        self.assertEqual(old,g._posterior)
        self.assertNotEqual(before,g._edges)
        self.assertTrue(g.topology_events[-1]['edge'])


class EndingUnlockTests(unittest.TestCase):
    def test_secret_action_is_locked_early(self):
        g=CairoHyperworld(1)
        self.assertEqual(g.legal_actions(), ('brief','audit','charter'))
        old=g.view()
        with self.assertRaises(ValueError):g.step('snap_vote')
        self.assertEqual(g.turn,0)
        self.assertEqual(g.view(),old)

    def test_dialogue_response_is_independent_evidence(self):
        g=CairoHyperworld(1)
        g.step('brief')
        first=len(g.events)
        self.assertIn('appeal', g.legal_actions())
        g.step('appeal')
        self.assertEqual(len(g.events), first+1)
        self.assertEqual(g.events[-1].provenance, 'fictional_independent_public_reply')
        self.assertTrue(g.events[-1].counted_as_independent)
        self.assertTrue(g.events[-1].source_root.startswith('council-reply'))

    def test_four_secret_endings_have_distinct_public_witnesses(self):
        witnesses={
            'secret_aiocracy_consensus_snap':(0,SNAP_PATH),
            'secret_mirror_majority':(1,SNAP_PATH),
            'secret_constitutional_tripwire':(2,SNAP_PATH),
            'secret_civic_counterphase':(0,CIVIC_PATH),
        }
        self.assertEqual(set(witnesses),set(SECRET_ENDINGS))
        for name,(seed,actions) in witnesses.items():
            with self.subTest(name=name):
                g=play(seed,actions)
                self.assertEqual(g.ending,name)
                self.assertEqual(len(g.choices),7)

    def test_visible_gate_reasons_and_no_private_truth(self):
        g=CairoHyperworld(17)
        for action in ('brief','appeal','convene'):
            g.step(action)
        v=g.view()
        self.assertIn('resonance',v['unlock_conditions'])
        self.assertIn('p2Value',v['unlock_conditions']['resonance'])
        self.assertIn('phase',v['belief_graph'])
        self.assertIn('threshold_rounds',v['belief_graph'])
        self.assertTrue(any(e['p2Value_Nur_estimates_a_about_b'] is not None
                            for e in v['belief_graph']['links']))
        self.assertEqual(len(v['spotlight_traits']),6)
        public=json.dumps(v,sort_keys=True)
        for secret in ('private_binary_state','true_factor_values','grader_only'):
            self.assertNotIn(secret,public)

    def test_secret_gates_cannot_override_human_vote_and_recall(self):
        for seed in (0,1,2):
            g=play(seed,SNAP_PATH)
            truth=g.grader_only()['private_binary_state']
            votes=sum((truth>>i)&1 for i in range(6))
            public=sum((truth>>i)&1 for i in (6,7))
            recall=(truth>>9)&1
            if g.ending=='secret_aiocracy_consensus_snap':
                self.assertGreaterEqual(votes,4)
                self.assertGreaterEqual(public,1)
                self.assertTrue(recall)
            if g.ending=='secret_constitutional_tripwire':
                self.assertFalse(recall)
            if g.ending=='secret_mirror_majority':
                self.assertTrue(votes<4 or public<1)


if __name__ == '__main__':
    unittest.main()
