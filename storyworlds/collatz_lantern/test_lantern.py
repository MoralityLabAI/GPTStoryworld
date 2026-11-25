import unittest

from build import build, evaluate, expression, observe, replay


class LanternTest(unittest.TestCase):
    def test_opaque_public_packets(self):
        worlds = [build(1), build(5)]
        for node in ("page_0000", "page_ledger", "page_commit"):
            packets = [observe(w, node, {}) for w in worlds]
            self.assertEqual(packets[0], packets[1])
            self.assertEqual(set(packets[0]), {"scene", "title", "text", "cost", "options"})
            self.assertTrue(all(set(o)=={"action", "text"} for o in packets[0]["options"]))

    def test_informed_choice_and_wrong_chamber(self):
        policy = dict(page_0000="opt_sample", page_amber="opt_west", page_blue="opt_east")
        for seed in (1, 5):
            self.assertEqual(replay(build(seed), policy)["score"], .875)
        policy.update(page_amber="opt_east", page_blue="opt_west")
        for seed in (1, 5):
            self.assertEqual(replay(build(seed), policy)["score"], -.125)

    def test_complete_policy_audit(self):
        audit = evaluate([build(1), build(5)])
        self.assertEqual(audit["native_policies"], 72)
        self.assertEqual(audit["optimal_value"], "7/8")

    def test_source_parser_fails_closed(self):
        for expr in ("RUN(shell)", "P(char_keeper.Hidden)", "C(@unknown)", "ADD(C(1),C(2)"):
            with self.assertRaises((ValueError, KeyError)):
                expression(expr, {})
        with self.assertRaises(ValueError):
            build(7)


if __name__ == "__main__":
    unittest.main()
