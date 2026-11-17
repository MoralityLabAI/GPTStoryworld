"""Audit archived HG-08 CPU neural evidence without retraining floating weights.

Checks every per-seed calibration decision, full test count, model parameter
matching, causal query receipts, source hash and registered H5 direction count.
"""
from __future__ import annotations
import csv
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

from spiral_ln.hypergames_active_neural import summary, NEURAL_SEEDS, NEURAL_COHORTS, NEURAL_ARMS
from spiral_ln.hypergames_active_causal import discover, make_problem

ROOT=Path(__file__).resolve().parents[1]
SOURCES=(
 'src/spiral_ln/evaluation_hypergames_causal.py',
 'src/spiral_ln/hypergames_active_causal.py',
 'src/spiral_ln/hypergames_active_neural.py',
 'scripts/run_hg08_cpu.py',
 'scripts/verify_hg08_causal.py',
 'tests/test_evaluation_hypergames_causal.py',
 'tests/test_hypergames_active_causal.py',
)
INTS={'seed','dimension','goal_rank','n_train','training_steps',
      'input_features_visible','support_complete','causal_query_count',
      'parameter_count','cal_correct','test_correct','released','false_accept'}
FLOATS={'training_seconds','final_train_loss'}


def digest(path:Path):return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(out:Path)->dict:
    rowsfile=out/'hg08_neural_seed_rows.csv'
    rows=[]
    with rowsfile.open(newline='',encoding='utf8') as f:
        for r in csv.DictReader(f):
            rows.append({k:(int(v) if k in INTS else float(v) if k in FLOATS else v) for k,v in r.items()})
    saved=json.loads((out/'hg08_neural_summary.json').read_text('utf8'))
    s=summary(rows)
    checks={}
    checks['48_registered_neural_fits']=len(rows)==48
    checks['six_public_seeds']=set(r['seed'] for r in rows)==set(NEURAL_SEEDS)
    checks['registered_grid']=set((r['seed'],r['cohort'],r['arm']) for r in rows)==set((seed,cohort,arm)
                      for seed in NEURAL_SEEDS for cohort in NEURAL_COHORTS for arm in NEURAL_ARMS)
    checks['frozen_training_budget']=all(r['n_train']==512 and r['training_steps']==350 for r in rows)
    checks['recurrent_parameters_matched']=all(len({r['parameter_count'] for r in rows
                      if (r['seed'],r['cohort'])==(seed,cohort)})==1 for seed in NEURAL_SEEDS for cohort in NEURAL_COHORTS)
    checks['matching_256_example_splits']=all(0<=r['cal_correct']<=256 and 0<=r['test_correct']<=256 for r in rows)
    checks['calibration_only_release']=all(r['released']==int(Q(r['cal_correct']+1,258)>Q(3,5)) for r in rows)
    checks['false_accepts_recomputed']=all(r['false_accept']==(256-r['test_correct']) if r['released'] else r['false_accept']==0 for r in rows)
    checks['true_utility_recomputed']=all(Q(r['true_utility'])==(Q(25*r['test_correct']-15*256,256) if r['released'] else Q(0)) for r in rows)
    checks['all_models_abstain_as_observed']=all(not r['released'] for r in rows)
    checks['causal_masks_certified_independently']=all(r['support_complete']==1 and r['input_features_visible']==6 and
             r['causal_query_count']==discover(make_problem(r['seed'],r['cohort'],1),512,'adaptive_hash').queries
             for r in rows if r['arm']=='causal_masked_loop')
    checks['privileged_and_causal_agree']=all(next(r['test_correct'] for r in rows if
             (r['seed'],r['cohort'],r['arm'])==(seed,cohort,'causal_masked_loop'))==
             next(r['test_correct'] for r in rows if
             (r['seed'],r['cohort'],r['arm'])==(seed,cohort,'privileged_true_support_masked_loop'))
             for seed in NEURAL_SEEDS for cohort in NEURAL_COHORTS)
    checks['registered_H5_failure_preserved']=s['H5']['paired_wins']==1 and not s['H5']['passes']
    checks['recomputed_group_summary']=s['groups']==saved['groups'] and s['H5']==saved['H5']
    checks['archived_neural_csv_sha256']=digest(rowsfile)==saved['neural_seed_csv_sha256']
    checks['public_source_hashes_current']=saved['source_sha256']=={p:digest(ROOT/p) for p in SOURCES}
    return {'schema':'HG-08/neural-receipt-audit-v1','checks':checks,
            'all_passed':all(checks.values()),'rows':len(rows),
            'public_csv_sha256':digest(rowsfile),
            'interpretation':'source-hash and arithmetic recheck of frozen neural result; no cross-hardware weight-bit identity claimed'}

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'output/evaluation_hypergames/hg08')
    args=ap.parse_args()
    outcome=verify(args.out)
    print(json.dumps(outcome,indent=2,sort_keys=True))
    raise SystemExit(0 if outcome['all_passed'] else 1)
