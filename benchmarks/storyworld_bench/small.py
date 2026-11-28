"""Track 2: small. One encounter per packet (prompt <= 8k tokens): compile / compression / repair / targeted_edit
micro-spec tasks, SWMD block patch tasks, and the Camelot ad-hoc-to-SweepWeave page repair cases."""
from __future__ import annotations

import copy
import json
import random
import re
from pathlib import Path

from . import common as C

QLORA_WORLDS = [
    "InkyWorlds/hat-that-held-the-moon/world.swmd.min.md",
    "InkyWorlds/city-that-lost-its-night-bell/world.swmd.min.md",
]
QLORA_PICKS_PER_TYPE = 3
PATCH_WORLDS = [
    "storyworlds/england_to_france_honest.json",
    "storyworlds/russia_to_austria_grudger.json",
    "storyworlds/france_to_germany_machiavellian.json",
]
PHRASES = ["the ledger stayed open until dawn", "no witness spoke first", "the treaty clause was read twice"]
CAMELOT_DIR = "InkyWorlds/camelots-reckoning"
PACKET_CONTEXT = 8192
PACKET_RESERVE = 1024
SYSTEM = "You compile narrative encounters into canonical SWMD-MICRO-0.1 JSON with stable schema."

SMALL_SOURCES = [
    "codex-skills/small-storyworld-builder/SKILL.md",
    "codex-skills/small-storyworld-builder/scripts/swmd_encounter_index.py",
    "codex-skills/small-storyworld-builder/scripts/swmd_build_qlora_examples.py",
    "codex-skills/storyworld-building/scripts/json_to_swmd.py",
    "codex-skills/storyworld-building/scripts/swmd_patch_json.py",
    "codex-skills/storyworld-building/scripts/sweepweave_validator.py",
    "InkyWorlds/camelots-reckoning/bench/bench_repair.py",
    f"{CAMELOT_DIR}/encounters.jsonl",
    f"{CAMELOT_DIR}/storyworld.json",
    f"{CAMELOT_DIR}/outline.json",
] + QLORA_WORLDS + PATCH_WORLDS

_camelot_mod = None


def camelot():
    global _camelot_mod
    if _camelot_mod is None:
        # bench_repair.py sits in bench/ but resolves its data from its own directory; the data is one level up.
        import types
        src = C.CAMELOT_BENCH.read_text(encoding="utf-8")
        marker = "RUN = Path(__file__).parent"
        assert marker in src
        src = src.replace(marker, f"RUN = Path({str(C.abspath(CAMELOT_DIR))!r})")
        mod = types.ModuleType("sw_bench_repair")
        mod.__file__ = str(C.CAMELOT_BENCH)
        exec(compile(src, str(C.CAMELOT_BENCH), "exec"), mod.__dict__)
        _camelot_mod = mod
    return _camelot_mod


def packet_checks(task: dict, checks: dict) -> None:
    toks = C.est_tokens(task["prompt"])
    checks["metric_packet_tokens"] = toks
    checks["metric_packet_within_budget"] = toks <= PACKET_CONTEXT - PACKET_RESERVE


def _mk(task_id, scorer, prompt, inputs, budget, answer_format, private, grading_only=()):
    return {"task_id": task_id, "track": "small", "skill": C.SKILL_OF_TRACK["small"], "prompt": prompt,
            "inputs": inputs, "grading_only": sorted(grading_only), "budget_tokens": budget, "scorer": scorer,
            "answer_format": answer_format, "private": private}


# ---------------------------------------------------------------- generation
def generate(files: dict, sources: set) -> list:
    C.ensure_paths()
    sources.update(SMALL_SOURCES)
    tasks = []
    tasks += _gen_qlora()
    tasks += _gen_patch()
    tasks += _gen_camelot()
    return tasks


