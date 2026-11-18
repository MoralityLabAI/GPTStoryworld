"""HGW-03: source-locked authored reaction scope and Dirac metric tests."""
from __future__ import annotations

import json
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_hyperworld import storyworld
from hyperworld_engine import CARDS, CairoHyperworld
from hyperworld_phase import FOCUS_EDGES
from hyperworld_reaction_math import (
    ACTION_AXES, EVENT_CAST, MathScope, audit_summary, dirac_distance_squared,
    plan, reaction_separation_squared, reaction_text, scope_projection_certificate, score,
)


def test_state(recipe, favorable=True):
    return {(owner, ring): F(1 if (coeff > 0) == favorable else -1)
            for owner, ring, coeff in recipe["terms"]}


class ReactionMathTests(unittest.TestCase):
    def test_cast_is_event_specific_and_matches_sources(self):
        self.assertEqual(len(EVENT_CAST), len(CARDS))
        for turn, (lead, partner, pair) in enumerate(EVENT_CAST):
            self.assertEqual(lead, CARDS[turn][1]);self.assertNotEqual(lead, partner)
            self.assertEqual(pair, FOCUS_EDGES[turn])
        self.assertEqual(EVENT_CAST[4][0], "char_neighborhoods")
        self.assertEqual(EVENT_CAST[5][0], "char_youssef")
        self.assertEqual(EVENT_CAST[6][0], "char_nabil")

    def test_all_84_ordinary_reactions_have_variable_scores_and_distinct_outcomes(self):
        world = storyworld()
        n_opts=0; n_reactions=0; seen=set()
        for turn, event in enumerate(world["encounters"][:len(CARDS)]):
            for option in event["options"]:
                action = option["hyperworld_action"]
                n_opts += 1
                self.assertEqual(len(option["reactions"]), 2)
                for i, reaction in enumerate(option["reactions"]):
                    n_reactions += 1
                    self.assertEqual(reaction["desirability_script"]["operator_type"], "Addition")
                    self.assertGreaterEqual(len(reaction["desirability_script"]["operands"]), 5)
                    self.assertEqual(reaction["text_script"]["value"], reaction_text(turn,action,i))
                    self.assertGreaterEqual(len(reaction["after_effects"]),5)
                    self.assertGreaterEqual(len({effect["Set"]["character"] for effect in reaction["after_effects"]}),3)
                    self.assertEqual(reaction["hyperworld_math_scope"]["lead"],CARDS[turn][1])
                    seen.add(reaction["text_script"]["value"])
        self.assertEqual((n_opts,n_reactions),(42,84))
        self.assertEqual(len(seen),n_reactions)

    def test_scope_grows_per_character_and_only_focal_beliefs(self):
        for budget in (1,2,3,4):
            scope=MathScope(vars_per_character=budget)
            for turn in range(len(EVENT_CAST)):
                for action in ACTION_AXES:
                    r=plan(turn,action,0,scope)
                    self.assertEqual(len(r["terms"]),2*budget+2+(1 if turn>=2 else 0))
                    chars={owner for owner,ring,_ in r["terms"] if len(ring)==1}
                    self.assertEqual(chars,set(r["cast"]))
                    p1=[t for t in r["terms"] if len(t[1])==2]
                    self.assertTrue(all(x[0]=="char_nur" and x[1][-1] in r["cast"] for x in p1))
                    p2=[t for t in r["terms"] if len(t[1])==3]
                    self.assertLessEqual(len(p2),1)
                    if p2:self.assertEqual(p2[0][1][1:],r["pair"])

    def test_score_bounds_and_both_responses_reachable(self):
        for turn in range(7):
            for action in ACTION_AXES:
                a,b=plan(turn,action,0),plan(turn,action,1)
                for recipe in (a,b):
                    self.assertLessEqual(sum(abs(c) for _,_,c in recipe["terms"]),F(34,100))
                    self.assertEqual(recipe["offset"],F(1,2))
                for expected in (0,1):
                    state=test_state(a,favorable=expected==0)
                    sa,sb=score(a,state),score(b,state)
                    self.assertTrue(F(16,100)<=sa<=F(84,100))
                    self.assertTrue(F(16,100)<=sb<=F(84,100))
                    self.assertEqual(sa+sb,F(1))
                    self.assertEqual(sa>sb, expected==0)

    def test_dirac_distance_is_exact_positive_and_separated(self):
        audit=audit_summary()
        self.assertEqual((audit["options"],audit["reactions"]),(42,84))
        self.assertGreater(F(audit["min_reaction_separation_squared"]),0)
        for turn in range(7):
            for action in ACTION_AXES:
                a,b=plan(turn,action,0),plan(turn,action,1)
                self.assertEqual(reaction_separation_squared(a,b),4*dirac_distance_squared(a["effects"]))
                self.assertGreater(dirac_distance_squared(a["effects"]),0)
                self.assertLess(dirac_distance_squared(a["effects"]),F(1,100))
        with self.assertRaises(ValueError):dirac_distance_squared((("x",("Axis",),F(1,2)),),{1:F(0)})

    def test_projection_certificate_is_sufficient(self):
        full=plan(4,"audit",0,MathScope(vars_per_character=4))
        small=plan(4,"audit",0,MathScope(vars_per_character=1,pvalue_terms=0,p2value_terms=0))
        state=test_state(full,True)
        certificate=scope_projection_certificate(full,small,state)
        self.assertGreaterEqual(certificate["omitted_preference_bound"],0)
        assert certificate["winner_certified"] is False or score(full,state)>F(1,2)
        same=scope_projection_certificate(full,full,state)
        self.assertTrue(same["winner_certified"])
        self.assertEqual(same["omitted_preference_bound"],0)

    def test_opt_in_runtime_reactions_are_public_reproducible_and_bounded(self):
        first = CairoHyperworld(17, reaction_math=True)
        second = CairoHyperworld(17, reaction_math=True)
        for action in ("brief", "audit", "brief", "charter", "audit", "charter", "charter"):
            self.assertIn(action,first.legal_actions())
            v1=first.step(action);v2=second.step(action)
            self.assertEqual(v1,v2)
            entry=v1["reaction_events"][-1]
            self.assertIn(entry["response"],(0,1))
            self.assertGreater(F(entry["effect_dirac_squared"]),0)
            self.assertLess(F(entry["effect_dirac_squared"]),F(1,100))
            self.assertEqual(sum(map(F,entry["scores"])),F(1))
            self.assertNotIn("private_binary_state",json.dumps(v1))
        self.assertEqual(len(first._reaction_events),7)
        self.assertIsNotNone(first.ending)

    def test_frozen_v02_default_is_identical_with_explicit_flag(self):
        g,h=CairoHyperworld(31),CairoHyperworld(31,reaction_math=False)
        for action in ("brief","audit","brief","charter","audit","charter","charter"):
            self.assertEqual(g.step(action),h.step(action))
        self.assertNotIn("reaction_events",g.view())

    def test_native_verdict_remains_external(self):
        world=storyworld()
        self.assertTrue(world["hyperworld"]["native_verdict_required"])
        verdict=world["encounters"][7]
        self.assertTrue(verdict["options"][0]["hyperworld_native_verdict_required"])
        self.assertEqual(len(verdict["options"][0]["reactions"]),8)
        self.assertNotIn("private_binary_state",json.dumps(world))


if __name__=="__main__":unittest.main()
