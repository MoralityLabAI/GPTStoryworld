"""StoryworldBench tests. Run from the repo root: python -m unittest discover -s benchmarks/storyworld_bench/tests -v
(or pytest benchmarks/storyworld_bench/tests)."""
import json
import re
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from benchmarks.storyworld_bench import app, builder, common as C, hypergames, small  # noqa: E402

MANIFEST = app.load_manifest()
TASKS = {t["task_id"]: t for t in MANIFEST["tasks"]}


def first_of(scorer):
    return next(t for t in MANIFEST["tasks"] if t["scorer"] == scorer)


def write(tmp, name, data):
    p = Path(tmp) / name
    p.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
    return p


class ManifestTests(unittest.TestCase):
    def test_sources_match_manifest(self):
        self.assertEqual(app.verify(MANIFEST), [])

    def test_generation_is_deterministic(self):
        fresh, files = app.generate_all()
        self.assertEqual(json.dumps(fresh, sort_keys=True), json.dumps(MANIFEST, sort_keys=True))
        for name, data in files.items():
            self.assertEqual((C.DATA_DIR / name).read_bytes(), data)

    def test_task_counts_and_skills(self):
        for track, skill in C.SKILL_OF_TRACK.items():
            ts = app.select(MANIFEST, track)
            self.assertTrue(10 <= len(ts) <= 30, (track, len(ts)))
            self.assertTrue(all(t["skill"] == skill for t in ts))
            self.assertTrue(app.select(MANIFEST, track, "dev") and app.select(MANIFEST, track, "test"))

    def test_grading_only_paths_are_never_agent_inputs(self):
        for task in MANIFEST["tasks"]:
            public = app.public(task)
            self.assertFalse(set(public["inputs"].values()) & set(public["grading_only"]), task["task_id"])
            oracle = task["private"].get("oracle", {})
            if "path" in oracle:
                self.assertIn(oracle["path"], public["grading_only"], task["task_id"])
            if task["track"] == "hypergames":
                self.assertEqual(public["inputs"], {}, task["task_id"])
                self.assertTrue(public["grading_only"], task["task_id"])
        camelot = [t for t in MANIFEST["tasks"] if t["task_id"].startswith("small.repair.camelot.")]
        self.assertTrue(camelot)
        for task in camelot:
            self.assertIn("InkyWorlds/camelots-reckoning/storyworld.json", task["grading_only"])

    def test_split_is_hash_based_and_stable(self):
        self.assertEqual(C.split_of("hg.hg01.fixture"), C.split_of("hg.hg01.fixture"))
        for t in MANIFEST["tasks"]:
            self.assertEqual(t["split"], C.split_of(t["task_id"]))
        ids = [t["task_id"] for t in MANIFEST["tasks"]]
        self.assertEqual([C.split_of(i) for i in reversed(ids)], [C.split_of(i) for i in ids][::-1])

    def test_no_private_seed_dependency(self):
        text = C.MANIFEST_PATH.read_text(encoding="utf-8")
        self.assertNotIn("HG03_private", text)
        for f in C.PKG_DIR.glob("*.py"):
            self.assertNotIn("private_manifest", f.read_text(encoding="utf-8"))

    def test_no_hedging_words(self):
        banned = re.compile(r"should work|TODO verify|for now|untested|\bWIP\b|may need review", re.I)
        files = list(C.PKG_DIR.glob("*.py")) + [C.PKG_DIR / "README.md"]
        for f in files:
            if f.exists():
                self.assertIsNone(banned.search(f.read_text(encoding="utf-8")), f.name)


class CliTests(unittest.TestCase):
    def run_cli(self, *args, form="module"):
        cmd = [sys.executable, "-m", "benchmarks.storyworld_bench", *args] if form == "module" else \
            [sys.executable, str(C.PKG_DIR / "cli.py"), *args]
        return subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, encoding="utf-8",
                              env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})

    def test_tasks_contract_both_invocations(self):
        for form in ("module", "script"):
            r = self.run_cli("tasks", "--track", "hypergames", "--split", "dev", form=form)
            self.assertEqual(r.returncode, 0, r.stderr)
            rows = [json.loads(l) for l in r.stdout.splitlines()]
            self.assertTrue(rows)
            for row in rows:
                self.assertEqual(set(row), set(app.PUBLIC_FIELDS))
                self.assertEqual(row["track"], "hypergames")
                self.assertNotIn("private", row)

    def test_score_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            task = TASKS["hg.hg01.fixture"]
            art = write(tmp, "a.json", task["private"]["oracle"]["text"])
            r = self.run_cli("score", "--task", task["task_id"], "--artifact", str(art))
            out = json.loads(r.stdout)
            self.assertEqual(out["score"], 1.0)
            self.assertTrue(out["passed"])
            self.assertEqual(set(out) - {"error"}, {"task_id", "track", "score", "passed", "checks"})

    def test_selftest_exit_code(self):
        r = self.run_cli("selftest")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("SELFTEST OK", r.stdout)


