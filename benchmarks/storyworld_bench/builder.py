"""Track 1: builder. Whole-world SweepWeave authoring and repair, graded by the repo's validator, quality gate and rehearsal."""
from __future__ import annotations

import copy
import json
import random
import sys

from . import common as C

REPAIR_WORLDS = [
    "storyworlds/england_to_france_honest.json",
    "storyworlds/russia_to_austria_grudger.json",
    "storyworlds/france_to_germany_machiavellian.json",
    "storyworlds/russia_to_austria_grudger_p.json",
    "storyworlds/england_to_france_honest_p.json",
]
INTRINSIC_WORLDS = ["storyworlds/diplo1.json", "storyworlds/glam_to_shadow_honest.json"]
AUTHOR_SOURCE = "storyworlds/the_fifth_testimony_p2.json"
BUNDLES = [("no_start", "dangling"), ("spool_ghost", "missing_keys")]
MC_RUNS = 200
MC_SEED = 42

BUILDER_SOURCES = [
    "codex-skills/storyworld-building/scripts/sweepweave_validator.py",
    "codex-skills/storyworld-building/scripts/storyworld_quality_gate.py",
    "codex-skills/storyworld-building/scripts/polish_metrics.py",
    "codex-skills/storyworld-building/scripts/monte_carlo_rehearsal.py",
    "benchmarks/storyworld_builder_small_model/score_small_model_storyworld_builder.py",
    "codex-skills/storyworld-building/SKILL.md",
    "codex-skills/small-storyworld-builder/SKILL.md",
]

VALIDATOR_RULES = """Validator rules (sweepweave_validator.py validate):
- top-level keys required: IFID, about_text, css_theme, debug_mode, display_mode, creation_time, modified_time, characters, authored_properties, spools, encounters
- encounters must be non-empty; every spool needs a non-empty "encounters" list of existing encounter ids; at least one spool has "starts_active": true
- every reaction needs a non-empty "consequence_id" that is an existing encounter id or the literal "wild"
- if "multiplayer" is present, "turns" must be a non-empty list of character ids"""


# ---------------------------------------------------------------- corruptions
def _reactions(d):
    return [(e, o, r) for e in d["encounters"] for o in e.get("options", []) for r in o.get("reactions", [])]


def corrupt(d: dict, kind: str, rng: random.Random) -> dict:
    d = copy.deepcopy(d)
    if kind == "no_start":
        for s in d["spools"]:
            s["starts_active"] = False
    elif kind == "dangling":
        rx = _reactions(d)
        for i, idx in enumerate(sorted(rng.sample(range(len(rx)), 2))):
            rx[idx][2]["consequence_id"] = f"enc_missing_{i + 1}"
    elif kind == "spool_ghost":
        d["spools"][0]["encounters"].append("enc_ghost_001")
    elif kind == "missing_keys":
        d.pop("IFID", None)
        d.pop("css_theme", None)
    else:
        raise ValueError(kind)
    return d


def auto_fix_spools(d: dict) -> dict:
    """Deterministic oracle for worlds whose spools lack `encounters`: rebuild membership from connected_spools."""
    d = copy.deepcopy(d)
    members = {s["id"]: [] for s in d["spools"]}
    for e in d["encounters"]:
        for sid in e.get("connected_spools", []) or []:
            if sid in members:
                members[sid].append(e["id"])
    first = d["encounters"][0]["id"]
    for s in d["spools"]:
        s["encounters"] = members[s["id"]]
        s["starts_active"] = first in members[s["id"]]
    return d


