"""Unit tests for the Storyworld MCP server (stdlib unittest; run from the repository root).

    PYTHONPATH=gdk python -m unittest discover -s gdk/tests -p "test_*.py" -v
"""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from storyworld_mcp.hypergames import correct, parse_answer
from storyworld_mcp.repo import StoryworldError
from storyworld_mcp.server import Service, handle, serve

ROOT = Path(__file__).resolve().parents[2]
CAIRO = "storyworlds/cairo_directorate_hyperworld/storyworld.json"


def service(mode: str = "all", read_only: bool = False, **kw) -> Service:
    work = Path(tempfile.mkdtemp(prefix="storyworld-gdk-test-"))
    return Service(ROOT, work, mode, kw.get("card_budget", 6144), kw.get("read_budget", 48000), read_only)


class WorldTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.svc = service()
        cls.created = cls.svc.call("world_new", {"world": "lighthouse", "title": "The Lighthouse Ledger",
                                                 "about": "Two keepers dispute a falsified log.",
                                                 "motif": "Every light is a promise.", "target_encounters": 16,
                                                 "endings": 3})

    def test_new_world_is_valid_and_summarised(self):
        self.assertTrue(self.created["valid"])
        summary = self.svc.call("world_summary", {"world": "lighthouse"})
        self.assertGreaterEqual(summary["encounters"], self.created["encounters"])
        self.assertTrue(summary["endings"])
        self.assertLess(summary["tokens"]["swmd"], summary["tokens"]["json"])
        self.assertTrue(self.svc.call("world_validate", {"world": "lighthouse"})["valid"])

    def test_quality_and_rehearsal_report(self):
        quality = self.svc.call("world_quality", {"world": "lighthouse"})
        self.assertEqual(quality["checks_passed"] + len(quality["failed"]), quality["checks_total"])
        rehearsal = self.svc.call("world_rehearse", {"world": "lighthouse", "runs": 50, "seed": 3})
        self.assertAlmostEqual(sum(rehearsal["endings"].values()), 1.0, places=3)

    def test_card_and_micro_edits(self):
        listing = self.svc.call("encounter_list", {"world": "lighthouse", "limit": 5})
        target = next(row["id"] for row in listing["encounters"] if not row["terminal"])
        card = self.svc.call("encounter_card", {"world": "lighthouse", "encounter_id": target})
        self.assertLessEqual(card["card_tokens"], card["card_budget"])
        cast = card["cast"]
        char = next(iter(cast))
        prop = cast[char][0]
        added = self.svc.call("option_add", {"world": "lighthouse", "encounter_id": target, "text": "Burn the log.",
                                             "reactions": [{"text": "Smoke rises.", "consequence_id": "wild",
                                                            "effects": [{"character": char, "property": prop, "delta": 0.1}],
                                                            "desirability": {"constant": 0.2, "terms": [
                                                                {"character": char, "property": prop, "coefficient": 0.5}]}}]})
        self.assertTrue(added["valid"])
        edited = self.svc.call("encounter_edit_text", {"world": "lighthouse", "encounter_id": target,
                                                       "options": [{"option_id": added["option_id"], "text": "Burn it."}]})
        self.assertEqual(edited["changed"], [added["option_id"]])
        changed = self.svc.call("reaction_set", {"world": "lighthouse", "encounter_id": target, "option_id": added["option_id"],
                                                 "reaction_id": added["reaction_ids"][0], "clear_effects": True})
        self.assertEqual(changed["effects"], 0)
        spool = self.svc.call("world_summary", {"world": "lighthouse"})["spools"][-1]["id"]
        ending = self.svc.call("encounter_add", {"world": "lighthouse", "encounter_id": "page_end_ash", "title": "Ash",
                                                 "text": "Only ash.", "spool_id": spool})
        self.assertTrue(ending["terminal"])
        ledger = (self.svc.ws.path("lighthouse").parent / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(ledger), 5)

    def test_refusals_leave_the_world_unchanged(self):
        before = self.svc.ws.path("lighthouse").read_bytes()
        target = self.svc.call("encounter_list", {"world": "lighthouse"})["encounters"][1]["id"]
        for args, code in (
            ({"world": "lighthouse", "encounter_id": target, "text": "x",
              "reactions": [{"text": "y", "consequence_id": "page_missing"}]}, "unknown_encounter"),
            ({"world": "lighthouse", "encounter_id": target, "text": "x",
              "reactions": [{"text": "y", "consequence_id": "wild",
                             "effects": [{"character": "char_nobody", "property": "Trust", "delta": 0.1}]}]}, "unknown_property"),
        ):
            with self.assertRaises(StoryworldError) as caught:
                self.svc.call("option_add", args)
            self.assertEqual(caught.exception.code, code)
        with self.assertRaises(StoryworldError) as caught:
            self.svc.call("option_add", {"world": "lighthouse", "encounter_id": target, "text": "x", "reactons": []})
        self.assertEqual(caught.exception.code, "bad_argument")
        self.assertEqual(before, self.svc.ws.path("lighthouse").read_bytes())

    def test_import_and_read_budget(self):
        imported = self.svc.call("world_import", {"world": "cairo", "source": CAIRO})
        self.assertTrue(imported["valid"])
        text = self.svc.call("world_read", {"world": "cairo", "format": "swmd"})
        self.assertIn("SWMD", text["text"][:200])
        tight = service(read_budget=500)
        tight.call("world_import", {"world": "cairo", "source": CAIRO})
        with self.assertRaises(StoryworldError) as caught:
            tight.call("world_read", {"world": "cairo"})
        self.assertEqual(caught.exception.code, "budget_exceeded")
        with self.assertRaises(StoryworldError):
            self.svc.call("world_import", {"world": "escape", "source": "../outside.json"})
        denied = Service(ROOT, Path(tempfile.mkdtemp()), "all", 6144, 48000, False, [CAIRO])
        with self.assertRaises(StoryworldError) as caught:
            denied.call("world_import", {"world": "cairo", "source": CAIRO})
        self.assertEqual(caught.exception.code, "denied_path")


