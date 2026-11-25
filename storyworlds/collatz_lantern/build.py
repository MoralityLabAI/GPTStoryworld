"""Compile the Lantern SWMD template and audit all public-observation policies."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import re
from collections import Counter
from fractions import Fraction
from pathlib import Path

from collatz_core import analyze, modular_labels, odd_step

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRIPTS = ROOT / "codex-skills/storyworld-building/scripts"


def load_helper(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PATCHER = load_helper("swmd_patch_json")
EXPORTER = load_helper("json_to_swmd")
SIMULATOR = load_helper("monte_carlo_rehearsal")
VALIDATOR = load_helper("sweepweave_validator")


def string(value):
    return dict(pointer_type="String Constant", value=value)


def pointer(path):
    character, prop = path.split(".")
    return dict(pointer_type="Bounded Number Pointer", character=character, keyring=[prop])


def expression(text: str, constants: dict):
    """Parse only the source's C/P/ADD/MUL grammar; reject unknown syntax."""
    match = re.fullmatch(r"([A-Z]+)\((.*)\)", text.strip())
    if not match:
        raise ValueError(f"invalid expression: {text}")
    op, body = match.groups()
    if op == "C":
        value = constants[body[1:]] if body.startswith("@") else float(body)
        return dict(pointer_type="Bounded Number Constant", value=value)
    if op == "P":
        if not re.fullmatch(r"char_keeper\.(Cost|Score)", body):
            raise ValueError(f"invalid property: {body}")
        return pointer(body)
    if op not in ("ADD", "MUL"):
        raise ValueError(f"unsupported operator: {op}")
    parts, depth, start = [], 0, 0
    for index, char in enumerate(body):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(body[start:index])
            start = index + 1
        if depth < 0:
            raise ValueError("unbalanced parentheses")
    if depth != 0:
        raise ValueError("unbalanced parentheses")
    parts.append(body[start:])
    return dict(operator_type={"ADD": "Addition", "MUL": "Multiplication"}[op],
                operands=[expression(part, constants) for part in parts])


def build(seed: int) -> dict:
    if seed not in (1, 5):
        raise ValueError("the registered fixture has two hidden starts")
    core = analyze(13)
    next_state = odd_step(seed, 13)[0]
    constants = dict(west=int(core.basin[seed] == 1), east=int(core.basin[seed] == 5),
                     amber=int(next_state % 4 == 1), blue=int(next_state % 4 == 3))
    encounters, active = [], False
    for raw in (HERE / "source.swmd.min.md").read_text().splitlines():
        line = raw.strip()
        if line == "# SWMD-0-MIN":
            active = True
            continue
        if not active or not line or line.startswith(("id:", "title:")):
            continue
        if line.startswith("ENC "):
            ident = line.split()[1]
            encounters.append(dict(id=ident, title=ident, text_script=string(ident),
                earliest_turn=0, latest_turn=99, acceptability_script=True,
                creation_index=len(encounters), options=[], connected_spools=["spool_lantern"]))
            continue
        match = re.fullmatch(r"ORX (\w+)/(\w+) -> (\w+) \| O:(.*?) \| E:(.*?) \| D:(.*)", line)
        if match is None or not encounters:
            raise ValueError(f"unsupported SWMD line: {line}")
        option_id, reaction_id, target, label, effect, desirability = match.groups()
        options = encounters[-1]["options"]
        option = next((o for o in options if o["id"] == option_id), None)
        if option is None:
            option = dict(id=option_id, text_script=string(label), visibility_script=True,
                          performability_script=True, reactions=[])
            options.append(option)
        elif option["text_script"]["value"] != label:
            raise ValueError("one option has inconsistent prose")
        effect_match = re.fullmatch(r"SET (char_keeper\.(?:Cost|Score)) = (.*)", effect)
        if not effect_match:
            raise ValueError("unsupported effect")
        property_path, rhs = effect_match.groups()
        option["reactions"].append(dict(id=reaction_id, consequence_id=target,
            text_script=string("Mara records your choice. Continue to see its consequence."),
            desirability_script=expression(desirability, constants),
            after_effects=[dict(effect_type="Bounded Number Effect", Set=pointer(property_path),
                                to=expression(rhs, constants))]))
    world = dict(IFID="SW-collatz-lantern-v1", storyworld_title="The Lantern Ledger",
        sweepweave_version="0.1.9", about_text=string("A finite arithmetic observation puzzle."),
        css_theme="default", debug_mode=False, display_mode="text", creation_time=1795564800,
        modified_time=1795564800,
        characters=[dict(id="char_keeper", name="Mara", bnumber_properties={"Cost": 0, "Score": 0})],
        authored_properties=[dict(id=name, property_name=name, depth=0, default_value=0)
                             for name in ("Cost", "Score")],
        spools=[dict(id="spool_lantern", spool_name="The ledger", starts_active=True,
                     creation_index=0, encounters=[e["id"] for e in encounters if e["options"]]),
                dict(id="spool_endings", spool_name="Endings", starts_active=False,
                     creation_index=1, encounters=[e["id"] for e in encounters if not e["options"]])],
        encounters=encounters)
    world, report = PATCHER.patch_world(world, PATCHER.parse_swmd_full(HERE/"prose.swmd.md"))
    assert all(not report[k] for k in ("missing_encounters", "missing_options", "missing_reactions"))
    assert report["reaction_consequence"] == 0
    return world


