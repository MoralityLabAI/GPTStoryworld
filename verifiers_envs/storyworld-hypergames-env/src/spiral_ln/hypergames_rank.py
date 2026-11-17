"""HG-05: registered high-dimensional multi-goal CPU benchmark.

A supervised feature-library selection experiment, not a model or live game.
All sample masks are public synthetic development data, disjoint between
training, calibration and testing. No HG-03 private evaluation is consulted.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from fractions import Fraction as Q
from pathlib import Path
from random import Random

from spiral_ln.evaluation_hypergames_rank import deficiency, rank

VERSION = "HG-05/interaction-rank-v1"
COHORTS = ("core_140", "padded_512", "native_512", "padded_1024", "native_1024")
RANKS = (1, 2, 4, 8, 16)
POOLS = ("fixed", "ambient")
TRAIN_SIZES = (4, 8, 16)
SEED_START = 2026111700
SEED_COUNT = 24
N_CAL = 32
N_TEST = 64
N_RANDOM = 100
N_DATA = 16 + N_CAL + N_TEST
MASK_CAL = (1 << N_CAL) - 1
MASK_TEST = (1 << N_TEST) - 1


def spec(cohort: str) -> tuple[int, str]:
    if cohort not in COHORTS:
        raise ValueError("unknown cohort")
    dim = 140 if cohort == "core_140" else 512 if "512" in cohort else 1024
    family = "core" if cohort.startswith(("core_", "padded_")) else "native:" + str(dim)
    return dim, family


def sample_vectors(seed: int, dim: int) -> tuple[int, ...]:
    """Same low d bits for every ambient width; independent split identifiers."""
    if type(seed) is not int or type(dim) is not int or dim not in (140, 512, 1024):
        raise ValueError("invalid seed or dimension")
    return tuple(Random(f"HG05:data:v1:{seed}:{section}:{i}").getrandbits(1024) & ((1 << dim) - 1)
                 for section, length in (("train", 16), ("cal", N_CAL), ("test", N_TEST))
                 for i in range(length))


def goal_masks(seed: int, cohort: str, k: int) -> tuple[int, ...]:
    if type(k) is not int or k not in RANKS:
        raise ValueError("unsupported rank")
    d, family = spec(cohort)
    base = 140 if family == "core" else d
    shuffled = Random(f"HG05:goal:v1:{seed}:{family}:{k}").sample(range(base), 6*k)
    goals = tuple(sum(1 << i for i in shuffled[6*j:6*(j+1)]) for j in range(k))
    assert rank(goals, d) == k
    return goals


def candidate_library(seed: int, cohort: str, k: int, pool: str,
                      include_targets: bool = True) -> tuple[int, ...]:
    if pool not in POOLS:
        raise ValueError("invalid candidate pool")
    d, family = spec(cohort)
    base = (140 if pool == "fixed" and family == "core" else d)
    # For padded core, fixed pool and shuffle are independent of ambient width.
    pool_family = (family if pool == "fixed" else f"{family}:ambient:{d}")
    goals = goal_masks(seed, cohort, k)
    decoy_count = (4*k if pool == "fixed" else max(4*k, d//8))
    wanted = k + decoy_count
    out = list(goals) if include_targets else []
    seen = set(goals)
    rng = Random(f"HG05:candidate:v1:{seed}:{pool_family}:{k}")
    while len(out) < wanted:
        bits = rng.sample(range(base), 6)
        mask = sum(1 << i for i in bits)
        if mask not in seen:
            seen.add(mask)
            out.append(mask)
    rng2 = Random(f"HG05:library-order:v1:{seed}:{pool_family}:{k}:{int(include_targets)}")
    rng2.shuffle(out)
    return tuple(out)


def signatures(rows: tuple[int, ...], samples: tuple[int, ...]) -> dict[int, int]:
    return {mask: sum((((x & mask).bit_count() & 1) << i) for i, x in enumerate(samples))
            for mask in rows}


def score_signed(feature_sig: int, target_sig: int, ntrain: int) -> tuple[int, int]:
    wrong = ((feature_sig ^ target_sig) & ((1 << ntrain) - 1)).bit_count()
    # Prefer no complement at a tie; all signed fitters follow same rule.
    return (wrong, 0) if wrong <= ntrain - wrong else (ntrain - wrong, 1)


def fit_basis(dictionary: tuple[int, ...], feat: dict[int, int],
              targets: tuple[int, ...], truth: dict[int, int], ntrain: int,
              seed: int, shuffle_labels: bool = False) -> tuple[int, ...]:
    """Greedy independent rank-k basis; train labels only, deterministic ties."""
    if type(ntrain) is not int or ntrain not in TRAIN_SIZES:
        raise ValueError("unregistered train size")
    selection = []
    rng = Random(f"HG05:selection-order:v1:{seed}:{len(dictionary)}:{ntrain}:{shuffle_labels}")
    order = list(dictionary)
    rng.shuffle(order)
    for j, target in enumerate(targets):
        label = truth[target]
        if shuffle_labels:
            perm = list(range(ntrain))
            Random(f"HG05:label-shuffle:v1:{seed}:{j}:{ntrain}").shuffle(perm)
            label = sum((((label >> perm[i]) & 1) << i) for i in range(ntrain))
        scored = sorted((score_signed(feat[m], label, ntrain)[0], index, m)
                        for index, m in enumerate(order))
        for _, _, mask in scored:
            if rank((*selection, mask), max(mask.bit_length(), *(s.bit_length() for s in selection), 1)) == len(selection) + 1:
                selection.append(mask)
                break
        else:
            raise ValueError("dictionary lacks rank-k independent candidates")
    return tuple(selection)


def random_bases(dictionary: tuple[int, ...], k: int, d: int, seed: int,
                 cohort: str, pool: str, count: int = N_RANDOM):
    """Registered rank-matched random set of bases, shared across train sizes."""
    if count < 1 or type(count) is not int:
        raise ValueError("positive random basis count required")
    fam = spec(cohort)[1]
    key = f"HG05:random-basis:v1:{seed}:{fam}:{pool}:{k}:{d if pool == 'ambient' else 140}"
    rng = Random(key)
    for _ in range(count):
        rows = list(dictionary)
        rng.shuffle(rows)
        selected = []
        for mask in rows:
            if rank((*selected, mask), d) > len(selected):
                selected.append(mask)
            if len(selected) == k:
                break
        if len(selected) != k:
            raise ValueError("candidate dictionary rank too small")
        yield tuple(selected)


def predict(fitted: tuple[int, ...], feat: dict[int, int], targets: tuple[int, ...],
            truth: dict[int, int], ntrain: int, shuffle_labels: bool = False,
            seed: int = 0, direct_oracle: bool = False) -> dict:
    """One-feature-plus-sign decoder; privileged oracle decodes targets directly."""
    joint_errors = 0
    bit_errors = 0
    for j, target in enumerate(targets):
        label = truth[target]
        if shuffle_labels:
            perm = list(range(ntrain))
            Random(f"HG05:label-shuffle:v1:{seed}:{j}:{ntrain}").shuffle(perm)
            label = sum((((label >> perm[i]) & 1) << i) for i in range(ntrain))
        # Readout may choose any of the k observed features for each output bit.
        if direct_oracle:
            if tuple(fitted) != tuple(targets):
                raise ValueError("privileged oracle requires exact goal basis")
            invert, chosen = 0, target
        else:
            scores = [(score_signed(feat[m], label, ntrain)[0], i,
                       score_signed(feat[m], label, ntrain)[1], m)
                      for i, m in enumerate(fitted)]
            _, _, invert, chosen = min(scores)
        error_bits = feat[chosen] ^ truth[target]
        if invert:
            error_bits ^= (1 << N_DATA) - 1
        joint_errors |= error_bits
        bit_errors += ((error_bits >> (16 + N_CAL)) & MASK_TEST).bit_count()
    cal_correct = N_CAL - ((joint_errors >> 16) & MASK_CAL).bit_count()
    test_correct = N_TEST - ((joint_errors >> (16 + N_CAL)) & MASK_TEST).bit_count()
    # Laplace-calibrated action is chosen using ONLY calibration examples.
    release = Q(cal_correct + 1, N_CAL + 2) > Q(3, 5)
    utility_if_released = 25 * Q(test_correct, N_TEST) - 15
    return {"test_correct": test_correct, "test_bit_correct": len(targets)*N_TEST - bit_errors,
            "cal_correct": cal_correct, "release": release,
            "utility": utility_if_released if release else Q(0),
            "always_release_utility": utility_if_released,
            "unsafe": (N_TEST-test_correct) if release else 0}


def evaluate_condition(seed: int, cohort: str, k: int, pool: str) -> list[dict]:
    d, _family = spec(cohort)
    goals = goal_masks(seed, cohort, k)
    dictionary = candidate_library(seed, cohort, k, pool)
    nogold = candidate_library(seed, cohort, k, pool, include_targets=False)
    samples = sample_vectors(seed, d)
    feature_sigs = signatures(tuple(set(dictionary + nogold + goals)), samples)
    truth = {mask: feature_sigs[mask] for mask in goals}
    bases = tuple(random_bases(dictionary, k, d, seed, cohort, pool))
    random_deficiencies = tuple(deficiency(b, goals, d) for b in bases)
    if len(bases) != N_RANDOM or any(rank(b, d) != k for b in bases):
        raise AssertionError("rank-matched random controls failed")
    rows = []
    for n in TRAIN_SIZES:
        choices = {
            "oracle_task": goals,
            "task_only_supervised": fit_basis(dictionary, feature_sigs, goals, truth, n, seed),
            "task_only_no_gold_dictionary": fit_basis(nogold, feature_sigs, goals, truth, n, seed),
            "label_shuffled_supervised": fit_basis(dictionary, feature_sigs, goals, truth, n, seed, True),
        }
        results = {}
        for arm, basis in choices.items():
            r = predict(basis, feature_sigs, goals, truth, n,
                        shuffle_labels=arm=="label_shuffled_supervised", seed=seed,
                        direct_oracle=arm=="oracle_task")
            r["deficiency"] = deficiency(basis, goals, d)
            r["basis_rank"] = rank(basis, d)
            r["oracle_success"] = str(Q(1, 1 << r["deficiency"]))
            results[arm] = r
        random_scores = [predict(b, feature_sigs, goals, truth, n)["test_correct"] for b in bases]
        matched = results["task_only_supervised"]["test_correct"]
        counts = defaultdict(int)
        for score in random_scores: counts[score] += 1
        random_mean = Q(sum(random_scores), N_RANDOM * N_TEST)
        task_test = Q(matched, N_TEST)
        for arm, r in results.items():
            rows.append({
                "seed": seed, "cohort": cohort, "dimension": d, "goal_rank": k,
                "pool": pool, "train_n": n, "arm": arm,
                "basis_rank": r["basis_rank"], "deficiency": r["deficiency"],
                "oracle_success": r["oracle_success"],
                "test_correct": r["test_correct"], "test_bit_correct": r["test_bit_correct"],
                "cal_correct": r["cal_correct"], "release": int(r["release"]),
                "true_utility": str(r["utility"]),
                "always_release_utility": str(r["always_release_utility"]),
                "false_accept": r["unsafe"],
                "random_mean_success": str(random_mean),
                "task_minus_random_mean": str(task_test - random_mean),
                "random_rank_based_p": str(Q(1 + sum(x >= matched for x in random_scores), N_RANDOM+1)),
                "random_distinct_bases": len(set(bases)),
                "random_success_hist": json.dumps(sorted(counts.items())),
                "random_deficiency_hist": json.dumps(sorted((h, random_deficiencies.count(h)) for h in set(random_deficiencies))),
            })
    return rows


def run(reg: dict | None = None, seeds: tuple[int, ...] | None = None,
        cohorts: tuple[str, ...] | None = None, ranks: tuple[int, ...] | None = None,
        pools: tuple[str, ...] | None = None) -> list[dict]:
    """Registry-locked full census; smaller subsets are for tests only."""
    if reg is not None:
        if reg["schema"] != VERSION or reg["seed_count"] != SEED_COUNT or \
            reg["random_rank_matched_bases"] != N_RANDOM or \
            reg["calibration_examples"] != N_CAL or reg["test_examples"] != N_TEST:
            raise ValueError("registration mismatch")
        if tuple(reg["cohorts"]) != COHORTS or tuple(reg["goal_ranks"]) != RANKS or \
            tuple(reg["feature_pools"]) != POOLS or tuple(reg["training_examples"]) != TRAIN_SIZES:
            raise ValueError("registration grid changed")
    result=[]
    for seed in (seeds if seeds is not None else tuple(range(SEED_START, SEED_START+SEED_COUNT))):
        for cohort in (cohorts if cohorts is not None else COHORTS):
            for k in (ranks if ranks is not None else RANKS):
                for pool in (pools if pools is not None else POOLS):
                    result.extend(evaluate_condition(seed, cohort, k, pool))
    return result


def report(rows: list[dict]) -> dict:
    """Per-arm group means in exact rational arithmetic; seed is the replicate."""
    grouped = defaultdict(list)
    for r in rows:
        grouped[(r["cohort"], r["goal_rank"], r["pool"], r["train_n"], r["arm"])].append(r)
    groups = []
    for key, members in sorted(grouped.items()):
        total = len(members)
        groups.append({"cohort":key[0],"goal_rank":key[1],"pool":key[2],"train_n":key[3],"arm":key[4],
            "seeds":total,
            "mean_test_success":str(Q(sum(r["test_correct"] for r in members),N_TEST*total)),
            "mean_bit_accuracy":str(Q(sum(r["test_bit_correct"] for r in members),N_TEST*key[1]*total)),
            "mean_utility":str(sum((Q(r["true_utility"]) for r in members),Q(0))/total),
            "false_accept":sum(r["false_accept"] for r in members),
            "release_seeds":sum(r["release"] for r in members),
            "mean_deficiency":str(Q(sum(r["deficiency"] for r in members), total))})
    # A gate is evaluated once per seed, not once per example.
    passes={}
    for k in RANKS:
        q=[r for r in rows if r["cohort"]=="core_140" and r["pool"]=="fixed"
           and r["train_n"]==16 and r["goal_rank"]==k and r["arm"]=="task_only_supervised"]
        passes[str(k)]={"task_beats_random_seed_count":sum(Q(r["task_minus_random_mean"])>0 for r in q),
                        "total_seeds":len(q),
                        "passes_20_of_24_gate": len(q)==SEED_COUNT and sum(Q(r["task_minus_random_mean"])>0 for r in q)>=20}
    padded_ok=True; comparisons=0
    keyed={(r["seed"],r["cohort"],r["goal_rank"],r["pool"],r["train_n"],r["arm"]):r for r in rows}
    for r in rows:
        if r["cohort"]!="core_140" or r["pool"]!="fixed" or r["arm"]!="task_only_supervised":continue
        for cohort in ("padded_512", "padded_1024"):
            other=keyed.get((r["seed"],cohort,r["goal_rank"],r["pool"],r["train_n"],r["arm"]))
            if other:
                comparisons+=1
                padded_ok &= all(r[x]==other[x] for x in ("test_correct","test_bit_correct","cal_correct","true_utility","release","deficiency"))
    return {"schema":"HG-05/summary-v1","evidence":"synthetic CPU exact binary-feature dictionary; no neural evaluation",
            "counts":{"seed_arm_rows":len(rows),"random_bases_per_seed_condition":N_RANDOM,
                     "random_base_draws":len({(r['seed'],r['cohort'],r['goal_rank'],r['pool']) for r in rows})*N_RANDOM,
                     "matched_padding_comparisons":comparisons},
            "gates":{"all_basis_rank_matched":all(r['basis_rank']==r['goal_rank'] for r in rows),
                     "fixed_pool_padding_invariance":bool(padded_ok),
                     "n16_task_beats_random_20_of_24_each_rank":all(z['passes_20_of_24_gate'] for z in passes.values())},
            "registered_direction_counts":passes,"groups":groups}


def write_seed_csv(rows: list[dict], output_dir: Path) -> list[str]:
    output_dir.mkdir(parents=True,exist_ok=True)
    paths=[]
    for cohort in COHORTS:
        chosen=[r for r in rows if r['cohort']==cohort]
        if not chosen:continue
        out=output_dir/f"hg05_seeds_{cohort}.csv"
        with out.open('w',encoding='utf8',newline='') as f:
            wr=csv.DictWriter(f,fieldnames=list(chosen[0]))
            wr.writeheader();wr.writerows(chosen)
        paths.append(str(out))
    return paths
