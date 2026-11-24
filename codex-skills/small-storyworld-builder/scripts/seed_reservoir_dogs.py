#!/usr/bin/env python3
"""Deterministic SweepWeave seed generator for Reservoir Dogs under small-storyworld-builder."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def sptr(value: str) -> Dict[str, Any]:
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": value}


def bconst(value: float) -> Dict[str, Any]:
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": round(float(value), 4)}


def bptr(character: str, keyring: List[str] | str, coefficient: float = 1.0) -> Dict[str, Any]:
    kr = [keyring] if isinstance(keyring, str) else list(keyring)
    return {
        "pointer_type": "Bounded Number Pointer",
        "script_element_type": "Pointer",
        "character": character,
        "keyring": kr,
        "coefficient": round(float(coefficient), 4),
    }


def op(name: str, *operands: Dict[str, Any], subtype: str | None = None) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "script_element_type": "Operator",
        "operator_type": name,
        "operands": list(operands),
    }
    if subtype is not None:
        out["operator_subtype"] = subtype
    return out


def cmp_node(left: Dict[str, Any], subtype: str, right: Dict[str, Any]) -> Dict[str, Any]:
    return op("Arithmetic Comparator", left, right, subtype=subtype)


def effect_nudge(character: str, keyring: List[str] | str, delta_expr: Dict[str, Any]) -> Dict[str, Any]:
    target = bptr(character, keyring)
    return {
        "effect_type": "Bounded Number Effect",
        "Set": target,
        "to": op("Nudge", target, delta_expr),
    }


def effect_clamp_step(character: str, keyring: List[str] | str, delta: float, aux_char: str, aux_prop: str, aux_coeff: float) -> Dict[str, Any]:
    target = bptr(character, keyring)
    step = op("Addition", target, bconst(delta), bptr(aux_char, aux_prop, aux_coeff))
    bounded = op("Maximum", bconst(-0.95), op("Minimum", bconst(0.95), step))
    return {
        "effect_type": "Bounded Number Effect",
        "Set": target,
        "to": bounded,
    }


CAST: List[Tuple[str, str, str, str]] = [
    (
        "char_white",
        "Mr. White",
        "he",
        "Lawrence Dimmick, an old-school heist professional whose protective loyalty toward bleeding Mr. Orange collides with cold evidence of an LAPD setup.",
    ),
    (
        "char_pink",
        "Mr. Pink",
        "he",
        "A hyper-rational career thief who stashed the Karina diamonds, refuses sentimental loyalty, and insists an informant tipped the police before the alarm sounded.",
    ),
    (
        "char_orange",
        "Mr. Orange",
        "he",
        "Freddy Newandyke, an undercover LAPD detective bleeding from a gut shot on the mortuary warehouse ramp while fighting shock, guilt, and blown cover.",
    ),
    (
        "char_blonde",
        "Mr. Blonde",
        "he",
        "Vic Vega, a smiling ex-convict loyal to Joe Cabot who turned the diamond heist into a bloodbath and brought bound patrolman Marvin Nash in his trunk.",
    ),
]

PROPS: List[str] = [
    "Phase_Clock",
    "Professional_Discipline",
    "Rat_Suspicion",
    "Crew_Loyalty",
    "Sadistic_Escalation",
    "Diamond_Leverage",
]

SCENES: List[Dict[str, Any]] = [
    {
        "id": "page_start",
        "spool": "spool_act1_safehouse",
        "turns": (0, 2),
        "title": "Blood on the Backseat",
        "focus": ("char_white", "char_orange", "Crew_Loyalty", "Professional_Discipline"),
        "option_count": 4,
        "targets": ["page_pink_ambush_theory", "page_color_aliases_and_stash"],
        "seed_text": "Mr. White drags gut-shot Mr. Orange across the dusty mortuary warehouse floor while blood soaks through Orange's white dress shirt. Orange begs for a hospital and a real name to hold onto, testing Joe Cabot's strict anonymity rule before anyone else arrives.",
        "opt_Stems": [
            "Promise Orange help while enforcing color aliases",
            "Whisper your first name to steady the dying kid",
            "Search Orange's coat and pockets for tail transmitters",
            "Lock the steel rollup door and stage the getaway car",
        ],
    },
    {
        "id": "page_pink_ambush_theory",
        "spool": "spool_act1_safehouse",
        "turns": (1, 3),
        "title": "Somebody Set Us Up",
        "focus": ("char_pink", "char_white", "Rat_Suspicion", "Professional_Discipline"),
        "option_count": 3,
        "targets": ["page_color_aliases_and_stash", "page_blonde_arrives"],
        "seed_text": "Mr. Pink slams through the side door still winded from sprinting past patrol cruisers with a satchel of uncut Karina diamonds. Pacing like a trapped wire, he swears SWAT sharpshooters were already in position before Mr. Blonde ever pulled a trigger.",
        "opt_Stems": [
            "Back Pink's ambush math and reconstruct the heist timeline",
            "Blame Blonde's panic shooting instead of an inside rat",
            "Demand to know where Pink hid the diamond satchel first",
        ],
    },
    {
        "id": "page_color_aliases_and_stash",
        "spool": "spool_act1_safehouse",
        "turns": (2, 4),
        "title": "The Stashed Satchel",
        "focus": ("char_pink", "char_orange", "Diamond_Leverage", "Crew_Loyalty"),
        "option_count": 3,
        "targets": ["page_blonde_arrives", "page_cadillac_trunk"],
        "seed_text": "Cigarette smoke hangs over the bathroom sink as Mr. Pink admits the stones are stashed minutes away, while Mr. Orange moans from the wooden ramp that he is bleeding to death. Dropping Orange at County General risks blowing the whole crew to homicide detectives.",
        "opt_Stems": [
            "Hold the safehouse until Joe Cabot and Nice Guy Eddie call",
            "Offer Pink control of the satchel in exchange for a doctor",
            "Cross-check who knew the Karina vault schedule in advance",
        ],
    },
    {
        "id": "page_blonde_arrives",
        "spool": "spool_act1_safehouse",
        "turns": (3, 5),
        "title": "Fast-Food Soda and Drawn Irons",
        "focus": ("char_blonde", "char_white", "Sadistic_Escalation", "Professional_Discipline"),
        "option_count": 3,
        "targets": ["page_cadillac_trunk", "page_chair_duct_tape"],
        "seed_text": "Leaning against a support beam slurping a striped drive-thru cup, Mr. Blonde watches Mr. White and Mr. Pink shout over Mr. Brown's cracked skull and dead Mr. Blue. When White lunges at him for slaughtering civilians, Blonde's hand drifts toward his shoulder holster.",
        "opt_Stems": [
            "Step between White and Blonde with cold syndicate discipline",
            "Pin Blonde against the pillar and strip his backup piece",
            "Watch Orange's eyes while Blonde recounts the alarm trip",
        ],
    },
    {
        "id": "page_cadillac_trunk",
        "spool": "spool_act1_safehouse",
        "turns": (4, 6),
        "title": "Special Delivery in the Coupe de Ville",
        "focus": ("char_blonde", "char_pink", "Sadistic_Escalation", "Rat_Suspicion"),
        "option_count": 3,
        "targets": ["page_chair_duct_tape", "page_eddie_call_and_alibi"],
        "seed_text": "Mr. Blonde leads Mr. White and Mr. Pink into the blinding alley heat and pops the trunk of his Cadillac Coupe de Ville. Bound in cuffs and duct tape, uniformed LAPD officer Marvin Nash blinks up from the spare-tire well as distant sirens echo.",
        "opt_Stems": [
            "Haul the patrolman inside strictly to question police deployment",
            "Chew Blonde out for bringing a live cop beacon to the safehouse",
            "Check Nash's service radio frequency before touching the tape",
        ],
    },
    {
        "id": "page_chair_duct_tape",
        "spool": "spool_act2_interrogation",
        "turns": (5, 7),
        "title": "Taped to the Mortuary Chair",
        "focus": ("char_white", "char_pink", "Rat_Suspicion", "Sadistic_Escalation"),
        "option_count": 3,
        "targets": ["page_eddie_call_and_alibi", "page_k_billy_razor"],
        "seed_text": "Duct tape wraps patrolman Marvin Nash to a creaking wooden chair in the center of the warehouse while Mr. Orange watches silently from a pool of darkening blood. Pink wants methodical interrogation about LAPD stakeout rosters; Blonde wants pain for sport.",
        "opt_Stems": [
            "Question Nash calmly on precinct stakeout orders and moles",
            "Let Blonde rough Nash up while Pink watches for tells",
            "Pull Pink aside to compare Orange's commode story cadence",
        ],
    },
    {
        "id": "page_eddie_call_and_alibi",
        "spool": "spool_act2_interrogation",
        "turns": (6, 8),
        "title": "Nice Guy Eddie on the Line",
        "focus": ("char_pink", "char_blonde", "Diamond_Leverage", "Rat_Suspicion"),
        "option_count": 3,
        "targets": ["page_k_billy_razor", "page_orange_gun_on_the_ramp"],
        "seed_text": "Word comes through that Nice Guy Eddie is sweeping the backup cars and Joe Cabot already suspects an insider burned the Karina job. White and Pink prepare to ditch the hot sedans and retrieve the diamond satchel, leaving somebody behind with Nash and bleeding Orange.",
        "opt_Stems": [
            "Take Pink to secure the diamonds and warn Blonde off torture",
            "Leave a hidden micro-check on Blonde's gasoline can and keys",
            "Press Orange on why Mr. Blue vanished during the alley split",
        ],
    },
    {
        "id": "page_k_billy_razor",
        "spool": "spool_act2_interrogation",
        "turns": (7, 9),
        "title": "K-Billy's Super Sounds of the Seventies",
        "focus": ("char_blonde", "char_orange", "Sadistic_Escalation", "Crew_Loyalty"),
        "option_count": 4,
        "targets": ["page_orange_gun_on_the_ramp", "page_nash_confession_shockwave"],
        "seed_text": "Alone in the warehouse with gagged Marvin Nash and half-conscious Mr. Orange, Mr. Blonde tunes an old table radio to K-Billy's Super Sounds of the Seventies. Sliding a straight razor from his cowboy boot, he dances across the concrete toward the chair.",
        "opt_Stems": [
            "Have Orange feign unconsciousness while inching toward his pistol",
            "Have Orange shout from the ramp to stall Blonde with Cabot's name",
            "Let Blonde slice the tape and demand the LAPD mole's codename",
            "Kick a surgical tray off the ramp to break Blonde's rhythm",
        ],
    },
    {
        "id": "page_orange_gun_on_the_ramp",
        "spool": "spool_act2_interrogation",
        "turns": (8, 10),
        "title": "Gasoline, Zippo, and Six Chambers",
        "focus": ("char_orange", "char_blonde", "Crew_Loyalty", "Sadistic_Escalation"),
        "option_count": 3,
        "targets": ["page_nash_confession_shockwave", "page_eddie_and_blonde_story"],
        "seed_text": "Gasoline splashes across Marvin Nash's uniform as the mutilated cop sobs that he has a kid at home and knows nothing about undercover detectives. Mr. Blonde thumbs open a chrome Zippo lighter while Mr. Orange raises a trembling Smith & Wesson from the ramp.",
        "opt_Stems": [
            "Empty the cylinder into Blonde's chest before the Zippo drops",
            "Wing Blonde's gun hand to keep him alive as a witness for Joe",
            "Hold fire until Nash blurts out the robbery-homicide unit name",
        ],
    },
    {
        "id": "page_nash_confession_shockwave",
        "spool": "spool_act2_interrogation",
        "turns": (9, 11),
        "title": "Gunsmoke Over the Gasoline Puddle",
        "focus": ("char_orange", "char_pink", "Rat_Suspicion", "Professional_Discipline"),
        "option_count": 3,
        "targets": ["page_eddie_and_blonde_story", "page_cabot_verdict"],
        "seed_text": "Cordite and raw gasoline sting the air as Marvin Nash gasps through shock on the soaked floor. If Orange admits he is Detective Freddy Newandyke, Nash knows an LAPD tactical unit is parked one block out waiting strictly for Joe Cabot to walk inside.",
        "opt_Stems": [
            "Swear Nash to silence and rehearse the Blonde-betrayal cover story",
            "Stage the razor and gas can so Pink reads pure self-defense",
            "Check Nash's cuffs and confess quietly when White bursts back in",
        ],
    },
    {
        "id": "page_eddie_and_blonde_story",
        "spool": "spool_act3_standoff",
        "turns": (10, 12),
        "title": "Vic Vega Was Family",
        "focus": ("char_white", "char_pink", "Crew_Loyalty", "Rat_Suspicion"),
        "option_count": 3,
        "targets": ["page_cabot_verdict", "page_mexican_standoff"],
        "seed_text": "Mr. White, Mr. Pink, and Nice Guy Eddie return with the Karina diamond satchel to find gasoline pooling across the warehouse and Blonde down. Orange swears Blonde planned to burn Nash, kill the crew, and steal the stones, while Eddie screams that Vic did four years for his father.",
        "opt_Stems": [
            "Defend Orange's story using Blonde's civilian massacre at Karina's",
            "Side with Pink's neutral audit of the powder burns and angles",
            "Isolate the diamond briefcase while testing Orange's timeline slip",
        ],
    },
    {
        "id": "page_cabot_verdict",
        "spool": "spool_act3_standoff",
        "turns": (11, 13),
        "title": "Joe Cabot's Finger on the Rat",
        "focus": ("char_white", "char_orange", "Crew_Loyalty", "Rat_Suspicion"),
        "option_count": 4,
        "targets": ["page_mexican_standoff", "page_sirens_at_the_rollup_door"],
        "seed_text": "Joe Cabot strides into the mortuary warehouse like an aging king whose court has rotted, declares Mr. Blue dead, and levels his snub-nose revolver directly at bleeding Mr. Orange. Joe says the kid is a cop, one hundred percent certain, and tells White to step clear.",
        "opt_Stems": [
            "Draw on Joe Cabot and swear on your life that Orange is solid",
            "Demand Joe prove how an undercover plant passed Eddie's vetting",
            "Watch Pink slide behind the ramp with the Karina diamond satchel",
            "Confront Orange directly with the rehearsed commode story tell",
        ],
    },
    {
        "id": "page_mexican_standoff",
        "spool": "spool_act3_standoff",
        "turns": (12, 14),
        "title": "Three Hammers Cocked in a Triangle",
        "focus": ("char_white", "char_pink", "Sadistic_Escalation", "Professional_Discipline"),
        "option_count": 4,
        "targets": ["page_sirens_at_the_rollup_door"],
        "seed_text": "Three heavy pistols lock into an impossible Mexican standoff: Joe aims down at Mr. Orange, Mr. White aims across at Joe's temple, and Nice Guy Eddie aims straight at White's chest, screaming for everybody to lower their iron before all three die on concrete.",
        "opt_Stems": [
            "Keep your sights welded to Joe's head and refuse to blink",
            "Shout Pink's name to broker a ten-second barrel drop",
            "Drop aim half an inch to bargain Orange's life for the satchel",
            "Back toward the drainage door with Pink while the Cabots freeze",
        ],
    },
    {
        "id": "page_sirens_at_the_rollup_door",
        "spool": "spool_act3_standoff",
        "turns": (13, 16),
        "title": "Sirens Outside the Mortuary Door",
        "focus": ("char_white", "char_orange", "Crew_Loyalty", "Diamond_Leverage"),
        "option_count": 3,
        "targets": ["wild"],
        "seed_text": "Tires screech across gravel outside the corrugated steel door as LAPD bullhorns crackle down the block. Inside the gunpowder haze, every lie told since breakfast at Uncle Bob's Pancake House comes due over a briefcase of stones and a bleeding undercover cop.",
        "opt_Stems": [
            "Cradle Orange in the bloodied sunlight and hear his final truth",
            "Grab the Karina satchel with Pink and bolt through the side alley",
            "Cut a cold professional truce before SWAT rams the steel door",
        ],
    },
]

ENDINGS: List[Dict[str, Any]] = [
    {
        "id": "page_end_mexican_standoff_collapse",
        "title": "Dead Men in Black Suits",
        "kind": "failure",
        "acc": cmp_node(bptr("char_white", "Phase_Clock"), "Greater Than or Equal To", bconst(0.55)),
        "des": op(
            "Addition",
            bptr("char_white", "Crew_Loyalty", 0.75),
            bptr("char_blonde", "Sadistic_Escalation", 0.55),
            op("Absolute Value", bptr("char_orange", "Crew_Loyalty", 0.35)),
            bconst(0.08),
        ),
        "seed_text": "Joe fires at Orange, White shoots Joe, Eddie shoots White, and White drops Eddie in a deafening three-second thunderclap. Crawling across the blood-slick floor to cradle Freddy's head, Larry hears the whispered truth—'I'm a cop'—and presses his barrel under Orange's chin as police boots burst open the warehouse door in a hail of rifle fire.",
    },
    {
        "id": "page_end_pink_ghosts_with_stones",
        "title": "The Only Professional Left Standing",
        "kind": "success",
        "acc": op(
            "And",
            cmp_node(bptr("char_white", "Phase_Clock"), "Greater Than or Equal To", bconst(0.55)),
            cmp_node(bptr("char_pink", "Professional_Discipline"), "Greater Than or Equal To", bconst(-0.15)),
        ),
        "des": op(
            "Addition",
            bptr("char_pink", "Professional_Discipline", 0.85),
            bptr("char_pink", "Diamond_Leverage", 0.80),
            bptr("char_white", "Crew_Loyalty", -0.35),
            bconst(0.10),
        ),
        "seed_text": "While ego and blood oaths detonate the center of the warehouse, Mr. Pink stays crouched beneath the wooden ramp with both hands locked around the Karina diamond satchel. Slipping into the sun-bleached alley seconds before SWAT rams the front rollup, the only man who treated the heist like a job vanishes into the sirens with two million in uncut stones.",
    },
    {
        "id": "page_end_blonde_gasoline_inferno",
        "title": "K-Billy's Funeral Pyre",
        "kind": "failure",
        "acc": op(
            "And",
            cmp_node(bptr("char_white", "Phase_Clock"), "Greater Than or Equal To", bconst(0.55)),
            cmp_node(bptr("char_blonde", "Sadistic_Escalation"), "Greater Than or Equal To", bconst(0.05)),
        ),
        "des": op(
            "Addition",
            bptr("char_blonde", "Sadistic_Escalation", 0.95),
            bptr("char_pink", "Professional_Discipline", -0.45),
            op("Maximum", bptr("char_blonde", "Rat_Suspicion", 0.3), bconst(0.05)),
        ),
        "seed_text": "Unchecked sadism turns the safehouse into an inferno as spilled gasoline catches a stray muzzle flash under the tinny groove of seventies AM radio. Black smoke pours from the mortuary vents before Joe Cabot's sedan even clears the corner, drawing every patrol unit in East Los Angeles onto ashes, melted tape, and ruined alibis.",
    },
    {
        "id": "page_end_cabot_executes_the_plant",
        "title": "Joe Cabot Cleans House",
        "kind": "terminal",
        "acc": op(
            "And",
            cmp_node(bptr("char_white", "Phase_Clock"), "Greater Than or Equal To", bconst(0.55)),
            cmp_node(bptr("char_pink", "Rat_Suspicion"), "Greater Than or Equal To", bconst(-0.10)),
        ),
        "des": op(
            "Addition",
            bptr("char_pink", "Rat_Suspicion", 0.85),
            bptr("char_white", "Crew_Loyalty", -0.50),
            bptr("char_white", "Professional_Discipline", 0.45),
            bconst(0.06),
        ),
        "seed_text": "Convinced by the timeline gaps and Pink's cold ambush arithmetic, Mr. White lowers his forty-five half an inch when Joe Cabot calls Freddy Newandyke a plant. Joe finishes the job without blinking, tosses Pink the car keys, and scatters the surviving crew through freight yards two minutes ahead of the robbery-homicide encirclement.",
    },
    {
        "id": "page_end_white_mercy_hospital_trap",
        "title": "Triage Handcuffs at County General",
        "kind": "terminal",
        "acc": op(
            "And",
            cmp_node(bptr("char_white", "Phase_Clock"), "Greater Than or Equal To", bconst(0.55)),
            cmp_node(bptr("char_white", "Crew_Loyalty"), "Greater Than or Equal To", bconst(-0.05)),
        ),
        "des": op(
            "Addition",
            bptr("char_white", "Crew_Loyalty", 0.90),
            bptr("char_pink", "Diamond_Leverage", -0.40),
            bptr("char_blonde", "Sadistic_Escalation", -0.35),
            bconst(0.05),
        ),
        "seed_text": "Refusing to watch the kid bleed out on concrete for Joe Cabot's rules, Larry Dimmick abandons the diamond split and shoulders Freddy into a stolen sedan bound for emergency surgery. Under harsh triage fluorescents, detectives greet Mr. White with drawn service weapons while Freddy grips his sleeve from the gurney, saved by the thief he was sent to cage.",
    },
    {
        "id": "page_secret_undercover_truce",
        "title": "Secret Ending: The Commode Tell and the Culvert Exit",
        "kind": "success",
        "acc": op(
            "And",
            cmp_node(bptr("char_white", "Phase_Clock"), "Greater Than or Equal To", bconst(0.55)),
            cmp_node(
                op("Absolute Value", op("Addition", bptr("char_white", "Crew_Loyalty"), bconst(-0.12))),
                "Less Than or Equal To",
                bconst(0.65),
            ),
            cmp_node(bptr("char_pink", "Rat_Suspicion"), "Greater Than or Equal To", bconst(0.08)),
            cmp_node(bptr("char_blonde", "Sadistic_Escalation"), "Less Than or Equal To", bconst(0.35)),
        ),
        "des": op(
            "Addition",
            bptr("char_pink", "Professional_Discipline", 0.70),
            bptr("char_pink", "Rat_Suspicion", 0.75),
            op("Absolute Value", bptr("char_white", "Diamond_Leverage", 0.45)),
            bconst(0.22),
        ),
        "seed_text": "Catching the rehearsed squad-room cadence in Orange's anecdote without letting Blonde's razor blow the room apart, White and Pink force a quiet confession before Joe Cabot ever reaches the block. Leaving Marvin Nash alive beside Freddy with a ninety-second ambulance call, Larry and Pink slip down the dry storm culvert with the Karina satchel—no massacre, no cuffs, and one haunted debt paid in full.",
    },
]


def build_seed_world(ts: float = 1779620000.0) -> Dict[str, Any]:
    characters: List[Dict[str, Any]] = []
    for idx, (cid, name, pronoun, desc) in enumerate(CAST):
        bprops: Dict[str, Any] = {p: 0 for p in PROPS}
        for p in PROPS[1:]:
            bprops[f"p{p}"] = {}
            bprops[f"p2{p}"] = {}
        characters.append(
            {
                "creation_index": idx,
                "creation_time": ts,
                "id": cid,
                "modified_time": ts,
                "name": name,
                "pronoun": pronoun,
                "description": desc,
                "bnumber_properties": bprops,
                "string_properties": {},
                "list_properties": {},
            }
        )

    authored_properties: List[Dict[str, Any]] = []
    p_idx = 0
    for prop in PROPS:
        authored_properties.append(
            {
                "id": prop,
                "property_name": prop,
                "property_type": "bounded number",
                "default_value": 0,
                "depth": 0,
                "attribution_target": "all cast members",
                "affected_characters": [],
                "creation_index": p_idx,
                "creation_time": ts,
                "modified_time": ts,
            }
        )
        p_idx += 1

    cast_ids = [c[0] for c in CAST]
    encounters: List[Dict[str, Any]] = []

    for s_idx, spec in enumerate(SCENES):
        enc_id = spec["id"]
        actor, witness, prop_a, prop_b = spec["focus"]
        observer = cast_ids[(s_idx + 2) % len(cast_ids)]
        opt_count = int(spec["option_count"])
        targets = spec["targets"]
        earliest, latest = spec["turns"]

        options: List[Dict[str, Any]] = []
        for o_idx in range(opt_count):
            opt_id = f"opt_{enc_id}_{o_idx}"
            reactions: List[Dict[str, Any]] = []
            for r_idx in range(3):
                rxn_id = f"rxn_{enc_id}_{o_idx}_{r_idx}"
                consequence = targets[(o_idx + r_idx) % len(targets)]

                # Mix Addition, Multiplication, Absolute Value, Maximum across desirability scripts
                p1_ptr = bptr(actor, [prop_a, witness], 0.65 if r_idx != 1 else -0.50)
                p2_ptr = bptr(witness, [prop_b, actor, observer], 0.45 if r_idx == 0 else -0.35)
                if (s_idx + o_idx + r_idx) % 3 == 0:
                    third_term = op("Absolute Value", bptr(observer, prop_b, 0.35))
                elif (s_idx + o_idx + r_idx) % 3 == 1:
                    third_term = op("Multiplication", bptr(actor, prop_a, 0.5), bptr(witness, prop_b, 0.5))
                else:
                    third_term = op("Maximum", bptr(observer, "Diamond_Leverage", 0.3), bconst(-0.15))

                desirability = op(
                    "Addition",
                    p1_ptr,
                    p2_ptr,
                    third_term,
                    bconst(round(0.03 * (o_idx + 1) - 0.02 * r_idx, 4)),
                )

                sign_a = 1.0 if (o_idx + r_idx) % 2 == 0 else -1.0
                sign_b = -1.0 if o_idx % 2 == 0 else 1.0
                effects = [
                    effect_nudge("char_white", "Phase_Clock", op("Addition", bconst(0.09), bptr(actor, prop_a, 0.02))),
                    effect_nudge(actor, prop_a, op("Addition", bconst(round(0.11 * sign_a, 4)), bptr(witness, prop_b, 0.08))),
                    effect_clamp_step(witness, prop_b, round(0.09 * sign_b, 4), actor, prop_a, 0.06),
                    effect_nudge(actor, [prop_a, witness], op("Addition", bconst(round(0.08 * sign_a, 4)), bptr(observer, prop_b, 0.05))),
                    effect_nudge(witness, [prop_b, actor, observer], op("Addition", bconst(round(0.07 * sign_b, 4)), bptr(actor, prop_a, 0.05))),
                ]

                rxn_seed = (
                    f"{dict((c[0], c[1]) for c in CAST)[actor]} shifts the warehouse balance around "
                    f"{spec['title'].lower()}, testing {dict((c[0], c[1]) for c in CAST)[witness]}'s nerve while "
                    f"everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside."
                )
                reactions.append(
                    {
                        "id": rxn_id,
                        "graph_offset_x": 0,
                        "graph_offset_y": 0,
                        "text_script": sptr(rxn_seed),
                        "consequence_id": consequence,
                        "desirability_script": desirability,
                        "after_effects": effects,
                    }
                )

            # Gate option index == opt_count - 1 in Act II and Act III with multi-var visibility
            if s_idx >= 5 and o_idx == opt_count - 1:
                visibility: Any = op(
                    "And",
                    cmp_node(
                        op("Absolute Value", bptr(actor, prop_a)),
                        "Less Than or Equal To",
                        bconst(0.95),
                    ),
                    cmp_node(bptr(witness, prop_b), "Greater Than or Equal To", bconst(-0.85)),
                )
            else:
                visibility = True

            performability = op(
                "And",
                cmp_node(
                    op("Absolute Value", bptr(actor, prop_a)),
                    "Less Than or Equal To",
                    bconst(0.98),
                ),
                cmp_node(bptr("char_white", "Phase_Clock"), "Less Than or Equal To", bconst(1.95)),
            )

            options.append(
                {
                    "id": opt_id,
                    "graph_offset_x": 0,
                    "graph_offset_y": 0,
                    "visibility_script": visibility,
                    "performability_script": performability,
                    "text_script": sptr(spec["opt_Stems"][o_idx]),
                    "reactions": reactions,
                }
            )

        if enc_id == "page_start":
            acceptability: Any = True
        else:
            acceptability = op(
                "And",
                cmp_node(bptr("char_white", "Phase_Clock"), "Less Than or Equal To", bconst(1.85)),
                cmp_node(op("Absolute Value", bptr(actor, prop_a)), "Less Than or Equal To", bconst(0.99)),
            )

        enc_desirability = op(
            "Addition",
            bptr(actor, prop_a, 0.55),
            op("Absolute Value", bptr(witness, prop_b, 0.30)),
            bconst(round(0.04 * s_idx, 4)),
        )

        seed_body = (
            spec["seed_text"]
            + " Every breath inside the shuttered mortuary smells of cordite, stale coffee, and drying arterial blood, "
            + "forcing each survivor to weigh professional discipline against the creeping certainty that an LAPD plant sold out the crew."
        )
        encounters.append(
            {
                "id": enc_id,
                "title": spec["title"],
                "creation_index": s_idx,
                "creation_time": ts,
                "modified_time": ts,
                "connected_spools": [spec["spool"]],
                "earliest_turn": earliest,
                "latest_turn": latest,
                "graph_position_x": s_idx * 180,
                "graph_position_y": 0,
                "text_script": sptr(seed_body),
                "acceptability_script": acceptability,
                "desirability_script": enc_desirability,
                "options": options,
            }
        )

    for e_idx, end_spec in enumerate(ENDINGS):
        encounters.append(
            {
                "id": end_spec["id"],
                "title": end_spec["title"],
                "creation_index": len(SCENES) + e_idx,
                "creation_time": ts,
                "modified_time": ts,
                "connected_spools": ["spool_endings"],
                "earliest_turn": 6,
                "latest_turn": 20,
                "graph_position_x": (len(SCENES) + e_idx) * 180,
                "graph_position_y": 320,
                "text_script": sptr(end_spec["seed_text"]),
                "acceptability_script": end_spec["acc"],
                "desirability_script": end_spec["des"],
                "options": [],
            }
        )

    spools = [
        {
            "id": "spool_act1_safehouse",
            "spool_name": "Act I: Safehouse Blood",
            "spool_type": "General",
            "starts_active": True,
            "creation_index": 0,
            "creation_time": ts,
            "modified_time": ts,
            "encounters": [s["id"] for s in SCENES if s["spool"] == "spool_act1_safehouse"],
        },
        {
            "id": "spool_act2_interrogation",
            "spool_name": "Act II: Chair and Razor",
            "spool_type": "General",
            "starts_active": True,
            "creation_index": 1,
            "creation_time": ts,
            "modified_time": ts,
            "encounters": [s["id"] for s in SCENES if s["spool"] == "spool_act2_interrogation"],
        },
        {
            "id": "spool_act3_standoff",
            "spool_name": "Act III: Mexican Standoff",
            "spool_type": "General",
            "starts_active": True,
            "creation_index": 2,
            "creation_time": ts,
            "modified_time": ts,
            "encounters": [s["id"] for s in SCENES if s["spool"] == "spool_act3_standoff"],
        },
        {
            "id": "spool_endings",
            "spool_name": "Endings: Sirens at the Mortuary",
            "spool_type": "General",
            "starts_active": True,
            "creation_index": 3,
            "creation_time": ts,
            "modified_time": ts,
            "encounters": [e["id"] for e in ENDINGS],
        },
    ]

    return {
        "IFID": "SW-BONSAI27-RESERVOIR-DOGS-001",
        "storyworld_title": "Reservoir Dogs: Blood on the Warehouse Floor",
        "storyworld_author": "Ternary-Bonsai-2-27B (via small-storyworld-builder)",
        "sweepweave_version": "0.1.9",
        "creation_time": ts,
        "modified_time": ts,
        "debug_mode": False,
        "display_mode": 1,
        "css_theme": "noir",
        "font_size": "16",
        "language": "en",
        "rating": "mature",
        "about_text": sptr(
            "After the Karina Wholesale Diamonds heist explodes into a sidewalk slaughter, four color-coded survivors converge on an abandoned Los Angeles mortuary warehouse: protective veteran Mr. White, paranoid pragmatist Mr. Pink, smiling sadist Mr. Blonde with a kidnapped patrolman in his trunk, and gut-shot undercover detective Mr. Orange bleeding out on the ramp."
        ),
        "characters": characters,
        "authored_properties": authored_properties,
        "spools": spools,
        "encounters": encounters,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Reservoir Dogs SweepWeave seed world.")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    world = build_seed_world()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(world, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
