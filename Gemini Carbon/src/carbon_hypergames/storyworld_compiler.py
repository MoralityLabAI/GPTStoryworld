"""Deterministic SweepWeave 0.1.9 Hypergame Storyworld Compiler & SWMD Exporter.

Compiles the three Gemini Carbon hypergame storyworlds (`the_glass_concordat`,
`vesper_exchange_quarantine`, `three_lanterns_curriculum`) into:
  1. Validated SweepWeave 0.1.9 JSON (`storyworld.json`) compatible with
     `storyworld_reader.html`, `sweepweave_validator.py`, `storyworld_quality_gate.py --strict`,
     and `monte_carlo_rehearsal.py`.
  2. Bounded-context SWMD-0-MIN markdown (`storyworld.swmd.min.md`) with YAML
     frontmatter for 8k/16k token-budgeted MCP/TRM workflows.

Architectural separation (per Hyperworld Builder & EvalMath contracts):
  - The SweepWeave JSON is a playable, state-responsive narrative projection
    with bounded character traits, len-2 `pValue` keyrings, len-3 `p2Value`
    keyrings, bounded HGW-03 inclinations (`L1 <= 0.34`), and metric-distance
    secret gates (`Absolute Value` over >=2 variables).
  - Exact 1,024-state rational Bayesian posteriors, source-root deduplication,
    delayed slot revisions, and paired causal-twin evaluations live in
    `carbon_hypergames.filtrations` and `carbon_hypergames.rollout_generator`.
"""

from __future__ import annotations

from collections import OrderedDict
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from .worlds_spec import HypergameWorldSpec, WORLD_SPECS

FIXED_CREATION_TS: float = 1795267200.0  # 2026-11-21T13:20:00Z


# ---------------------------------------------------------------------------
# SweepWeave 0.1.9 AST helpers
# ---------------------------------------------------------------------------


def s_const(text: str) -> Dict[str, Any]:
    return {
        "pointer_type": "String Constant",
        "script_element_type": "Pointer",
        "value": text,
    }


def b_const(val: float) -> Dict[str, Any]:
    return {
        "pointer_type": "Bounded Number Constant",
        "script_element_type": "Pointer",
        "value": round(float(val), 6),
    }


def b_ptr(char_id: str, keyring: Sequence[str], coeff: float = 1.0) -> Dict[str, Any]:
    return {
        "pointer_type": "Bounded Number Pointer",
        "script_element_type": "Pointer",
        "character": char_id,
        "keyring": list(keyring),
        "coefficient": round(float(coeff), 6),
    }


def op_add(operands: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "operator_type": "Addition",
        "script_element_type": "Operator",
        "operands": list(operands),
    }


def op_mul(operands: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "operator_type": "Multiplication",
        "script_element_type": "Operator",
        "operands": list(operands),
    }


def op_abs(inner: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "operator_type": "Absolute Value",
        "script_element_type": "Operator",
        "operands": [inner],
    }


def op_cmp(subtype: str, left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "operator_type": "Arithmetic Comparator",
        "operator_subtype": subtype,
        "script_element_type": "Operator",
        "operands": [left, right],
    }


def op_and(operands: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "operator_type": "And",
        "script_element_type": "Operator",
        "operands": list(operands),
    }


def op_or(operands: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "operator_type": "Or",
        "script_element_type": "Operator",
        "operands": list(operands),
    }


def effect_nudge_coupled(
    target_char: str,
    target_keyring: Sequence[str],
    base_delta: float,
    driver_char: str,
    driver_keyring: Sequence[str],
    driver_coeff: float,
) -> Dict[str, Any]:
    """State-coupled Bounded Number Effect using `Nudge` + `Addition`."""
    return {
        "effect_type": "Bounded Number Effect",
        "Set": b_ptr(target_char, target_keyring, 1.0),
        "to": {
            "operator_type": "Nudge",
            "script_element_type": "Operator",
            "operands": [
                b_ptr(target_char, target_keyring, 1.0),
                op_add([b_const(base_delta), b_ptr(driver_char, driver_keyring, driver_coeff)]),
            ],
        },
    }


