"""Unit tests for exact 1,024-state rational filtrations, Brier identity, and Dirac metrics."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys
import unittest

CARBON_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CARBON_DIR / "src"))

from carbon_hypergames.filtrations import (  # noqa: E402
    EvidenceEvent,
    NUM_WORLDS,
    bit_marginal,
    causal_twin_parameters,
    clifford_dirac_distance_sq,
    evaluate_bounded_inclination,
    indices_to_mask,
    minimum_interventional_probes,
    pair_correlation_moment,
    posterior_from_events,
    project_social_beliefs,
    uniform_prior,
    verify_delayed_revision_brier_identity,
)


class TestFiltrationsAndBrier(unittest.TestCase):
    def test_uniform_prior_normalization(self) -> None:
        prior = uniform_prior()
        self.assertEqual(len(prior), NUM_WORLDS)
        self.assertEqual(sum(prior, Fraction(0, 1)), Fraction(1, 1))
        self.assertEqual(bit_marginal(prior, 0), Fraction(1, 2))

    def test_xor_parity_shifts_p2_without_moving_first_order_marginals(self) -> None:
        evs = [
            EvidenceEvent(
                event_id="ev_xor",
                turn=1,
                slot_id="slot_xor",
                source_root="root_1",
                mask=indices_to_mask([0, 1]),
                reported_bit=0,  # Z_0 == Z_1 with reliability 7/8
                reliability=Fraction(7, 8),
                hop_depth=2,
            )
        ]
        post = posterior_from_events(evs, mode="exact_full_bayes")
        self.assertEqual(sum(post, Fraction(0, 1)), Fraction(1, 1))
        # First-order marginals stay strictly 1/2!
        self.assertEqual(bit_marginal(post, 0), Fraction(1, 2))
        self.assertEqual(bit_marginal(post, 1), Fraction(1, 2))
        # Pair correlation moment shifts to 1 - 2*(1/8) = +3/4!
        self.assertEqual(pair_correlation_moment(post, 0, 1), Fraction(3, 4))

        proj = project_social_beliefs(
            post,
            principal_ids=["c0", "c1", "c2"],
            trait_name="Trust",
            protagonist_id="protag",
        )
        self.assertEqual(proj["pvalues"]["protag"][("Trust", "c0")], Fraction(0, 1))
        self.assertEqual(proj["pvalues"]["protag"][("Trust", "c1")], Fraction(0, 1))
        self.assertEqual(proj["p2values"]["protag"][("Trust", "c0", "c1")], Fraction(3, 8))

    def test_provenance_dedup_prevents_relay_inflation(self) -> None:
        # 4 relays of false bit=0 at q=5/8 vs 1 independent audit of true bit=1 at q=7/8
        evs = [
            EvidenceEvent(
                event_id=f"echo_{i}",
                turn=1,
                slot_id="slot_echo",
                source_root="shared_echo_root",
                mask=indices_to_mask([0]),
                reported_bit=0,
                reliability=Fraction(5, 8),
                is_relay_duplicate=(i > 0),
            )
            for i in range(4)
        ] + [
            EvidenceEvent(
                event_id="audit_1",
                turn=2,
                slot_id="slot_audit",
                source_root="independent_audit_root",
                mask=indices_to_mask([0]),
                reported_bit=1,
                reliability=Fraction(7, 8),
            )
        ]
        p_naive = bit_marginal(posterior_from_events(evs, mode="first_order_relay_naive"), 0)
        p_dedup = bit_marginal(posterior_from_events(evs, mode="exact_full_bayes"), 0)
        self.assertLess(p_naive, Fraction(1, 2))
        self.assertGreater(p_dedup, Fraction(3, 4))

    def test_eval_rev01_pythagorean_brier_identity(self) -> None:
        cert = verify_delayed_revision_brier_identity(n_slots=4, revised_slot=0)
        self.assertTrue(cert["exact_zero_residual"])
        self.assertTrue(cert["strict_positive_info_loss"])
        self.assertTrue(cert["named_slot_collision_distinct_posteriors"])

    def test_causal_twins_and_qi02_probe_floor(self) -> None:
        twins = causal_twin_parameters()
        self.assertEqual(twins["observational_agreement"], Fraction(25, 32))
        self.assertEqual(twins["direct_do_delta"], Fraction(9, 16))
        self.assertEqual(twins["confounded_do_delta"], Fraction(0, 1))
        probe = minimum_interventional_probes(Fraction(5, 100))
        self.assertGreaterEqual(int(probe["integer_probe_floor"]), 16)

    def test_bounded_inclinations_and_clifford_dirac_norm(self) -> None:
        i0, i1, l1 = evaluate_bounded_inclination(
            features={"x": Fraction(1, 1), "y": Fraction(-1, 1)},
            linear_terms={"x": Fraction(20, 100), "y": Fraction(-10, 100)},
            bilinear_terms={("x", "y"): Fraction(4, 100)},
        )
        self.assertEqual(i0 + i1, Fraction(1, 1))
        self.assertLessEqual(l1, Fraction(34, 100))
        self.assertGreaterEqual(i0, Fraction(16, 100))
        self.assertLessEqual(i0, Fraction(84, 100))
        with self.assertRaises(ValueError):
            evaluate_bounded_inclination(
                features={"x": Fraction(1, 1)},
                linear_terms={"x": Fraction(35, 100)},
            )

        d_sq = clifford_dirac_distance_sq(
            {
                ("c0", "Duty"): Fraction(1, 10),
                ("protag", "pTrust", "c0"): Fraction(1, 5),
                ("protag", "p2Trust", "c0", "c1"): Fraction(1, 4),
            }
        )
        # (1 * 1/10)^2 + (3/2 * 1/5)^2 + (2 * 1/4)^2 = 1/100 + 9/100 + 25/100 = 35/100 = 7/20
        self.assertEqual(d_sq, Fraction(7, 20))


if __name__ == "__main__":
    unittest.main()
