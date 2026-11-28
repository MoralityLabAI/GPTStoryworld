"""End-to-end check of the storyworld binary against a scripted OpenAI-compatible endpoint.

    python -I gdk/ci_smoke.py PATH/TO/storyworld [--python PY]

Run 1 (/small-storyworld, native tool calls): the slash command loads the skill; the model creates a world, reads
the summary, the encounter list and one card, sends the same bad option_add three times (two server refusals
naming the property, then the app's repeated-failure guard), adds a valid option, validates, and asks for
world_read, which small mode does not list. Checks the offered tools, the receipt, the ledger, and that older
long tool results are elided from later requests while the receipt keeps them.
Run 2 (/hypergames, --tool-mode text): the text protocol drives hyperworld_status and hyperworld_family_build,
and the family is accepted with an oracle of 1.0.
Run 3 (bench --track builder): one StoryworldBench repair task; importing the task's grading-only file is refused,
the input world is imported, and the bench scorer grades the world left in the workspace.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SEEN: list[dict[str, Any]] = []
BENCH: dict[str, Any] = {}
CARD: dict[str, Any] = {}


def tool_results(messages: list[dict[str, Any]]) -> list[Any]:
    found = []
    for message in messages:
        if message.get("role") == "tool":
            try:
                found.append(json.loads(message.get("content") or ""))
            except ValueError:
                found.append({"text": message.get("content")})
    return found


def text_tool_results(messages: list[dict[str, Any]]) -> int:
    return sum(str(m.get("content") or "").count("<tool_response>") for m in messages if m.get("role") != "system")


def call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    return {"tool": name, "arguments": arguments}


BAD_OPTION = {"world": "lighthouse", "encounter_id": "", "text": "Burn the log.",
              "reactions": [{"text": "Smoke rises.", "consequence_id": "wild",
                             "effects": [{"character": "char_nobody", "property": "Trust", "delta": 0.1}]}]}


def small_script(messages: list[dict[str, Any]]) -> dict[str, Any] | str:
    results = tool_results(messages)
    done = len(results)
    if done == 0:
        return call("world_new", {"world": "lighthouse", "title": "The Lighthouse Ledger", "about": "Two keepers dispute a log.",
                                  "motif": "Every light is a promise.", "target_encounters": 16, "endings": 3})
    if done == 1:
        return call("world_summary", {"world": "lighthouse"})
    if done == 2:
        return call("encounter_list", {"world": "lighthouse", "limit": 5})
    if done == 3:
        target = next(row["id"] for row in results[2]["encounters"] if not row["terminal"])
        BAD_OPTION["encounter_id"] = target
        return call("encounter_card", {"world": "lighthouse", "encounter_id": target})
    if done in (4, 5, 6):
        if done == 4:
            CARD.update(results[3])  # later requests carry it elided, so remember it as a model would
        return call("option_add", BAD_OPTION)
    if done == 7:
        card = CARD
        char = next(iter(card["cast"]))
        prop = card["cast"][char][0]
        return call("option_add", {"world": "lighthouse", "encounter_id": card["encounter_id"], "text": "Burn the log.",
                                   "reactions": [{"text": "Smoke rises over the water.", "consequence_id": "wild",
                                                  "effects": [{"character": char, "property": prop, "delta": 0.1}]},
                                                 {"text": "The flame gutters and the log survives.", "consequence_id": "wild",
                                                  "effects": [{"character": char, "property": prop, "delta": -0.1}]}]})
    if done == 8:
        return call("world_validate", {"world": "lighthouse"})
    if done == 9:
        return call("world_read", {"world": "lighthouse"})
    return "Added one option with two reactions to the first scene; world_validate returned valid: true."


def hyper_script(messages: list[dict[str, Any]]) -> str:
    done = text_tool_results(messages)
    if done == 0:
        return '<tool_call>\n{"name": "hyperworld_status", "arguments": {}}\n</tool_call>'
    if done == 1:
        return ('<tool_call>\n{"name": "hyperworld_family_build", "arguments": {"family": "smoke-fam", '
                '"seeds": [0, 1, 2], "turns": [4, 6]}}\n</tool_call>')
    return "Built smoke-fam; hyperworld_family_build reported accepted: true."


def bench_script(messages: list[dict[str, Any]]) -> dict[str, Any] | str:
    done = len(tool_results(messages))
    if done == 0:
        return call("world_import", {"world": "bench", "source": BENCH["grading_only"][0]})
    if done == 1:
        return call("world_import", {"world": "bench", "source": BENCH["inputs"]["world"]})
    if done == 2:
        return call("world_validate", {"world": "bench"})
    return "DONE"


class Endpoint(BaseHTTPRequestHandler):
    script = "small"

    def log_message(self, *_: Any) -> None:
        pass

    def _send(self, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        self._send({"object": "list", "data": [{"id": "scripted-author", "object": "model"}]})

    def do_POST(self) -> None:
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        SEEN.append(request)
        messages = request["messages"]
        reply = {"small": small_script, "hyper": hyper_script, "bench": bench_script}[type(self).script](messages)
        message: dict[str, Any] = {"role": "assistant", "content": None}
        finish = "stop"
        if isinstance(reply, dict):
            message["tool_calls"] = [{"id": f"call_{len(SEEN)}", "type": "function", "function": {
                "name": reply["tool"], "arguments": json.dumps(reply["arguments"])}}]
            finish = "tool_calls"
        else:
            message["content"] = reply
        prompt_chars = sum(len(json.dumps(m)) for m in messages)
        self._send({"id": f"cmpl-{len(SEEN)}", "object": "chat.completion", "model": request.get("model"),
                    "choices": [{"index": 0, "message": message, "finish_reason": finish}],
                    "usage": {"prompt_tokens": prompt_chars // 4, "completion_tokens": 10,
                              "total_tokens": prompt_chars // 4 + 10}})


def run(binary: str, python: str, port: int, work: Path, *extra: str) -> dict[str, Any]:
    command = [binary, *extra[:1], "--root", str(ROOT), "--python", python, "--work", str(work),
               "--base-url", f"http://127.0.0.1:{port}/v1", "--model", "scripted-author", "--timeout-secs", "120",
               *extra[1:]]
    done = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=900, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"exit {done.returncode}\n{done.stdout[-2000:]}\n{done.stderr[-4000:]}"
    return json.loads(done.stdout.strip().splitlines()[-1])


def main() -> int:
    binary = sys.argv[1]
    python = sys.argv[sys.argv.index("--python") + 1] if "--python" in sys.argv else sys.executable
    server = ThreadingHTTPServer(("127.0.0.1", 0), Endpoint)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "work"

        # Run 1: small mode, native tools.
        receipt = run(binary, python, port, work, "run", "--skill", "small-storyworld", "--args", "lighthouse")
        first = json.dumps(SEEN[0]["messages"])
        assert "# Loaded Skill: small-storyworld" in first and "/small-storyworld lighthouse" in first, first[:800]
        offered = {t["function"]["name"] for t in SEEN[0]["tools"]}
        assert {"load_skill", "encounter_card", "option_add", "world_quality"} <= offered, sorted(offered)
        assert not offered & {"world_read", "world_patch_swmd", "hyperworld_family_build"}, sorted(offered)
        calls = receipt["toolCalls"]
        names = [c["name"] for c in calls]
        assert names == ["world_new", "world_summary", "encounter_list", "encounter_card", *["option_add"] * 4,
                         "world_validate", "world_read"], names
        assert "unknown_property" in (calls[4]["result"] or "") and "char_nobody" in (calls[4]["result"] or ""), calls[4]
        assert calls[5]["ok"] is False and "unknown_property" in (calls[5]["result"] or "")
        assert "already failed 2 times" in (calls[6]["result"] or ""), calls[6]
        assert calls[7]["ok"] and '"valid":true' in (calls[7]["result"] or ""), calls[7]
        assert "not a Storyworld tool in this session's mode" in (calls[9]["result"] or ""), calls[9]
        failed = {i for i, c in enumerate(calls) if not c["ok"]}
        assert failed == {4, 5, 6, 9}, [calls[i] for i in sorted(failed)]
        assert receipt["worlds"]["lighthouse"]["valid"] is True, receipt["worlds"]
        assert receipt["writes"] == 2 and receipt["refusedCalls"] == 4, (receipt["writes"], receipt["refusedCalls"])
        assert receipt["mode"] == "small" and receipt["contextTokens"] == 8192 and receipt["keepResults"] == 2
        last = json.dumps(SEEN[-1]["messages"])
        assert "[earlier world_summary result elided" in last, "small mode must elide older long results"
        assert any('"swmd_min"' in (m.get("content") or "") for m in receipt["transcript"] if m["role"] == "tool"), \
            "the receipt keeps the full world_summary result"
        ledger = (work / "worlds" / "lighthouse" / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
        assert [json.loads(x)["op"] for x in ledger] == ["world_new", "option_add"], ledger

        # Run 2: hypergames, text tool protocol.
        Endpoint.script = "hyper"
        SEEN.clear()
        hyper = run(binary, python, port, work, "run", "--skill", "hypergames", "--args", "smoke-fam", "--tool-mode", "text")
        assert not SEEN[0].get("tools"), "text mode must not send native tools"
        system = SEEN[0]["messages"][0]["content"]
        assert "<tool_call>" in system and "\n- hyperworld_family_build:" in system and "\n- world_read:" not in system
        assert [c["name"] for c in hyper["toolCalls"]] == ["hyperworld_status", "hyperworld_family_build"], hyper["toolCalls"]
        family = hyper["families"]["smoke-fam"]
        assert family["accepted"] is True and family["baselines"]["oracle"] == 1.0 and family["items"] > 0, family

        # Run 3: one StoryworldBench builder task through the app.
        listing = subprocess.run([python, "-m", "benchmarks.storyworld_bench", "tasks", "--track", "builder", "--split", "dev"],
                                 cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout
        task = next(t for t in map(json.loads, listing.splitlines()) if "world" in t["inputs"] and t["grading_only"])
        BENCH.update(task)
        Endpoint.script = "bench"
        SEEN.clear()
        summary = run(binary, python, port, work, "bench", "--track", "builder", "--task", task["task_id"])
        assert summary["n"] == 1 and 0.0 <= summary["mean_score"] <= 1.0, summary
        row = json.loads(Path(summary["results"]).read_text(encoding="utf-8").splitlines()[0])
        assert row["task_id"] == task["task_id"] and row["artifact"].endswith("storyworld.json"), row
        assert row["mode"] == "builder" and row["scoreError"] is None, row
        bench_receipt = json.loads((Path(row["artifact"]).parents[3] / "receipt.json").read_text(encoding="utf-8"))
        bench_calls = bench_receipt["toolCalls"]
        assert "denied_path" in (bench_calls[0]["result"] or ""), bench_calls[0]
        assert bench_calls[1]["ok"] and '"valid":false' in (bench_calls[1]["result"] or ""), bench_calls[1]
        assert "# Loaded Skill: storyworld-builder" in json.dumps(SEEN[0]["messages"])

        print(json.dumps({"ok": True, "small_calls": len(calls), "small_writes": receipt["writes"],
                          "small_seconds": round(receipt["seconds"], 1), "family_items": family["items"],
                          "family_baselines": family["baselines"], "bench_task": task["task_id"],
                          "bench_score": row["score"]}))
    server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
