"""Orchestration only: drives goblin-gdk/Inky Mini through the campaign outline
one encounter at a time, trunk first then round-robin across the 11 branches.
No story content is written here -- every scene/option/ending line comes back
from the teacher call. This script builds bounded prompts, validates replies,
retries malformed ones, and logs progress for an external Monitor to watch.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

SERVER_WAIT_MAX_SECS = 1800
SERVER_WAIT_POLL_SECS = 15


def wait_for_server():
    """Block until squid5080 answers, or give up after SERVER_WAIT_MAX_SECS (server-down
    time doesn't count against a slot's content-retry budget)."""
    waited = 0
    while True:
        try:
            probe = subprocess.run(
                ["wsl.exe", "-d", "Ubuntu-24.04", "-u", "root", "--", "curl", "-sf", "--max-time", "3",
                 "http://127.0.0.1:18090/v1/models"],
                capture_output=True, timeout=15,
            )
            ok = probe.returncode == 0
        except subprocess.TimeoutExpired:
            ok = False
        if ok:
            if waited:
                print(f"SERVER back up after {waited}s", flush=True)
            return
        if waited >= SERVER_WAIT_MAX_SECS:
            raise RuntimeError(f"squid5080 unreachable after waiting {waited}s")
        if waited == 0 or waited % 60 == 0:
            print(f"SERVER down, waited {waited}s so far (power cap or restart in progress)", flush=True)
        time.sleep(SERVER_WAIT_POLL_SECS)
        waited += SERVER_WAIT_POLL_SECS

RUN = Path(__file__).parent
OUTLINE = json.loads((RUN / "outline.json").read_text(encoding="utf-8"))
ENCOUNTERS_PATH = RUN / "encounters.jsonl"
STATE_PATH = RUN / "state.json"
GOBLIN_GDK = "/root/gdk-build/goblin-gdk/target/release/goblin-gdk"
BASE_URL = "http://127.0.0.1:18090/v1/"
MODEL = "inkling-2-mini"
MAX_TOKENS = 7000
TIMEOUT_SECS = 300
MAX_RETRIES = 4

CAST_SHORT = ", ".join(c["name"] for c in OUTLINE["cast"])
TRUNK = OUTLINE["branch_outline"]["trunk"]
BRANCHES = {b["ending_id"]: b for b in OUTLINE["branch_outline"]["branches"]}
ENDINGS = {e["ending_id"]: e for e in OUTLINE["endings"]}

REQUIRED_KEYS = {"encounter_id", "branch", "index_in_branch", "characters_present",
                 "scene", "state_summary", "options", "is_ending", "ending_id", "ending_text",
                 "canvas_art_svg"}


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"trunk_done": 0, "branch_done": {b: 0 for b in BRANCHES}, "total": 0, "failures": 0}


def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def load_recent(branch, n=2):
    if not ENCOUNTERS_PATH.exists():
        return []
    rows = [json.loads(line) for line in ENCOUNTERS_PATH.read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["branch"] == branch]
    return rows[-n:]


def load_trunk_tail(n=2):
    return load_recent("trunk", n)


def build_task(branch, index, budget):
    is_last = index == budget
    if branch == "trunk":
        context_desc = f"Shared trunk establishing the central conflict: {TRUNK['description']}"
        recent = load_trunk_tail()
        ending_note = ("This is the LAST trunk encounter. End it at a natural branch point, "
                        "where the realm's situation could plausibly tip toward any of the 11 "
                        "named endings, without resolving toward one yet." if is_last else "")
    else:
        b = BRANCHES[branch]
        e = ENDINGS[branch]
        context_desc = f"Branch toward ending '{e['title']}' ({branch}): {b['throughline']}"
        recent = load_trunk_tail() if index == 1 else load_recent(branch)
        ending_note = (f"This is the LAST encounter of this branch. It MUST resolve the story "
                        f"into ending '{e['title']}' ({branch}): {e['description']} Tone: "
                        f"{e['tone']}. Set is_ending=true, ending_id=\"{branch}\", and write "
                        f"ending_text as a closing paragraph." if is_last else
                        "Set is_ending=false and ending_id=null; this is not the final encounter.")

    prompt = f"""You are the teacher in a DataGoblin AGN-04 live storyworld campaign. Classic \
public-domain Arthurian cast only: {CAST_SHORT}. Setting: {OUTLINE['setting']}

{context_desc}

Recent prior encounters in this thread (most recent last), for continuity -- do not repeat them:
{json.dumps(recent, indent=2) if recent else "(none yet -- this is the first encounter of this thread)"}

Write encounter number {index} of {budget} in this thread as a single JSON object with exactly \
these keys: encounter_id (string, unique, like "{branch}_{index:03d}"), branch ("{branch}"), \
index_in_branch ({index}), characters_present (array of names from the cast), scene (2-4 \
sentences advancing the plot with original dialogue/action, no verbatim reuse of any existing \
text), state_summary (one sentence a later encounter could use for continuity), options (array \
of 2-3 objects, each with id, label, and a one-sentence consequence that actually changes what \
happens next -- no inert options), is_ending (boolean), ending_id (string or null), ending_text \
(string or null), canvas_art_svg (string). {ending_note}

