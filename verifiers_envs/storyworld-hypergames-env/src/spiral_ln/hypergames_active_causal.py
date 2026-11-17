"""HG-08: prospective sparse causal-intervention discovery on parity storyworlds.

All target masks are owned by the grader. Policies receive a public problem and
an oracle exposing ONLY the chosen intervention's k-bit causal delta. Queries
are charged one each including recursive searches and singleton certificates.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
from random import Random
from typing import Callable

from spiral_ln.evaluation_hypergames_causal import (
    causal_difference, peel_known, support_certified, information_lower_bound,
)

VERSION = 'HG-08/active-causal-v1'
SEEDS = tuple(range(202611170801, 202611170825))
COHORTS = ('core_140','padded_512','native_512','padded_1024','native_1024')
RANKS = (1,2)
BUDGETS = (64,128,256,512)
POLICIES = ('adaptive_hash','random_singletons','fixed_partition','random_dense')
N_TEST = 256
WIDTH = 6
BUCKETS = 16


def seed_int(*parts: object) -> int:
    label = 'HG08:' + ':'.join(map(str, parts))
    return int.from_bytes(hashlib.sha256(label.encode('utf8')).digest()[:8], 'little')


def cohort_info(cohort: str) -> tuple[int, str]:
    if cohort not in COHORTS:
        raise ValueError('unregistered cohort')
    d = 140 if cohort == 'core_140' else 512 if '512' in cohort else 1024
    family = 'core' if cohort.startswith(('core_', 'padded_')) else 'native'+str(d)
    return d, family


@dataclass(frozen=True)
class PublicProblem:
    seed: int
    cohort: str
    dimension: int
    goal_rank: int
    support_width: int = WIDTH


def make_problem(seed: int, cohort: str, goal_rank: int) -> PublicProblem:
    if type(seed) is not int or goal_rank not in RANKS:
        raise ValueError('invalid public problem')
    return PublicProblem(seed, cohort, cohort_info(cohort)[0], goal_rank)


def _private_goal(problem: PublicProblem) -> tuple[int, ...]:
    d, family = cohort_info(problem.cohort)
    available = 140 if family == 'core' else d
    rng = Random(seed_int('support', problem.seed, family, problem.goal_rank))
    coordinates = rng.sample(range(available), WIDTH*problem.goal_rank)
    return tuple(sum(1 << t for t in coordinates[j*WIDTH:(j+1)*WIDTH])
                 for j in range(problem.goal_rank))


class BudgetExhausted(Exception):
    pass


class InterventionOracle:
    def __init__(self, problem: PublicProblem, budget: int):
        if type(budget) is not int or budget < 0:
            raise ValueError('budget must be nonnegative integer')
        self._problem = problem
        self._private = _private_goal(problem)
        self.budget = budget
        self.calls = 0
        self.transcript = []

    def query(self, coordinate_mask: int) -> tuple[int, ...]:
        if self.calls >= self.budget:
            raise BudgetExhausted()
        answer = causal_difference(self._private, coordinate_mask, self._problem.dimension)
        self.calls += 1
        self.transcript.append((coordinate_mask, answer))
        return answer


@dataclass
class Discovery:
    known: tuple[frozenset[int], ...]
    queries: int
    transcript: tuple[tuple[int, tuple[int, ...]], ...]
    completed: bool
    policy: str

    @property
    def minimum_verified(self) -> int:
        return min(map(len, self.known))


def _mask(indices) -> int:
    return sum(1 << i for i in indices)


def _done(known: list[set[int]]) -> bool:
    return all(len(row) == WIDTH for row in known)


def discover(problem: PublicProblem, budget: int, policy: str) -> Discovery:
    if policy not in POLICIES:
        raise ValueError('unknown policy')
    oracle = InterventionOracle(problem, budget)
    known = [set() for _ in range(problem.goal_rank)]
    verified: dict[int, tuple[int, ...]] = {}
    d = problem.dimension

    def certify_one(index: int):
        if index in verified:
            response = verified[index]
        else:
            response = oracle.query(1 << index)
            verified[index] = response
        for j, hit in enumerate(response):
            if hit:
                known[j].add(index)
                if len(known[j]) > WIDTH:
                    raise AssertionError('more than registered true support size')

    def recover_from_block(items: list[int], j: int, residual: int):
        """Residual parity=1 guarantees at least one as-yet-unfound cause."""
        assert residual == 1 and len(items) > 0
        nodes = items
        while len(nodes) > 1:
            left = nodes[:len(nodes)//2]
            answer = oracle.query(_mask(left))
            correction = sum(i in known[j] for i in left) & 1
            if answer[j] ^ correction:
                nodes = left
            else:
                nodes = nodes[len(nodes)//2:]
        certify_one(nodes[0])
        if nodes[0] not in known[j]:
            raise AssertionError('odd-bucket splitting failed to find a causal coordinate')

    try:
        if policy == 'random_singletons':
            order = list(range(d))
            Random(seed_int('singletons', problem.seed, problem.cohort, problem.goal_rank)).shuffle(order)
            for index in order:
                if _done(known): break
                certify_one(index)
        elif policy in ('adaptive_hash', 'fixed_partition'):
            max_rounds = 32 if policy == 'adaptive_hash' else 1
            for round_idx in range(max_rounds):
                if _done(known): break
                order = list(range(d))
                Random(seed_int('buckets', problem.seed, problem.cohort,
                                problem.goal_rank, round_idx)).shuffle(order)
                partitions = [[] for _ in range(BUCKETS)]
                for n, idx in enumerate(order):
                    partitions[n % BUCKETS].append(idx)
                for bucket in partitions:
                    if _done(known): break
                    block_mask = _mask(bucket)
                    raw = oracle.query(block_mask)
                    # The original delta remains valid as known singleton causes are peeled.
                    while True:
                        residuals = peel_known(raw, block_mask,
                                               tuple(frozenset(v) for v in known), d)
                        choices = [j for j in range(problem.goal_rank)
                                   if residuals[j] and len(known[j]) < WIDTH]
                        if not choices: break
                        recover_from_block(bucket, choices[0], 1)
        else: # Random dense full-rank parity observation baseline.
            pivots: dict[int, tuple[int,int]] = {}
            for qid in range(budget):
                if len(pivots) == d:break
                rng = Random(seed_int('dense',problem.seed,problem.cohort,
                                      problem.goal_rank,qid))
                mask = rng.getrandbits(d)
                answer = oracle.query(mask)
                row, y = mask, sum(v<<j for j,v in enumerate(answer))
                while row:
                    pivot = row.bit_length()-1
                    if pivot in pivots:
                        previous, prev_y = pivots[pivot]
                        row ^= previous; y ^= prev_y
                    else:
                        pivots[pivot] = (row,y)
                        break
            if len(pivots) == d:
                solutions = [0] * problem.goal_rank
                for i in range(d):
                    row, code = pivots[i]
                    rest = row ^ (1 << i)
                    for j in range(problem.goal_rank):
                        if ((code >> j)&1) ^ ((rest & solutions[j]).bit_count()&1):
                            solutions[j] |= 1<<i
                for j,mask in enumerate(solutions):
                    known[j].update(i for i in range(d) if (mask>>i)&1)
                if any(len(k)!=WIDTH for k in known):
                    raise AssertionError('full-rank reconstruction violates known six-sparsity')
                # Verified by full-rank linear system, no singleton probes required.
                for i in range(d):
                    if any(i in known[j] for j in range(problem.goal_rank)):
                        verified[i] = tuple(int(i in row) for row in known)
    except BudgetExhausted:
        pass
    complete = _done(known)
    if complete and policy != 'random_dense':
        if not support_certified(verified, d, problem.goal_rank, WIDTH):
            raise AssertionError('completed support lacks positive singleton transcript')
    return Discovery(tuple(frozenset(row) for row in known), oracle.calls,
                     tuple(oracle.transcript), complete, policy)


@lru_cache(maxsize=512)
def independent_test_masks(problem: PublicProblem, count: int=N_TEST) -> tuple[int,...]:
    if type(count) is not int or count<1: raise ValueError('count must be positive')
    # Generate full 1,024-bit vector before truncating for paired padding invariance.
    rngprefix='test'
    return tuple(Random(seed_int('data',problem.seed,rngprefix,i)).getrandbits(1024) &
                 ((1 << problem.dimension)-1) for i in range(count))



def symbolic_recurrent_code(state: int, known: tuple[frozenset[int],...], dimension: int) -> tuple[int,...]:
    """Exact six-step per-output XOR accumulator after causal support discovery.

    This is a fixed symbolic recurrent *algorithm*, not a learned network.
    """
    if type(state) is not int or state < 0 or state >> dimension:
        raise ValueError('invalid public input state')
    outputs=[]
    for support in known:
        accumulator=0
        for index in sorted(support):
            if type(index) is not int or not 0 <= index < dimension:
                raise ValueError('invalid causal coordinate')
            accumulator ^= (state >> index) & 1
        outputs.append(accumulator)
    return tuple(outputs)

def grade(problem: PublicProblem, result: Discovery) -> dict:
    real = _private_goal(problem)
    if result.completed:
        tests = independent_test_masks(problem)
        predicted = tuple(_mask(row) for row in result.known)
        test_correct = sum(symbolic_recurrent_code(s,result.known,problem.dimension)==
                           tuple((s&mask).bit_count()&1 for mask in real) for s in tests)
        if test_correct!=N_TEST or predicted!=real:
            raise AssertionError('completed support certificate did not predict exact parity')
    else:
        test_correct = 0
    return {'release':int(result.completed),'test_correct':test_correct,
            'false_accept':N_TEST-test_correct if result.completed else 0,
            'true_utility':'10' if result.completed else '0'}


def evaluate(condition_seed: int, cohort: str, k: int,
             budgets: tuple[int,...]=BUDGETS) -> list[dict]:
    public = make_problem(condition_seed, cohort, k)
    out=[]
    for policy in POLICIES:
        for budget in budgets:
            found = discover(public,budget,policy)
            checked = grade(public,found)
            out.append({
                'seed':condition_seed,'cohort':cohort,'dimension':public.dimension,'goal_rank':k,
                'policy':policy,'budget':budget,'query_count':found.queries,
                'support_certified':int(found.completed),
                'recovered_per_output':','.join(str(len(v)) for v in found.known),
                'information_lower_bound':information_lower_bound(public.dimension,WIDTH),
                'transcript_sha256':hashlib.sha256(json.dumps(
                  [(hex(m), a) for m,a in found.transcript],separators=(',',':')).encode()).hexdigest(),
                **checked,
            })
    return out


def run(seeds=SEEDS,cohorts=COHORTS,ranks=RANKS, budgets=BUDGETS) -> list[dict]:
    rows=[]
    for seed in seeds:
        for cohort in cohorts:
            for k in ranks:
                rows.extend(evaluate(seed,cohort,k,budgets))
    return rows


def summarize(rows: list[dict]) -> dict:
    grouped=defaultdict(list)
    for row in rows:
        grouped[row['cohort'],row['goal_rank'],row['policy'],row['budget']].append(row)
    groups=[]
    for (cohort,k,policy,budget),sub in sorted(grouped.items()):
        groups.append({'cohort':cohort,'goal_rank':k,'policy':policy,'budget':budget,
                       'n_seeds':len(sub),'complete':sum(r['support_certified'] for r in sub),
                       'mean_queries':str(Q(sum(r['query_count'] for r in sub),len(sub))),
                       'false_accepts':sum(r['false_accept'] for r in sub),
                       'mean_true_utility':str(Q(sum(Q(r['true_utility']) for r in sub),len(sub)))})
    def val(s,cohort,k,policy,budget):
        return next(r for r in rows if r['seed']==s and r['cohort']==cohort and
                    r['goal_rank']==k and r['policy']==policy and r['budget']==budget)
    if {x['seed'] for x in rows} == set(SEEDS) and set(r['budget'] for r in rows)==set(BUDGETS):
        h1=sum(val(s,'native_1024',1,'adaptive_hash',128)['support_certified'] >
               val(s,'native_1024',1,'random_singletons',128)['support_certified'] for s in SEEDS)
        h2=sum(val(s,'native_1024',1,'adaptive_hash',256)['support_certified'] for s in SEEDS)
        h3={f'{cohort}/{k}':sum(val(s,cohort,k,'adaptive_hash',512)['support_certified'] for s in SEEDS)
            for cohort in COHORTS for k in RANKS}
        gate={'H1':{'paired_wins':h1,'passes':h1>=16},
              'H2':{'completions':h2,'passes':h2>=20},
              'H3':{'by_cohort':h3,'passes':all(n>=20 for n in h3.values())},
              'H4':{'passes':all(r['test_correct']==N_TEST and r['false_accept']==0
                                     for r in rows if r['support_certified'])}}
    else:gate={}
    return {'schema':VERSION,'counts':{'rows':len(rows),'seeds':len({r['seed'] for r in rows}),
            'conditions':len({(r['seed'],r['cohort'],r['goal_rank']) for r in rows})},
            'groups':groups,'registered_gates':gate,
            'scope':'public synthetic causal XOR intervention oracle; no trained neural model'}


def write_rows(rows:list[dict],path:Path):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


if __name__ == '__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--smoke',action='store_true')
    args=ap.parse_args()
    rows=run(seeds=SEEDS[:2] if args.smoke else SEEDS,
             cohorts=('core_140','native_1024') if args.smoke else COHORTS,
             ranks=(1,) if args.smoke else RANKS)
    write_rows(rows,args.out/'hg08_intervention_seed_rows.csv')
    summary=summarize(rows)
    (args.out/'hg08_intervention_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(summary['counts'],summary['registered_gates'])