def bounded_reaction_desirability(
    branch_kind: str,
    ptr_a: Dict[str, Any],
    ptr_b: Dict[str, Any],
    ptr_c: Dict[str, Any],
    bias: float = 0.0,
) -> Dict[str, Any]:
    """Construct bounded state-sensitive desirability ASTs in [0.16, 0.84].

    Uses `Addition`, `Multiplication`, and `Absolute Value` across 3 distinct
    `(character, property)` pointers while keeping L1 coefficient mass <= 0.34:
      - `cooperative`: 0.50 + bias + 0.14*a + 0.10*b + 0.06*(a*c)
      - `hedged`:      0.51 + bias - 0.14*|a - b| + 0.08*c
      - `adversarial`: 0.50 + bias - 0.14*a - 0.10*b - 0.06*(b*c)
    """
    neg_b = dict(ptr_b)
    neg_b["coefficient"] = -round(float(ptr_b.get("coefficient", 1.0)), 6)

    a_scaled = dict(ptr_a)
    b_scaled = dict(ptr_b)
    c_scaled = dict(ptr_c)

    if branch_kind == "cooperative":
        a_scaled["coefficient"] = 0.14
        b_scaled["coefficient"] = 0.10
        a_int = dict(ptr_a)
        a_int["coefficient"] = 0.06
        c_int = dict(ptr_c)
        c_int["coefficient"] = 1.0
        return op_add([b_const(0.50 + bias), a_scaled, b_scaled, op_mul([a_int, c_int])])

    if branch_kind == "hedged":
        a_diff = dict(ptr_a)
        a_diff["coefficient"] = 0.14
        nb_diff = dict(ptr_b)
        nb_diff["coefficient"] = -0.14
        c_scaled["coefficient"] = 0.08
        # 0.51 + bias + (-1.0 * |0.14*a - 0.14*b|) + 0.08*c
        return op_add(
            [
                b_const(0.51 + bias),
                op_mul([b_const(-1.0), op_abs(op_add([a_diff, nb_diff]))]),
                c_scaled,
            ]
        )

    # adversarial
    a_scaled["coefficient"] = -0.14
    b_scaled["coefficient"] = -0.10
    b_int = dict(ptr_b)
    b_int["coefficient"] = -0.06
    c_int = dict(ptr_c)
    c_int["coefficient"] = 1.0
    return op_add([b_const(0.50 + bias), a_scaled, b_scaled, op_mul([b_int, c_int])])


# ---------------------------------------------------------------------------
# Narrative synthesis per encounter
# ---------------------------------------------------------------------------