For canvas_art_svg: write one complete, self-contained SVG document (starting with <svg \
xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500">...</svg>, using only <path>, \
<polygon>, <circle>, <ellipse>, <rect> and <linearGradient>/<radialGradient> fills -- no \
external images or fonts) illustrating this exact scene in the style of Eyvind Earle: flat, \
stylized, highly textured silhouettes, tall narrow stylized trees (especially elongated cypress \
and pine shapes built from repeated small triangular or scalloped foliage units), a jewel-toned \
and often moonlit or twilight palette (deep teals, violets, golds, burnt oranges), dramatic \
layered backgrounds, and decorative, almost tapestry-like composition rather than realistic \
perspective. Compose it yourself for this scene's specific action and characters; do not reuse \
a previous encounter's SVG.

Reply with the JSON object only, no surrounding prose.
"""
    return prompt


def call_teacher(task_text):
    task_path = RUN / "_task_tmp.txt"
    receipt_path = RUN / "_receipt_tmp.json"
    task_path.write_text(task_text, encoding="utf-8")
    wsl_task = "/mnt/c/Users/patri/Documents/Codex/agn04-arthurian/campaign/_task_tmp.txt"
    cmd = [
        "wsl.exe", "-d", "Ubuntu-24.04", "-u", "root", "--", GOBLIN_GDK,
        "--no-packet", "--task-file", wsl_task, "--base-url", BASE_URL,
        "--model", MODEL, "--max-tokens", str(MAX_TOKENS), "--timeout-secs", str(TIMEOUT_SECS),
    ]
    env = {"MSYS_NO_PATHCONV": "1"}
    import os
    full_env = {**os.environ, **env}
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                             env=full_env, timeout=TIMEOUT_SECS + 30)
    if result.returncode != 0:
        raise RuntimeError(f"goblin-gdk exit {result.returncode}: {result.stderr[-500:]}")
    receipt = json.loads(result.stdout)
    return receipt


def validate(card):
    if set(card.keys()) != REQUIRED_KEYS:
        raise ValueError(f"key mismatch: {sorted(card.keys())}")
    if not isinstance(card["options"], list) or not (2 <= len(card["options"]) <= 4):
        raise ValueError("options must be a 2-4 item list")
    return card


def run_slot(branch, index, budget):
    task_text = build_task(branch, index, budget)
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            wait_for_server()
            receipt = call_teacher(task_text)
            card = json.loads(receipt["answer"])
            card = validate(card)
            return card, receipt, attempt
        except Exception as exc:  # malformed reply or call failure; retry
            last_error = exc
            print(f"RETRY branch={branch} index={index} attempt={attempt} error={exc}", flush=True)
            time.sleep(2)
    raise RuntimeError(f"giving up on branch={branch} index={index} after {MAX_RETRIES} attempts: {last_error}")


def main():
    state = load_state()
    target_total = 300
    start = time.time()

    while state["trunk_done"] < TRUNK["encounter_budget"]:
        idx = state["trunk_done"] + 1
        card, receipt, attempts = run_slot("trunk", idx, TRUNK["encounter_budget"])
        with ENCOUNTERS_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps({**card, "evidence_class": "proposed", "verified": False,
                                 "output_tokens": receipt["provider_output_tokens"],
                                 "inference_seconds": receipt["inference_seconds"]}) + "\n")
        state["trunk_done"] = idx
        state["total"] += 1
        save_state(state)
        print(f"PROGRESS trunk {idx}/{TRUNK['encounter_budget']} total={state['total']} "
              f"attempts={attempts} elapsed={time.time()-start:.0f}s", flush=True)

    branch_ids = list(BRANCHES.keys())
    while any(state["branch_done"][b] < BRANCHES[b]["encounter_budget"] for b in branch_ids):
        for b in branch_ids:
            budget = BRANCHES[b]["encounter_budget"]
            if state["branch_done"][b] >= budget:
                continue
            idx = state["branch_done"][b] + 1
            card, receipt, attempts = run_slot(b, idx, budget)
            with ENCOUNTERS_PATH.open("a", encoding="utf-8") as f:
                f.write(json.dumps({**card, "evidence_class": "proposed", "verified": False,
                                     "output_tokens": receipt["provider_output_tokens"],
                                     "inference_seconds": receipt["inference_seconds"]}) + "\n")
            state["branch_done"][b] = idx
            state["total"] += 1
            save_state(state)
            print(f"PROGRESS branch={b} {idx}/{budget} total={state['total']}/{target_total} "
                  f"attempts={attempts} elapsed={time.time()-start:.0f}s", flush=True)

    print(f"DONE total={state['total']} trunk={state['trunk_done']} "
          f"branches={state['branch_done']} elapsed={time.time()-start:.0f}s", flush=True)


if __name__ == "__main__":
    main()
