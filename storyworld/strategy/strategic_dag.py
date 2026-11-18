"""Compact, epistemically separated strategic DAGs for StarCraft-style storyworlds.

This research prototype consumes forecasts and synthetic transitions. It does not
control Pluto or read hidden game state. Only the owning player's observations
belong in a belief update.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from typing import Dict, Mapping, Sequence


def normalize_probabilities(values: Mapping[str, float]) -> Dict[str, float]:
    if not values:
        raise ValueError("a belief needs at least one hypothesis")
    if any(not math.isfinite(v) or v < 0 for v in values.values()):
        raise ValueError("belief weights must be finite and nonnegative")
    total = sum(values.values())
    if total <= 0 or not math.isfinite(total):
        raise ValueError("zero or nonfinite belief evidence")
    return {k: values[k] / total for k in sorted(values)}


def bayes_update(prior: Mapping[str, float], evidence: Mapping[str, float]) -> Dict[str, float]:
    """P(h|e) proportional to P(e|h) P(h). Missing likelihoods are zero."""
    normalize_probabilities(prior)
    if any(not math.isfinite(v) or not 0 <= v <= 1 for v in evidence.values()):
        raise ValueError("likelihoods must lie in [0, 1]")
    if not set(evidence).issubset(prior):
        raise ValueError("evidence contains an unknown hypothesis")
    return normalize_probabilities({k: p * evidence.get(k, 0.0) for k, p in prior.items()})


@dataclass(frozen=True)
class Belief:
    """Our PValues and our estimates of the opponent's PValues (P2Values)."""
    first: Mapping[str, float]
    second: Mapping[str, float]

    def __post_init__(self) -> None:
        object.__setattr__(self, "first", normalize_probabilities(self.first))
        object.__setattr__(self, "second", normalize_probabilities(self.second))

    def observe_opponent(self, likelihood: Mapping[str, float]) -> "Belief":
        return Belief(bayes_update(self.first, likelihood), self.second)

    def observe_opponent_scout(self, likelihood: Mapping[str, float]) -> "Belief":
        """Update our estimate of which of our openings the opponent expects."""
        return Belief(self.first, bayes_update(self.second, likelihood))

    def as_storyworld_pointers(
        self, self_id: str = "char_pluto", enemy_id: str = "char_opponent"
    ) -> list[dict]:
        """Encode categorical forecasts as bounded-number P/P2 properties.

        Property name Opening_X denotes a hypothesis. The number 2*p-1 is a
        documented encoding convention, not a statistical p-value.
        """
        rows = []
        for name, p in self.first.items():
            rows.append({"character": self_id,
                         "keyring": [f"Opening_{name}", enemy_id],
                         "value": 2.0 * p - 1.0})
        for name, p in self.second.items():
            rows.append({"character": self_id,
                         "keyring": [f"Opening_{name}", enemy_id, self_id],
                         "value": 2.0 * p - 1.0})
        return rows


@dataclass(frozen=True)
class Edge:
    outcome: str
    probability: float
    reward: float
    target: str


@dataclass(frozen=True)
class Node:
    id: str
    stage: int
    public_key: str
    belief: Belief
    actions: Mapping[str, tuple[Edge, ...]]
    terminal_value: float | None = None