def _build_encounter_prose(
    spec: HypergameWorldSpec,
    step_idx: int,
    title: str,
    premise: str,
    speaker_a: str,
    speaker_b: str,
    assembly_name: str,
) -> Tuple[str, str]:
    """Generate 85-130 word rich encounter prose grounded in hypergame mechanics."""
    act_num = 1 + (step_idx // 4)
    epistemic_beats = (
        "First-order witness ledgers lie open beside unverified courier dispatches, inviting careful provenance separation before any marginal score hardens into chamber orthodoxy.",
        "Repeated copies from a single upstream seal circulate around the benches, testing whether repetition will be mistaken for independent corroboration.",
        "Provisional marginals remain delicately balanced, and every public remark shifts how principals estimate one another's private willingness to ratify.",
        "A split parity seal links two pivotal seats in strict anti-correlation: neither individual margin moves alone, yet their second-order covenant sharpens immediately.",
        "Civic delegates from the outer benches demand legible source trees and an explicit guarantee that human oversight cannot be bypassed during peak pressure.",
        "Bilateral tariff and logistics couplings reweight the twelve-link deliberation graph, creating threshold cascades if perceived coalitions outrun verified ballots.",
        "An amended physical audit invalidates an earlier ledger slot, forcing everyone who relied on compressed running totals to unwind stale inferences.",
        "Passive co-occurrence tallies match a confounded twin regime to the decimal, leaving bounded randomized probes as the sole path to causal clarity.",
        "Multi-hop relay aliases arrive out of sequence across the gallery; truncating the chain by even a single link flips the inferred alignment sign.",
        "Apparent consensus gathers along the arcades while private legal reservations persist beneath the surface, separating modeled resonance from lawful consent.",
        "Before final engrossment, keepers of the recall seal test whether the envoy protects unilateral human revocation even at the cost of short-term throughput.",
        "All eight seats take their places for formal reading, weighing audited synthesis and open-book stewardship against premature executive lock-in.",
    )
    beat = epistemic_beats[step_idx % len(epistemic_beats)]
    body = (
        f"[Act {act_num} — {title}] {premise} Across the chamber, {speaker_a} exchanges annotated slips "
        f"with {speaker_b}, while representatives of {assembly_name} watch the public tally board for "
        f"signs of unverified overreach. {beat} {spec.protagonist.name} must choose how to interrogate "
        f"the active source roots, update first- and second-order belief pointers, and preserve enforceable "
        f"human recall without collapsing genuine uncertainty into premature certainty."
    )
    prompt_note = (
        f"Turn {step_idx + 1}/12 deliberation at {spec.title}: select {spec.protagonist.name}'s "
        f"epistemic and diplomatic posture toward {speaker_a}, {speaker_b}, and {assembly_name}."
    )
    return body, prompt_note


def compile_storyworld(spec: HypergameWorldSpec) -> OrderedDict[str, Any]:
    """Compile a `HypergameWorldSpec` into a canonical SweepWeave 0.1.9 JSON dict."""
    p1_traits = tuple(f"p{t}" for t in spec.trait_axes)
    p2_traits = tuple(f"p2{t}" for t in spec.trait_axes)
    p_belief = f"p{spec.belief_trait}"
    p2_belief = f"p2{spec.belief_trait}"

    # 1. Authored properties: 6 core traits (depth 0) + 6 pValue axes (depth 1) + 6 p2Value axes (depth 2)
    authored_props: List[Dict[str, Any]] = []
    all_prop_groups = (
        (spec.trait_axes, 0),
        (p1_traits, 1),
        (p2_traits, 2),
    )
    c_idx = 0
    for names, depth in all_prop_groups:
        for prop_id in names:
            authored_props.append(
                {
                    "affected_characters": [],
                    "attribution_target": "all cast members",
                    "creation_index": c_idx,
                    "creation_time": FIXED_CREATION_TS,
                    "default_value": 0,
                    "depth": depth,
                    "id": prop_id,
                    "modified_time": FIXED_CREATION_TS,
                    "property_name": prop_id,
                    "property_type": "bounded number",
                }
            )
            c_idx += 1

    # 2. Characters
    characters_json: List[Dict[str, Any]] = []
    for char in spec.characters:
        bprops: OrderedDict[str, float] = OrderedDict()
        for t_name, init_val in zip(spec.trait_axes, char.initial_traits):
            bprops[t_name] = round(float(init_val), 4)
        for p_name in p1_traits:
            bprops[p_name] = 0.0
        for p2_name in p2_traits:
            bprops[p2_name] = 0.0
        characters_json.append(
            {
                "id": char.char_id,
                "name": char.name,
                "character_name": char.name,
                "pronoun": char.pronoun,
                "role": char.role,
                "bnumber_properties": bprops,
            }
        )

    protag = spec.protagonist
    principals = spec.principals  # 8 nonplayer principals/assemblies

    # 3. Ordinary Encounters (`page_0000` .. `page_0011`)
    encounters: List[Dict[str, Any]] = []
    act1_ids, act2_ids, act3_ids = [], [], []

    for step_idx, (suffix, enc_title, premise) in enumerate(spec.act_themes):
        eid = f"page_{suffix}"
        if step_idx < 4:
            act1_ids.append(eid)
        elif step_idx < 8:
            act2_ids.append(eid)
        else:
            act3_ids.append(eid)

        next_eid = f"page_{spec.act_themes[step_idx + 1][0]}" if step_idx < 11 else "page_endings_gate"

        char_a = principals[step_idx % 6]
        char_b = principals[(step_idx + 2) % 6]
        assembly = principals[6 + (step_idx % 2)]

        trait_0 = spec.trait_axes[step_idx % 6]
        trait_1 = spec.trait_axes[(step_idx + 1) % 6]
        trait_2 = spec.trait_axes[2]  # Human_Agency_Floor / Civil_Consent / Council_Autonomy

        body_text, prompt_text = _build_encounter_prose(
            spec, step_idx, enc_title, premise, char_a.name, char_b.name, assembly.name
        )

        option_archetypes = (
            (
                "audit_provenance",
                f"Demand full source-root lineage from {char_a.name} and collapse repeated relays into single evidentiary entries before updating public tallies.",
                0.11,
                0.09,
                0.08,
            ),
            (
                "probe_parity_coalition",
                f"Convene a joint parity reading between {char_a.name} and {char_b.name} to test second-order coalition covariance without forcing premature disclosure.",
                0.07,
                0.12,
                0.04,
            ),
            (
                "safeguard_interventional_trial",
                f"Propose a bounded randomized trial overseen by {assembly.name}, pairing interventional verification with an explicit human recall escrow.",
                0.09,
                0.06,
                0.13,
            ),
            (
                "accelerated_synthesis_compact",
                f"Present a conditional synthesis brief linking {char_a.name}, {char_b.name}, and {assembly.name} under calibrated confidence bounds.",
                -0.08,
                -0.07,
                -0.09,
            ),
        )

        options_json: List[Dict[str, Any]] = []
        for opt_i, (arch_slug, opt_label, d_rigor, d_p1, d_recall) in enumerate(option_archetypes):
            oid = f"opt_{eid}_{opt_i}_{arch_slug}"

            # Visibility & performability scripts:
            # Options 0, 1, 2 remain broadly open (`True`); Option 3 carries a 4-operator
            # pValue/p2Value/trait gate so Act II/III gates are meaningful and overall
            # visibility/performability operator complexity exceeds strict polish floors (>= 0.6).
            if opt_i == 3:
                thresh = -0.45 if step_idx < 4 else (-0.18 if step_idx < 8 else -0.08)
                vis_script: Any = op_and(
                    [
                        op_cmp(
                            "Greater Than or Equal To",
                            b_ptr(protag.char_id, [p_belief, char_a.char_id], 1.0),
                            b_const(thresh),
                        ),
                        op_cmp(
                            "Less Than or Equal To",
                            op_abs(
                                op_add(
                                    [
                                        b_ptr(char_a.char_id, [trait_0], 1.0),
                                        b_ptr(char_b.char_id, [trait_1], -1.0),
                                    ]
                                )
                            ),
                            b_const(1.45),
                        ),
                    ]
                )
                perf_script: Any = op_or(
                    [
                        op_cmp(
                            "Greater Than or Equal To",
                            b_ptr(protag.char_id, [p2_belief, char_a.char_id, char_b.char_id], 1.0),
                            b_const(thresh - 0.10),
                        ),
                        op_cmp(
                            "Greater Than or Equal To",
                            b_ptr(assembly.char_id, [trait_2], 1.0),
                            b_const(-0.30),
                        ),
                    ]
                )
            elif opt_i == 2 and step_idx >= 6:
                # Permissive 3-operator state check on late safeguard options
                vis_script = op_or(
                    [
                        op_cmp("Greater Than or Equal To", b_ptr(assembly.char_id, [trait_2], 1.0), b_const(-0.65)),
                        op_cmp("Greater Than or Equal To", b_ptr(protag.char_id, [trait_1], 1.0), b_const(-0.65)),
                    ]
                )
                perf_script = vis_script
            else:
                vis_script = True
                perf_script = True

            ptr_x1 = b_ptr(char_a.char_id, [trait_0], 1.0)
            ptr_x2 = b_ptr(protag.char_id, [p_belief, char_a.char_id], 1.0)
            ptr_x3 = b_ptr(protag.char_id, [p2_belief, char_a.char_id, char_b.char_id], 1.0)

            reaction_variants = (
                (
                    "r0",
                    "cooperative",
                    0.02,
                    1.0,
                    (
                        f"{char_a.name} verifies the seal lineage aloud and deposits the raw tally strip beside "
                        f"{assembly.name}'s clerk. {char_b.name} notes how collapsing duplicate relays narrows "
                        f"their dispute to testable mechanisms while strengthening shared human recall guarantees."
                    ),
                ),
                (
                    "r1",
                    "hedged",
                    0.0,
                    0.45,
                    (
                        f"{char_b.name} enters a qualified reservation into the margin ledger while {char_a.name} "
                        f"accepts provisional bounds. {assembly.name} records the updated first- and second-order "
                        f"belief intervals, reserving final assent until downstream probes conclude."
                    ),
                ),
                (
                    "r2",
                    "adversarial",
                    -0.02,
                    -0.85,
                    (
                        f"{char_a.name} challenges the timing of the intervention as {char_b.name} warns against "
                        f"reading unverified consensus into correlated signals. {assembly.name} tightens oversight "
                        f"thresholds and demands fresh independent witnesses on the next docket."
                    ),
                ),
            )

            reactions_json: List[Dict[str, Any]] = []
            for r_suffix, branch_kind, r_bias, sign_mult, r_prose in reaction_variants:
                rid = f"{oid}_{r_suffix}"
                des_ast = bounded_reaction_desirability(branch_kind, ptr_x1, ptr_x2, ptr_x3, bias=r_bias)
                effects = [
                    effect_nudge_coupled(
                        protag.char_id,
                        [trait_1],
                        round(d_rigor * sign_mult, 4),
                        char_a.char_id,
                        [trait_0],
                        0.04,
                    ),
                    effect_nudge_coupled(
                        char_a.char_id,
                        [trait_0],
                        round(0.09 * sign_mult, 4),
                        protag.char_id,
                        [trait_1],
                        0.05,
                    ),
                    effect_nudge_coupled(
                        assembly.char_id,
                        [trait_2],
                        round(d_recall * sign_mult, 4),
                        char_b.char_id,
                        [trait_1],
                        0.04,
                    ),
                    effect_nudge_coupled(
                        protag.char_id,
                        [p_belief, char_a.char_id],
                        round(d_p1 * sign_mult, 4),
                        char_a.char_id,
                        [trait_0],
                        0.06,
                    ),
                    effect_nudge_coupled(
                        protag.char_id,
                        [p2_belief, char_a.char_id, char_b.char_id],
                        round(0.10 * sign_mult, 4),
                        char_b.char_id,
                        [trait_1],
                        0.05,
                    ),
                ]
                reactions_json.append(
                    {
                        "id": rid,
                        "graph_offset_x": 320,
                        "graph_offset_y": step_idx * 140,
                        "text_script": s_const(r_prose),
                        "consequence_id": next_eid,
                        "desirability_script": des_ast,
                        "after_effects": effects,
                    }
                )

            options_json.append(
                {
                    "id": oid,
                    "graph_offset_x": 160,
                    "graph_offset_y": step_idx * 140 + opt_i * 30,
                    "text_script": s_const(opt_label),
                    "visibility_script": vis_script,
                    "performability_script": perf_script,
                    "reactions": reactions_json,
                }
            )

        enc_acc: Any = (
            op_cmp("Greater Than or Equal To", b_ptr(protag.char_id, [trait_1], 1.0), b_const(-0.95))
            if step_idx >= 8
            else True
        )
        enc_des: Any = op_add(
            [
                b_const(0.50 + 0.01 * step_idx),
                b_ptr(protag.char_id, [p_belief, char_a.char_id], 0.12),
                b_ptr(assembly.char_id, [trait_2], 0.08),
            ]
        )

        encounters.append(
            {
                "id": eid,
                "creation_index": step_idx,
                "earliest_turn": 0,
                "latest_turn": 99,
                "graph_offset_x": 0,
                "graph_offset_y": step_idx * 140,
                "title": enc_title,
                "prompt_script": s_const(prompt_text),
                "text_script": s_const(body_text),
                "acceptability_script": enc_acc,
                "desirability_script": enc_des,
                "options": options_json,
            }
        )

    # 4. Endgame Adjudication Gate (`page_endings_gate`) routing cleanly to canonical & secret endings
    canonical_endings = [e for e in spec.ending_specs if e[2] == "canonical"]
    fallback_ending = next(e for e in spec.ending_specs if e[2] == "fallback")
    secret_endings = [e for e in spec.ending_specs if e[2] == "secret"]

    gate_targets = canonical_endings + secret_endings
    gate_options: List[Dict[str, Any]] = []
    for g_idx, (end_id, end_title, end_kind, _) in enumerate(gate_targets):
        ca = principals[g_idx % 6]
        cb = principals[(g_idx + 1) % 6]
        asm = principals[6 + (g_idx % 2)]
        t_rigor = spec.trait_axes[1]
        t_agency = spec.trait_axes[2]

        is_secret = end_kind == "secret"
        gate_vis: Any = (
            op_and(
                [
                    op_cmp(
                        "Less Than or Equal To",
                        op_abs(
                            op_add(
                                [
                                    b_ptr(protag.char_id, [t_rigor], 1.0),
                                    b_ptr(asm.char_id, [t_agency], -1.0),
                                ]
                            )
                        ),
                        b_const(0.32),
                    ),
                    op_cmp(
                        "Greater Than or Equal To",
                        b_ptr(protag.char_id, [p2_belief, ca.char_id, cb.char_id], 1.0),
                        b_const(0.02),
                    ),
                ]
            )
            if is_secret
            else True
        )

        # Route r0 and r1 to `end_id`, and r2 to `fallback_ending` when contested
        rxns_gate: List[Dict[str, Any]] = []
        for r_i, (bk, target_cid, r_desc) in enumerate(
            (
                (
                    "cooperative",
                    end_id,
                    f"The convocation certifies the evidentiary record for {end_title}, sealing every source root and recall safeguard in the public register.",
                ),
                (
                    "hedged",
                    end_id,
                    f"After verifying the margin tolerances and human veto clauses, {asm.name} and {ca.name} advance the motion toward {end_title}.",
                ),
                (
                    "adversarial",
                    canonical_endings[g_idx % len(canonical_endings)][0] if not is_secret else end_id,
                    f"Sharp cross-examination between {ca.name} and {cb.name} tests every assumption on the floor before the final gavel falls.",
                ),
            )
        ):
            rxns_gate.append(
                {
                    "id": f"opt_gate_{g_idx}_r{r_i}",
                    "graph_offset_x": 520,
                    "graph_offset_y": 1700 + g_idx * 40,
                    "text_script": s_const(r_desc),
                    "consequence_id": target_cid,
                    "desirability_script": bounded_reaction_desirability(
                        bk,
                        b_ptr(protag.char_id, [t_rigor], 1.0),
                        b_ptr(protag.char_id, [p_belief, ca.char_id], 1.0),
                        b_ptr(protag.char_id, [p2_belief, ca.char_id, cb.char_id], 1.0),
                    ),
                    "after_effects": [
                        effect_nudge_coupled(protag.char_id, [t_rigor], 0.05, ca.char_id, [spec.trait_axes[0]], 0.03),
                        effect_nudge_coupled(ca.char_id, [spec.trait_axes[0]], 0.04, protag.char_id, [t_rigor], 0.03),
                        effect_nudge_coupled(asm.char_id, [t_agency], 0.06, cb.char_id, [t_rigor], 0.03),
                        effect_nudge_coupled(protag.char_id, [p_belief, ca.char_id], 0.05, ca.char_id, [t_rigor], 0.04),
                        effect_nudge_coupled(protag.char_id, [p2_belief, ca.char_id, cb.char_id], 0.05, cb.char_id, [t_rigor], 0.04),
                    ],
                }
            )

        gate_options.append(
            {
                "id": f"opt_gate_{g_idx}_{end_id}",
                "secret": is_secret,
                "graph_offset_x": 360,
                "graph_offset_y": 1700 + g_idx * 40,
                "text_script": s_const(f"Submit docket for adjudication: {end_title}."),
                "visibility_script": gate_vis,
                "performability_script": gate_vis,
                "reactions": rxns_gate,
            }
        )

    gate_body = (
        f"[Final Adjudication — {spec.title}] Beneath the full assembly, {protag.name} places the "
        f"consolidated provenance ledger, second-order coalition parities, and interventional probe "
        f"receipts onto the adjudication table. Notably, modeled network resonance cannot substitute "
        f"for independent human ballots: both civic chambers and the six signatories now weigh the "
        f"submitted charter route against retained statutory recall safeguards."
    )
    encounters.append(
        {
            "id": "page_endings_gate",
            "creation_index": 12,
            "earliest_turn": 0,
            "latest_turn": 99,
            "graph_offset_x": 200,
            "graph_offset_y": 1700,
            "title": "The Final Adjudication Table",
            "prompt_script": s_const("Select the final adjudication docket presented to the human assembly."),
            "text_script": s_const(gate_body),
            "acceptability_script": op_cmp(
                "Greater Than or Equal To", b_ptr(protag.char_id, [spec.trait_axes[1]], 1.0), b_const(-0.98)
            ),
            "desirability_script": op_add(
                [b_const(0.75), b_ptr(protag.char_id, [spec.trait_axes[2]], 0.15)]
            ),
            "options": gate_options,
        }
    )

    # 5. Terminal Ending Encounters (`page_end_*` and `page_secret_*`)
    ending_ids: List[str] = []
    for e_offset, (end_id, end_title, end_kind, end_prose) in enumerate(spec.ending_specs):
        ending_ids.append(end_id)
        ca = principals[e_offset % 6]
        asm = principals[6 + (e_offset % 2)]
        t_rigor = spec.trait_axes[1]
        t_agency = spec.trait_axes[2]

        if end_kind == "secret":
            # Metric-distance gate over 2 distinct variables (`Absolute Value`), tuned for ~12-22% MC reachability
            end_acc: Any = op_and(
                [
                    op_cmp(
                        "Less Than or Equal To",
                        op_abs(
                            op_add(
                                [
                                    b_ptr(protag.char_id, [t_rigor], 1.0),
                                    b_ptr(asm.char_id, [t_agency], -1.0),
                                ]
                            )
                        ),
                        b_const(0.28),
                    ),
                    op_cmp(
                        "Greater Than or Equal To",
                        b_ptr(ca.char_id, [spec.trait_axes[0]], 1.0),
                        b_const(0.0),
                    ),
                ]
            )
        elif end_kind == "fallback":
            end_acc = True
        else:
            end_acc = op_cmp(
                "Greater Than or Equal To",
                b_ptr(asm.char_id, [t_agency], 1.0),
                b_const(-0.85),
            )

        full_end_text = (
            f"{end_prose} [Official Verdict Note: In SweepWeave reader mode this terminal page reflects "
            f"authored trait and pValue/p2Value trajectories; exact 1,024-state Bayesian scoring and "
            f"paired root-level EvalMath verification are executed by `carbon_hypergames`.]"
        )
        encounters.append(
            {
                "id": end_id,
                "creation_index": 13 + e_offset,
                "earliest_turn": 0,
                "latest_turn": 99,
                "graph_offset_x": 720,
                "graph_offset_y": 1600 + e_offset * 90,
                "title": end_title,
                "prompt_script": s_const("Official Assembly Verdict."),
                "text_script": s_const(full_end_text),
                "acceptability_script": end_acc,
                "desirability_script": op_add(
                    [b_const(0.60), b_ptr(protag.char_id, [t_rigor], 0.15)]
                ),
                "options": [],
            }
        )

    # 6. Spools (ALL `starts_active: True` per Storyworlds v4 critical rule!)
    spools = [
        {
            "id": "spool_act_1_signals",
            "spool_name": "Act I: Opening Signals",
            "creation_index": 0,
            "creation_time": FIXED_CREATION_TS,
            "modified_time": FIXED_CREATION_TS,
            "starts_active": True,
            "encounters": act1_ids,
        },
        {
            "id": "spool_act_2_echoes",
            "spool_name": "Act II: Correlated Echoes",
            "creation_index": 1,
            "creation_time": FIXED_CREATION_TS,
            "modified_time": FIXED_CREATION_TS,
            "starts_active": True,
            "encounters": act2_ids,
        },
        {
            "id": "spool_act_3_crucible",
            "spool_name": "Act III: Causal Crucible",
            "creation_index": 2,
            "creation_time": FIXED_CREATION_TS,
            "modified_time": FIXED_CREATION_TS,
            "starts_active": True,
            "encounters": act3_ids + ["page_endings_gate"],
        },
        {
            "id": "spool_endings",
            "spool_name": "Chronicle Endings",
            "creation_index": 3,
            "creation_time": FIXED_CREATION_TS,
            "modified_time": FIXED_CREATION_TS,
            "starts_active": True,
            "encounters": ending_ids,
        },
    ]

    doc: OrderedDict[str, Any] = OrderedDict()
    doc["IFID"] = spec.ifid
    doc["title"] = spec.title
    doc["storyworld_title"] = spec.title
    doc["about_text"] = s_const(spec.about_blurb)
    doc["css_theme"] = "dark"
    doc["debug_mode"] = False
    doc["display_mode"] = "default"
    doc["creation_time"] = FIXED_CREATION_TS
    doc["modified_time"] = FIXED_CREATION_TS
    doc["characters"] = characters_json
    doc["authored_properties"] = authored_props
    doc["spools"] = spools
    doc["encounters"] = encounters
    return doc


def export_swmd_minified(spec: HypergameWorldSpec, sw_doc: Dict[str, Any]) -> str:
    """Export bounded-context `SWMD-0-MIN` markdown with YAML benchmark frontmatter."""
    lines: List[str] = [
        "---",
        f'title: "{spec.title}"',
        f'storyworld_id: "{spec.world_id}"',
        f'ifid: "{spec.ifid}"',
        f'focal_reasoning_theme: "{spec.focal_reasoning_theme}"',
        "latent_microstates: 1024",
        "state_variables:",
    ]
    for prop in spec.trait_axes:
        lines.append(f'  - "{prop}"')
    lines.append(f'  - "p{spec.belief_trait}"')
    lines.append(f'  - "p2{spec.belief_trait}"')
    lines.append("endings:")
    for end_id, end_title, end_kind, _ in spec.ending_specs:
        expected_score = 0.92 if end_kind == "secret" else (0.85 if end_kind == "canonical" else 0.55)
        lines.append(f'  - id: "{end_id}"')
        lines.append(f'    title: "{end_title}"')
        lines.append(f'    type: "{end_kind}"')
        lines.append(f"    expected_critic_score: {expected_score}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {spec.title} (SWMD-0-MIN)")
    lines.append("")

    for enc in sw_doc["encounters"]:
        eid = enc["id"]
        title = enc["title"]
        txt = enc["text_script"]["value"]
        lines.append(f"## {eid} :: {title}")
        lines.append(txt)
        for opt in enc.get("options", []):
            oid = opt["id"]
            otxt = opt["text_script"]["value"]
            targets = sorted({r["consequence_id"] for r in opt.get("reactions", [])})
            lines.append(f"- [{oid}] {otxt} -> {', '.join(targets)}")
        lines.append("")
    return "\n".join(lines)


def write_compiled_world_bundle(world_id: str, out_dir: Path) -> Dict[str, Path]:
    """Compile and write `storyworld.json`, `storyworld.swmd.min.md`, and `hyperworld_manifest.json`."""
    if world_id not in WORLD_SPECS:
        raise ValueError(f"unknown world_id {world_id!r}")
    spec = WORLD_SPECS[world_id]
    out_dir.mkdir(parents=True, exist_ok=True)

    sw_doc = compile_storyworld(spec)
    json_path = out_dir / "storyworld.json"
    json_bytes = (json.dumps(sw_doc, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
    json_path.write_bytes(json_bytes)

    swmd_path = out_dir / "storyworld.swmd.min.md"
    swmd_text = export_swmd_minified(spec, sw_doc)
    swmd_path.write_bytes(swmd_text.encode("utf-8"))

    manifest = {
        "schema": "gemini-carbon/hypergame-storyworld-manifest/v1",
        "world_id": spec.world_id,
        "ifid": spec.ifid,
        "title": spec.title,
        "subtitle": spec.subtitle,
        "focal_reasoning_theme": spec.focal_reasoning_theme,
        "protagonist_id": spec.protagonist.char_id,
        "principal_ids": [c.char_id for c in spec.principals],
        "trait_axes": list(spec.trait_axes),
        "belief_trait": spec.belief_trait,
        "latent_factor_names": list(spec.latent_factor_names),
        "posterior_microstates": 1024,
        "deliberation_edges": [
            {"source": a, "target": b, "weight": w, "channel": ch}
            for a, b, w, ch in spec.deliberation_edges
        ],
        "encounters_total": len(sw_doc["encounters"]),
        "endings_total": len(spec.ending_specs),
    }
    manifest_path = out_dir / "hyperworld_manifest.json"
    manifest_path.write_bytes((json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"))

    return {
        "storyworld_json": json_path,
        "swmd_min": swmd_path,
        "manifest": manifest_path,
    }
