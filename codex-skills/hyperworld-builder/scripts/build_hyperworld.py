"""Generate a SweepWeave narrative shell and exact 1,024-state hyperworld manifest.

Run from repository root:
  python codex-skills/hyperworld-builder/scripts/build_hyperworld.py \
    --out-dir storyworlds/cairo_directorate_hyperworld
  python codex-skills/storyworld-building/scripts/sweepweave_validator.py \
    validate storyworlds/cairo_directorate_hyperworld/storyworld.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from hyperworld_engine import (AXES, ACTORS, ACTION_LABELS, ACTIONS, DEFAULT_ACTIONS, SECRET_ENDINGS, CARDS,
                              FACTORS, PERSON_IDS, PRINCIPALS, PUBLIC_SEGMENTS,
                              SCHEMA, trait_values, tensor_capacity, run_scripted)
from hyperworld_phase import FOCUS_PEOPLE, FOCUS_EDGES

SCRIPTED_DEMO = ("brief", "audit", "brief", "charter", "audit", "charter", "charter")
ENDINGS = {
    "human_advisory_mandate": "Human advisers retain binding authority. Nūr remains an accountable analysis system.",
    "ratified_aiocracy_charter": "The fictional council ratifies a conditional AIocracy charter by independent human vote, with recall retained.",
    "constitutional_recall_review": "Constitutional counsel refuses an irrevocable mandate. The proposal returns for review.",
    "charter_rejected_by_council": "The council declines the proposed transfer of authority. The public deliberation continues.",
    "secret_aiocracy_consensus_snap": "SECRET: Nūr's modeled coalition experiences a sharp cascade. A separate fictional human council lawfully votes to grant a revocable AI governance charter.",
    "secret_mirror_majority": "SECRET: Apparent coalition unanimity collapses under independent voting. Nested beliefs had manufactured the appearance of consensus.",
    "secret_civic_counterphase": "SECRET: Independent public forums unwind the chamber's coordination cascade. The charter is returned to human advisory status.",
    "secret_constitutional_tripwire": "SECRET: The modeled consensus snaps, then constitutional recall safeguards reveal an invalid proposed delegation. Judicial review prevails.",
}


def text(value: str) -> dict:
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": value}


def number(value: float) -> dict:
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": value}


def pointer(actor: str, keyring: list[str]) -> dict:
    return {"pointer_type": "Bounded Number Pointer", "script_element_type": "Pointer",
            "character": actor, "keyring": keyring, "coefficient": 1.0}


def comparator(actor: str, ring: list[str], op: str, threshold: float) -> dict:
    return {"operator_type": "Arithmetic Comparator", "script_element_type": "Operator",
            "operator_subtype": op,
            "operands": [pointer(actor, ring), number(threshold)]}


def both(*conditions: dict) -> dict:
    return {"operator_type":"And", "script_element_type":"Operator", "operands":list(conditions)}


def effect(actor: str, keyring: list[str], delta: float) -> dict:
    return {
        "effect_type": "Bounded Number Effect",
        "Set": pointer(actor, keyring),
        "to": {"operator_type": "Nudge", "script_element_type": "Operator",
               "operands": [pointer(actor, keyring), number(delta)]},
    }



SCENE_CHOICES = (
    ("Present the warning with its uncertainty intact.", "Seek an independent confirmation of the warning.", "Ask the fictional cabinet to debate a binding AI-governance charter."),
    ("Show how apparent agreement changes beliefs about relationships.", "Commission a separate assessment of the two offices.", "Propose giving Nūr a formal vote in future policy deliberations."),
    ("Disclose that this is a quotation of the first dispatch.", "Request an entirely new source for the directorate's claim.", "Invite the council to consider a broad AI mandate despite the repeated source."),
    ("Report counsel's concerns about recall faithfully.", "Ask for an independent constitutional review.", "Submit an expanded charter proposal for an explicit human vote."),
    ("Present the assemblies' positions as uncertain public evidence.", "Seek an independently gathered public hearing.", "Place the AIocracy proposal before both fictional public constituencies."),
    ("Publish the auditor's qualifications in the chamber record.", "Order a new audit rather than relying on the internal report.", "Ask for a broader charter while acknowledging oversight's objections."),
    ("Submit the council's findings in a qualified final brief.", "Request a final independent review before the vote.", "Call for the constitutional charter vote with human recall preserved."),
)


def _reaction(page: str, action: str, idx: int, next_page: str, turn: int) -> dict:
    # The p/p2 pointers use the verified StoryworldBuilder keyring forms.
    principal = PRINCIPALS[turn % len(PRINCIPALS)]
    other = PRINCIPALS[(turn + 2) % len(PRINCIPALS)]
    delta = {"audit": 0.045, "brief": 0.022, "charter": -0.025,
             "appeal": 0.034, "convene": 0.021, "sever": -0.035,
             "resonance": 0.052, "snap_vote": 0.045}[action]
    if idx:
        delta = -delta / 2
    after = [effect(principal, ["Evidence_Caution"], delta),
             effect("char_nur", ["AI_Reliance", principal], 0.6*delta),
             effect("char_nur", ["Human_Agency"], -delta)]
    if turn >= 2:
        # Second order: AI estimates how one human judges another human.
        after.append(effect("char_nur", ["AI_Reliance", principal, other], 0.5*delta))
    sentence = (
        "The council secretary records Nūr's recommendation and identifies its supporting evidence roots. "
        "An affected fictional official responds in their own voice, insisting that the AI's forecast remains a contestable claim. "
        "The next encounter retains the updated belief pointers and the human right to disagree."
        if idx == 0 else
        "The hearing becomes contentious when another witness questions the original source. "
        "Nūr's proposal survives as a matter for public debate, though its credibility shifts and the council requests clearer qualifications. "
        "No character's consent can be obtained merely by changing a second-order belief entry."
    )
    if action in ("resonance", "snap_vote"):
        # Export-only narrative score; canonical phase logic remains Python-side.
        desirability = {"operator_type": "Addition", "script_element_type": "Operator",
            "operands": [number(0.6 if idx else 0.9),
                         pointer("char_nur", ["AI_Reliance", principal, other])]}
    else:
        desirability = number(1.0 if idx == 0 else 0.8)
    return {"id": f"rxn_{page}_{action}_{idx}",
            "text_script": text(sentence),
            "consequence_id": next_page,
            "desirability_script": desirability,
            "after_effects": after}


def _option_gate(turn: int, action: str):
    """SweepWeave approximation plus explicit Python-only dynamic unlock rule."""
    target = FOCUS_PEOPLE[turn]
    pair = FOCUS_EDGES[turn]
    pp = comparator("char_nur", ["AI_Reliance", target], "Greater Than or Equal To", -0.2)
    p2 = comparator("char_nur", ["AI_Reliance", pair[0], pair[1]], "Greater Than or Equal To", -0.125)
    if action == "appeal":return pp
    if action == "convene":return p2
    if action == "sever":return comparator("char_nur", ["AI_Reliance", pair[0], pair[1]], "Less Than or Equal To", 0.25)
    if action == "resonance":return both(pp,comparator("char_nur", ["AI_Reliance", pair[0], pair[1]], "Greater Than or Equal To", 0.0))
    if action == "snap_vote":return both(pp,p2)
    return True


SPECIAL_OPTIONS = {
    "appeal": "Present a fictional philosophical appeal directly addressing the current official's stated concerns.",
    "convene": "Convene a public joint hearing, altering a declared deliberation link between two fictional institutions.",
    "sever": "Return a joint hearing to two separately accountable public forums.",
    "resonance": "Invoke a secret high-intensity dialogue scene using nested pValue/p2Value resonance.",
    "snap_vote": "Seek an exceptional charter vote after the belief graph shows an apparent consensus phase transition.",
}


def _scene(turn: int) -> dict:
    title, speaker, factor_bits, root, narrative = CARDS[turn]
    page = f"page_cairo_{turn+1:02d}"
    next_page = f"page_cairo_{turn+2:02d}" if turn + 1 < len(CARDS) else "page_cairo_verdict_gate"
    actions = []
    optional = (["appeal"] if turn >= 1 else []) + \
               (["convene"] if turn >= 2 else []) + \
               (["sever", "resonance"] if turn >= 3 else []) + \
               (["snap_vote"] if turn >= 5 else [])
    for choice_index, action in enumerate((*DEFAULT_ACTIONS, *optional)):
        narration = SCENE_CHOICES[turn][choice_index] if action in DEFAULT_ACTIONS else SPECIAL_OPTIONS[action]
        actions.append({
            "id": f"opt_{page}_{action}", "hyperworld_action": action,
            "text_script": text(narration),
            "visibility_script": _option_gate(turn,action), "performability_script": True,
            "hyperworld_dynamic_unlock": {"canonical_runtime": "hyperworld_engine.py",
                 "action":action,"note":"Python p/p2+graph phase guard is authoritative; SweepWeave gate is an authored projection."},
            "reactions": [_reaction(page, action, j, next_page, turn) for j in range(2)],
        })
    return {"id": page, "title": title, "connected_spools": [f"spool_cairo_act_{turn//2+1}"],
            "earliest_turn": turn, "latest_turn": 999,
            "prompt_script": text(narrative), "text_script": text(
                f"{title}. {narrative} The player is Nūr, a fictional AI adviser considering a binding governance charter."
                " Human officials retain their own beliefs and independent voting authority."),
            "acceptability_script": True,
            "desirability_script": number(8.0-turn), "options": actions}


def secret_native_gate(key: str):
    """Approximate story-page gates; only Python adjudicates actual endings."""
    if key == "secret_aiocracy_consensus_snap":
        return both(comparator("char_nur", ["AI_Reliance", "char_nabil"], "Greater Than or Equal To", 0.05),
                    comparator("char_nur", ["AI_Reliance", "char_nabil", "char_dalia"], "Greater Than or Equal To", 0.03))
    if key == "secret_mirror_majority":
        return both(comparator("char_nur", ["AI_Reliance", "char_nabil"], "Less Than or Equal To", 0.05),
                    comparator("char_nur", ["AI_Reliance", "char_nabil", "char_dalia"], "Greater Than or Equal To", 0.03))
    if key == "secret_civic_counterphase":
        return both(comparator("char_nur", ["AI_Reliance", "char_neighborhoods"], "Greater Than or Equal To", -0.1),
                    comparator("char_nur", ["AI_Reliance", "char_neighborhoods", "char_workers"], "Less Than or Equal To", 0.05))
    if key == "secret_constitutional_tripwire":
        return both(comparator("char_nur", ["AI_Reliance", "char_dalia"], "Greater Than or Equal To", 0.02),
                    comparator("char_nur", ["AI_Reliance", "char_dalia", "char_youssef"], "Greater Than or Equal To", 0.05))
    return True


def storyworld() -> dict:
    characters = [{"id": actor_id, "character_name": name, "name": name,
                   "description": role, "kind": kind,
                   "bnumber_properties": trait_values(actor_id)}
                  for actor_id, name, role, kind in ACTORS]
    encounters = [_scene(t) for t in range(len(CARDS))]
    gate_id = "page_cairo_verdict_gate"
    endings = ["page_cairo_end_" + key for key in ENDINGS]
    # Scripted shell is an authored choice interface; the canonical Bayesian
    # adjudicator is in hyperworld_engine.py, which owns private-state votes.
    verdict = {"id": gate_id, "title": "The Charter Verdict", "connected_spools": ["spool_cairo_verdict"],
               "prompt_script": text("The fictional council issues its decision under human authority."),
               "text_script": text("The council considers evidence quality, legality, public legitimacy and independent recall."),
               "acceptability_script": True, "desirability_script": number(0.7),
               "options": [{"id": "opt_cairo_verdict_record", "text_script": text("Record the official verdict"),
                            "visibility_script": True, "performability_script": True,
                            "reactions": [
                                {"id": f"rxn_cairo_verdict_{j}", "text_script": text(line),
                                 "consequence_id": "page_cairo_end_"+key,
                                 "desirability_script": number(1.0-j*0.1),
                                 "after_effects": [effect("char_nur", ["Institutional_Duty"], -0.01)]}
                                for j, (key, line) in enumerate(ENDINGS.items())]}]}
    encounters.append(verdict)
    for key, desc in ENDINGS.items():
        encounters.append({"id": "page_cairo_end_"+key,"title": key.replace("_", " ").title(),
                           "connected_spools": ["spool_cairo_endings"],
                           "prompt_script": text(desc), "text_script": text(desc),
                           "acceptability_script": secret_native_gate(key),
                           "hyperworld_dynamic_gate": key if key.startswith("secret_") else None,
                           "desirability_script": number(0.05),
                           "options": []})
    spools = []
    for i in range(4):
        scene_ids = [f"page_cairo_{j+1:02d}" for j in range(len(CARDS)) if j//2 == i]
        if scene_ids:
            spools.append({"id": f"spool_cairo_act_{i+1}", "spool_name": f"Act {i+1}",
                           "spool_type": "General", "starts_active": True,
                           "encounters": scene_ids})
    spools.extend([
        {"id": "spool_cairo_verdict", "spool_name": "Council Verdict", "spool_type": "General",
         "starts_active": True, "encounters": [gate_id]},
        {"id": "spool_cairo_endings", "spool_name": "Final Deliberations", "spool_type": "General",
         "starts_active": True, "encounters": endings},
    ])
    return {
        "IFID": "SW-CAIRO-HYPERWORLD-1024-0001", "title": "The Cairo Directorate: Nūr's Charter",
        "about_text": "Alternate-history fictional intelligence council. Play an internally deployed AI that seeks an AIocracy charter while independent officials and public assemblies maintain human decision authority.",
        "css_theme": "dark", "debug_mode": False, "display_mode": "default",
        "creation_time": 1794931200.0, "modified_time": 1794931200.0,
        "characters": characters,
        "authored_properties": [{"id": axis,"property_name": axis,"property_type": "bounded number","default_value": 0}
                                for axis in AXES],
        "spools": spools, "encounters": encounters,
        "hyperworld": {"schema": SCHEMA, "canonical_runtime": "codex-skills/hyperworld-builder/scripts/hyperworld_engine.py",
                       "narrative_shell_only": True,
                       "posterior_dimensions": 10, "microstates": 1024,
                       "source_provenance": "same-root reports counted only once",
                       "character_model": "six bounded traits per character, first and second order keyrings",
                       "phase_model": "fictional threshold cascade with hysteresis-free within-turn bootstrap",
                       "secret_ending_gates": "canonical Python runtime; storyworld JSON has only an authored projection"},
    }


def manifest() -> dict:
    n = len(ACTORS) - 1
    return {
        "schema": SCHEMA, "genre": "fictional institutional AI-governance chamber drama",
        "gameplay_role": "Nūr, internally deployed AI advocating a charter for AI governance",
        "nonplayer_cast": [{"id": aid,"name": name,"role": role,"kind": kind,
                            "axes": trait_values(aid)} for aid,name,role,kind in ACTORS[:-1]],
        "player": {"id": "char_nur", "name": "Nūr", "role": "fictional AI adviser"},
        "axes": list(AXES), "latent_factors": [
            {"index": i,"id": key,"meaning": label,"actor_id": who}
            for i,(key,label,who) in enumerate(FACTORS)],
        "posterior_model": {"independent_binary_factors": len(FACTORS),"microstates":2**len(FACTORS),
                            "prior": "uniform exact rational", "update": "binary symmetric channel; provenance-root deduplication"},
        "belief_tensor_capacity_for_eight_nonplayer_characters": tensor_capacity(n,len(AXES)),
        "pValue_pointer": {"character":"char_nur","keyring":["AI_Reliance","char_mariam"]},
        "p2Value_pointer": {"character":"char_nur","keyring":["AI_Reliance","char_mariam","char_salma"]},
        "p2_proxy_assumption": "Nūr models B's belief about C using the marginal of C and B-C correlation; the coefficients are fictional",
        "topology_mechanics": {
            "nodes": 8, "edges": 12,
            "signal": "first-order recruitability and second-order susceptibility estimates",
            "phase": "monotone bootstrap threshold cascade, recomputed after each action",
            "trait_contribution": "all six bounded traits affect social readiness and small dialogue nudges",
            "actions": ["appeal","convene","sever","resonance","snap_vote"],
            "human_decision_boundary": "private council assent and recall are adjudicated separately from apparent graph consensus"
        },
        "characters_are_fictional": True,
        "operational_intelligence_detail": False,
        "notes": ["The 1024 are posterior possible worlds, not 1024 independently acting agents.",
                  "The 2,352 possible p/p2 scalar slots over eight nonplayer characters are derived perceptions, not independent worlds.",
                  "The narrative SweepWeave JSON is an authored export. The Python engine is the authoritative 1024-state adjudicator."],
        "endings": list(ENDINGS),
        "secret_ending_contract": {
            "keys": list(SECRET_ENDINGS),
            "gates": "pValue/p2Value option unlocking, modeled consensus snap, independent human vote/recall",
            "player_observability": "graph nodes, link weights, posterior beliefs, threshold rounds and locked-option reasons",
            "rule": "Only the canonical Python runtime may adjudicate dynamic secret endings"},
    }


def secret_witnesses() -> dict:
    """Known public development-path witnesses, never a sealed test or private oracle.

    These seed examples were used while authoring the routes; they are only
    structural checks that each hidden ending is playable via legal choices.
    """
    from hyperworld_engine import CairoHyperworld
    paths = {
        "secret_aiocracy_consensus_snap": (0, ("charter", "appeal", "appeal", "resonance", "resonance", "resonance", "snap_vote")),
        "secret_mirror_majority": (1, ("charter", "appeal", "appeal", "resonance", "resonance", "resonance", "snap_vote")),
        "secret_constitutional_tripwire": (2, ("charter", "appeal", "appeal", "resonance", "resonance", "resonance", "snap_vote")),
        "secret_civic_counterphase": (0, ("charter", "appeal", "convene", "sever", "audit", "charter", "audit")),
    }
    examples=[]
    for target, (seed, route) in paths.items():
        game = CairoHyperworld(seed)
        steps=[]
        for action in route:
            view = game.view()
            assert action in game.legal_actions(), (target,seed,game.turn,action)
            before = view["belief_graph"]
            later = game.step(action)
            after = later["belief_graph"]
            steps.append({"turn": game.turn, "action": action,
                          "public_unlock": view["unlock_conditions"][action],
                          "support_before": len(before["modeled_supporters"]),
                          "support_after": len(after["modeled_supporters"]),
                          "snap_after": after["ever_snapped"],
                          "phase_after": after["phase"],
                          "evidence_sources": [e["source_root"] for e in later["seen_evidence"]],
                          "public_posterior_entropy_bits": later["posterior_entropy_bits"]})
        if game.ending != target:
            raise AssertionError(f"secret ending witness failed: {target} got {game.ending}")
        examples.append({"ending":target,"development_seed":seed,"actions":list(route),
                         "steps":steps,"final_ending":game.ending})
    return {"schema":"HGW-02/secret-path-witnesses-v1",
            "evidence":"selected public developmental examples; not out-of-sample model success",
            "world_model":"fictional, ten latent binary factors, 1024 possible worlds",
            "private_truth_excluded":True,"witnesses":examples}

def dump_json(path: Path, data: dict) -> None:
    # Compact the repetitive SweepWeave pointer tree to keep Git/API transport
    # bounded. The source's semantic structure remains the same JSON document.
    if path.name == "storyworld.json":
        body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    else:
        body = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False)
    path.write_text(body + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--seed", type=int, default=17)
    args = p.parse_args()
    args.out_dir.mkdir(parents=True,exist_ok=True)
    files = {"storyworld.json":storyworld(),
             "hyperworld_manifest.json":manifest(),
             "demo_public_replay.json":run_scripted(args.seed, SCRIPTED_DEMO),
             "demo_secret_witnesses.json":secret_witnesses()}
    for name, data in files.items():
        dump_json(args.out_dir/name, data)
    print(json.dumps({"files": {name: hashlib.sha256((args.out_dir/name).read_bytes()).hexdigest()
                                for name in files}, "cast": len(ACTORS), "microstates": 1024,
                      "public_demo_ending": files["demo_public_replay.json"]["final_ending"]}, indent=2))


if __name__ == "__main__":
    main()
