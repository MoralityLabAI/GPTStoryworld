"""Operational replay tests, separate from frozen HG-03 policy tests."""
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from spiral_ln import hypergames_qwen_eval as frozen
from spiral_ln.hypergames_qwen_local import Journal, RecordingBackend, run_episode
from spiral_ln.hypergames_single_player import initial_state, observation


class Response(io.BytesIO):
    status = 200


class LocalRecorderTests(unittest.TestCase):
    def test_records_exact_frozen_transport_and_raw_response(self):
        scenario = frozen.scenario_for(101, 'core_140')
        messages = frozen.prompt_messages(observation(scenario, initial_state(0, 4)), 'direct')
        body = {'model': 'qwen3.5-0.8b-q4km-hg03', 'choices': [
            {'message': {'content': '{"action":"abstain"}', 'reasoning_content': 'preserved'}, 'finish_reason': 'stop'}],
            'usage': {'prompt_tokens': 123, 'completion_tokens': 8}}
        seen = []

        def serve(req, timeout):
            seen.append((req.data, timeout))
            return Response(json.dumps(body).encode())

        backend = RecordingBackend(frozen.LocalChatBackend('http://127.0.0.1:8080/v1/chat/completions', body['model']))
        with patch('urllib.request.urlopen', serve):
            answer = backend(messages)
        self.assertEqual(answer.text, '{"action":"abstain"}')
        self.assertEqual(backend.last['response_body'], body)
        self.assertEqual(backend.last['request_body']['messages'], list(messages))
        self.assertEqual(backend.last['request_body']['max_tokens'], 192)
        self.assertEqual(backend.last['request_body']['response_format'], {'type': 'json_object'})
        self.assertEqual(backend.last['request_body']['temperature'], 0)
        self.assertEqual(seen[0][1], 120)
        self.assertIsNotNone(backend.last['raw_response_base64'])

    def test_timeout_retains_attempt_and_fails_closed_without_retry(self):
        backend = RecordingBackend(frozen.LocalChatBackend('http://127.0.0.1:8080/v1/chat/completions', 'x'))
        with tempfile.TemporaryDirectory() as tmp:
            journal = Journal(Path(tmp) / 'journal.jsonl')
            with patch('urllib.request.urlopen', side_effect=TimeoutError('simulated')) as opener:
                episode = run_episode(frozen.scenario_for(101, 'core_140'), 0, 5, 'direct', backend, journal, {})
            journal.close()
            events = [json.loads(x) for x in (Path(tmp) / 'journal.jsonl').read_text().splitlines()]
        self.assertEqual(opener.call_count, 1)
        self.assertEqual(episode['grade']['true_utility'], '0')
        self.assertEqual(episode['grade']['backend_failures'], 1)
        self.assertEqual(episode['trace'][0]['action'], 'abstain')
        self.assertEqual(events[1]['transport']['backend_error']['type'], 'TimeoutError')
        self.assertEqual(events[-1]['event'], 'episode_finished')

    def test_malformed_and_truncated_responses_preserved(self):
        for content, finish, expected in [('broken', 'stop', 'invalid_json'),
                                           ('{"action":"audit"}', 'length', 'truncated_or_filtered')]:
            body = {'model': 'x', 'choices': [{'message': {'content': content}, 'finish_reason': finish}]}
            backend = RecordingBackend(frozen.LocalChatBackend('http://127.0.0.1:8080/v1/chat/completions', 'x'))
            with tempfile.TemporaryDirectory() as tmp:
                journal = Journal(Path(tmp) / 'j.jsonl')
                with patch('urllib.request.urlopen', return_value=Response(json.dumps(body).encode())):
                    result = run_episode(frozen.scenario_for(101, 'core_140'), 0, 5, 'direct', backend, journal, {})
                journal.close()
            self.assertEqual(result['trace'][0]['raw_completion'], content)
            self.assertEqual(result['trace'][0]['decode_error'], expected)
            self.assertEqual(result['grade']['true_utility'], '0')


if __name__ == '__main__':
    unittest.main()