class Repairs(unittest.TestCase):
    def test_masked_errors_and_structure_tools(self):
        svc = service("builder")
        svc.call("world_import", {"world": "cairo", "source": CAIRO})
        path = svc.ws.path("cairo")
        data = json.loads(path.read_text(encoding="utf-8"))
        data.pop("IFID")
        data.pop("css_theme")
        for spool in data["spools"]:
            spool["starts_active"] = False
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(sorted(svc.call("world_validate", {"world": "cairo"})["errors"]), ["IFID: missing", "css_theme: missing"])
        # Restoring the keys reveals the spool error the validator had not reached; that is progress, not a regression.
        fixed = svc.call("world_set_fields", {"world": "cairo", "fields": {"IFID": "cairo-repair", "css_theme": "lilac"}})
        self.assertEqual(fixed["validator_errors"], ["spools: no starts_active spool"])
        with self.assertRaises(StoryworldError) as caught:
            svc.call("world_set_fields", {"world": "cairo", "fields": {"encounters": "x"}})
        self.assertEqual(caught.exception.code, "bad_argument")
        spool = data["spools"][0]["id"]
        started = svc.call("spool_set", {"world": "cairo", "spool_id": spool, "starts_active": True})
        self.assertTrue(started["valid"])
        with self.assertRaises(StoryworldError) as caught:
            svc.call("spool_set", {"world": "cairo", "spool_id": spool, "encounters": ["page_ghost"]})
        self.assertEqual(caught.exception.code, "unknown_encounter")
        added = svc.call("character_add", {"world": "cairo", "character_id": "char_ferryman", "name": "The Ferryman",
                                           "properties": ["Trust", "Debt"]})
        self.assertTrue(added["valid"])
        cast = {c["id"]: c["properties"] for c in svc.call("world_summary", {"world": "cairo"})["characters"]}
        self.assertEqual(cast["char_ferryman"], ["Debt", "Trust"])

    def test_import_keeps_a_broken_world_for_repair(self):
        svc = service("builder")
        broken = "benchmarks/storyworld_bench/data/builder"
        candidates = sorted((ROOT / broken).glob("builder.repair.*.json"))
        if not candidates:
            self.skipTest("StoryworldBench data is not in this checkout")
        imported = svc.call("world_import", {"world": "broken", "source": f"{broken}/{candidates[0].name}"})
        self.assertFalse(imported["valid"])
        self.assertTrue(imported["validator_errors"])