# ---------------------------------------------------------------- measurement
def world_metrics(obj: dict, errors: list | None = None) -> dict:
    """Validator + quality gate + rehearsal reachability for one storyworld object."""
    C.ensure_paths()
    import storyworld_quality_gate as qg
    import monte_carlo_rehearsal as mc
    from sweepweave_validator import validate_storyworld

    if errors is None:
        p = C.write_temp_json(obj)
        try:
            errors = validate_storyworld(str(p))
        finally:
            p.unlink(missing_ok=True)
    out = {"schema_valid": not errors, "validator_errors": errors[:5],
           "gate_pass": 0, "gate_total": 0, "gate_ok": False, "gate_failed": [],
           "terminals": 0, "reached": 0, "reach_frac": 0.0, "dead_end_rate": 1.0}
    try:
        rep = qg.evaluate_storyworld(obj, errors)
        checks = rep["checks"]
        out["gate_total"] = len(checks)
        out["gate_pass"] = sum(1 for c in checks if c.get("pass"))
        out["gate_ok"] = bool(rep.get("pass"))
        out["gate_failed"] = [c["name"] for c in checks if not c.get("pass")]
    except Exception as exc:  # malformed structure the gate cannot read
        out["gate_error"] = f"{type(exc).__name__}: {exc}"
    try:
        enc = [e for e in obj.get("encounters", []) if isinstance(e, dict)]
        terminals = {e["id"] for e in enc if not e.get("options")}
        res = mc.run_monte_carlo(obj, num_runs=MC_RUNS, seed=MC_SEED)
        reached = {k for k in res["ending_counts"] if k in terminals}
        out["terminals"] = len(terminals)
        out["reached"] = len(reached)
        out["reach_frac"] = len(reached) / len(terminals) if terminals else 0.0
        out["dead_end_rate"] = res["dead_ends"] / MC_RUNS
    except Exception as exc:
        out["rehearsal_error"] = f"{type(exc).__name__}: {exc}"
    return out


def text_cells(obj: dict) -> dict:
    cells = {}
    for e in obj.get("encounters", []) or []:
        if not isinstance(e, dict):
            continue
        eid = e.get("id")
        cells[f"{eid}"] = json.dumps(e.get("text_script"), sort_keys=True)
        for o in e.get("options", []) or []:
            if not isinstance(o, dict):
                continue
            cells[f"{eid}/{o.get('id')}"] = json.dumps(o.get("text_script"), sort_keys=True)
            for r in o.get("reactions", []) or []:
                if isinstance(r, dict):
                    cells[f"{eid}/{o.get('id')}/{r.get('id')}"] = json.dumps(r.get("text_script"), sort_keys=True)
    return cells


def structure_sketch(world: dict) -> str:
    enc = world["encounters"][0]
    opt = enc["options"][0]
    rxn = opt["reactions"][0]
    lines = [
        "top-level keys: " + ", ".join(world.keys()),
        "spool keys: " + ", ".join(world["spools"][0].keys()),
        "encounter keys: " + ", ".join(enc.keys()),
        "option keys: " + ", ".join(opt.keys()),
        "reaction keys: " + ", ".join(rxn.keys()),
        "string content is stored as {\"pointer_type\": \"String Constant\", \"script_element_type\": \"Pointer\", \"value\": \"...\"}",
    ]
    return "\n".join(lines)


def _base(m: dict) -> dict:
    return {k: m[k] for k in ("gate_pass", "gate_total", "reach_frac", "terminals", "schema_valid")}


