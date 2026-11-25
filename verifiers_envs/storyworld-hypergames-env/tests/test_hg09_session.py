import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

from spiral_ln.hg09_session import (
    Journal, read_journal, CodexDispatch, run_episode, hg08_grade, make_prompt,
)
from spiral_ln.hypergames_active_causal import make_problem, _private_goal


def mock_reply(text):
    return {'answer': text, 'valid_transport': True, 'usage': {'input_tokens': 1, 'output_tokens': 2}}


class SessionTests(unittest.TestCase):
    def test_journal_tamper_and_create_only(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'a.jsonl'
            j = Journal(p)
            j.write({'type': 'request', 'prompt': 'public'})
            j.close()
            self.assertEqual(len(read_journal(p)), 1)
            with self.assertRaises(FileExistsError): Journal(p)
            p.write_text(p.read_text().replace('public', 'SECRET'))
            with self.assertRaises(ValueError): read_journal(p)

    def test_hidden_modes_identical_before_audit(self):
        prompts = []
        def dispatch(m, e, prompt):
            prompts.append(prompt)
            return mock_reply('{"action":"abstain"}')
        with tempfile.TemporaryDirectory() as td:
            for bit in (0, 1):
                run_episode({'task': 'HG-02', 'seed': 202611170801, 'dimension': 140,
                             'horizon': 5, 'hidden_mode': bit}, 'test', 'direct',
                            Path(td) / f'{bit}.jsonl', dispatch)
        self.assertEqual(prompts[0], prompts[1])
        self.assertNotIn('hidden_mode', prompts[0])
        self.assertNotIn('final_grade', prompts[0])

    def test_query_response_and_grade_not_in_future_prompt(self):
        prompts = []
        def dispatch(m, e, prompt):
            prompts.append(prompt)
            return mock_reply('{"query_indices":[1,2,3]}' if len(prompts) == 1 else '{"abstain":true}')
        spec = {'task': 'HG-08', 'seed': 202611170801, 'cohort': 'core_140', 'goal_rank': 1, 'budget': 64}
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'episode.jsonl'
            result = run_episode(spec, 'test', 'direct', p, dispatch)
            rows = read_journal(p)
        self.assertEqual(result['query_count'], 1)
        self.assertNotIn('seed', prompts[0])
        self.assertNotIn('true_utility', prompts[1])
        self.assertIn('goal_delta', prompts[1])
        self.assertEqual(rows[-1]['type'], 'final_grade')

    def test_transport_failure_never_scores_as_abstention(self):
        with tempfile.TemporaryDirectory() as td:
            result = run_episode({'task': 'HG-02', 'seed': 17, 'dimension': 140,
                                  'horizon': 4, 'hidden_mode': 0}, 'test', 'direct',
                                 Path(td) / 'x.jsonl', lambda *a: {
                                     'answer': '', 'valid_transport': False, 'usage': None})
        self.assertEqual(result['status'], 'incomplete')
        self.assertNotIn('true_utility', result)

    def test_exact_recovery_is_not_singleton_certificate(self):
        p = make_problem(202611170801, 'core_140', 1)
        real = _private_goal(p)
        grade = hg08_grade(p, [], real)
        self.assertTrue(grade['exact_support'])
        self.assertFalse(grade['release_certified'])
        self.assertEqual(grade['test_correct'], 256)
        probes = [(1 << i, (1,)) for i in range(140) if real[0] >> i & 1]
        self.assertTrue(hg08_grade(p, probes, real)['release_certified'])
        wrong = (real[0] ^ 1 ^ (1 << next(i for i in range(140) if real[0] >> i & 1)),)
        self.assertFalse(hg08_grade(p, [], wrong)['exact_support'])

    def test_codex_usage_nulls_and_tool_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            dispatch = CodexDispatch(td, executable='codex')
            events = [{'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '{"ready":true}'}},
                      {'type': 'turn.completed', 'usage': {'input_tokens': 10, 'output_tokens': 3,
                                                         'reasoning_output_tokens': 1}}]
            proc = SimpleNamespace(stdout='\n'.join(map(json.dumps, events)), stderr='', returncode=0)
            with patch('spiral_ln.hg09_session.subprocess.run', return_value=proc):
                reply = dispatch('gpt-6.1-sol', 'low', 'public')
            self.assertTrue(reply['valid_transport'])
            self.assertIsNone(reply['max_output_tokens'])
            self.assertIsNone(reply['backend_snapshot'])
            events.insert(0, {'type': 'item.started', 'item': {'type': 'command_execution', 'command': 'read secret'}})
            proc.stdout = '\n'.join(map(json.dumps, events))
            with patch('spiral_ln.hg09_session.subprocess.run', return_value=proc):
                self.assertFalse(dispatch('gpt-6.1-sol', 'low', 'public')['valid_transport'])


if __name__ == '__main__': unittest.main()
