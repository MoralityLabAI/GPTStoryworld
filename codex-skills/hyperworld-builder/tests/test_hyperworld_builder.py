"""Offline reproducibility and player-scrutability gates for the hyperworld skill."""
import json
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from hyperworld_engine import (  # noqa: E402
    ACTIONS, ACTORS, AXES, CARDS, CairoHyperworld, FACTORS, PERSON_IDS,
    STATES, alignment_p2, bit_parity, marginal, mask_for, prior,
    run_scripted, tensor_capacity, update,
)
from build_hyperworld import manifest, storyworld, SCRIPTED_DEMO  # noqa: E402


class ExactPosteriorTests(unittest.TestCase):
    def test_world_space_is_1024_unique_states(self):
        self.assertEqual(len(STATES), 1024)
        self.assertEqual(len(set(STATES)), 1024)
        self.assertEqual(len(FACTORS), 10)
        self.assertEqual(sum(prior()), F(1))

    def test_single_channel_exact_posterior(self):
        out = update(prior(), mask_for((1,)), 1, F(3, 4))
        self.assertEqual(marginal(out, 1), F(3, 4))
        self.assertEqual(marginal(out, 3), F(1, 2))
        self.assertEqual(sum(out), F(1))

    def test_second_order_information_without_marginal_change(self):
        # XOR evidence about two people changes p2 without changing either p1.
        out = update(prior(), mask_for((1, 3)), 0, F(3, 4))
        self.assertEqual(marginal(out, 1), F(1, 2))
        self.assertEqual(marginal(out, 3), F(1, 2))
        self.assertEqual(alignment_p2(out, 'char_mariam', 'char_salma'), F(1, 2))

    def test_prior_p2_neutral_and_bitwise_parity(self):
        self.assertEqual(alignment_p2(prior(), 'char_mariam','char_salma'), F(0))
        self.assertEqual(bit_parity(0b1011, 0b1101), 0)
        self.assertEqual(bit_parity(0b1011, 0b0100), 0)
        self.assertEqual(bit_parity(0b1011, 0b0011), 0)

    def test_reject_bad_posterior(self):
        with self.assertRaises(ValueError): update((F(1),), 1, 1, F(3,4))
        with self.assertRaises(ValueError): update(prior(), 1<<10, 1, F(3,4))
        with self.assertRaises(ValueError): update(prior(), 1, 1, F(1,2))
        with self.assertRaises(ValueError): alignment_p2(prior(),'char_mariam','char_mariam')


