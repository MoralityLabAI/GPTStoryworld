"""Small series-level opponent model for the Pluto strategic-DAG prototype.

Payoffs and response policies are supplied externally. The bundled experiment
uses illustrative numbers, not replay-estimated StarCraft win probabilities.
"""
from __future__ import annotations

import json
from typing import Mapping

from .strategic_dag import Belief, normalize_probabilities


def forecast_responses(
    belief: Belief,
    counters: Mapping[str, Mapping[str, float]],
    responsiveness: float = 0.85,
) -> dict[str, float]:
    """Mix opponent's base tendency with a counter to what it expects us to do.

    Our first-order PValues forecast enemy openings. Our P2Values estimate
    the enemy's beliefs about our openings, which shape its likely counter.
    """
    if not 0 <= responsiveness <= 1:
        raise ValueError("responsiveness outside [0,1]")
    hypotheses = set(belief.first)
    if set(belief.second) != set(counters):
        raise ValueError("counter table must cover all second-order hypotheses")
    result = {h: (1 - responsiveness) * p for h, p in belief.first.items()}
    for our_opening, probability in belief.second.items():
        counter = normalize_probabilities(counters[our_opening])
        if set(counter) != hypotheses:
            raise ValueError("counter response categories differ from first-order hypotheses")
        for enemy_opening, p in counter.items():
            result[enemy_opening] += responsiveness * probability * p
    return normalize_probabilities(result)


def opening_values(
    belief: Belief,
    payoff: Mapping[str, Mapping[str, float]],
    counters: Mapping[str, Mapping[str, float]],
    responsiveness: float = 0.85,
) -> dict[str, float]:
    """Expected win probability for each supported own opening."""
    if set(payoff) != set(belief.second):
        raise ValueError("payoff table must cover own opening hypotheses")
    response = forecast_responses(belief, counters, responsiveness)
    result = {}
    for opening, vs_enemy in payoff.items():
        if set(vs_enemy) != set(response):
            raise ValueError("payoff row has incompatible enemy openings")
        if any(not 0 <= p <= 1 for p in vs_enemy.values()):
            raise ValueError("win payoffs outside [0,1]")
        result[opening] = sum(response[e] * vs_enemy[e] for e in response)
    return result


def choose_opening(
    belief: Belief,
    payoff: Mapping[str, Mapping[str, float]],
    counters: Mapping[str, Mapping[str, float]],
    responsiveness: float = 0.85,
) -> tuple[str, dict[str, float]]:
    values = opening_values(belief, payoff, counters, responsiveness)
    return max(sorted(values), key=lambda k: values[k]), values


def observe_completed_game(
    belief: Belief, our_opening: str, their_opening: str,
    enemy_learning: float = 0.70, our_learning: float = 0.30,
) -> Belief:
    """Recency model applied only after a game's true openings are known.

    enemy_learning: presumed opponent updating its picture of our next plan.
    our_learning: our own updating of the opponent's opening tendency.
    These rates are experimental assumptions to fit, not mind-reading.
    """
    for val in (enemy_learning, our_learning):
        if not 0 <= val <= 1:
            raise ValueError("learning rates outside [0,1]")
    if our_opening not in belief.second or their_opening not in belief.first:
        raise ValueError("unknown observed opening")
    first = {h: (1 - our_learning) * p + our_learning * (h == their_opening)
             for h, p in belief.first.items()}
    second = {h: (1 - enemy_learning) * p + enemy_learning * (h == our_opening)
              for h, p in belief.second.items()}
    return Belief(first, second)


def illustrative_environment() -> tuple[Belief, dict, dict]:
    """Frozen toy ZvT responses chosen to expose counter-adaptation."""
    belief = Belief(
        {"bio_FE": 0.35, "factory": 0.40, "wraith": 0.25},
        {"9_pool": 0.10, "12_hatch": 0.80, "3_hatch_muta": 0.10},
    )
    counters = {
        "9_pool": {"bio_FE": .90, "factory": .05, "wraith": .05},
        "12_hatch": {"bio_FE": .05, "factory": .90, "wraith": .05},
        "3_hatch_muta": {"bio_FE": .05, "factory": .05, "wraith": .90},
    }
    payoff = {
        "9_pool": {"bio_FE": .35, "factory": .65, "wraith": .55},
        "12_hatch": {"bio_FE": .65, "factory": .30, "wraith": .45},
        "3_hatch_muta": {"bio_FE": .48, "factory": .55, "wraith": .28},
    }
    return belief, payoff, counters


def toy_reverse_sweep(initial_score: tuple[int, int] = (0, 2)) -> dict:
    """Counterfactual continuation from 0-2, with no sampled wins.

    The probability product assumes conditional independence of three
    decisive games under the supplied behavioral transition model.
    """
    if initial_score != (0, 2):
        raise ValueError("toy experiment is explicitly the 0-2 continuation")
    initial, payoff, counters = illustrative_environment()

    def rollout(adaptive: bool) -> dict:
        belief = initial
        record = []
        frozen_opening = choose_opening(initial, payoff, counters, 0.0)[0]
        likelihood = 1.0
        for game in (3, 4, 5):
            decision = choose_opening(belief, payoff, counters)[0] if adaptive else frozen_opening
            predicted = forecast_responses(belief, counters)
            # The opponent responds to its own current expectations. For the
            # toy environment these beliefs are represented by the same P2
            # dynamics used by our model. This is a matched-model upper bound.
            enemy = max(sorted(predicted), key=lambda k: predicted[k])
            game_win = payoff[decision][enemy]
            likelihood *= game_win
            record.append({
                "game": game, "our_opening": decision, "enemy_response": enemy,
                "conditional_win_probability": game_win,
                "enemy_response_forecast": predicted,
            })
            belief = observe_completed_game(belief, decision, enemy)
        return {"games": record, "modeled_reverse_sweep_probability": likelihood}

    return {
        "synthetic": True,
        "starting_score": list(initial_score),
        "first_and_second_order": rollout(True),
        "static_first_order": rollout(False),
        "interpretation": "matched toy countermodel; not Pluto game results",
    }


if __name__ == "__main__":
    print(json.dumps(toy_reverse_sweep(), sort_keys=True, indent=2))