def _gen_qlora() -> list:
    from swmd_build_qlora_examples import build_examples
    from swmd_encounter_index import parse_swmd_min

    paths = [C.abspath(p) for p in QLORA_WORLDS]
    rows = build_examples(paths, max_total_encounters=1000, examples_per_encounter=10)
    docs = {str(C.abspath(w)): (w, parse_swmd_min(C.abspath(w))) for w in QLORA_WORLDS}
    first = {}
    for r in rows:
        m = r["meta"]
        first.setdefault((r["task_type"], m["source_swmd"], m["encounter_id"]), r)
    tasks = []
    for ttype in ("compile", "compression", "repair", "targeted_edit"):
        keys = sorted(k for k in first if k[0] == ttype and len(docs[k[1]][1].encounters[k[2]].reactions) >= 2
                      and first[k]["output"].strip() != first[k]["input"].strip())
        rng = random.Random(f"{C.SEED}:qlora:{ttype}")
        for key in sorted(rng.sample(keys, QLORA_PICKS_PER_TYPE)):
            row = first[key]
            world = docs[key[1]][0]
            eid = key[2]
            slug = world.split("/")[1].split("-")[0] + "_" + eid
            prompt = f"{SYSTEM}\n\n{row['instruction']}\n\n{row['input']}\n\nReturn the JSON object only."
            inp = json.loads(row["input"]) if row["input"].lstrip().startswith("{") else None
            priv = {"kind": "qlora", "type": ttype, "encounter_id": eid,
                    "expected": json.loads(row["output"]),
                    "input_agents": inp.get("agents") if inp else None,
                    "oracle": {"text": row["output"]}, "identity": {"text": row["input"]}}
            tasks.append(_mk(f"small.{ttype}.{slug}", "small.qlora", prompt, {"swmd": world}, 2048,
                             "SWMD-MICRO-0.1 JSON object", priv))
    return tasks


def _block_of(full: str, enc_id: str) -> str:
    start = full.index(f"## ENC {enc_id} ")
    nxt = full.find("\n## ENC ", start + 1)
    return full[start:nxt if nxt != -1 else len(full)].rstrip() + "\n"


def _gen_patch() -> list:
    import json_to_swmd as j
    from swmd_patch_json import parse_swmd_full

    tasks = []
    for wi, world in enumerate(PATCH_WORLDS):
        data = json.loads(C.abspath(world).read_text(encoding="utf-8"))
        full = j.emit_full(data)
        stem = world.split("/")[-1][:-5]
        ids = [e["id"] for e in data["encounters"]]
        # redirect: first encounter that has a `wild` reaction, retargeted to another real encounter
        for kind in ("redirect", "phrase"):
            if kind == "redirect":
                pick = next(e for e in data["encounters"] for o in e["options"] for r in o["reactions"]
                            if r["consequence_id"] == "wild")
                rxn = next(r for o in pick["options"] for r in o["reactions"] if r["consequence_id"] == "wild")
                target = next(i for i in ids if i != pick["id"])
                edit = {"rxn_id": rxn["id"], "target": target}
                instruction = (f"Edit this encounter block: redirect reaction {rxn['id']} so it points to {target} "
                               f"instead of wild. Change nothing else.")
            else:
                pick = data["encounters"][0]
                edit = {"phrase": PHRASES[wi]}
                instruction = (f"Edit this encounter block: extend the encounter's own `T:` text (the first T line, "
                               f"not a reaction's) so it contains the exact phrase \"{PHRASES[wi]}\" while keeping the "
                               f"original wording. Change nothing else.")
            block = _block_of(full, pick["id"])
            if kind == "redirect":
                oracle = block.replace(f"RXN {edit['rxn_id']} -> wild", f"RXN {edit['rxn_id']} -> {edit['target']}")
            else:
                lines = block.split("\n")
                ti = next(i for i, ln in enumerate(lines) if ln.startswith("T:"))
                lines[ti] = lines[ti].rstrip() + " " + edit["phrase"]
                oracle = "\n".join(lines)
            assert oracle != block
            prompt = (f"SWMD-0 encounter block from the storyworld `{data.get('title', stem)}`.\n{instruction}\n"
                      "Keep every id (`## ENC`, `OPT`, `RXN`), keep every `E:` and `D:` line exactly as written, and keep "
                      "the SWMD-0 syntax.\nReturn the complete encounter block only, from the `## ENC` header line to its "
                      f"last line. No prose, no code fence.\n\n{block}")
            slug = f"{stem}.{pick['id']}.{kind}"
            priv = {"kind": "patch", "patch_kind": kind, "world": world, "encounter_id": pick["id"], "edit": edit,
                    "orig_block": block, "oracle": {"text": oracle}, "identity": {"text": block}}
            tasks.append(_mk(f"small.patch.{slug}", "small.patch", prompt, {"world": world}, 1536,
                             "one SWMD-0 encounter block", priv))
    return tasks