def observe(world: dict, encounter_id: str, state: dict) -> dict:
    """The complete agent packet. Native authoring JSON stays evaluator-side."""
    encounter = next(e for e in world["encounters"] if e["id"] == encounter_id)
    return dict(scene=encounter_id, title=encounter["title"],
        text=encounter["text_script"]["value"],
        cost=state.get(("char_keeper", "Cost"), 0),
        options=[dict(action=o["id"], text=o["text_script"]["value"])
                 for o in encounter["options"]])


def replay(world: dict, policy: dict) -> dict:
    state, history, ident = {}, [], SIMULATOR.starting_encounter(world)
    by_id = {e["id"]: e for e in world["encounters"]}
    for _ in range(5):
        encounter = by_id[ident]
        if not encounter["options"]:
            return dict(ending=ident, score=state[("char_keeper", "Score")], history=history)
        option_id = policy[ident]
        observation = observe(world, ident, state)
        option = next(o for o in encounter["options"] if o["id"] == option_id)
        reaction = SIMULATOR.select_reaction(option, state)
        SIMULATOR.apply_effects(reaction, state)
        history.append(dict(observation=observation, action=option_id))
        ident = reaction["consequence_id"]
    raise AssertionError("unexpected loop or dead end")


def evaluate(worlds: list[dict]) -> dict:
    nodes = [e for e in worlds[0]["encounters"] if e["options"]]
    policies, histogram = [], Counter()
    for index, actions in enumerate(itertools.product(*[[o["id"] for o in e["options"]] for e in nodes])):
        policy = dict(zip([e["id"] for e in nodes], actions))
        replays = [replay(w, policy) for w in worlds]
        value = sum(Fraction(str(r["score"])) for r in replays) / 2
        histogram[str(value)] += 1
        policies.append(dict(index=index, policy=policy, mean_value=str(value), replays=replays))
    q, core = modular_labels(13), analyze(13)
    assert q[1] == q[5] and core.basin[1] != core.basin[5]
    assert observe(worlds[0], "page_0000", {}) == observe(worlds[1], "page_0000", {})
    assert observe(worlds[0], "page_ledger", {}) == observe(worlds[1], "page_ledger", {})
    optimum = max(Fraction(p["mean_value"]) for p in policies)
    no_sample = [p for p in policies if all(t["action"] != "opt_sample"
                 for r in p["replays"] for t in r["history"])]
    blind = max(Fraction(p["mean_value"]) for p in no_sample)
    assert optimum == Fraction(7, 8) and blind == Fraction(1, 2)
    return dict(schema="lantern.audit.v1", evidence="exact finite fixture", d=13,
        evaluator_only_hidden_starts=[1, 5], odd_cycles=[[1], [5, 7]], shared_quotient=q[1],
        initial_observations_equal=True, ledger_observations_equal=True,
        native_policies=len(policies), native_replays=2*len(policies),
        score_histogram=dict(sorted(histogram.items())), optimal_value=str(optimum),
        best_without_sample=str(blind), sample_cost="1/8", value_of_sampling=str(optimum-blind),
        source_sha256={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                       for name in ("source.swmd.min.md", "prose.swmd.md", "collatz_core.py")},
        policies=policies)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--write", action="store_true")
    modes.add_argument("--check", action="store_true")
    args = parser.parse_args()
    worlds = [build(seed) for seed in (1, 5)]
    outputs = {}
    for stem, world in zip(("world_a", "world_b"), worlds):
        outputs[f"native/{stem}.json"] = json.dumps(world, indent=2)+"\n"
        outputs[f"native/{stem}.swmd.min.md"] = EXPORTER.emit_minified(world)
    outputs["public_initial.json"] = json.dumps(observe(worlds[0], "page_0000", {}), indent=2)+"\n"
    audit = evaluate(worlds)
    outputs["audit.json"] = json.dumps(audit, indent=2, sort_keys=True)+"\n"
    for name, payload in outputs.items():
        path = HERE/name
        if args.write:
            path.parent.mkdir(exist_ok=True)
            path.write_text(payload, encoding="utf-8")
        elif path.read_text(encoding="utf-8") != payload:
            raise SystemExit(f"export drift: {name}")
    for stem in ("world_a", "world_b"):
        errors = VALIDATOR.validate_storyworld(str(HERE/f"native/{stem}.json"))
        if errors:
            raise SystemExit(str(errors))
    print(f"Lantern: {audit['native_policies']} policies, {audit['native_replays']} native Python replays; optimum 7/8")


if __name__ == "__main__":
    main()
