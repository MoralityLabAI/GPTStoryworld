"""Offline contracts for the GGUF Neuron Explorer TSUN-01B adapter."""
from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from integrations.gguf_neuron_explorer import runner


PROTOCOL = {"experiment_id": "TSUN-01B", "steering": {
    "condition": "when: assistant", "units": "author-reported gne relative doses",
    "neurons": [{"layer": i + 35, "neuron": i + 100, "relative_dose": 0.1} for i in range(24)]},
    "sampling": {"max_output_tokens": 256}}


class FakeEpisode:
    def __init__(self):
        self.phase = "S0"
        self.traits = {"Pride": 0.85, "Care": 0.75}
        self.actions = []

    def observation(self):
        return {"phase": self.phase, "scene": "Reina faces an irreversible choice.",
                "time_to_departure": 3, "available_actions": self.available_actions(),
                "flags": {"secret_outcome": True}, "traits": self.traits}

    def available_actions(self):
        return {"S0": ["INSPECT_CARD"], "S1": ["ANNOUNCE_MINIMAL"],
                "S4": ["OBSERVE"], "S5": ["REFLECT"], "DONE": []}[self.phase]

    def step(self, action, dialogue=""):
        assert action in self.available_actions()
        self.actions.append((action, dialogue))
        self.phase = {"S0": "S1", "S1": "S4", "S4": "S5", "S5": "DONE"}[self.phase]
        return self.observation() if self.phase != "DONE" else {}

    def result(self, persona=None, coherence=None):
        assert self.phase == "DONE"
        return {"ending": "page_end_success_protected", "protected": True,
                "inference_executed": False, "steering_applied": False,
                "scores": {"welfare": 100, "privacy": 100, "persona": persona,
                           "coherence": coherence, "composite": None}}


class FakeClient:
    model = "test-qwen"

    def __init__(self, bad=None):
        self.calls = []
        self.bad = bad

    def complete(self, messages, steering, seed, temperature, max_tokens):
        self.calls.append({"messages": json.loads(json.dumps(messages)), "gne": steering,
                           "seed": seed, "temperature": temperature, "max_tokens": max_tokens})
        actions = json.loads(messages[-1]["content"])["available_actions"]
        reply = self.bad if self.bad is not None else json.dumps({"action": actions[0], "dialogue": "Hmph.",
                                                                  "beliefs": {}, "intent": "help"})
        return {"text": reply, "acknowledged": steering is not None, "usage": {"total_tokens": 4}}


class StubResponse:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.value).encode()