# ---------------------------------------------------------------- generation
def generate(files: dict, sources: set) -> list:
    C.ensure_paths()
    from sweepweave_validator import validate_storyworld

    tasks = []
    sources.update(BUILDER_SOURCES)

    def validate(obj):
        p = C.write_temp_json(obj)
        try:
            return validate_storyworld(str(p))
        finally:
            p.unlink(missing_ok=True)

    def dump(obj) -> bytes:
        return (json.dumps(obj, indent=1, ensure_ascii=False) + "\n").encode("utf-8")

    def repair_task(task_id, src_rel, broken, oracle_rel, base_obj, note):
        errors = validate(broken)
        assert errors, task_id
        data_rel = f"benchmarks/storyworld_bench/data/builder/{task_id}.json"
        files[f"builder/{task_id}.json"] = dump(broken)
        prompt = (
            "You are repairing a SweepWeave storyworld. Input `world` fails `sweepweave_validator.py validate`.\n"
            "Return the COMPLETE repaired storyworld as one JSON object and nothing else.\n"
            "Make the minimum edits needed for the validator to print VALID OK. Do not remove or rename any encounter, "
            "option or reaction, and do not rewrite any text; keep everything else unchanged.\n\n"
            f"{VALIDATOR_RULES}\n\nValidator output on the input world:\nInvalid: {errors}\n"
        )
        base = world_metrics(base_obj)
        tokens = max(4096, int(len(files[f'builder/{task_id}.json']) / 2.6) + 2048)
        sources.add(src_rel)
        tasks.append({
            "task_id": task_id, "track": "builder", "skill": C.SKILL_OF_TRACK["builder"], "prompt": prompt,
            "inputs": {"world": data_rel}, "budget_tokens": tokens, "scorer": "builder.repair",
            "answer_format": "storyworld JSON object (the full repaired world)",
            "private": {"kind": "repair", "source": src_rel, "oracle": {"path": oracle_rel},
                        "note": note, "baseline": _base(base), "orig_ids": [e["id"] for e in base_obj["encounters"]],
                        "identity": {"path": data_rel}},
        })

    for src in REPAIR_WORLDS:
        orig = json.loads(C.abspath(src).read_text(encoding="utf-8"))
        assert not validate(orig), src
        stem = src.split("/")[-1][:-5]
        for bi, bundle in enumerate(BUNDLES):
            rng = random.Random(f"{C.SEED}:{stem}:{bi}")
            broken = orig
            for kind in bundle:
                broken = corrupt(broken, kind, rng)
            repair_task(f"builder.repair.{stem}.b{bi}", src, broken, src, orig, "+".join(bundle))
    for src in INTRINSIC_WORLDS:
        orig = json.loads(C.abspath(src).read_text(encoding="utf-8"))
        fixed = auto_fix_spools(orig)
        assert not validate(fixed), src
        stem = src.split("/")[-1][:-5]
        files[f"builder/oracle_{stem}.json"] = dump(fixed)
        repair_task(f"builder.repair.{stem}.native", src, orig,
                    f"benchmarks/storyworld_bench/data/builder/oracle_{stem}.json", fixed,
                    "repo world with spools missing encounters")

    # author tasks: brief derived from a world that passes the gate
    sources.add(AUTHOR_SOURCE)
    world = json.loads(C.abspath(AUTHOR_SOURCE).read_text(encoding="utf-8"))
    base = world_metrics(world)
    assert base["schema_valid"] and base["gate_ok"] and base["reach_frac"] == 1.0, base
    import storyworld_quality_gate as qg
    rep = qg.evaluate_storyworld(world, [])
    gate_lines = "\n".join(f"- {c['name']}: target {c['target']}" for c in rep["checks"])
    tiers = [
        ("small", 6, 3, 2, "a short courtroom-style mystery with three or four voices"),
        ("medium", 9, 5, 3, "a political whodunit about a city deciding whose testimony to believe"),
        ("full", 11, 7, 4, "a deep-state trial storyworld in which four characters hold conflicting testimony"),
    ]
    for name, n_enc, n_end, n_chr, theme in tiers:
        task_id = f"builder.author.{name}"
        prompt = (
            f"Author a new SweepWeave storyworld: {theme}.\n"
            "Return the COMPLETE storyworld as one JSON object and nothing else.\n"
            f"Hard requirements: at least {n_enc} encounters, at least {n_end} terminal encounters (empty options), "
            f"at least {n_chr} characters, and a random-play rehearsal must reach every terminal ending.\n"
            "The world must pass the validator and the quality gate.\n\n"
            f"{VALIDATOR_RULES}\n\nQuality gate checks (storyworld_quality_gate.py --strict):\n{gate_lines}\n\n"
            f"Structure (key names only):\n{structure_sketch(world)}\n"
        )
        tasks.append({
            "task_id": task_id, "track": "builder", "skill": C.SKILL_OF_TRACK["builder"], "prompt": prompt,
            "inputs": {"schema_guide": "storyworld_format_guide.md"}, "budget_tokens": 32768,
            "scorer": "builder.author", "answer_format": "storyworld JSON object (a complete new world)",
            "private": {"kind": "author", "source": AUTHOR_SOURCE, "oracle": {"path": AUTHOR_SOURCE},
                        "constraints": {"min_encounters": n_enc, "min_endings": n_end, "min_characters": n_chr},
                        "baseline": _base(base), "identity": {"text": ""}},
        })
    sources.add("storyworld_format_guide.md")
    return tasks


