"""Bench: can Inky Mini itself do the ad-hoc-to-SweepWeave repair pass (the one this session did by
hand in to_storyworld_json.py), following only the checklist now written into
codex-skills/small-storyworld-builder/SKILL.md's Repair Addendum? Each sampled raw encounter is
handed to Inky with the checklist; its reply is scored against the known-correct page already in
storyworld.json (itself VALID OK under sweepweave_validator.py), plus a live validator run on a
reconstructed mini-storyworld. No story content is judged -- this is a structural/schema bench.
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

RUN = Path(__file__).parent
ENCOUNTERS = {json.loads(l)["encounter_id"]: json.loads(l) for l in (RUN / "encounters.jsonl").read_text(encoding="utf-8").splitlines()}
GROUND_TRUTH = json.loads((RUN / "storyworld.json").read_text(encoding="utf-8"))
GT_PAGES = {p["id"]: p for p in GROUND_TRUTH["encounters"]}
OUTLINE = json.loads((RUN / "outline.json").read_text(encoding="utf-8"))
VALIDATOR = Path("/c/projects/GPTStoryworld/codex-skills/storyworld-building/scripts/sweepweave_validator.py")
VALIDATOR_WIN = r"C:\projects\GPTStoryworld\codex-skills\storyworld-building\scripts\sweepweave_validator.py"

GOBLIN_GDK = "/root/gdk-build/goblin-gdk/target/release/goblin-gdk"
BASE_URL = "http://127.0.0.1:18090/v1/"
MODEL = "inkling-2-mini"
MAX_TOKENS = 9000
TIMEOUT_SECS = 180

SAMPLE_IDS = ["trunk_005", "e06_005", "e01_001", "e01_012", "e05_010", "e01_023", "e09_023", "trunk_051"]

CHECKLIST = """You are repairing one raw story encounter into this repo's SweepWeave storyworld
page schema. Output ONE JSON object only, no prose, with exactly these keys: id, text_script,
options. Rules:
- "id" is the given encounter_id, unchanged.
- "text_script" is {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": <scene text, copied EXACTLY, do not rewrite or trim it>}. If an ending_text is given, append it to the
  scene text with a blank line between them, still verbatim, no new words of your own.
- If "is_ending" is true: "options" MUST be an empty list []. A terminal page has no options.
- Otherwise, for each item in the given options list, produce one options[] entry:
  {"id": "<encounter_id>_opt<N>" (N = 0-based index), "text_script": {String Constant, value = the
  option's label verbatim}, "visibility_script": {"pointer_type":"Boolean Constant","script_element_type":"Pointer","value": true},
  "performability_script": same shape with value true, "reactions": [...]}.
- Each option's "reactions" is normally a ONE-element list: {"id": "<option_id>_r1", "text_script":
  {String Constant, value = that option's consequence text verbatim}, "consequence_id": <the
  next_encounter_id given below>, "desirability_script": {"pointer_type":"Bounded Number Constant","script_element_type":"Pointer","value": 1.0}, "after_effects": []}.
- EXCEPTION: if "branch_point_fanout" is given (a list of head encounter ids), this is the one
  encounter where the story could tip toward any of several endings. Then EVERY option's
  "reactions" must be a list with ONE reaction per id in branch_point_fanout (not one), each with
  its own reaction id, "text_script" value "" (no invented transition text), that head id as
  consequence_id, and desirability_script value 1.0.

Raw encounter:
__ENCOUNTER_JSON__
__EXTRA_CONTEXT__
Reply with the JSON object only."""


def build_task(row: dict) -> tuple[str, str | None]:
    branch = row["branch"]
    idx = row["index_in_branch"]
    if branch == "trunk" and idx == OUTLINE["branch_outline"]["trunk"]["encounter_budget"]:
        heads = [f"{b['ending_id']}_001" for b in OUTLINE["branch_outline"]["branches"]]
        extra = f"branch_point_fanout: {json.dumps(heads)}\n"
        next_id = None
    elif row.get("is_ending"):
        extra = ""
        next_id = None
    else:
        same_branch = sorted((r for r in ENCOUNTERS.values() if r["branch"] == branch), key=lambda r: r["index_in_branch"])
        pos = next(i for i, r in enumerate(same_branch) if r["encounter_id"] == row["encounter_id"])
        next_id = same_branch[pos + 1]["encounter_id"]
        extra = f"next_encounter_id: \"{next_id}\"\n"
    raw = {k: row[k] for k in ("encounter_id", "characters_present", "scene", "options", "is_ending", "ending_text")}
    prompt = CHECKLIST.replace("__ENCOUNTER_JSON__", json.dumps(raw, indent=2)).replace("__EXTRA_CONTEXT__", extra)
    return prompt, next_id


def call_teacher(task_text: str) -> dict:
    task_path = RUN / "_bench_task_tmp.txt"
    task_path.write_text(task_text, encoding="utf-8")
    wsl_task = "/mnt/c/Users/patri/Documents/Codex/agn04-arthurian/campaign/_bench_task_tmp.txt"
    cmd = [
        "wsl.exe", "-d", "Ubuntu-24.04", "-u", "root", "--", GOBLIN_GDK,
        "--no-packet", "--task-file", wsl_task, "--base-url", BASE_URL,
        "--model", MODEL, "--max-tokens", str(MAX_TOKENS), "--timeout-secs", str(TIMEOUT_SECS),
    ]
    import os
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                             env={**os.environ, "MSYS_NO_PATHCONV": "1"}, timeout=TIMEOUT_SECS + 30)
    if result.returncode != 0:
        raise RuntimeError(f"goblin-gdk exit {result.returncode}: {result.stderr[-400:]}")
    return json.loads(result.stdout)


def extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    return json.loads(text[start:end + 1])


def score_page(encounter_id: str, page: dict, next_id: str | None, row: dict) -> dict:
    gt = GT_PAGES[encounter_id]
    out = {"encounter_id": encounter_id, "parse_ok": True, "checks": {}}
    out["checks"]["id_correct"] = page.get("id") == encounter_id
    got_text = page.get("text_script", {}).get("value", "")
    want_text = gt["text_script"]["value"]
    out["checks"]["text_verbatim"] = got_text.strip() == want_text.strip()
    if row.get("is_ending"):
        out["checks"]["terminal_empty_options"] = page.get("options") == []
    else:
        opts = page.get("options", [])
        out["checks"]["option_count_matches"] = len(opts) == len(row["options"])
        labels_ok = all(
            o.get("text_script", {}).get("value", "").strip() == row["options"][i]["label"].strip()
            for i, o in enumerate(opts) if i < len(row["options"])
        )
        out["checks"]["option_labels_verbatim"] = labels_ok and len(opts) == len(row["options"])
        if next_id:
            cids = [r.get("consequence_id") for o in opts for r in o.get("reactions", [])]
            out["checks"]["consequence_id_correct"] = len(cids) > 0 and all(c == next_id for c in cids)
        else:
            heads = {r.get("consequence_id") for o in opts for r in o.get("reactions", [])}
            expected = {f"{b['ending_id']}_001" for b in OUTLINE["branch_outline"]["branches"]}
            out["checks"]["fanout_complete"] = heads == expected
            per_option_fanout = all(len(o.get("reactions", [])) == len(expected) for o in opts)
            out["checks"]["fanout_per_option"] = per_option_fanout
    out["all_pass"] = all(out["checks"].values())
    return out


def validate_with_sweepweave(page: dict, encounter_id: str, next_id: str | None, row: dict) -> tuple[bool, str]:
    mini = json.loads(json.dumps(GROUND_TRUTH))  # deep copy of a known-valid world
    pages_by_id = {p["id"]: p for p in mini["encounters"]}
    pages_by_id[encounter_id] = page
    mini["encounters"] = list(pages_by_id.values())
    tmp = RUN / f"_bench_mini_{encounter_id}.json"
    tmp.write_text(json.dumps(mini), encoding="utf-8")
    result = subprocess.run(
        [r"C:\Users\patri\AppData\Local\Programs\Python\Python312\python.exe", VALIDATOR_WIN, "validate", str(tmp)],
        capture_output=True, text=True,
    )
    tmp.unlink(missing_ok=True)
    return result.returncode == 0, result.stdout.strip()


def main():
    results = []
    for eid in SAMPLE_IDS:
        row = ENCOUNTERS[eid]
        prompt, next_id = build_task(row)
        t0 = time.time()
        try:
            receipt = None
            last_exc = None
            for attempt in range(3):
                try:
                    receipt = call_teacher(prompt)
                    break
                except FileNotFoundError as exc:
                    last_exc = exc
                    time.sleep(3)
            if receipt is None:
                raise last_exc
            page = extract_json(receipt["answer"])
            dt = time.time() - t0
            score = score_page(eid, page, next_id, row)
            valid_ok, valid_msg = validate_with_sweepweave(page, eid, next_id, row)
            score["validator_ok"] = valid_ok
            score["validator_msg"] = valid_msg if not valid_ok else "VALID OK"
            score["seconds"] = round(dt, 1)
        except Exception as exc:
            score = {"encounter_id": eid, "parse_ok": False, "error": str(exc), "seconds": round(time.time() - t0, 1)}
        results.append(score)
        print(json.dumps(score), flush=True)
    (RUN / "bench_repair_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    n = len(results)
    parse_ok = sum(1 for r in results if r.get("parse_ok"))
    all_pass = sum(1 for r in results if r.get("all_pass"))
    valid_ok = sum(1 for r in results if r.get("validator_ok"))
    print(f"\nSUMMARY: {n} sampled | parse_ok {parse_ok}/{n} | all_struct_checks_pass {all_pass}/{n} | validator_ok {valid_ok}/{n}")


if __name__ == "__main__":
    main()