def _linf(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    if set(left) != set(right):
        return math.inf
    return max((abs(left[k] - right[k]) for k in left), default=0.0)


class StrategicDAG:
    """Finite-horizon decision DAG with explicit chance edges and typed beliefs."""

    def __init__(self, nodes: Sequence[Node], discount: float = 1.0):
        if not 0 <= discount <= 1:
            raise ValueError("discount must lie in [0, 1]")
        self.nodes = {node.id: node for node in nodes}
        if len(self.nodes) != len(nodes):
            raise ValueError("duplicate node ids")
        self.discount = discount
        self._validate()

    def _validate(self) -> None:
        for node in self.nodes.values():
            if node.stage < 0:
                raise ValueError(f"negative stage at {node.id}")
            if node.terminal_value is not None:
                if node.actions or not math.isfinite(node.terminal_value):
                    raise ValueError(f"invalid terminal node {node.id}")
                continue
            if not node.actions:
                raise ValueError(f"nonterminal node without actions: {node.id}")
            for action, edges in node.actions.items():
                if not action or not edges:
                    raise ValueError(f"empty action/edge at {node.id}")
                total = 0.0
                seen = set()
                for edge in edges:
                    if (not math.isfinite(edge.probability)
                            or edge.probability < 0
                            or not math.isfinite(edge.reward)):
                        raise ValueError(f"invalid probability/reward at {node.id}")
                    if edge.outcome in seen:
                        raise ValueError(f"duplicate observation {edge.outcome} at {node.id}")
                    seen.add(edge.outcome)
                    target = self.nodes.get(edge.target)
                    if target is None or target.stage <= node.stage:
                        raise ValueError(f"missing/nonforward edge from {node.id}")
                    total += edge.probability
                if abs(total - 1) > 1e-9:
                    raise ValueError(f"action {action} at {node.id} has mass {total}")

    def values(self) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
        """Exact backward induction for the supplied finite synthetic/empirical DAG."""
        v: dict[str, float] = {}
        q: dict[str, dict[str, float]] = {}
        for node in sorted(self.nodes.values(), key=lambda n: (-n.stage, n.id)):
            if node.terminal_value is not None:
                q[node.id] = {}
                v[node.id] = node.terminal_value
            else:
                q[node.id] = {
                    action: sum(e.probability * (e.reward + self.discount * v[e.target])
                                for e in edges)
                    for action, edges in sorted(node.actions.items())
                }
                v[node.id] = max(q[node.id].values())
        return v, q

    def compactify(
        self, *, q_epsilon: float = 0.02, belief_epsilon: float = 0.03,
        transition_epsilon: float = 0.01, reward_epsilon: float = 0.01
    ) -> dict:
        """Bottom-up approximate bisimulation with an explicit regret check.

        Nodes merge only within the same stage/public-state class. Their
        outgoing outcomes must reach the same already-compacted child classes.
        Each candidate is checked against every class member to prevent
        transitive drift across an epsilon chain.
        """
        if min(q_epsilon, belief_epsilon, transition_epsilon, reward_epsilon) < 0:
            raise ValueError("negative compactification tolerance")
        _, q = self.values()
        groups: list[list[str]] = []
        quotient: dict[str, int] = {}

        def compatible(a: Node, b: Node) -> bool:
            if (a.stage != b.stage or a.public_key != b.public_key
                    or sorted(a.actions) != sorted(b.actions)
                    or (a.terminal_value is None) != (b.terminal_value is None)):
                return False
            if (_linf(a.belief.first, b.belief.first) > belief_epsilon
                    or _linf(a.belief.second, b.belief.second) > belief_epsilon
                    or _linf(q[a.id], q[b.id]) > q_epsilon):
                return False
            if a.terminal_value is not None:
                return abs(a.terminal_value - b.terminal_value) <= q_epsilon
            for action in a.actions:
                ea = sorted(a.actions[action], key=lambda e: e.outcome)
                eb = sorted(b.actions[action], key=lambda e: e.outcome)
                if len(ea) != len(eb):
                    return False
                for x, y in zip(ea, eb):
                    if (x.outcome != y.outcome or quotient[x.target] != quotient[y.target]
                            or abs(x.probability - y.probability) > transition_epsilon
                            or abs(x.reward - y.reward) > reward_epsilon):
                        return False
            return True

        for node in sorted(self.nodes.values(), key=lambda n: (-n.stage, n.id)):
            match = next(
                (i for i, members in enumerate(groups)
                 if all(compatible(node, self.nodes[other]) for other in members)),
                None,
            )
            if match is None:
                match = len(groups)
                groups.append([])
            groups[match].append(node.id)
            quotient[node.id] = match

        regret = 0.0
        for members in groups:
            representative = members[0]
            if not q[representative]:
                continue
            best = max(sorted(q[representative]), key=lambda a: q[representative][a])
            for node_id in members:
                regret = max(regret, max(q[node_id].values()) - q[node_id][best])
        return {
            "original_nodes": len(self.nodes),
            "compact_nodes": len(groups),
            "compression_ratio": len(self.nodes) / len(groups),
            "maximum_empirical_greedy_regret": regret,
            "greedy_regret_bound_from_q": 2 * q_epsilon,
            "node_to_class": {k: quotient[k] for k in sorted(quotient)},
            "classes": [sorted(members) for members in groups],
        }


def example() -> StrategicDAG:
    """Illustrative observations and outcomes, never measured Pluto win rates."""
    prior = Belief(
        {"bio_FE": 0.45, "factory": 0.35, "wraith": 0.20},
        {"12_hatch": 0.75, "9_pool": 0.25},
    )
    factory = prior.observe_opponent({"bio_FE": 0.15, "factory": 0.80, "wraith": 0.35})
    bio = prior.observe_opponent({"bio_FE": 0.85, "factory": 0.20, "wraith": 0.10})
    nodes = [
        Node("win_a", 2, "ZvT:terminal", prior, {}, 1.0),
        Node("win_b", 2, "ZvT:terminal", prior, {}, 1.0),
        Node("loss_a", 2, "ZvT:terminal", prior, {}, 0.0),
        Node("loss_b", 2, "ZvT:terminal", prior, {}, 0.0),
    ]

    def decision(node_id: str, beliefs: Belief, strong_muta: float,
                 win_id: str, loss_id: str) -> Node:
        return Node(
            node_id, 1, "ZvT:one_base_scout", beliefs,
            {
                "muta": (Edge("win", strong_muta, 0, win_id),
                         Edge("loss", 1 - strong_muta, 0, loss_id)),
                "hydra": (Edge("win", 1 - strong_muta / 2, 0, win_id),
                          Edge("loss", strong_muta / 2, 0, loss_id)),
            },
        )

    nodes.extend([
        decision("factory_1", factory, 0.30, "win_a", "loss_a"),
        decision("factory_2", factory, 0.30, "win_b", "loss_b"),
        decision("bio_1", bio, 0.75, "win_a", "loss_a"),
        Node(
            "game3", 0, "ZvT:series_0_2", prior,
            {
                "12_hatch": (Edge("scout_factory", .45, 0, "factory_1"),
                             Edge("scout_bio", .55, 0, "bio_1")),
                "9_pool": (Edge("scout_factory", .45, -0.02, "factory_2"),
                            Edge("scout_bio", .55, -0.02, "bio_1")),
            },
        ),
    ])
    return StrategicDAG(nodes)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Print deterministic illustrative DAG")
    args = parser.parse_args()
    if not args.demo:
        parser.error("use --demo")
    graph = example()
    v, q = graph.values()
    print(json.dumps({
        "synthetic": True,
        "root_v": v["game3"],
        "root_q": q["game3"],
        "factory_pvalues": graph.nodes["factory_1"].belief.first,
        "compactification": graph.compactify(),
        "storyworld_keyrings": graph.nodes["factory_1"].belief.as_storyworld_pointers(),
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
