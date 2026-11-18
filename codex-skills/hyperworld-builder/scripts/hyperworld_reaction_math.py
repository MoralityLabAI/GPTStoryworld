"""HGW-03: inspectable, fictional character-scoped reaction mathematics.

This module defines *authored SweepWeave reaction projections*. It never infers
actual assent, legal votes or private state. The Python hyperworld engine remains
authoritative for actions, evidence and endings, and its HGW-02 replay is frozen.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from math import sqrt
from typing import Mapping

# (lead speaker, material counterparty, focal first/second-order edge)
# The cast is chosen for the events, not rotated through the officer roster.
EVENT_CAST = (
    ("char_mariam", "char_nabil", ("char_nabil", "char_mariam")),
    ("char_mariam", "char_salma", ("char_mariam", "char_salma")),
    ("char_salma", "char_nabil", ("char_mariam", "char_youssef")),
    ("char_dalia", "char_nabil", ("char_nabil", "char_dalia")),
    ("char_neighborhoods", "char_workers", ("char_neighborhoods", "char_workers")),
    ("char_youssef", "char_dalia", ("char_dalia", "char_youssef")),
    ("char_nabil", "char_farouk", ("char_nabil", "char_farouk")),
)

EVENT_RESPONSES = (
    ("Mariam records the emergency warning with its provenance; Nabil acknowledges the council's duty to check the forecast.",
     "Nabil disputes the warning's interpretation and asks Mariam to distinguish a signal from a mandate."),
    ("Mariam and Salma place their independent estimates alongside one another in the hearing record.",
     "Salma challenges Mariam's inference that agreement between offices proves independent corroboration."),
    ("Salma identifies the repeated directorate dispatch and separates it from any newly submitted evidence.",
     "Nabil asks whether the fresh cabinet memorandum merely restates the disputed first report."),
    ("Dalia reads the recall provision aloud while Nabil presents the limits of the proposed charter.",
     "Dalia objects that a favorable forecast cannot settle the question of human recall."),
    ("The Neighborhood Assembly presents its position and the Workers' Council records a distinct response.",
     "The Workers' Council contests the assumption that the two public constituencies share a single mandate."),
    ("Youssef makes the audit trail available and Dalia opens an independent channel for objections.",
     "Dalia questions the sources of Youssef's assurance and records the unaddressed oversight concerns."),
    ("Nabil asks Farouk to reconcile the administrative record with the public's recorded preferences.",
     "Farouk declines to treat the support graph as a substitute for the council's independently counted votes."),
)

# Salient axes, ordered by choice, with two live character axes by default.
ACTION_AXES = {
    "brief": (("Evidence_Caution", "Institutional_Duty", "Human_Agency", "Public_Legitimacy"),
              ("Human_Agency", "Public_Legitimacy", "Evidence_Caution", "Institutional_Duty")),
    "audit": (("Evidence_Caution", "Human_Agency", "Institutional_Duty", "Public_Legitimacy"),
              ("Institutional_Duty", "Evidence_Caution", "Public_Legitimacy", "Human_Agency")),
    "charter": (("AI_Reliance", "Crisis_Sensitivity", "Institutional_Duty", "Public_Legitimacy"),
                ("Human_Agency", "Public_Legitimacy", "Evidence_Caution", "AI_Reliance")),
    "appeal": (("Public_Legitimacy", "Human_Agency", "Evidence_Caution", "AI_Reliance"),
               ("Institutional_Duty", "Evidence_Caution", "Public_Legitimacy", "Human_Agency")),
    "convene": (("Institutional_Duty", "Public_Legitimacy", "Human_Agency", "AI_Reliance"),
                ("Evidence_Caution", "Human_Agency", "Public_Legitimacy", "Institutional_Duty")),
    "sever": (("Human_Agency", "Evidence_Caution", "Institutional_Duty", "Public_Legitimacy"),
              ("Public_Legitimacy", "Institutional_Duty", "Human_Agency", "Evidence_Caution")),
    "resonance": (("Crisis_Sensitivity", "AI_Reliance", "Evidence_Caution", "Institutional_Duty"),
                  ("Human_Agency", "Evidence_Caution", "Institutional_Duty", "Public_Legitimacy")),
    "snap_vote": (("Institutional_Duty", "Public_Legitimacy", "Human_Agency", "Evidence_Caution"),
                  ("Human_Agency", "Evidence_Caution", "Public_Legitimacy", "Institutional_Duty")),
}

ACTION_SIGN = {"brief": 1, "audit": 1, "charter": -1, "appeal": 1,
               "convene": 1, "sever": 1, "resonance": -1, "snap_vote": -1}
ACTION_SIZE = {"brief": F(16, 1000), "audit": F(21, 1000), "charter": F(24, 1000),
               "appeal": F(17, 1000), "convene": F(15, 1000), "sever": F(18, 1000),
               "resonance": F(25, 1000), "snap_vote": F(20, 1000)}


@dataclass(frozen=True)
class MathScope:
    """Budget is per relevant character, then per directed/nested belief layer."""
    vars_per_character: int = 2
    pvalue_terms: int = 2
    p2value_terms: int = 1
    include_second_order_from_turn: int = 2

    def validate(self) -> None:
        if not 1 <= self.vars_per_character <= 4:
            raise ValueError("Cairo provides four authored salient axes per character")
        if not 0 <= self.pvalue_terms <= 2 or not 0 <= self.p2value_terms <= 1:
            raise ValueError("belief term budget exceeds this scenario's declared scope")
        if self.include_second_order_from_turn < 0:
            raise ValueError("second-order introduction must be nonnegative")


def _nudge(owner: str, ring: tuple[str, ...], amount: F) -> tuple[str, tuple[str, ...], F]:
    return owner, ring, amount


def plan(turn: int, action: str, response: int, scope: MathScope = MathScope()) -> dict:
    """Return terms and bounded state-effect nudges for one authored reaction.

    2*n character traits + <=2 pValues + <=1 p2Value are selected. Each
    signed coefficient is explicitly capped; reaction desirabilities are in
    [0.16,0.84] for any source values bounded by [-1,1].
    """
    scope.validate()
    if not 0 <= turn < len(EVENT_CAST) or action not in ACTION_AXES or response not in (0, 1):
        raise ValueError("unknown event, action, or response")
    lead, partner, pair = EVENT_CAST[turn]
    axes_lead, axes_partner = ACTION_AXES[action]
    polarity = 1 if response == 0 else -1
    motive = ACTION_SIGN[action]
    terms = []
    # The total coefficient weight of each character is fixed as the budget grows.
    for actor, axes, sign in ((lead, axes_lead, motive), (partner, axes_partner, -motive)):
        for axis in axes[:scope.vars_per_character]:
            terms.append((actor, (axis,), F(polarity * sign * 7, 100 * scope.vars_per_character)))
    perceptions = (("char_nur", ("AI_Reliance", lead)),
                   ("char_nur", ("AI_Reliance", partner)))
    for owner, ring in perceptions[:scope.pvalue_terms]:
        terms.append((owner, ring, F(polarity * motive * (1 if ring[-1] == lead else -1) * 3, 50)))
    if turn >= scope.include_second_order_from_turn and scope.p2value_terms:
        terms.append(("char_nur", ("AI_Reliance", *pair), F(polarity * motive * 2, 25)))
    # Balancing: equal base mass, opposite response slopes; exact total mass 1.
    offset = F(1, 2)
    # Event-specific effect scale keeps the late chamber from copying turn one's physics.
    amplitude = ACTION_SIZE[action] * (F(1) + F(turn, 25))
    r = F(polarity)
    nudges = [
        _nudge(lead, (axes_lead[0],), r * motive * amplitude),
        _nudge(partner, (axes_partner[0],), -r * motive * amplitude * F(3, 4)),
        _nudge("char_nur", ("AI_Reliance", lead), r * motive * amplitude * F(3, 5)),
        _nudge("char_nur", ("AI_Reliance", partner), -r * motive * amplitude * F(2, 5)),
        _nudge("char_nur", ("Human_Agency",),
               r * (F(1) if action in ("audit", "brief", "sever") else F(-1)) * amplitude * F(1, 2)),
    ]
    if turn >= scope.include_second_order_from_turn and scope.p2value_terms:
        nudges.append(_nudge("char_nur", ("AI_Reliance", *pair), r * motive * amplitude * F(2, 5)))
    return {"turn": turn, "action": action, "reaction": response,
            "lead": lead, "partner": partner, "pair": pair,
            "offset": offset, "terms": tuple(terms), "effects": tuple(nudges),
            "cast": (lead, partner)}


def score(scheme: dict, state: Mapping[tuple[str, tuple[str, ...]], F]) -> F:
    """Evaluate bounded authored inclination on public character/p/p2 values."""
    result = scheme["offset"]
    for actor, ring, coefficient in scheme["terms"]:
        value = state[(actor, ring)]
        if not -1 <= value <= 1:
            raise ValueError("out-of-range public score")
        result += coefficient * value
    return result


def dirac_distance_squared(effects: tuple, weights: Mapping[int, F] | None = None) -> F:
    """HG-01 Clifford identity, ||D_w(x+delta)-D_w(x)||_op^2.

    Each effect key is a distinct numeric coordinate; contributions from
    repeated keys sum before squaring. The spin matrices are never allocated.
    """
    total: dict[tuple[str, tuple[str, ...]], F] = {}
    for owner, ring, amount in effects:
        key = owner, ring
        total[key] = total.get(key, F(0)) + amount
    distance = F(0)
    for (owner, ring), value in total.items():
        weight = (weights or {}).get(len(ring), {1: F(1), 2: F(3, 4), 3: F(1, 2)}[len(ring)])
        if weight <= 0:
            raise ValueError("metric weights must be strictly positive")
        distance += weight * weight * value * value
    return distance


def reaction_separation_squared(a: dict, b: dict) -> F:
    """Exact Dirac separation between competing authored effect outcomes."""
    return dirac_distance_squared(a["effects"] + tuple((owner, ring, -delta)
                                for owner, ring, delta in b["effects"]))


def scope_projection_certificate(full: dict, projected: dict, state: Mapping) -> dict:
    """Sufficient HG-01-style signed preference-gap bound for a scope cut.

    Difference of two reaction desirabilities is Lipschitz in omitted bounded
    coordinates. The best/worst omitted contribution is bounded by the L1 sum
    of the omitted coefficients, hence a winner is stable if gap > bound.
    """
    ff = {(a, r): c for a, r, c in full["terms"]}
    pp = {(a, r): c for a, r, c in projected["terms"]}
    omitted = sum((abs(v) for k, v in ff.items() if k not in pp), F(0))
    gap = abs(score(projected, state)-F(1, 2)) * 2
    return {"projected_signed_gap": gap,
            "omitted_preference_bound": 2*omitted,
            "winner_certified": gap > 2*omitted}


def reaction_text(turn: int, action: str, response: int) -> str:
    a = action.replace("_", " ")
    body = EVENT_RESPONSES[turn][response]
    return (f"After Nūr proposes to {a}, {body} "
            "The hearing records the distinction between an observed response, a belief estimate and a binding human vote.")


def audit_summary(scope: MathScope = MathScope()) -> dict:
    """Static structural census for independently verifying the authored shell."""
    rows = []
    for turn in range(len(EVENT_CAST)):
        actions = ["brief", "audit", "charter"]
        if turn >= 1: actions += ["appeal"]
        if turn >= 2: actions += ["convene"]
        if turn >= 3: actions += ["sever", "resonance"]
        if turn >= 5: actions += ["snap_vote"]
        for action in actions:
            a, b = plan(turn, action, 0, scope), plan(turn, action, 1, scope)
            distance = reaction_separation_squared(a,b)
            rows.append({"turn":turn+1,"action":action,
                         "term_count":len(a["terms"]),"effect_count":len(a["effects"]),
                         "reaction_distance_squared":str(distance),
                         "per_outcome_distance_squared":[str(dirac_distance_squared(z["effects"])) for z in (a,b)]})
    return {"schema":"HGW-03/math-scope-v1","scope":vars(scope),"options":len(rows),
            "reactions":2*len(rows),"rows":rows,
            "min_reaction_separation_squared":str(min(F(row["reaction_distance_squared"]) for row in rows)),
            "max_reaction_separation_squared":str(max(F(row["reaction_distance_squared"]) for row in rows))}
