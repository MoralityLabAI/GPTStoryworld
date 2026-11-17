"""HG-06: prospectively registered, public CPU compositional-goal discovery.

A k-output goal contains k independent six-sparse GF(2) parities. The public
feature library has only two-sparse component and nuisance rows. Three-feature
XORs can reconstruct the goal; one/two-feature XORs have a structural floor.
The environment never reads the private HG-03 seed manifest or model weights.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
from random import Random

from spiral_ln.evaluation_hypergames_rank import deficiency, rank

VERSION = "HG-06/compositional-parity-v1"
COHORTS = ("core_140", "padded_512", "native_512", "padded_1024", "native_1024")
RANKS = (1, 2, 4, 8)
POOLS = ("fixed", "ambient")
TRAIN_SIZES = (8, 16, 32, 64)
SEED_START = 202611170600
SEED_COUNT = 24
N_CAL = 32
N_TEST = 128
N_RANDOM = 100
N_TRAIN_MAX = 64
N_DATA = N_TRAIN_MAX + N_CAL + N_TEST
ALL_DATA_MASK = (1 << N_DATA) - 1
CAL_MASK = ((1 << N_CAL) - 1) << N_TRAIN_MAX
TEST_MASK = ((1 << N_TEST) - 1) << (N_TRAIN_MAX + N_CAL)
ARMS = ("privileged_goal_oracle", "task_xor1", "task_xor2", "task_xor3",
        "missing_component_xor3", "shuffled_label_xor3")


def cohort_spec(cohort: str) -> tuple[int, str]:
    if cohort not in COHORTS:
        raise ValueError("unregistered cohort")
    d = 140 if cohort == "core_140" else 512 if "512" in cohort else 1024
    family = "core" if cohort.startswith(("core_", "padded_")) else f"native_{d}"
    return d, family


def _bits(rows: tuple[int, ...], d: int) -> None:
    if any(type(v) is not int or v <= 0 or v.bit_length() > d for v in rows):
        raise ValueError("feature outside ambient coordinate bounds")


@lru_cache(maxsize=512)
def instance(seed: int, cohort: str, k: int, pool: str):
    """Returns dimension, target masks, original component pairs, full/ablated dictionaries."""
    if type(seed) is not int or k not in RANKS or type(k) is not int or pool not in POOLS:
        raise ValueError("invalid seed, rank or pool")
    d, family = cohort_spec(cohort)
    goal_dim = 140 if family == "core" else d
    rng = Random(f"HG06:goals:v1:{seed}:{family}:{k}")
    positions = rng.sample(range(goal_dim), 6 * k)
    fragments = tuple(tuple((1 << positions[6*j + 2*t]) | (1 << positions[6*j + 2*t + 1])
                            for t in range(3)) for j in range(k))
    targets = tuple(a ^ b ^ c for a, b, c in fragments)
    reserved = set(positions)
    decoy_dim = (140 if pool == "fixed" and family == "core" else d)
    if len(set(positions)) != 6*k or rank(targets, d) != k:
        raise AssertionError("goal rank construction failed")
    nuisance = [i for i in range(decoy_dim) if i not in reserved]
    if len(nuisance) < 2:
        raise ValueError("insufficient independent nuisance coordinates")
    n_decoys = 6 * k if pool == "fixed" else max(6*k, d // 32)
    family_key = family if pool == "fixed" else family + f":{d}"
    dec_rng = Random(f"HG06:decoys:v1:{seed}:{family_key}:{k}:{pool}")
    decoys: list[int] = []
    used = {m for trio in fragments for m in trio}
    while len(decoys) <= n_decoys + k:
        a,b = dec_rng.sample(nuisance, 2)
        mask = (1 << a) | (1 << b)
        if mask not in used:
            used.add(mask)
            decoys.append(mask)
    gold = [m for trio in fragments for m in trio]
    dictionary = gold + decoys[:n_decoys]
    ablated = [m for trio in fragments for m in trio[:2]] + decoys[:n_decoys + k]
    Random(f"HG06:shuffle:full:v1:{seed}:{family_key}:{k}:{pool}").shuffle(dictionary)
    Random(f"HG06:shuffle:ablated:v1:{seed}:{family_key}:{k}:{pool}").shuffle(ablated)
    full, missing = tuple(dictionary), tuple(ablated)
    if len(full) != len(missing) or len(set(full)) != len(full):
        raise AssertionError("dictionary mismatch")
    _bits(full, d)
    _bits(missing, d)
    if any(x.bit_count() != 2 for x in full + missing):
        raise AssertionError("dictionary contains an exact six-bit goal row")
    if deficiency(full, targets, d) or deficiency(missing, targets, d) != k:
        raise AssertionError("compositional capacity/ablation rank invalid")
    return d, targets, fragments, full, missing


@lru_cache(maxsize=512)
def samples(seed: int, dimension: int) -> tuple[int, ...]:
    if type(seed) is not int or dimension not in (140,512,1024):
        raise ValueError("invalid source vector request")
    return tuple(Random(f"HG06:data:v1:{seed}:{part}:{i}").getrandbits(1024) & ((1 << dimension) - 1)
                 for part, n in (("train",N_TRAIN_MAX),("cal",N_CAL),("test",N_TEST))
                 for i in range(n))


def signatures(masks: tuple[int, ...], states: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(((x & m).bit_count() & 1) << j for j, x in enumerate(states)) for m in masks)


def complement_label(sig: int, label: int, n: int) -> tuple[int,int]:
    wrong = ((sig ^ label) & ((1<<n)-1)).bit_count()
    if wrong <= n-wrong:
        return wrong,0
    return n-wrong,1


@lru_cache(maxsize=8)
def _candidate_combinations(masks: tuple[int, ...], sigs: tuple[int, ...], order: int):
    """Full ordered candidate space, shared across train sizes of one condition."""
    if order not in (1,2,3):
        raise ValueError("unsupported composition order")
    return tuple((tuple(indices), _xor(masks[i] for i in indices),
                  _xor(sigs[i] for i in indices)) for indices in itertools.combinations(range(len(masks)), order))


def _xor(rows):
    v = 0
    for x in rows:
        v ^= x
    return v


def fit(candidates: tuple[tuple[tuple[int,...],int,int], ...], truth_sig: int,
        n: int, shuffled_label: int | None = None) -> tuple[tuple[int,...],int,int,int]:
    """Exhaustive minimum training error, deterministic ties, exact rational bit losses."""
    if n not in TRAIN_SIZES:
        raise ValueError("nonregistered train size")
    label = truth_sig if shuffled_label is None else shuffled_label
    best = None
    mask = (1<<n)-1
    for ids, worldmask, sig in candidates:
        delta = (sig ^ label) & mask
        errors = delta.bit_count()
        signed = (errors, 0) if errors <= n-errors else (n-errors,1)
        value = (signed[0], signed[1], ids)
        if best is None or value < best[0]:
            best = (value,(ids,worldmask,sig,signed[1]))
            if signed[0] == 0 and signed[1] == 0:
                break
    assert best is not None
    return best[1]


def shuffled_training(sig: int, n: int, seed: int, family: str, k: int,
                      j: int, pool: str) -> int:
    perm = list(range(n))
    Random(f"HG06:shuffle-labels:v1:{seed}:{family}:{k}:{j}:{n}:{pool}").shuffle(perm)
    return sum(((sig>>perm[i])&1)<<i for i in range(n))


def random_composite_bases(dictionary: tuple[int,...], sigs: tuple[int,...],
                           dimension: int, k: int, seed: int, family: str, pool: str):
    """Independent random triple-composition choices; enforce rank k on composite rows."""
    rng = Random(f"HG06:random100:v1:{seed}:{family}:{pool}:{k}:{len(dictionary)}")
    triples = _candidate_combinations(dictionary,sigs,3)
    if not triples:
        raise ValueError("no rank-matched triples")
    for _ in range(N_RANDOM):
        chosen=[]
        masks=[]
        for _goal in range(k):
            for attempt in range(1024):
                ids, mask, sig = triples[rng.randrange(len(triples))]
                if rank((*masks, mask),dimension)>len(masks):
                    chosen.append((ids,mask,sig,0))
                    masks.append(mask)
                    break
            else:
                raise AssertionError("100 draw rank matching exhausted")
        yield tuple(chosen)


def _score(pred: tuple[tuple[tuple[int,...],int,int,int],...], true_sigs: tuple[int,...]):
    error = 0
    bit_errors = 0
    predicted_masks=[]
    for (ids, mask, sig, invert), target in zip(pred,true_sigs):
        predicted_masks.append(mask)
        diff = (sig ^ ((ALL_DATA_MASK) if invert else 0)) ^ target
        error |= diff
        bit_errors += ((diff & TEST_MASK) >> (N_TRAIN_MAX+N_CAL)).bit_count()
    calcorrect = N_CAL - ((error & CAL_MASK) >> N_TRAIN_MAX).bit_count()
    testcorrect = N_TEST - ((error & TEST_MASK) >> (N_TRAIN_MAX+N_CAL)).bit_count()
    release = Q(calcorrect+1,N_CAL+2)>Q(3,5)
    q = Q(testcorrect,N_TEST)
    return {
      "test_correct":testcorrect,"bit_correct":len(pred)*N_TEST-bit_errors,
      "cal_correct":calcorrect,"release":int(release),"false_accept":N_TEST-testcorrect if release else 0,
      "utility":25*q-15 if release else Q(0),
      "ungated_utility":25*q-15,
      "predicted_rows":tuple(predicted_masks),
    }


def evaluate_condition(seed:int,cohort:str,k:int,pool:str):
    d, family = cohort_spec(cohort)
    d, targets, fragments, full, ablated=instance(seed,cohort,k,pool)
    states = samples(seed,d)
    sig_full = signatures(full,states)
    sig_missing = signatures(ablated,states)
    target_sig=signatures(targets,states)
    normal_candidates={order:_candidate_combinations(full,sig_full,order) for order in (1,2,3)}
    missing_candidates=_candidate_combinations(ablated,sig_missing,3)
    random_bases=tuple(random_composite_bases(full,sig_full,d,k,seed,
                                            family if pool=="fixed" else family+f":{d}",pool))
    if len(random_bases)!=N_RANDOM or any(rank(tuple(row[1] for row in basis),d)!=k for basis in random_bases):
        raise AssertionError("rank-matched random arms are invalid")
    rows=[]
    for n in TRAIN_SIZES:
        train_mask=(1 << n)-1
        # Candidate fit multiplicities expose finite-sample inverse-goal ambiguity;
        # this count inspects ONLY the registered training prefix.
        multiplicities=Counter(sig & train_mask for _,_,sig in normal_candidates[3])
        train_ambiguities=tuple(multiplicities[t & train_mask] +
                               multiplicities[(t & train_mask)^train_mask]
                               for t in target_sig)
        fits={
          "privileged_goal_oracle": tuple(((),targets[j],target_sig[j],0) for j in range(k)),
          "task_xor1":tuple(fit(normal_candidates[1],t,n) for t in target_sig),
          "task_xor2":tuple(fit(normal_candidates[2],t,n) for t in target_sig),
          "task_xor3":tuple(fit(normal_candidates[3],t,n) for t in target_sig),
          "missing_component_xor3":tuple(fit(missing_candidates,t,n) for t in target_sig),
          "shuffled_label_xor3":tuple(fit(normal_candidates[3],t,n,shuffled_training(t,n,seed,
                                     family,k,j,pool)) for j,t in enumerate(target_sig)),
        }
        measures={arm:_score(pred,target_sig) for arm,pred in fits.items()}
        random_scores=[]
        random_def=[]
        for basis in random_bases:
            signed=[]
            for j,(ids,mask,sig,_) in enumerate(basis):
                error,sign=complement_label(sig,target_sig[j],n)
                signed.append((ids,mask,sig,sign))
            m=_score(tuple(signed),target_sig)
            random_scores.append(m["test_correct"])
            random_def.append(deficiency(tuple(m_[1] for m_ in signed),targets,d))
        random_hist=sorted(Counter(random_scores).items())
        random_mean=Q(sum(random_scores),N_RANDOM*N_TEST)
        tscore=measures["task_xor3"]["test_correct"]
        for arm, s in measures.items():
            rows.append({
              "seed":seed,"cohort":cohort,"dimension":d,"goal_rank":k,"pool":pool,
              "train_n":n,"arm":arm,"feature_pool_size":len(full),
              "test_correct":s["test_correct"],"bit_correct":s["bit_correct"],
              "cal_correct":s["cal_correct"],"release":s["release"],
              "true_utility":str(s["utility"]),"ungated_utility":str(s["ungated_utility"]),
              "false_accept":s["false_accept"],
              "observed_rank":rank(s["predicted_rows"],d),
              "deficiency":deficiency(s["predicted_rows"],targets,d),
              "random_mean_test_accuracy":str(random_mean),
              "task_minus_random_mean":str(Q(tscore,N_TEST)-random_mean),
              "random_rank_p":str(Q(1+sum(v>=tscore for v in random_scores),N_RANDOM+1)),
              "random_distinct_bases":len(set(tuple(row[1] for row in base) for base in random_bases)),
              "random_test_hist":json.dumps(random_hist,separators=(',',':')),
              "random_deficiency_hist":json.dumps(sorted(Counter(random_def).items()),separators=(',',':')),
              "candidate_triples":len(normal_candidates[3]),
              "training_exact_triples_total":sum(train_ambiguities),
              "training_exact_triples_max":max(train_ambiguities),
              "union_bound_spurious":str(min(Q(1),Q(k * (2*len(normal_candidates[3])-1),1<<n))),
            })
    return rows


def run(seeds=None,cohorts=None,ranks=None,pools=None):
    result=[]
    for seed in (tuple(range(SEED_START,SEED_START+SEED_COUNT)) if seeds is None else seeds):
      for cohort in (COHORTS if cohorts is None else cohorts):
        for k in (RANKS if ranks is None else ranks):
          for pool in (POOLS if pools is None else pools):
            result.extend(evaluate_condition(seed,cohort,k,pool))
    return result


def aggregate(rows):
    groups=defaultdict(list)
    for row in rows:
        groups[(row['cohort'],row['goal_rank'],row['pool'],row['train_n'],row['arm'])].append(row)
    grouped=[]
    for (cohort,k,pool,n,arm),part in sorted(groups.items()):
        grouped.append({"cohort":cohort,"goal_rank":k,"pool":pool,"train_n":n,
          "arm":arm,"seeds":len(part),
          "mean_joint_accuracy":str(Q(sum(x['test_correct'] for x in part),N_TEST*len(part))),
          "mean_bit_accuracy":str(Q(sum(x['bit_correct'] for x in part),N_TEST*k*len(part))),
          "mean_true_utility":str(sum((Q(x['true_utility']) for x in part),Q(0))/len(part)),
          "false_accept":sum(x['false_accept'] for x in part),
          "release_seeds":sum(x['release'] for x in part),
          "mean_deficiency":str(Q(sum(x['deficiency'] for x in part),len(part)))})
    key={(r['seed'],r['cohort'],r['goal_rank'],r['pool'],r['train_n'],r['arm']):r for r in rows}
    padcount=0
    padding_ok=True
    for row in rows:
        if row['cohort'] != 'core_140' or row['pool']!='fixed': continue
        for cohort in ('padded_512','padded_1024'):
            other=key[(row['seed'],cohort,row['goal_rank'],row['pool'],row['train_n'],row['arm'])]
            fields=('test_correct','bit_correct','cal_correct','true_utility','release','false_accept','deficiency','observed_rank')
            if any(row[f]!=other[f] for f in fields):padding_ok=False
            padcount+=1
    directions={}
    for k in RANKS:
        good=0
        better=0
        for seed in range(SEED_START,SEED_START+SEED_COUNT):
            t=key[(seed,'core_140',k,'fixed',64,'task_xor3')]
            p=key[(seed,'core_140',k,'fixed',64,'task_xor2')]
            good+=(t['test_correct']==N_TEST)
            better+=(t['test_correct']>p['test_correct'])
        directions[str(k)]={"exact_full_test":good,"beats_xor2":better,
                            "n_seed":SEED_COUNT,"passed":good>=20 and better>=20}
    science={"n64_xor3_exact_and_beats_xor2_20of24_each_rank":all(x['passed'] for x in directions.values()),
             "fixed_pool_padding_identity":padding_ok,
             "oracle_perfect":all(r['test_correct']==N_TEST for r in rows if r['arm']=='privileged_goal_oracle'),
             "all_missing_component_target_deficient":all(r['deficiency']==r['goal_rank'] for r in rows if r['arm']=='missing_component_xor3')}
    return {"schema":"HG-06/compositional-summary-v1",
      "evidence_level":"synthetic CPU finite feature-learner results; no neural model",
      "counts":{"rows":len(rows),"seeds":SEED_COUNT,"conditions":len(rows)//(len(ARMS)*len(TRAIN_SIZES)),
                "random_composite_draws":len(rows)//(len(ARMS)*len(TRAIN_SIZES))*N_RANDOM,
                "padding_matches":padcount},
      "registered_science_gates":science,"directions":directions,"groups":grouped}


def write_csv(rows,destination:Path):
    destination.mkdir(parents=True,exist_ok=True)
    files=[]
    for cohort in COHORTS:
        sub=[row for row in rows if row['cohort']==cohort]
        if not sub:continue
        path=destination/f'hg06_seed_rows_{cohort}.csv'
        with path.open('w',encoding='utf8',newline='') as file:
            writer=csv.DictWriter(file,fieldnames=list(sub[0]))
            writer.writeheader()
            writer.writerows(sub)
        files.append(path)
    return files