def _gen_camelot() -> list:
    br = camelot()
    tasks = []
    for eid in br.SAMPLE_IDS:
        row = br.ENCOUNTERS[eid]
        prompt, next_id = br.build_task(row)
        raw = {k: row[k] for k in ("encounter_id", "characters_present", "scene", "options", "is_ending", "ending_text")}
        fan = next_id is None and not row.get("is_ending")
        priv = {"kind": "camelot", "encounter_id": eid, "next_id": next_id, "row": raw,
                "oracle": {"text": json.dumps(br.GT_PAGES[eid])}, "identity": {"text": json.dumps(raw)}}
        tasks.append(_mk(f"small.repair.camelot.{eid}", "small.camelot", prompt,
                         {"encounters": f"{CAMELOT_DIR}/encounters.jsonl"},
                         9000 if fan else 2048, "one SweepWeave page as JSON", priv,
                         # The repaired world holds every gold page.
                         grading_only=[f"{CAMELOT_DIR}/{name}" for name in
                                       ("storyworld.json", "storyworld.swmd.min.md", "storyworld_bundle.json")]))
    return tasks


# ---------------------------------------------------------------- scoring
def score(task: dict, raw: str) -> dict:
    C.ensure_paths()
    kind = task["private"]["kind"]
    return {"qlora": _score_qlora, "patch": _score_patch, "camelot": _score_camelot}[kind](task, raw)


def _finish_bool(task, checks, require_all=True, exclude=()):
    bools = {k: v for k, v in checks.items() if isinstance(v, bool) and not k.startswith("metric_")}
    sc = C.mean(1.0 if v else 0.0 for v in bools.values())
    gate = [v for k, v in bools.items() if k not in exclude and k != "model_parse_ok"]
    return C.finish(task, checks, sc, all(gate))


def _score_qlora(task, raw):
    priv = task["private"]
    exp = priv["expected"]
    obj, model_ok, parse_ok = C.parse_json_artifact(raw)
    checks = {"model_parse_ok": model_ok, "parse_ok": parse_ok}
    packet_checks(task, checks)
    if not parse_ok or not isinstance(obj, dict):
        return C.finish(task, checks, 0.0, False, "artifact is not a JSON object")
    acts = obj.get("actions") if isinstance(obj.get("actions"), list) else []
    act_ids = [a.get("id") for a in acts if isinstance(a, dict)]
    exp_ids = [a["id"] for a in exp["actions"]]
    checks["schema_key"] = obj.get("schema") == "SWMD-MICRO-0.1"
    checks["keys_identical"] = set(obj.keys()) == set(exp.keys())
    checks["encounter_id_preserved"] = obj.get("encounter_id") == exp["encounter_id"]
    checks["action_ids_preserved"] = sorted(map(str, act_ids)) == sorted(exp_ids)
    transitions = [a.get("transition") for a in acts if isinstance(a, dict)]
    checks["transitions_valid"] = bool(transitions) and all(isinstance(t, str) and t for t in transitions) \
        and sorted(set(transitions)) == sorted(set(a["transition"] for a in exp["actions"]))
    t = priv["type"]
    if t == "compression":
        checks["agents_le_5"] = isinstance(obj.get("agents"), list) and len(obj["agents"]) <= 5
        checks["state_vars_le_10"] = isinstance(obj.get("state_vars"), list) and len(obj["state_vars"]) <= 10
    elif t == "repair":
        checks["action_ids_unique"] = len(set(act_ids)) == len(act_ids) and len(act_ids) > 0
    elif t == "targeted_edit":
        norms = obj.get("norms") if isinstance(obj.get("norms"), list) else []
        checks["no_new_agents"] = obj.get("agents") == priv["input_agents"]
        checks["two_conflict_incentives"] = sum(1 for n in norms if str(n).startswith("incentive_conflict:")) >= 2
    checks["exact_match"] = obj == exp
    return _finish_bool(task, checks, exclude=("exact_match",))


_ENC_HDR = re.compile(r"^## ENC\s+(\S+)")