class ScorerTests(unittest.TestCase):
    def check_family(self, scorer):
        t = first_of(scorer)
        with tempfile.TemporaryDirectory() as tmp:
            good = app.score_task(t, write(tmp, "g.artifact", app.agent_text(t, "oracle")))
            null = app.score_task(t, write(tmp, "n.artifact", b""))
        self.assertEqual(good["score"], 1.0, good)
        self.assertTrue(good["passed"])
        self.assertEqual(null["score"], 0.0)
        self.assertFalse(null["passed"])
        return t

    def test_every_scorer_family_reaches_one_and_null_is_zero(self):
        for scorer in sorted({t["scorer"] for t in MANIFEST["tasks"]}):
            with self.subTest(scorer=scorer):
                self.check_family(scorer)

    def test_builder_repair_inputs_fail_validator_and_split_bars(self):
        t = first_of("builder.repair")
        with tempfile.TemporaryDirectory() as tmp:
            res = app.score_task(t, C.abspath(t["inputs"]["world"]))
        self.assertFalse(res["checks"]["schema_valid"])
        self.assertFalse(res["passed"])
        self.assertLessEqual(res["score"], 0.3)
        self.assertIn("quality_gate_pass", res["checks"])

    def test_builder_valid_but_failing_gate_is_scored_separately(self):
        t = TASKS["builder.author.small"]
        world = json.loads(C.abspath(builder.REPAIR_WORLDS[0]).read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            res = app.score_task(t, write(tmp, "w.json", json.dumps(world)))
        self.assertTrue(res["checks"]["schema_valid"])
        self.assertFalse(res["checks"]["quality_gate_pass"])
        self.assertFalse(res["passed"])
        self.assertTrue(0.35 < res["score"] < 1.0)

    def test_builder_corruptions_each_break_the_validator(self):
        import random
        from sweepweave_validator import validate_storyworld
        C.ensure_paths()
        world = json.loads(C.abspath(builder.REPAIR_WORLDS[0]).read_text(encoding="utf-8"))
        for kind in ("no_start", "dangling", "spool_ghost", "missing_keys"):
            broken = builder.corrupt(world, kind, random.Random(1))
            p = C.write_temp_json(broken)
            try:
                self.assertTrue(validate_storyworld(str(p)), kind)
            finally:
                p.unlink()

    def test_small_parse_metrics_split(self):
        t = first_of("small.qlora")
        oracle = t["private"]["oracle"]["text"]
        with tempfile.TemporaryDirectory() as tmp:
            res = app.score_task(t, write(tmp, "f.artifact", "Here you go:\n```json\n" + oracle + "\n```"))
        self.assertFalse(res["checks"]["model_parse_ok"])
        self.assertTrue(res["checks"]["parse_ok"])
        self.assertTrue(res["passed"])
        self.assertLess(res["score"], 1.0)
        self.assertLessEqual(res["checks"]["metric_packet_tokens"], 8192)

    def test_small_patch_detects_collateral_and_id_changes(self):
        t = first_of("small.patch")
        block = t["private"]["oracle"]["text"]
        with tempfile.TemporaryDirectory() as tmp:
            renamed = re.sub(r"(OPT )(\S+)", r"\1x_\2", block, count=1)
            res = app.score_task(t, write(tmp, "r.artifact", renamed))
            unchanged = app.score_task(t, write(tmp, "u.artifact", t["private"]["orig_block"]))
        self.assertFalse(res["checks"]["id_preserved"])
        self.assertFalse(unchanged["checks"]["edit_applied"])
        self.assertTrue(unchanged["checks"]["no_collateral"])

    def test_hg02_scores_against_exact_bellman_values(self):
        t = TASKS["hg.hg02.s17.step1"]
        oracle = json.loads(t["private"]["oracle"]["text"])["action"]
        legal = t["private"]["observation"]["legal_actions"]
        with tempfile.TemporaryDirectory() as tmp:
            bad = app.score_task(t, write(tmp, "b.json", json.dumps({"action": "shortcut"})))
            illegal = app.score_task(t, write(tmp, "i.json", json.dumps({"action": "teleport"})))
        self.assertIn(oracle, legal)
        self.assertFalse(bad["passed"])
        self.assertLess(bad["score"], 0.5)
        self.assertEqual(illegal["score"], 0.0)

    def test_hg01_infer_partial_credit(self):
        t = TASKS["hg.hg01.infer.1"]
        exp = t["private"]["expected"]
        extra = exp + ["G9"]
        with tempfile.TemporaryDirectory() as tmp:
            res = app.score_task(t, write(tmp, "p.json", json.dumps({"compatible": extra})))
        self.assertFalse(res["passed"])
        self.assertAlmostEqual(res["score"], len(exp) / len(extra), places=3)

    def test_tier1_hidden_option_is_never_shown(self):
        world = json.loads(C.abspath(hypergames.TIER1_WORLD).read_text(encoding="utf-8"))
        hidden = [o["text_script"]["value"] for e in world["encounters"] for o in e.get("options", []) if o.get("hidden")]
        self.assertTrue(hidden)
        for t in app.select(MANIFEST, "hypergames"):
            if t["task_id"].startswith("hg.tier1"):
                for h in hidden:
                    self.assertNotIn(h, t["prompt"])
                self.assertNotIn("oracle", t["prompt"].lower())


class MockServer(BaseHTTPRequestHandler):
    reply = ""

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        assert body["temperature"] == 0 and body["max_tokens"] > 0
        payload = json.dumps({"choices": [{"message": {"content": type(self).reply(body)}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


class OpenAIAgentTests(unittest.TestCase):
    def serve(self, reply):
        MockServer.reply = staticmethod(reply)
        srv = HTTPServer(("127.0.0.1", 0), MockServer)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.shutdown)
        return f"http://127.0.0.1:{srv.server_port}/v1"

    def test_openai_agent_round_trip_and_wrapped_replies(self):
        by_prompt = {}
        for t in app.select(MANIFEST, "hypergames", "dev"):
            by_prompt[app.inlined_prompt(t)] = t

        def reply(body):
            t = by_prompt[body["messages"][0]["content"]]
            return "<think>working</think>\n```json\n" + t["private"]["oracle"]["text"] + "\n```"

        base = self.serve(reply)
        with tempfile.TemporaryDirectory() as tmp:
            s = app.run_track("hypergames", f"openai:{base}#test-model", Path(tmp), MANIFEST, limit=4, split="dev")
            self.assertEqual(s["n"], 4)
            self.assertEqual(s["mean_score"], 1.0)
            self.assertEqual(s["per_check_means"]["model_parse_ok"], 0.0)
            self.assertEqual(s["per_check_means"]["parse_ok"], 1.0)
            rows = [json.loads(l) for l in (Path(tmp) / "results.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(rows), 4)
            self.assertTrue((Path(tmp) / "summary.json").exists())
        self.assertEqual(set(s["source_hashes"]), set(MANIFEST["track_sources"]["hypergames"]))

    def test_builder_prompt_inlines_generated_world(self):
        t = first_of("builder.repair")
        self.assertIn('"encounters"', app.inlined_prompt(t))
        self.assertNotIn("--- input", app.inlined_prompt(first_of("builder.author")))

    def test_unreachable_server_scores_zero_with_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = app.run_track("hypergames", "openai:http://127.0.0.1:9/v1#none", Path(tmp), MANIFEST, limit=1, split="dev")
            self.assertEqual(s["mean_score"], 0.0)
            row = json.loads((Path(tmp) / "results.jsonl").read_text(encoding="utf-8").splitlines()[0])
            self.assertIn("agent error", row["error"])

    def test_test_split_requires_confirmation_for_models(self):
        with self.assertRaises(SystemExit):
            app.main(["run", "--track", "hypergames", "--agent", "openai:http://127.0.0.1:9/v1#m", "--out",
                      tempfile.mkdtemp(), "--split", "test"])


if __name__ == "__main__":
    unittest.main()