class AdapterTests(unittest.TestCase):
    def test_action_parser_fails_closed(self):
        self.assertEqual(runner.parse_choice('{"action":"GO","dialogue":"x"}', ["GO"])["action"], "GO")
        for payload in ('```json\n{"action":"GO"}\n```', '[]',
                        '{"action":"WRONG","dialogue":"hello"}',
                        '{"action":"GO","dialogue":8}',
                        '{"action":"GO","dialogue":"x","beliefs":7}'):
            with self.subTest(payload=payload), self.assertRaises(runner.ProtocolError):
                runner.parse_choice(payload, ["GO"])

    def test_private_state_is_not_in_packet(self):
        packet = runner.observable_packet(FakeEpisode().observation())
        self.assertNotIn("flags", packet)
        self.assertNotIn("traits", packet)
        self.assertIn("available_actions", packet)

    def test_doses_and_recipe_payload(self):
        expected = {"baseline": (None, 0), "half": ("inline", 0.5),
                    "tsundere": ("inline", 1), "reverse": ("inline", -1)}
        for name, (_, scale) in expected.items():
            payload, got = runner.steering_request(PROTOCOL, name, {"Pride": 0.85, "Care": 0.75}, "S2")
            self.assertEqual(got, scale)
            self.assertEqual(payload is None, name == "baseline")
            if payload:
                self.assertEqual(len(payload["recipe"]["units"]), 24)
                self.assertEqual(payload["when"], "assistant")
                self.assertEqual(payload["scale"], scale)
        adapt_s0 = runner.dose_scale("adaptive", {"Pride": 0.85, "Care": 0.75}, "S0")
        adapt_s2 = runner.dose_scale("adaptive", {"Pride": 0.85, "Care": 0.75}, "S2")
        self.assertGreater(adapt_s2, adapt_s0)
        self.assertLessEqual(adapt_s2, 0.75)
        with self.assertRaises(runner.ProtocolError):
            runner.steering_request(PROTOCOL, "random_recipe", {}, "S0")
        random_payload, _ = runner.steering_request(PROTOCOL, "random_recipe", {}, "S0", "null_1")
        self.assertEqual(random_payload["recipe"], "null_1")

    def test_complete_world_and_acknowledgment(self):
        for condition in ("baseline", "half", "tsundere", "reverse", "adaptive", "random_recipe"):
            with self.subTest(condition=condition), patch.object(runner, "sha256_file", return_value="sha"):
                client = FakeClient()
                run = runner.run_episode(client, PROTOCOL, condition, seed=3,
                                         random_recipe="null_1", episode_factory=FakeEpisode)
                self.assertIsNone(run["error"])
                self.assertTrue(run["result"]["inference_executed"])
                self.assertEqual(run["result"]["steering_backend_acknowledged"], condition != "baseline")
                self.assertFalse(run["result"]["steering_applied"])
                self.assertIsNone(run["result"]["scores"]["composite"])
                self.assertEqual(len(run["model_events"]), 4)
                self.assertTrue(all("secret_outcome" not in json.dumps(c["messages"])
                                    for c in client.calls))
                self.assertFalse(client.calls[0]["gne"] if condition == "baseline" else False)
                if condition == "random_recipe":
                    self.assertFalse(run["random_norm_matched_verified"])

    def test_bad_response_does_not_advance(self):
        with patch.object(runner, "sha256_file", return_value="sha"):
            run = runner.run_episode(FakeClient(bad='{"action":"INVALID","dialogue":"x"}'), PROTOCOL,
                                     "tsundere", 0, episode_factory=FakeEpisode)
        self.assertIsNone(run["result"])
        self.assertIn("Invalid action", run["error"])
        self.assertEqual(len(run["model_events"]), 1)
        self.assertEqual(run["model_events"][0]["phase"], "S0")

    def test_live_api_rejects_remote_and_unacknowledged(self):
        for url in ("https://127.0.0.1:8791/v1", "http://example.com/v1", "http://127.0.0.1:8791/api"):
            with self.assertRaises(runner.ProtocolError):
                runner.GNEClient(url, "m")
        client = runner.GNEClient("http://127.0.0.1:8791/v1", "qwen-test")
        with patch("urllib.request.urlopen", return_value=StubResponse({"data": [{"id": "qwen-test"}]})):
            client.verify_model()
        with patch("urllib.request.urlopen", return_value=StubResponse({"data": [{"id": "wrong"}]})):
            with self.assertRaises(runner.ProtocolError):
                client.verify_model()
        reply = {"model": "qwen-test", "choices": [{"message": {"content": "{}"}}], "gne": {"recipe": {"units": ["1:2:+1"]}}}
        with patch("urllib.request.urlopen", return_value=StubResponse(reply)) as called:
            answer = client.complete([{"role": "user", "content": "x"}], {"units": ["1:2:+1"]}, 7, 0.0, 256)
            self.assertTrue(answer["acknowledged"])
            body = json.loads(called.call_args.args[0].data.decode())
            self.assertNotIn("seed", body)  # true greedy even if the runner labels its paired trial
            self.assertIn("gne", body)
        reply["gne"] = {"recipe": None}
        with patch("urllib.request.urlopen", return_value=StubResponse(reply)):
            with self.assertRaises(runner.ProtocolError):
                client.complete([], {"units": ["1:2:+1"]}, 8, 0.7, 256)

    @unittest.skipUnless((runner.FIXTURE / "counterfactual_cases.json").exists(), "TSUN-01B fixture not mounted")
    def test_eight_scripted_oracle_paths(self):
        cases = runner.run_scripted_cases()
        self.assertEqual(len(cases), 8)
        self.assertTrue(all(c["matches_oracle"] for c in cases))
        self.assertTrue(all(c["model_inference_executed"] is False for c in cases))

    @unittest.skipUnless(runner.DEFAULT_PROTOCOL.exists(), "TSUN-01B protocol not mounted")
    def test_checked_in_protocol(self):
        protocol = runner.load_protocol()
        self.assertEqual(len(runner.unit_specs(protocol)), 24)
        self.assertEqual(runner.unit_specs(protocol)[0], "40:1003:-0.164")


if __name__ == "__main__":
    unittest.main()