class Modes(unittest.TestCase):
    def test_small_mode_hides_whole_world_tools(self):
        names = {t["name"] for t in service("small").tools()}
        self.assertIn("encounter_card", names)
        self.assertNotIn("world_read", names)
        self.assertNotIn("world_patch_swmd", names)
        self.assertNotIn("hyperworld_family_build", names)

    def test_read_only_hides_writes(self):
        names = {t["name"] for t in service("all", read_only=True).tools()}
        self.assertIn("world_quality", names)
        self.assertNotIn("option_add", names)
        self.assertNotIn("hyperworld_family_build", names)

    def test_protocol_frames(self):
        svc = service("small")
        lines = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                 {"jsonrpc": "2.0", "method": "notifications/initialized"},
                 {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                 {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "world_read", "arguments": {"world": "x"}}}]
        reader = io.BytesIO(("\n".join(json.dumps(x) for x in lines) + "\n").encode())
        writer = io.BytesIO()
        serve(svc, reader, writer)
        replies = [json.loads(x) for x in writer.getvalue().decode().splitlines()]
        self.assertEqual([r["id"] for r in replies], [1, 2, 3])
        self.assertIn("one encounter at a time", replies[0]["result"]["instructions"])
        self.assertTrue(replies[2]["result"]["isError"])
        self.assertEqual(replies[2]["result"]["structuredContent"]["error"], "unknown_tool")
        self.assertIsNone(handle(svc, {"jsonrpc": "2.0", "method": "notifications/initialized"}))


class HypergameFamilies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.svc = service("hypergames")
        cls.built = cls.svc.call("hyperworld_family_build", {"family": "relay-traps", "seeds": [0, 1, 2], "turns": [3, 5]})

    def test_answer_parsing(self):
        self.assertEqual(parse_answer({"answer": "3/8"}), Fraction(3, 8))
        self.assertEqual(parse_answer("0.375"), Fraction(3, 8))
        self.assertEqual(parse_answer("37.5%"), Fraction(3, 8))
        self.assertIsNone(parse_answer("about a third"))
        self.assertTrue(correct("marginal", Fraction(3750, 10000), Fraction(3, 8)))
        self.assertFalse(correct("fresh_count", Fraction(3), Fraction(4)))

    def test_family_is_accepted_with_separated_baselines(self):
        built = self.built
        self.assertGreater(built["items"], 0)
        self.assertEqual(built["baselines"]["oracle"], 1.0)
        self.assertEqual(built["baselines"]["naive"], 0.0)
        self.assertTrue(built["accepted"], built["rejection_reasons"])
        self.assertIn("relay of that same report", built["sample_prompt"])
        folder = Path(built["folder"])
        items = (folder / "items.jsonl").read_text(encoding="utf-8")
        self.assertNotIn('"exact"', items)

    def test_scoring_oracle_naive_and_blank(self):
        folder = Path(self.built["folder"])
        grader = [json.loads(x) for x in (folder / "grader.jsonl").read_text(encoding="utf-8").splitlines()]
        oracle = self.svc.call("hyperworld_family_score", {"family": "relay-traps",
                                                           "answers": [{"id": g["id"], "answer": g["exact"]} for g in grader]})
        self.assertEqual(oracle["score"], 1.0)
        naive = self.svc.call("hyperworld_family_score", {"family": "relay-traps",
                                                          "answers": [{"id": g["id"], "answer": g["naive"]} for g in grader]})
        self.assertEqual(naive["score"], 0.0)
        self.assertEqual(naive["naive_trap_rate"], 1.0)
        blank = self.svc.call("hyperworld_family_score", {"family": "relay-traps", "answers": []})
        self.assertEqual(blank["answered"], 0)

    def test_view_and_illegal_action(self):
        view = self.svc.call("hyperworld_view", {"seed": 4, "actions": ["brief"]})
        self.assertEqual(view["turn"], 1)
        self.assertNotIn("private_binary_state", json.dumps(view))
        with self.assertRaises(StoryworldError) as caught:
            self.svc.call("hyperworld_view", {"seed": 4, "actions": ["snap_vote"]})
        self.assertEqual(caught.exception.code, "illegal_action")

    def test_freeze_refuses_repository_paths(self):
        with self.assertRaises(StoryworldError) as caught:
            self.svc.call("hyperworld_family_freeze", {"family": "relay-traps", "heldout_dir": str(ROOT / "gdk" / "work")})
        self.assertEqual(caught.exception.code, "bad_argument")


if __name__ == "__main__":
    unittest.main()
