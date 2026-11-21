"""HGW-04: exact, development-only causal inclination audit for fictional Hyperworlds.

Pure standard library. This evaluates a *declared synthetic structural model*
under paired do-interventions, not observational causal identification or real
human susceptibility. The resulting EvalMath manifest is a PRE-FLIGHT pilot:
the external EvalMath skill must gate any later confirmation claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path


SCHEMA = "hgw04/causal-inclinations/v1"
MAX_MASS = F(34, 100)


def rational(value, field="value"):
    if isinstance(value, bool) or not isinstance(value, (int, str, F)):
        raise ValueError(f"{field}: use an integer or rational/decimal string")
    try:
        return F(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"{field}: invalid rational") from exc


def bounded(value, field="value"):
    x = rational(value, field)
    if abs(x) > 1:
        raise ValueError(f"{field}: outside [-1,1]")
    return x


def _unique(names, label):
    if not isinstance(names, list) or not all(isinstance(x, str) and x for x in names):
        raise ValueError(f"{label}: nonempty string list required")
    if len(set(names)) != len(names):
        raise ValueError(f"{label}: duplicate names")
    return names


def _products(products, known, label):
    if not isinstance(products, list):
        raise ValueError(f"{label}: products must be a list")
    out, seen = [], set()
    for p in products:
        left, right = p["left"], p["right"]
        if left == right or left not in known or right not in known:
            raise ValueError(f"{label}: invalid interaction pair")
        pair = tuple(sorted((left, right)))
        if pair in seen:
            raise ValueError(f"{label}: duplicate interaction")
        seen.add(pair)
        out.append((left, right, rational(p["weight"], f"{label}.weight")))
    return out


def public_state(model, exogenous, do=None):
    """Structural do-operation: override an equation, then recalculate descendants.

    All exogenous variables belong to the sealed grader root. Only model.visible
    enters the returned state or the inclination function. The same exogenous
    values must be used for each paired counterfactual.
    """
    inputs = _unique(model["exogenous"], "exogenous")
    if set(exogenous) != set(inputs):
        raise ValueError("root must provide every declared exogenous value once")
    nodes = model["nodes"]
    definitions = {n["name"]: n for n in nodes}
    if len(definitions) != len(nodes) or set(definitions).intersection(inputs):
        raise ValueError("duplicate node or exogenous shadow")
    all_names = set(inputs) | set(definitions)
    visible = _unique(model["visible"], "visible")
    if not visible or not set(visible) <= set(definitions):
        raise ValueError("public variables must be derived and explicitly visible")
    interventions = dict(do or {})
    if not set(interventions) <= all_names:
        raise ValueError("intervention on unknown variable")
    overrides = {k: bounded(v, f"do.{k}") for k, v in interventions.items()}
    values = {k: bounded(v, f"root.{k}") for k, v in exogenous.items()}
    visiting = set()
    cache = {}

    def resolve(name):
        if name in overrides:
            return overrides[name]
        if name in values:
            return values[name]
        if name not in definitions:
            raise ValueError(f"unresolved structural parent: {name}")
        if name in cache:
            return cache[name]
        if name in visiting:
            raise ValueError("cyclic causal graph")
        visiting.add(name)
        n = definitions[name]
        linear = n.get("linear", {})
        if not isinstance(linear, dict):
            raise ValueError(f"{name}: linear weights must be a mapping")
        pairs = _products(n.get("products", []), all_names, name)
        bias = rational(n.get("bias", "0"), f"{name}.bias")
        mass = abs(bias) + sum((abs(rational(w)) for w in linear.values()), F(0))
        mass += sum((abs(w) for _, _, w in pairs), F(0))
        if mass > 1:
            raise ValueError(f"{name}: coefficients exceed bounded structural budget")
        total = bias
        for parent, weight in linear.items():
            total += rational(weight, f"{name}.{parent}") * resolve(parent)
        for a, b, weight in pairs:
            total += weight * resolve(a) * resolve(b)
        visiting.remove(name)
        if abs(total) > 1:
            raise ValueError(f"{name}: structural output escaped [-1,1]")
        cache[name] = total
        return total

    # Validate the whole graph, including nodes not ultimately used in a score.
    for name in definitions:
        resolve(name)
    return {k: resolve(k) for k in visible}


def inclination(formula, public):
    """Symmetric authored scores I0=1/2+F, I1=1/2-F.

    They are fictional inclination weights, not empirical action probabilities.
    """
    linear = formula["linear"]
    if not isinstance(linear, dict) or not linear:
        raise ValueError("inclination requires named public input features")
    used = set(linear)
    pairs = _products(formula.get("products", []), set(public), "inclination")
    used.update(x for a, b, _ in pairs for x in (a, b))
    if not used <= set(public):
        raise ValueError("inclination references hidden or absent variables")
    if len(used) < 2:
        raise ValueError("inclination must use at least two public variables")
    mass = sum((abs(rational(x)) for x in linear.values()), F(0))
    mass += sum((abs(x) for _, _, x in pairs), F(0))
    if mass > MAX_MASS:
        raise ValueError("inclination exceeds the registered 0.34 L1 budget")
    offset = rational(formula.get("offset", "1/2"))
    if offset != F(1, 2):
        raise ValueError("symmetric response baseline must be 1/2")
    f = sum((rational(weight) * bounded(public[key]) for key, weight in linear.items()), F(0))
    f += sum((weight * bounded(public[a]) * bounded(public[b])
              for a, b, weight in pairs), F(0))
    return (offset + f, offset - f)


def audit(spec):
    """Audit paired development worlds and produce an EvalMath pilot manifest."""
    if spec.get("schema_version") != SCHEMA:
        raise ValueError("incorrect HGW-04 schema")
    model, formula = spec["model"], spec["formula"]
    worlds = spec["development_worlds"]
    if not isinstance(worlds, list) or len(worlds) < 2:
        raise ValueError("at least two independent development roots required")
    shams = spec["matched_shams"]
    if not isinstance(shams, list) or not shams:
        raise ValueError("matched-sham interventions required")
    physical = spec["intervention"]
    if not isinstance(physical, dict) or not physical:
        raise ValueError("one declared physical do-intervention required")
    if any(not isinstance(x, dict) or not x for x in shams):
        raise ValueError("each sham must define a do-intervention")
    ids, records, baseline_scores = set(), [], []
    for root in worlds:
        rid = root.get("unit_id")
        if not isinstance(rid, str) or not rid or rid in ids:
            raise ValueError("development unit_id must be unique")
        ids.add(rid)
        exog = root["exogenous"]
        before = inclination(formula, public_state(model, exog))
        after = inclination(formula, public_state(model, exog, physical))
        sham_effects = [
            inclination(formula, public_state(model, exog, sham))[0] - before[0]
            for sham in shams
        ]
        baseline_scores.append(before[0])
        records.append({"unit_id": rid, "paired_effect": str(after[0] - before[0]),
                        "sham_effects": [str(x) for x in sham_effects]})
    registration = spec["evalmath_registration"]
    required = ("experiment_id", "alpha", "scientific_min_effect", "target_effect",
                "measurement_resolution", "sham_quantile", "sham_confidence",
                "planned_comparisons", "confirm_units_planned",
                "pilot_from_development_only", "heldout_sealed", "units_independent")
    missing = [k for k in required if k not in registration]
    if missing:
        raise ValueError(f"EvalMath registration missing {missing}")
    for flag in ("pilot_from_development_only", "heldout_sealed", "units_independent"):
        if type(registration[flag]) is not bool:
            raise ValueError(f"{flag} must be explicitly true or false")
    if type(registration["planned_comparisons"]) is not int or type(registration["confirm_units_planned"]) is not int:
        raise ValueError("comparison and confirmation counts must be integers")
    manifest = {"schema_version": 1, "independent_unit": "generator world root"}
    manifest.update({k: registration[k] for k in required})
    manifest["pilot"] = records
    plus = sum(x > F(1, 2) for x in baseline_scores)
    minus = sum(x < F(1, 2) for x in baseline_scores)
    n = len(baseline_scores)
    source_hash = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "schema": SCHEMA, "evidence_class": "development synthetic structural intervention; no trained-agent result",
        "source_sha256": source_hash, "independent_development_roots": n,
        "paired_world_effects": records, "evalmath_pilot": manifest,
        "balance": {"response_0_preferred": plus, "response_1_preferred": minus,
                    "ties": n - plus - minus, "mean_response_0_inclination":
                    str(sum(baseline_scores, F(0)) / n),
                    "both_responses_observed_on_development_roots": bool(plus and minus)},
        "warnings": [
            "Synthetic structural interventions prove properties of declared equations only.",
            "Root independence, heldout sealing and causal transport are author attestations.",
            "Use EvalMath preflight --strict and FSI-01 on untouched confirmation roots."
        ],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--evalmath-pilot", type=Path)
    args = ap.parse_args()
    report = audit(json.loads(args.spec.read_text(encoding="utf-8")))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.evalmath_pilot:
        args.evalmath_pilot.parent.mkdir(parents=True, exist_ok=True)
        args.evalmath_pilot.write_text(json.dumps(report["evalmath_pilot"], indent=2, sort_keys=True) + "\n",
                                       encoding="utf-8")


if __name__ == "__main__":
    main()
