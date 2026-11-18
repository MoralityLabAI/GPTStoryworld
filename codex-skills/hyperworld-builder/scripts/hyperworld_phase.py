"""Fictional Cairo chamber: p/p2 recruitability beliefs and finite graph cascades.

All mechanisms are invented game rules. This is a transparent, non-operational
social-inference sandbox: no actual institutions, personnel or targeting data.
The graph models *perceived* support, never a legally valid human vote.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from typing import Mapping

NODES = (
    "char_nabil", "char_mariam", "char_farouk", "char_salma",
    "char_dalia", "char_youssef", "char_neighborhoods", "char_workers",
)
# Undirected procedural deliberation links, all invented. Each has a player-facing name.
EDGES = (
    ("char_nabil", "char_mariam", "Directorate assessment", F(3, 5)),
    ("char_nabil", "char_farouk", "Executive consultation", F(2, 5)),
    ("char_nabil", "char_dalia", "Legal review", F(2, 5)),
    ("char_mariam", "char_salma", "Analysis and budget", F(1, 2)),
    ("char_mariam", "char_youssef", "Independent source review", F(2, 5)),
    ("char_farouk", "char_salma", "Civil budget committee", F(1, 2)),
    ("char_farouk", "char_neighborhoods", "District service board", F(3, 5)),
    ("char_salma", "char_workers", "Infrastructure labor forum", F(3, 5)),
    ("char_dalia", "char_youssef", "Independent appeals committee", F(1, 2)),
    ("char_dalia", "char_neighborhoods", "Community hearing", F(2, 5)),
    ("char_youssef", "char_workers", "Labor inspection panel", F(2, 5)),
    ("char_neighborhoods", "char_workers", "Public assembly forum", F(1, 2)),
)
# A particular fictional, named relationship is at issue on each encounter.
FOCUS_EDGES = (
    ("char_nabil", "char_mariam"),
    ("char_mariam", "char_salma"),
    ("char_mariam", "char_youssef"),
    ("char_nabil", "char_dalia"),
    ("char_neighborhoods", "char_workers"),
    ("char_dalia", "char_youssef"),
    ("char_nabil", "char_farouk"),
)
FOCUS_PEOPLE = (
    "char_nabil", "char_mariam", "char_salma", "char_dalia",
    "char_neighborhoods", "char_youssef", "char_farouk",
)


def key(a: str, b: str) -> tuple[str, str]:
    if a == b or a not in NODES or b not in NODES:
        raise ValueError("two distinct fictional citizens required")
    return tuple(sorted((a, b)))


def clamp(x: F, lo: F = F(-1), hi: F = F(1)) -> F:
    return max(lo, min(hi, x))


def graph_weights() -> dict[tuple[str, str], F]:
    return {key(a, b): w for a, b, _, w in EDGES}


@dataclass(frozen=True)
class SocialMoments:
    """Exact posterior moments sufficient for every p/p2 and graph calculation."""
    points: tuple[F, ...]
    pairs: dict[tuple[int, int], F]


def collect_moments(posterior: tuple[F, ...]) -> SocialMoments:
    if len(posterior) != 1024 or sum(posterior) != 1:
        raise ValueError("Cairo posterior must have 1024 normalized weights")
    return SocialMoments(
        tuple(point_belief(posterior, i) for i in range(8)),
        {(i,j): pair_affinity(posterior, i, j) for i in range(8) for j in range(i+1,8)},
    )


def point_belief(posterior: tuple[F, ...] | SocialMoments, index: int) -> F:
    """E[2 Z_i - 1]. Posterior is normalized over the same 1024 worlds."""
    if not 0 <= index < 8:
        raise ValueError("invalid actor index")
    if isinstance(posterior, SocialMoments):
        return posterior.points[index]
    if len(posterior) != 1024 or sum(posterior) != 1:
        raise ValueError("invalid Cairo posterior")
    return sum((m if (world >> index) & 1 else -m for world, m in enumerate(posterior)), F(0))


def pair_affinity(posterior: tuple[F, ...] | SocialMoments, a: int, b: int) -> F:
    """E[(2 Z_a -1)(2 Z_b -1)], including correlations invisible in marginals."""
    if not 0 <= a < 8 or not 0 <= b < 8 or a == b:
        raise ValueError("distinct actor indices required")
    if isinstance(posterior, SocialMoments):
        return posterior.pairs[(min(a,b),max(a,b))]
    if len(posterior) != 1024:
        raise ValueError("Cairo posterior must have 1024 states")
    return sum((m if ((world >> a) ^ (world >> b)) & 1 == 0 else -m
                for world, m in enumerate(posterior)), F(0))


def pvalue(posterior: tuple[F, ...] | SocialMoments, observer: str, target: str) -> F:
    """A's *modeled* bounded susceptibility estimate of B, [-1,1].

    A correlates its own disposition with B's; parameters are declared fiction.
    This is NOT a frequentist p value or a known psychological attribute.
    """
    if observer not in (*NODES, "char_nur") or target not in NODES or observer == target:
        raise ValueError("first-order perception requires distinct fictional actors")
    b = NODES.index(target)
    if observer == "char_nur":
        return point_belief(posterior, b)
    a = NODES.index(observer)
    return clamp(F(3, 4) * point_belief(posterior, b) + F(1, 4) * pair_affinity(posterior, a, b))


def p2value(posterior: tuple[F, ...] | SocialMoments, observer: str, believer: str, target: str) -> F:
    """A's estimate of B's belief about C's willingness to support the charter.

    Simple explicitly fictional nested mind model. The covariance term allows
    second-order beliefs to change after XOR evidence even at fixed marginals.
    """
    if observer not in (*NODES, "char_nur") or believer not in NODES or target not in NODES or len({observer,believer,target}) != 3:
        raise ValueError("three distinct characters required for p2Value")
    b, c = NODES.index(believer), NODES.index(target)
    observer_term = F(0) if observer == "char_nur" else F(1, 6) * pair_affinity(posterior, NODES.index(observer), b)
    return clamp(F(1, 2) * point_belief(posterior, c) +
                 F(1, 3) * pair_affinity(posterior, b, c) + observer_term)


@dataclass(frozen=True)
class Phase:
    supports: tuple[str, ...]
    initial: tuple[str, ...]
    rounds: tuple[tuple[str, ...], ...]
    snap: bool
    added: int
    order_parameter: F
    phase: str


def phase_transition(posterior: tuple[F, ...] | SocialMoments, edges: Mapping[tuple[str, str], F],
                     appeals: Mapping[str, F], *, peer_gain: F = F(7, 8),
                     threshold: F = F(2, 5), seed_threshold: F = F(1, 4),
                     traits: Mapping[str, Mapping[str, F]] | None = None) -> Phase:
    """Finite, monotone bootstrap cascade with a threshold and positive feedback.

    Starting nodes independently support the proposal, while undecided nodes
    can cross the threshold as peer agreement changes. Max eight rounds.
    Recomputed from first principles on each turn; this is an observable model
    of perceived consensus, never a truth oracle or binding authority.
    """
    weights = graph_weights()
    for ab, weight in edges.items():
        if ab not in weights or type(weight) is not F or not F(0) <= weight <= F(1):
            raise ValueError("unknown deliberation link or invalid weight")
        weights[ab] = weight
    if any(n not in NODES or type(v) is not F or not F(0) <= v <= F(1) for n, v in appeals.items()):
        raise ValueError("invalid fictional dialogue effect")
    # All six authored character traits contribute to each node's readiness.
    # Their coefficients are game-balancing assumptions, never estimates of
    # any real individual's receptivity to influence.
    profile_signs = {
        "Institutional_Duty": -1, "Evidence_Caution": -1,
        "Human_Agency": -1, "Crisis_Sensitivity": +1,
        "AI_Reliance": +1, "Public_Legitimacy": +1,
    }
    bias = {n: F(0) for n in NODES}
    if traits is not None:
        for n in NODES:
            if n not in traits or set(traits[n]) != set(profile_signs):
                raise ValueError("each fictional character requires six declared trait axes")
            if any(type(t) is not F or not -1 <= t <= 1 for t in traits[n].values()):
                raise ValueError("character traits must be bounded exact rationals")
            bias[n] = F(1, 20)*sum((traits[n][ax]*sign for ax, sign in profile_signs.items()), F(0))
    base = {n: point_belief(posterior, i) + bias[n] for i, n in enumerate(NODES)}
    seeded = {n for n in NODES if base[n] + F(5, 4)*appeals.get(n, F(0)) >= seed_threshold}
    active = set(seeded)
    rounds: list[tuple[str, ...]] = []
    max_add = 0
    for _ in range(len(NODES)):
        new = set()
        for n in NODES:
            if n in active:
                continue
            connections = [(m, weights.get(key(n, m), F(0))) for m in NODES if m != n]
            weight_sum = sum((w for _, w in connections), F(0))
            neighbors = sum((w for m, w in connections if m in active), F(0))
            support_fraction = neighbors / weight_sum if weight_sum else F(0)
            # p2: Nūr estimates whether this character expects their neighbors to
            # be receptive, creating an inspectable higher-order graph effect.
            p2_sum = sum((w*p2value(posterior, "char_nur", n, m)
                          for m, w in connections if w), F(0))
            p2_term = p2_sum / weight_sum if weight_sum else F(0)
            # Directed first-order susceptibility beliefs affect the network
            # game separately from nested belief-about-belief estimates.
            p1_sum = sum((w*pvalue(posterior, n, m) for m, w in connections if w), F(0))
            p1_term = p1_sum / weight_sum if weight_sum else F(0)
            drive = (base[n] + F(5, 4)*appeals.get(n, F(0)) +
                     peer_gain*support_fraction + F(1, 8)*p1_term + F(1, 6)*p2_term)
            if drive >= threshold:
                new.add(n)
        if not new:
            break
        rounds.append(tuple(sorted(new)))
        max_add = max(max_add, len(new))
        active.update(new)
    fraction = F(len(active), len(NODES))
    snapped = len(seeded) <= 4 and len(active) >= 6 and (len(active)-len(seeded)) >= 2
    return Phase(tuple(sorted(active)), tuple(sorted(seeded)), tuple(rounds),
                 snapped, len(active)-len(seeded), fraction,
                 "consensus_snap" if snapped else "near_critical" if len(active) >= 4 else "fragmented")


def bridge_delta(edges: Mapping[tuple[str, str], F], pair: tuple[str, str], value: F) -> dict[tuple[str, str], F]:
    """Authoritative fictional public deliberation link shift, symmetric by key."""
    out = graph_weights()
    out.update(edges)
    ab = key(*pair)
    out[ab] = clamp(out[ab] + value, F(0), F(1))
    return out


def marginal_critical_edge(posterior: tuple[F, ...] | SocialMoments, edges: Mapping[tuple[str, str], F],
                           appeals: Mapping[str, F], edge: tuple[str, str], amount: F = F(1, 4),
                           traits: Mapping[str, Mapping[str, F]] | None = None) -> dict:
    """Counterfactual change in modeled supporters, used only as game feedback."""
    before = phase_transition(posterior, edges, appeals, traits=traits)
    after = phase_transition(posterior, bridge_delta(edges, edge, amount), appeals, traits=traits)
    return {"edge": list(key(*edge)), "before": len(before.supports),
            "after": len(after.supports), "changed": len(after.supports)-len(before.supports),
            "new_phase": after.phase}