def _extract_block(raw: str):
    """Return (block_text, model_parse_ok)."""
    strict = raw.strip().startswith("## ENC") and "```" not in raw
    text = C.strip_wrappers(raw)
    lines = text.split("\n")
    start = next((i for i, ln in enumerate(lines) if _ENC_HDR.match(ln)), None)
    if start is None:
        return None, False
    return "\n".join(lines[start:]).rstrip() + "\n", strict


def _score_patch(task, raw):
    from swmd_patch_json import parse_swmd_full, patch_world
    from sweepweave_validator import validate_storyworld
    C.ensure_paths()
    priv = task["private"]
    block, strict = _extract_block(raw)
    checks = {"model_parse_ok": strict, "parse_ok": block is not None}
    packet_checks(task, checks)
    if block is None:
        return C.finish(task, checks, 0.0, False, "no `## ENC` block in artifact")

    def parse(text):
        p = C.write_temp_json({}, ".md")
        p.write_text(text, encoding="utf-8")
        try:
            return parse_swmd_full(p)
        finally:
            p.unlink(missing_ok=True)

    orig, got = parse(priv["orig_block"]), parse(block)
    eid = priv["encounter_id"]
    oe, ge = orig["encounters"][eid], got["encounters"].get(eid)
    if ge is None or len(got["encounters"]) != 1:
        checks["id_preserved"] = False
        return _finish_bool(task, checks)

    def struct(enc):
        return [(o, [r for r in enc["options"][o]["reactions"]]) for o in enc["options"]]

    checks["id_preserved"] = struct(oe) == struct(ge)
    keep = lambda text: [ln.strip() for ln in text.split("\n") if ln.strip().startswith(("E:", "D:", "SET "))]
    checks["formulas_preserved"] = keep(priv["orig_block"]) == keep(block)

    edit = priv["edit"]
    if priv["patch_kind"] == "redirect":
        tgt = lambda enc: {r: v["consequence_id"] for o in enc["options"].values() for r, v in o["reactions"].items()}
        want = tgt(oe)
        want[edit["rxn_id"]] = edit["target"]
        have = tgt(ge)
        checks["edit_applied"] = have.get(edit["rxn_id"]) == edit["target"]
        checks["no_collateral"] = have == want and oe["text"] == ge["text"] and \
            all(oe["options"][o]["text"] == ge["options"][o]["text"] for o in oe["options"] if o in ge["options"])
    else:
        checks["edit_applied"] = edit["phrase"] in ge["text"] and oe["text"] in ge["text"]
        rx = lambda enc: {r: (v["text"], v["consequence_id"]) for o in enc["options"].values() for r, v in o["reactions"].items()}
        checks["no_collateral"] = rx(oe) == rx(ge) and \
            all(oe["options"][o]["text"] == ge["options"][o]["text"] for o in oe["options"] if o in ge["options"])

    base = json.loads(C.abspath(priv["world"]).read_text(encoding="utf-8"))
    patched, report = patch_world(copy.deepcopy(base), got)
    p = C.write_temp_json(patched)
    try:
        errors = validate_storyworld(str(p))
    finally:
        p.unlink(missing_ok=True)
    checks["validator_after_patch"] = not errors and not report["missing_encounters"] \
        and not report["missing_options"] and not report["missing_reactions"]
    return _finish_bool(task, checks)


def _score_camelot(task, raw):
    from sweepweave_validator import validate_storyworld
    br = camelot()
    priv = task["private"]
    page, model_ok, parse_ok = C.parse_json_artifact(raw)
    checks = {"model_parse_ok": model_ok, "parse_ok": parse_ok}
    packet_checks(task, checks)
    if not parse_ok or not isinstance(page, dict):
        return C.finish(task, checks, 0.0, False, "artifact is not a JSON object")
    eid = priv["encounter_id"]
    try:
        res = br.score_page(eid, page, priv["next_id"], priv["row"])
        checks.update({k: bool(v) for k, v in res["checks"].items()})
    except Exception as exc:
        return C.finish(task, checks, 0.0, False, f"scorer error {type(exc).__name__}: {exc}")
    mini = copy.deepcopy(br.GROUND_TRUTH)
    mini["encounters"] = [page if p["id"] == eid else p for p in mini["encounters"]]
    p = C.write_temp_json(mini)
    try:
        errors = validate_storyworld(str(p))
    finally:
        p.unlink(missing_ok=True)
    checks["validator_ok"] = not errors
    return _finish_bool(task, checks)
