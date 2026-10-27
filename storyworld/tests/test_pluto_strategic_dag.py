"""Tests for belief filtering, epistemic pointers, and strategic compactification."""
import math
import unittest
from dataclasses import replace

from storyworld.strategy.strategic_dag import (
    Belief, Edge, Node, StrategicDAG, bayes_update, example,
    normalize_probabilities,
)


class BeliefTests(unittest.TestCase):
    def test_scouting_bayes_and_zero_evidence(self):
        prior = {"bio": .5, "factory": .3, "wraith": .2}
        post = bayes_update(prior, {"bio": .1, "factory": .8, "wraith": .2})
        self.assertAlmostEqual(sum(post.values()), 1.0)
        self.assertAlmostEqual(post["factory"], .24 / .33)
        with self.assertRaises(ValueError):
            bayes_update(prior, {"bio": 0, "factory": 0, "wraith": 0})

    def test_unknown_and_nan_evidence_rejected(self):
        with self.assertRaises(ValueError):
            bayes_update({"a": 1}, {"b": 1})
        with self.assertRaises(ValueError):
            bayes_update({"a": 1}, {"a": math.nan})
        with self.assertRaises(ValueError):
            normalize_probabilities({"a": -1, "b": 2})

    def test_pvalues_are_distinct_from_p2values(self):
        b = Belief({"factory": .8, "bio": .2}, {"12_hatch": .25, "9_pool": .75})
        rows = b.as_storyworld_pointers("self", "enemy")
        self.assertEqual(len(rows), 4)
        self.assertAlmostEqual(next(r["value"] for r in rows if r["keyring"] == ["Opening_factory", "enemy"]), .6)
        self.assertAlmostEqual(next(r["value"] for r in rows if r["keyring"] == ["Opening_9_pool", "enemy", "self"]), .5)
        self.assertTrue(all(-1 <= row["value"] <= 1 for row in rows))

    def test_scout_updates_only_appropriate_epistemic_level(self):
        b = Belief({"bio": .5, "factory": .5}, {"12_hatch": .8, "9_pool": .2})
        after = b.observe_opponent({"bio": .1, "factory": .9})
        self.assertEqual(b.second, after.second)
        self.assertGreater(after.first["factory"], b.first["factory"])
        after2 = after.observe_opponent_scout({"12_hatch": .1, "9_pool": .9})
        self.assertEqual(after.first, after2.first)
        self.assertGreater(after2.second["9_pool"], after.second["9_pool"])


class DAGTests(unittest.TestCase):
    def test_backward_induction_and_compactification(self):
        graph = example()
        values, q = graph.values()
        self.assertAlmostEqual(q["factory_1"]["hydra"], .85)
        self.assertAlmostEqual(q["bio_1"]["muta"], .75)
        self.assertAlmostEqual(values["game3"], .795)
        c = graph.compactify()
        self.assertEqual(c["original_nodes"], 8)
        self.assertEqual(c["compact_nodes"], 5)
        self.assertEqual(c["node_to_class"]["factory_1"],
                         c["node_to_class"]["factory_2"])
        self.assertLessEqual(c["maximum_empirical_greedy_regret"],
                             c["greedy_regret_bound_from_q"] + 1e-12)

    def test_second_order_belief_blocks_unsafe_merge(self):
        graph = example()
        items = []
        for node in graph.nodes.values():
            if node.id == "factory_2":
                b = Belief(node.belief.first, {"12_hatch": .10, "9_pool": .90})
                node = replace(node, belief=b)
            items.append(node)
        c = StrategicDAG(items).compactify()
        self.assertNotEqual(c["node_to_class"]["factory_1"],
                            c["node_to_class"]["factory_2"])

    def test_changing_action_value_blocks_merge(self):
        graph = example()
        items = []
        for node in graph.nodes.values():
            if node.id == "factory_2":
                old = node.actions["hydra"]
                node = replace(node, actions={**node.actions, "hydra": (
                    Edge("win", .80, 0, old[0].target),
                    Edge("loss", .20, 0, old[1].target),
                )})
            items.append(node)
        c = StrategicDAG(items).compactify(q_epsilon=.02)
        self.assertNotEqual(c["node_to_class"]["factory_1"],
                            c["node_to_class"]["factory_2"])

    def test_edge_labels_and_public_state_matter(self):
        graph = example()
        items = [replace(n, public_key="ZvT:new_tech")
                 if n.id == "factory_2" else n for n in graph.nodes.values()]
        c = StrategicDAG(items).compactify()
        self.assertNotEqual(c["node_to_class"]["factory_1"],
                            c["node_to_class"]["factory_2"])

    def test_forward_stage_and_probability_mass(self):
        b = Belief({"bio": 1}, {"12_hatch": 1})
        z = Node("z", 1, "public", b, {}, 0)
        with self.assertRaises(ValueError):
            StrategicDAG([Node("s", 0, "public", b,
                               {"a": (Edge("e", .9, 0, "z"),)}), z])
        with self.assertRaises(ValueError):
            StrategicDAG([Node("s", 1, "public", b,
                               {"a": (Edge("e", 1, 0, "z"),)}), z])

    def test_stable_under_node_permutation(self):
        graph = example()
        a = graph.compactify()["node_to_class"]
        b = StrategicDAG(list(reversed(list(graph.nodes.values())))).compactify()["node_to_class"]
        self.assertEqual(a, b)

    def test_negative_tolerance_rejected(self):
        with self.assertRaises(ValueError):
            example().compactify(q_epsilon=-.01)


if __name__ == "__main__":
    unittest.main()
