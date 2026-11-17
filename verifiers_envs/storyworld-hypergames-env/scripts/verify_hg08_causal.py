"""HG-08 deterministic source-hashed exact causal mathematics receipt."""
from __future__ import annotations
import hashlib
import json
from fractions import Fraction as Q
from itertools import product
from math import comb
from pathlib import Path
from random import Random

from spiral_ln.evaluation_hypergames_causal import (
    parity, causal_difference, direct_difference, peel_known,
    support_certified, information_lower_bound, ideal_joint_code_success,
    forced_release_utility,
)
from spiral_ln.hypergames_active_causal import (
    make_problem, _private_goal, InterventionOracle, discover, grade,
)

ROOT=Path(__file__).resolve().parents[1]
SOURCES=(
    'src/spiral_ln/evaluation_hypergames_causal.py',
    'src/spiral_ln/hypergames_active_causal.py',
    'src/spiral_ln/hypergames_active_neural.py',
    'scripts/verify_hg08_causal.py',
    'tests/test_evaluation_hypergames_causal.py',
    'tests/test_hypergames_active_causal.py',
)

def verify()->dict:
    checks={}
    independent=0
    for d in range(1,5):
        for p in range(1<<d):
            for x in range(1<<d):
                for flip in range(1<<d):
                    direct=parity(p,x^flip,d)^parity(p,x,d)
                    assert causal_difference((p,),flip,d)[0] == direct
                    independent+=1
    checks['4680_independent_finite_derivatives']=independent==4680
    multi=0
    rng=Random(2026111708)
    for dim in (140,512,1024):
        for _ in range(100):
            rows=tuple(rng.getrandbits(dim) for _ in range(2))
            x=rng.getrandbits(dim);flip=rng.getrandbits(dim)
            assert causal_difference(rows,flip,dim)==direct_difference(rows,x,flip,dim)
            multi+=1
    checks['300_multioutput_highdim_derivatives']=multi==300
    checks['three_exact_information_lower_bounds']=[information_lower_bound(d,6) for d in (140,512,1024)]==[34,45,51]
    checks['entropy_power_of_two_boundary']=all((1<<information_lower_bound(d,s))>=comb(d,s) for d in range(1,11) for s in range(d+1))
    raw=(1,0); subset=0b11010; known=(frozenset((1,3)),frozenset((2,)))
    checks['causal_peeling_involution']=peel_known(peel_known(raw,subset,known,5),subset,known,5)==raw
    checks['singleton_certificate_positive']=support_certified({0:(1,),2:(1,),4:(1,)},8,1,3)
    checks['singleton_certificate_incomplete']=not support_certified({0:(1,),2:(1,)},8,1,3)
    checks['one_missing_bit_forced_release_negative']=forced_release_utility(Q(1,2))==Q(-5,2)
    checks['complete_support_best_release']=forced_release_utility(Q(1))==Q(10)
    checks['two_missing_bits_joint_ceiling']=ideal_joint_code_success((1,), (2,4), 4)==Q(1,4)
    p=make_problem(202611170801,'native_1024',2)
    a=discover(p,512,'adaptive_hash')
    checks['active_support_exact_at_smoke_1024']=a.completed and all(len(x)==6 for x in a.known) and tuple(sum(1<<i for i in x) for x in a.known)==_private_goal(p)
    checks['simulator_test_grade_no_false_release']=grade(p,a)['test_correct']==256 and grade(p,a)['false_accept']==0
    checks['strict_64_budget']=discover(p,64,'adaptive_hash').queries<=64
    q=InterventionOracle(p,1);q.query(0)
    try:q.query(1);over_budget=False
    except Exception:over_budget=True
    checks['oracle_budget_cap']=over_budget and q.calls==1
    c=make_problem(202611170801,'core_140',1)
    z=make_problem(202611170801,'padded_512',1)
    checks['core_padded_same_goal']=_private_goal(c)==_private_goal(z)
    result={'schema':'HG-08/causal-exact-math-v1',
       'evidence':'exact finite-field causal mechanics and independent enumerative checks; public synthetic only',
       'counts':{'finite_derivative_cases':independent,'high_dimension_derivative_cases':multi},
       'checks':checks,'all_passed':all(checks.values()),
       'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}}
    return result

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    result=verify();text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(text)
    else:print(text,end='')
    raise SystemExit(0 if result['all_passed'] else 1)
