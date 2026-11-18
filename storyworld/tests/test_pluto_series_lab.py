"""Series-level opponent response and counter-adaptation smoke tests."""
import unittest

from storyworld.strategy.series_lab import (
    choose_opening, forecast_responses, illustrative_environment,
    observe_completed_game, opening_values, toy_reverse_sweep,
)
from storyworld.strategy.strategic_dag import Belief


class SeriesTests(unittest.TestCase):
    def test_first_second_order_response_mixture(self):
        b = Belief({"bio": .5, "factory": .5},
                   {"rush": .8, "expand": .2})
        counters = {
            "rush": {"bio": 1, "factory": 0},
            "expand": {"bio": 0, "factory": 1},
        }
        mixture = forecast_responses(b, counters, responsiveness=.9)
        self.assertAlmostEqual(mixture["bio"], .77)
        self.assertAlmostEqual(mixture["factory"], .23)

    def test_opponent_expectation_affects_opening(self):
        belief, payoff, counters = illustrative_environment()
        choice, all_values = choose_opening(belief, payoff, counters)
        self.assertEqual(choice, "9_pool")
        self.assertEqual(set(all_values), set(payoff))
        after = observe_completed_game(belief, "9_pool", "factory")
        next_choice, _ = choose_opening(after, payoff, counters)
        self.assertEqual(next_choice, "12_hatch")
        self.assertGreater(after.second["9_pool"], belief.second["9_pool"])
        self.assertGreater(after.first["factory"], belief.first["factory"])

    def test_reverse_sweep_toy_is_explicitly_synthetic(self):
        result = toy_reverse_sweep()
        self.assertTrue(result["synthetic"])
        a = result["first_and_second_order"]
        b = result["static_first_order"]
        self.assertEqual([g["our_opening"] for g in a["games"]],
                         ["9_pool", "12_hatch", "9_pool"])
        self.assertEqual([g["our_opening"] for g in b["games"]],
                         ["9_pool"] * 3)
        self.assertGreater(a["modeled_reverse_sweep_probability"],
                           b["modeled_reverse_sweep_probability"])

    def test_bad_counter_category_and_response_weight_rejected(self):
        belief, payoff, counters = illustrative_environment()
        bad = {**counters, "9_pool": {"unknown": 1}}
        with self.assertRaises(ValueError):
            forecast_responses(belief, bad)
        with self.assertRaises(ValueError):
            forecast_responses(belief, counters, responsiveness=1.1)
        with self.assertRaises(ValueError):
            opening_values(belief, {"9_pool": payoff["9_pool"]}, counters)

    def test_completed_game_validation_and_epistemic_separation(self):
        belief, _, _ = illustrative_environment()
        updated = observe_completed_game(belief, "9_pool", "factory",
                                         enemy_learning=0, our_learning=1)
        self.assertEqual(updated.second, belief.second)
        self.assertEqual(updated.first["factory"], 1)
        with self.assertRaises(ValueError):
            observe_completed_game(belief, "unknown", "factory")
        with self.assertRaises(ValueError):
            observe_completed_game(belief, "9_pool", "factory", our_learning=-.1)


if __name__ == "__main__":
    unittest.main()