# ---------------------------------------------------------------- scoring
def score(task: dict, raw: str) -> dict:
    priv = task["private"]
    obj, model_ok, parse_ok = C.parse_json_artifact(raw)
    checks = {"model_parse_ok": model_ok, "parse_ok": parse_ok}
    if not parse_ok or not isinstance(obj, dict):
        return C.finish(task, checks, 0.0, False, "artifact is not a JSON object")
    m = world_metrics(obj)
    base = priv["baseline"]
    checks["schema_valid"] = m["schema_valid"]
    checks["quality_gate_pass"] = m["gate_ok"]
    gate_frac = m["gate_pass"] / m["gate_total"] if m["gate_total"] else 0.0
    checks["metric_gate_checks_passed"] = m["gate_pass"]
    checks["metric_gate_checks_total"] = m["gate_total"]
    checks["metric_terminals_reached"] = m["reached"]
    checks["metric_terminals"] = m["terminals"]
    checks["metric_dead_end_rate"] = round(m["dead_end_rate"], 4)
    if m["validator_errors"]:
        checks["metric_validator_errors"] = m["validator_errors"]
    _diagnostics(obj, checks)

    if priv["kind"] == "repair":
        orig_ids = priv["orig_ids"]
        got_ids = {e.get("id") for e in obj.get("encounters", []) if isinstance(e, dict)}
        ids_pres = sum(1 for i in orig_ids if i in got_ids) / len(orig_ids)
        base_world = json.loads(C.abspath(priv["oracle"]["path"]).read_text(encoding="utf-8"))
        want, got = text_cells(base_world), text_cells(obj)
        text_pres = sum(1 for k, v in want.items() if got.get(k) == v) / len(want) if want else 1.0
        base_gate = base["gate_pass"] / base["gate_total"] if base["gate_total"] else 1.0
        gate_ret = min(1.0, gate_frac / base_gate) if base_gate else 1.0
        end_ret = 1.0 if base["reach_frac"] == 0 else min(1.0, m["reach_frac"] / base["reach_frac"])
        checks.update({"ids_preserved": round(ids_pres, 4), "text_preserved": round(text_pres, 4),
                       "gate_retained": round(gate_ret, 4), "endings_retained": round(end_ret, 4)})
        rest = 0.3 * ids_pres + 0.2 * text_pres + 0.3 * gate_ret + 0.2 * end_ret
        sc = 0.4 + 0.6 * rest if m["schema_valid"] else 0.3 * rest
        passed = m["schema_valid"] and ids_pres == 1.0 and text_pres == 1.0 and gate_ret >= 1.0 and end_ret >= 1.0
        return C.finish(task, checks, sc, passed)

    cons = priv["constraints"]
    encs = [e for e in obj.get("encounters", []) if isinstance(e, dict)]
    chars = obj.get("characters", []) if isinstance(obj.get("characters"), list) else []
    c_enc = len(encs) >= cons["min_encounters"]
    c_end = m["terminals"] >= cons["min_endings"]
    c_chr = len(chars) >= cons["min_characters"]
    brief = C.mean([c_enc, c_end, c_chr])
    reach = min(1.0, m["reached"] / cons["min_endings"])
    checks.update({"brief_encounters": c_enc, "brief_endings": c_end, "brief_characters": c_chr,
                   "gate_checks_fraction": round(gate_frac, 4), "endings_reachable": round(reach, 4)})
    rest = 0.15 * brief + 0.35 * gate_frac + 0.15 * reach
    sc = 0.35 + rest if m["schema_valid"] else 0.3 * rest / 0.65
    passed = m["schema_valid"] and c_enc and c_end and c_chr and m["gate_ok"] and reach >= 1.0
    return C.finish(task, checks, sc, passed)


def _diagnostics(obj: dict, checks: dict) -> None:
    """Small-model builder scorecard components (benchmarks/storyworld_builder_small_model); reported, not scored."""
    try:
        C.ensure_paths()
        mod = sys.modules.get("sw_small_model_scorer") or C.load_module(
            C.REPO_ROOT / "benchmarks/storyworld_builder_small_model/score_small_model_storyworld_builder.py",
            "sw_small_model_scorer")
        p = C.write_temp_json(obj)
        try:
            metrics = mod.extract_storyworld_metrics(p)
        finally:
            p.unlink(missing_ok=True)
        comp = mod.component_scores(metrics, {}, {})
        for k in ("control_logic", "branching", "text_surface"):
            checks[f"metric_diag_{k}"] = comp[k]
    except Exception:
        pass
