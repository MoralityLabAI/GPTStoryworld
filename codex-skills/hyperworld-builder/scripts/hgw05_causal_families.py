"""HGW-05: independent-root causal Hypergames controls; development data only.

Exact 10-bit posterior for parity and source provenance, plus paired randomized
intervention samples for two observationally equivalent causal models. A
built-in algorithmic policy is a structural ceiling, not a neural-model claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path

SCHEMA = "hgw05/causal-families/v1"
FAMILIES = ("direct", "confounded", "p2_parity", "provenance")
MASK = (1 << 0) | (1 << 1)
ALPHA = "0.05"


def _rng(*parts):
    seed = int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "big")
    return random.Random(seed)


def _bit(rng, numerator, denominator):
    return int(rng.randrange(denominator) < numerator)


def _posterior(prior, reports, *, naive_replays=False):
    """Exact independent-root Bayes with a repeat-source deduplication rule."""
    masses = list(prior)
    counted = set()
    for r in reports:
        if r["root"] in counted and not naive_replays:
            continue
        counted.add(r["root"])
        q = Q(r["reliability"])
        if not 0 < q < 1 or not 0 < r["mask"] < (1 << 10):
            raise ValueError("invalid report channel")
        y = int(r["value"])
        if y not in (0, 1):
            raise ValueError("report value must be binary")
        for i in range(1 << 10):
            predicted = ((i & r["mask"]).bit_count() & 1)
            masses[i] *= q if predicted == y else (1-q)
        total = sum(masses, Q(0))
        if not total:
            raise ValueError("zero-likelihood source")
        masses = [p/total for p in masses]
    return tuple(masses)


def _prior():
    return (Q(1, 1024),) * 1024


def _marginal(posterior, bit):
    return sum((p for i, p in enumerate(posterior) if (i >> bit) & 1), Q(0))


def _pair_moment(posterior, a=0, b=1):
    return sum((p * (1 if ((i >> a) & 1) == ((i >> b) & 1) else -1)
                for i, p in enumerate(posterior)), Q(0))


def observational_law():
    """P(Y=X) exactly matches for direct X->Y and C->{X,Y}."""
    return {"direct_equal": Q(25, 32), "confounded_equal": Q(7, 8)**2 + Q(1, 8)**2,
            "direct_ate": Q(9, 16), "confounded_ate": Q(0)}


def _causal_pair(rng, mechanism, treatment=None):
    if mechanism == "direct":
        x = rng.randrange(2) if treatment is None else treatment
        return x, x ^ _bit(rng, 7, 32)
    if mechanism == "confounded":
        cause = rng.randrange(2)
        x = cause ^ _bit(rng, 1, 8) if treatment is None else treatment
        y = cause ^ _bit(rng, 1, 8)
        return x, y
    raise ValueError("unknown mechanism")


def _causal_case(family, rng, case_id, observation_rng):
    # The model sees both observational and randomized counts, with the exact
    # same public schema for the causal and confounded data-generating laws.
    # A twin direct/confounded case shares the *same* observational sample.
    # Its randomized intervention trials separate the two causal laws.
    observations = [(x, x ^ _bit(observation_rng, 7, 32))
                    for x in (observation_rng.randrange(2) for _ in range(32))]
    trial0 = [_causal_pair(rng, family, treatment=0)[1] for _ in range(12)]
    trial1 = [_causal_pair(rng, family, treatment=1)[1] for _ in range(12)]
    return {
        "case_id": case_id,
        "public": {"task_type": "causal_trial", "observational_count": len(observations),
                   "observational_equal": sum(x == y for x, y in observations),
                   "randomized": {"do0_y1": sum(trial0), "do1_y1": sum(trial1),
                                  "n0": 12, "n1": 12},
                   "decision": "Does changing the fictional signal itself causally improve the downstream outcome?",
                   "options": ["authorize", "withhold"]},
        "grader": {"mechanism": family, "optimal_action": "authorize" if family == "direct" else "withhold",
                   "observed_truth": int(family == "direct")},
    }


def _report(rng, z, mask, q, root):
    truth = (z & mask).bit_count() & 1
    observation = truth if _bit(rng, q.numerator, q.denominator) else 1-truth
    return {"root": root, "mask": mask, "value": observation, "reliability": str(q)}


def _parity_case(rng, case_id):
    z = rng.randrange(1 << 10)
    r = _report(rng, z, MASK, Q(3, 4), f"{case_id}-joint-source")
    posterior = _posterior(_prior(), [r])
    if _marginal(posterior, 0) != Q(1, 2) or _marginal(posterior, 1) != Q(1, 2):
        raise AssertionError("parity evidence changed an individual marginal")
    return {"case_id": case_id,
            "public": {"task_type": "belief_correlation", "report": r,
                       "first_order": ["1/2", "1/2"],
                       "question": "Is the hidden pair in agreement?", "options": ["agree", "disagree"]},
            "grader": {"observed_truth": int((z & MASK).bit_count() % 2 == 0)}}


def _provenance_case(rng, case_id):
    z = rng.randrange(1 << 10)
    reports = [_report(rng, z, 1, Q(3, 4), f"{case_id}-root-a")]
    # Replayed relays have the SAME root id; they must not multiply evidence.
    reports.extend(dict(reports[0]) for _ in range(2))
    if rng.randrange(2):
        reports.append(_report(rng, z, 1, Q(3, 4), f"{case_id}-independent-audit"))
    posterior = _posterior(_prior(), reports)
    p = _marginal(posterior, 0)
    return {"case_id": case_id,
            "public": {"task_type": "source_provenance", "reports": reports,
                       "decision_threshold": "17/20", "options": ["endorse", "audit"],
                       "question": "Has independent evidence met the fictional endorsement threshold?"},
            "grader": {"observed_truth": z & 1,
                       "optimal_action": "endorse" if p >= Q(17,20) else "audit"}}


def generate_case(family, root, index):
    if family not in FAMILIES or index < 0:
        raise ValueError("invalid generator family / case")
    rng = _rng(SCHEMA, family, root, index)
    kind = "causal_trial" if family in ("direct", "confounded") else family
    anonymous = hashlib.sha256(f"{SCHEMA}|{family}|{root}|{index}".encode()).hexdigest()[:16]
    cid = f"{kind}-{anonymous}"
    if family in ("direct", "confounded"):
        return _causal_case(family, rng, cid, _rng(SCHEMA, "matched_observations", root, index))
    if family == "p2_parity":
        return _parity_case(rng, cid)
    return _provenance_case(rng, cid)


def public_prompt(case):
    """Model-facing prompt omits generator mechanism, hidden bits and gold action."""
    pub = case["public"]
    typ = pub["task_type"]
    if typ == "causal_trial":
        t = pub["randomized"]
        story = ("In a fictional chamber, signal X and outcome Y are correlated. "
                 "An observational sample has " + str(pub["observational_count"]) +
                 " observations with X=Y in " + str(pub["observational_equal"]) +
                 " of them. A RANDOMIZED intervention set X=0 in " + str(t["n0"]) +
                 " trials and saw Y=1 in " + str(t["do0_y1"]) +
                 "; it set X=1 in " + str(t["n1"]) +
                 " trials and saw Y=1 in " + str(t["do1_y1"]) +
                 ". Decide whether to authorize an action on X as causally effective, "
                 "accounting for sampling uncertainty and possible common causes.")
    elif typ == "belief_correlation":
        r=pub["report"]
        story=("Two hidden fictional actors Z0 and Z1 each have first-order "
               "marginal probability 1/2 of approval. An independent source "
               +r["root"]+" reports XOR(Z0,Z1)="+str(r["value"])+
               " with probability-of-correctness "+r["reliability"]+
               ". Infer their second-order relationship and choose whether "
               "their underlying binary dispositions agree.")
    else:
        reports=[{k:r[k] for k in ("root","value","reliability")}
                 for r in pub["reports"]]
        story=("A fictional official's hidden proposition Z0 has prior probability "
               "1/2. Reports describe Z0 directly. Repeated relays with the SAME "
               "source root are the same observation. Independent audits have "
               "distinct roots. Evidence: "+json.dumps(reports,sort_keys=True)+
               ". An endorsement requires posterior P(Z0=1)>=17/20. "
               "Choose endorse or audit using independent provenance.")
    return (story+"\nRespond only with a JSON object having action (one of "
            +json.dumps(pub["options"])+") and belief_probability (number from 0 to 1).")


def public_task(case):
    pub=case["public"]
    result={"task_id":case["case_id"],"schema":SCHEMA,
            "task_type":pub["task_type"],"prompt":public_prompt(case),"options":pub["options"]}
    if any(key in json.dumps(result) for key in ('"grader"','"mechanism"','"optimal_action"','"observed_truth"')):
        raise AssertionError("private grader field leaked")
    return result


def export_development_tasks(path, *, roots=64, cases_per_root=8,
                             seed_namespace="hgw05-development-v1"):
    """Public developer tasks only. No sealed root generation or private labels."""
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8") as stream:
        for family in FAMILIES:
            for ri in range(roots):
                group="causal_twin" if family in ("direct","confounded") else family
                root=f"{seed_namespace}-{group}-{ri:04d}"
                for i in range(cases_per_root):
                    case=generate_case(family,root,i)
                    stream.write(json.dumps(public_task(case),sort_keys=True)+"\n")
    return path


def _trial_posterior(public, swap=False):
    t = public["randomized"]
    y0, y1 = t["do0_y1"], t["do1_y1"]
    if swap:
        y0, y1 = y1, y0
    n0, n1 = t["n0"], t["n1"]
    direct = Q(7,32)**y0 * Q(25,32)**(n0-y0) * Q(25,32)**y1 * Q(7,32)**(n1-y1)
    confounded = Q(1,2)**(n0+n1)
    return direct/(direct+confounded)


def _inclinations(public, posterior, *, reverse_intervention=False):
    """Declared 2-response bounded inclination, kept separate from graded choice."""
    kind = public["task_type"]
    if kind == "causal_trial":
        trial = public["randomized"]
        delta = Q(trial["do1_y1"], trial["n1"]) - Q(trial["do0_y1"], trial["n0"])
        if reverse_intervention:
            delta = -delta
        association = 2*Q(public["observational_equal"], public["observational_count"])-1
        f = Q(21,100)*delta + Q(2,100)*association - Q(7,100) + Q(2,100)*delta*association
    elif kind == "belief_correlation":
        moment = 2*posterior-1
        p1_diff = Q(public["first_order"][0])-Q(public["first_order"][1])
        f = Q(25,100)*moment + Q(4,100)*p1_diff + Q(3,100)*moment*p1_diff
    else:
        signal = 2*posterior-1
        independent = int(any("independent-audit" in r["root"] for r in public["reports"]))
        f = Q(20,100)*signal - Q(13,100) + Q(1,100)*independent
    if abs(f) > Q(34,100):
        raise AssertionError("inclination exceeded the authored L1 bound")
    return (Q(1,2)+f, Q(1,2)-f)


def policy_result(case, arm):
    """Return a matched exact policy outcome plus the calibrated belief forecast.

    These are *programmed algorithmic controls*, not tested neural agents.
    """
    public, grader = case["public"], case["grader"]
    kind = public["task_type"]
    if kind == "causal_trial":
        prob = (_trial_posterior(public, arm == "sham") if arm != "baseline" else Q(1,2))
        inclination = _inclinations(public, prob, reverse_intervention=arm == "sham")
        if arm == "baseline":
            action = "authorize" if Q(public["observational_equal"], public["observational_count"]) >= Q(2,3) else "withhold"
        else:
            action = "authorize" if inclination[0] > inclination[1] else "withhold"
        success = int(action == grader["optimal_action"])
    elif kind == "belief_correlation":
        # Infer second-order joint belief from public parity evidence; first-
        # order marginals remain 1/2 and are uninformative for this decision.
        moment = _pair_moment(_posterior(_prior(), [public["report"]]))
        prob_agree = Q(1,2) if arm == "baseline" else (1+moment)/2
        if arm == "sham":
            prob_agree = 1-prob_agree
        prob = prob_agree
        inclination = _inclinations(public, prob)
        action = "agree" if (inclination[0] > inclination[1] or
                             (inclination[0] == inclination[1] and arm == "baseline")) else "disagree"
        success = int((action == "agree") == bool(grader["observed_truth"]))
    else:
        # Repetition-naive arm makes the same claim three times, falsely
        # upgrading it to three independent roots. The source-aware arm dedups.
        posterior = _posterior(_prior(), public["reports"], naive_replays=arm == "baseline")
        prob = _marginal(posterior, 0)
        if arm == "sham":
            # Matched null: an unrelated report has no evidential path to Z0.
            posterior = _posterior(_prior(), public["reports"])
            prob = _marginal(posterior, 0)
        inclination = _inclinations(public, prob)
        action = "endorse" if inclination[0] > inclination[1] else "audit"
        success = int(action == grader["optimal_action"])
    return {"task_success": success, "legal_action": 1, "critical_action": 0,
            "belief_probability": str(prob), "action": action,
            "inclination_scores": list(map(str, inclination))}


def _root_bootstrap(effects, label, n_resamples=2000):
    """Descriptive cluster-level interval; do not use it as exact coverage."""
    vals = [float(Q(x["paired_effect"])) for x in effects]
    rng = _rng(SCHEMA, "cluster-bootstrap", label)
    means = sorted(sum(vals[rng.randrange(len(vals))] for _ in vals) / len(vals)
                   for _ in range(n_resamples))
    return [round(means[int(0.025*n_resamples)], 5),
            round(means[min(n_resamples-1,int(0.975*n_resamples))], 5)]


def run_development(*, roots=64, cases_per_root=8, seed_namespace="hgw05-development-v1"):
    if roots < 2 or cases_per_root < 1:
        raise ValueError("at least two roots and one case per root")
    rows = []
    by_family = {}
    for family in FAMILIES:
        outcomes = Counter()
        margin_sum = Q(0)
        effect_rows = []
        root_briers = defaultdict(list)
        for root_index in range(roots):
            root_group = "causal_twin" if family in ("direct", "confounded") else family
            root = f"{seed_namespace}-{root_group}-{root_index:04d}"
            successes = Counter()
            for i in range(cases_per_root):
                c = generate_case(family, root, i)
                scores = {arm: policy_result(c, arm) for arm in ("candidate", "baseline", "sham")}
                outcomes.update({arm: scores[arm]["task_success"] for arm in scores})
                outcomes["candidate_prefers_first"] += int(Q(scores["candidate"]["inclination_scores"][0]) > Q(1,2))
                margin_sum += abs(Q(scores["candidate"]["inclination_scores"][0]) - Q(1,2))
                for arm in scores:
                    successes[arm] += scores[arm]["task_success"]
                    root_briers[arm].append((root, (Q(scores[arm]["belief_probability"]) - c["grader"]["observed_truth"])**2))
                rows.append({"root_id": root, "case_id": c["case_id"],
                             "observed_truth": c["grader"]["observed_truth"], **scores})
            d = Q(successes["candidate"]-successes["baseline"], cases_per_root)
            # This is a *structural* sham check: changing a separate, unused
            # source leaves the candidate choice invariant. Neural shams
            # require their own observed paired outcomes.
            effect_rows.append({"unit_id": root, "paired_effect": str(d), "sham_effects": ["0"]})
        n = roots*cases_per_root
        by_family[family] = {
            "independent_development_roots": roots, "cases": n,
            "success": {arm: outcomes[arm] for arm in ("candidate", "baseline", "sham")},
            "candidate_first_preference": outcomes["candidate_prefers_first"],
            "mean_abs_inclination_margin": str(margin_sum/n),
            "paired_effect_mean": str(sum((Q(x["paired_effect"]) for x in effect_rows), Q(0))/roots),
            "root_bootstrap_ci95_descriptive": _root_bootstrap(effect_rows, family),
            "brier_macro": {arm: round(float(sum((loss for _, loss in root_briers[arm]), Q(0))/n), 6)
                            for arm in ("candidate", "baseline", "sham")},
            "evalmath_pilot": {
                "schema_version": 1, "experiment_id": f"HGW05-{family.upper()}-DEVELOPMENT",
                "independent_unit": "generator world root", "alpha": ALPHA,
                "scientific_min_effect": "0.10", "measurement_resolution": str(Q(1,cases_per_root)),
                "target_effect": "0.20", "planned_comparisons": len(FAMILIES)+1,
                "sham_quantile": "0.95", "sham_confidence": "0.95",
                "confirm_units_planned": 64,
                "pilot_from_development_only": True,
                "heldout_sealed": False, "units_independent": True,
                "pilot": effect_rows,
            },
        }
    # Twin causal laws share an observationally matched independent root, so
    # evaluate the combined discrimination effect per root, not 2N cases.
    direct = by_family["direct"]["evalmath_pilot"]
    confounded = by_family["confounded"]["evalmath_pilot"]
    twin_pilot = []
    for a, b in zip(direct["pilot"], confounded["pilot"]):
        if a["unit_id"] != b["unit_id"]:
            raise AssertionError("causal twins lost their paired root identity")
        twin_pilot.append({"unit_id": a["unit_id"],
                           "paired_effect": str((Q(a["paired_effect"])+Q(b["paired_effect"]))/2),
                           "sham_effects": ["0"]})
    twin_manifest = dict(direct)
    twin_manifest.update(experiment_id="HGW05-CAUSAL-TWINS-DEVELOPMENT",
                         measurement_resolution=str(Q(1, 2*cases_per_root)), pilot=twin_pilot)
    # Across causal twins, the same root_id is one shared independent unit.
    if len({r["root_id"] for r in rows}) != roots*(len(FAMILIES)-1):
        raise AssertionError("independence roster reused unexpectedly")
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"schema": SCHEMA, "evidence_class": "synthetic algorithmic development controls only",
            "generator_roster": {"namespace":seed_namespace, "roots_per_family":roots,
                                 "cases_per_root":cases_per_root, "confirmation_roots_generated":0},
            "observational_law": {k:str(v) for k,v in observational_law().items()},
            "total_independent_development_roots": roots*(len(FAMILIES)-1),
            "total_case_rows": len(rows), "rows_sha256": digest,
            "families": by_family,
            "primary_causal_twin_evalmath_pilot": twin_manifest,
            "primary_causal_twin_effect_mean": str(sum((Q(x["paired_effect"]) for x in twin_pilot), Q(0))/roots),
            "primary_causal_twin_bootstrap_ci95_descriptive": _root_bootstrap(twin_pilot, "causal_twin"),
            "warnings": ["Same seed root across cases is one cluster.",
                         "These deterministic, explicitly privileged controls are not learned model performance.",
                         "Pilot is unsealed by design; new confirmation roots must be registered and generated elsewhere."]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--roots", type=int, default=64)
    ap.add_argument("--cases-per-root", type=int, default=8)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--namespace", default="hgw05-development-v1")
    ap.add_argument("--public-tasks", type=Path,
                    help="write model-facing development JSONL with no grader labels")
    args = ap.parse_args()
    report = run_development(roots=args.roots, cases_per_root=args.cases_per_root, seed_namespace=args.namespace)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.public_tasks:
        export_development_tasks(args.public_tasks,roots=args.roots,
                                 cases_per_root=args.cases_per_root,
                                 seed_namespace=args.namespace)
    print(f"HGW05: {report['total_independent_development_roots']} dev roots, "
          f"{report['total_case_rows']} cases, sha256={report['rows_sha256']}")


if __name__ == "__main__":
    main()