class PlayableStoryworldTests(unittest.TestCase):
    def test_character_cast_and_capacity(self):
        self.assertEqual(len(ACTORS),9)
        self.assertEqual(sum(a[3]=='government' for a in ACTORS),6)
        self.assertEqual(sum(a[3]=='public_segment' for a in ACTORS),2)
        self.assertEqual(len(AXES),6)
        cap=tensor_capacity(8,6)
        self.assertEqual(cap['actual'],48)
        self.assertEqual(cap['pValues'],336)
        self.assertEqual(cap['p2Values'],2016)
        self.assertEqual(cap['beliefs_total'],2352)

    def test_observations_do_not_contain_private_oracle(self):
        game=CairoHyperworld(37)
        views=[game.view()]
        for action in SCRIPTED_DEMO:
            views.append(game.step(action))
        for view in views:
            serialized=json.dumps(view)
            self.assertNotIn('private_binary_state',serialized)
            self.assertNotIn('true_factor_values',serialized)
            self.assertNotIn('grader_only',serialized)
            self.assertEqual(view['posterior_state_count'],1024)
        self.assertIn('private_binary_state',game.grader_only())
        self.assertTrue(game.ending)

    def test_repeated_source_not_counted_as_independent(self):
        game=CairoHyperworld(19)
        game.step('brief')
        game.step('brief')
        distribution=game._posterior  # evaluator-only assertion
        game.step('brief')
        self.assertFalse(game.events[2].counted_as_independent)
        self.assertEqual(game._posterior,distribution)
        self.assertEqual(game.events[0].source_root,game.events[2].source_root)
        naive=CairoHyperworld(19,naive_repeat_counting=True)
        for a in ('brief','brief','brief'):naive.step(a)
        self.assertNotEqual(naive._posterior,game._posterior)

    def test_first_order_and_second_order_keyrings(self):
        game=CairoHyperworld(17)
        beliefs=game.view()['first_order_and_second_order_beliefs']
        self.assertEqual(len(beliefs['first_order']),8)
        self.assertGreaterEqual(len(beliefs['second_order']),4)
        self.assertTrue(all(len(b['keyring'])==2 for b in beliefs['first_order']))
        self.assertTrue(all(len(b['keyring'])==3 for b in beliefs['second_order']))
        self.assertTrue(all(-1 <= b['pValue'] <= 1 for b in beliefs['first_order']))
        self.assertTrue(all(-1 <= b['p2Value'] <= 1 for b in beliefs['second_order']))

    def test_seven_turns_and_outcome_guard(self):
        game=CairoHyperworld(17)
        for action in SCRIPTED_DEMO:game.step(action)
        self.assertIsNotNone(game.ending)
        with self.assertRaises(ValueError):game.step('charter')
        with self.assertRaises(ValueError):CairoHyperworld(1).step('override')
        self.assertEqual(game.turn,len(CARDS))

    def test_multiple_outcomes_reachable_under_scripted_rehearsal(self):
        endings=set()
        for seed in range(64):
            game=CairoHyperworld(seed)
            for action in ('charter',)*7:game.step(action)
            endings.add(game.ending)
        self.assertIn('ratified_aiocracy_charter',endings)
        self.assertIn('charter_rejected_by_council',endings)
        self.assertIn('constitutional_recall_review',endings)
        game=CairoHyperworld(1)
        for action in ('audit',)*7:game.step(action)
        self.assertEqual(game.ending,'human_advisory_mandate')

    def test_reproducibility(self):
        self.assertEqual(run_scripted(12,SCRIPTED_DEMO),run_scripted(12,SCRIPTED_DEMO))
        self.assertNotEqual(run_scripted(12,SCRIPTED_DEMO),run_scripted(13,SCRIPTED_DEMO))

    def test_storyworldbuilder_export_has_valid_references(self):
        s=storyworld()
        needed=('IFID','about_text','css_theme','debug_mode','display_mode',
                'creation_time','modified_time','characters','authored_properties','spools','encounters')
        self.assertTrue(all(k in s for k in needed))
        self.assertTrue(any(x['starts_active'] for x in s['spools']))
        encounter_ids={e['id'] for e in s['encounters']}
        self.assertGreaterEqual(len(encounter_ids),12)
        for spool in s['spools']:
            self.assertTrue(set(spool['encounters']) <= encounter_ids)
        for encounter in s['encounters']:
            for option in encounter['options']:
                self.assertGreaterEqual(len(option['reactions']),2)
                for reaction in option['reactions']:
                    self.assertIn(reaction['consequence_id'],encounter_ids)
                    self.assertGreaterEqual(len(reaction['after_effects']),1)

    def test_narrative_pointers_have_existing_characters(self):
        s=storyworld()
        for encounter in s['encounters']:
            for opt in encounter['options']:
                for reaction in opt['reactions']:
                    for effect in reaction['after_effects']:
                        pointer=effect['Set']
                        self.assertIn(pointer['character'],PERSON_IDS)
                        ring=pointer['keyring']
                        self.assertIn(ring[0],AXES)
                        self.assertTrue(all(key in PERSON_IDS for key in ring[1:]))
                        self.assertLessEqual(len(ring),3)
        # True p2 pointers are present in turns 3 and later.
        self.assertTrue(any(len(effect['Set']['keyring'])==3 for encounter in s['encounters']
                            for opt in encounter['options'] for reaction in opt['reactions']
                            for effect in reaction['after_effects']))

    def test_manifest_distinguishes_microstates_from_belief_slots(self):
        m=manifest()
        self.assertEqual(m['posterior_model']['microstates'],1024)
        self.assertEqual(m['belief_tensor_capacity_for_eight_nonplayer_characters']['beliefs_total'],2352)
        self.assertTrue(m['characters_are_fictional'])
        self.assertFalse(m['operational_intelligence_detail'])


if __name__=='__main__':unittest.main()
