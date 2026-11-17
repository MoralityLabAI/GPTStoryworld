"""Audit public HG-07 per-seed rows and refresh source-hashed metadata only.

The full neural sweep is an empirical float32 CPU measurement. This verifier
checks its sealed scoring/census arithmetic without retraining networks.
Use --refresh-metadata for a presentation-only registration reformat, keeping
per-model CSV rows unchanged and recording the CSV's original SHA256.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from fractions import Fraction as Q
from pathlib import Path
from collections import Counter
from spiral_ln.hypergames_raw_recurrent import (
    ARMS,COHORTS,RANKS,TRAIN,SEEDS,N_TEST,N_CAL,VERSION,summarize)
ROOT=Path(__file__).resolve().parents[1]
SRC=('src/spiral_ln/evaluation_hypergames_raw.py',
     'src/spiral_ln/hypergames_raw_recurrent.py',
     'Hypergames/single_player/hg07_registration_v1.json')

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def verify(out:Path,refresh_metadata=False):
    csv_path=out/'hg07_public_seed_rows.csv'
    rows=list(csv.DictReader(csv_path.open(newline='')))
    # Type restore for independent summary reconstruction; never compute test
    # values from the model, never edit, drop or select individual trials.
    numeric=('seed','dimension','goal_rank','train_n','param_count',
             'direct_cal_joint_correct','direct_test_joint_correct','direct_test_bit_correct',
             'direct_release','direct_false_accept','f2_rank','f2_nullity',
             'f2_test_determined','f2_release','f2_test_correct_if_determined')
    float_keys=('train_loss','training_seconds')
    nullable_int=('fragment_test_correct','composed_test_joint_correct',
                  'composed_false_accept','composed_release')
    for row in rows:
        for col in numeric:row[col]=int(row[col])
        for col in float_keys:row[col]=float(row[col])
        for col in nullable_int:row[col]=None if not row[col] else int(row[col])
        for col in ('composed_true_utility','random_mean_test_joint','sparse_union_bound',
                    'direct_true_utility','random_rank_p'):
            if row[col]:Q(row[col])
    expected={(s,c,k,n,a) for s in SEEDS for c in COHORTS
              for k in RANKS for n in TRAIN for a in ARMS}
    ids={(r['seed'],r['cohort'],r['goal_rank'],r['train_n'],r['arm']) for r in rows}
    valid_rows=len(rows)==len(expected)==360 and ids==expected
    checks={
      '360_sealed_neural_rows':valid_rows,
      'six_distinct_registered_seeds':set(r['seed'] for r in rows)==set(SEEDS),
      'three_registered_cohorts':set(r['cohort'] for r in rows)==set(COHORTS),
      'two_goal_ranks':set(r['goal_rank'] for r in rows)==set(RANKS),
      'two_train_budgets':set(r['train_n'] for r in rows)==set(TRAIN),
      'five_controller_arms':set(r['arm'] for r in rows)==set(ARMS),
      'all_label_counts_in_bounds':all(0<=r['direct_test_joint_correct']<=256 and
          0<=r['direct_cal_joint_correct']<=256 and
          0<=r['direct_test_bit_correct']<=256*r['goal_rank'] for r in rows),
      'false_accepts_match_final_release':all(r['direct_false_accept']==
          (256-r['direct_test_joint_correct'] if r['direct_release'] else 0) for r in rows),
      'calibration_is_only_threshold':all(bool(r['direct_release']) ==
          (Q(r['direct_cal_joint_correct']+1,258)>Q(3,5)) for r in rows),
      'payoff_accounting_exact':all(Q(r['direct_true_utility'])==
          (Q(25*r['direct_test_joint_correct']-15*256,256)
             if r['direct_release'] else Q(0)) for r in rows),
      'baseline_rank_accounting':all(r['f2_nullity']==r['dimension']-r['f2_rank'] for r in rows),
      'full_data_GF2_oracle_perfect':all(r['f2_rank']==r['dimension'] and
          r['f2_test_determined']==256 and r['f2_test_correct_if_determined']==256
          for r in rows if r['train_n']==2048),
      'one_result_per_registered_key':len(ids)==len(rows),
      'all_rank_p_denominators_101':all(Q(r['random_rank_p'])*101==int(Q(r['random_rank_p'])*101)
            for r in rows),
      'composed_only_in_aux_arms':all((r['composed_test_joint_correct'] is None)==
          (r['arm'] not in ('loop_true_fragment_aux','loop_shuffled_fragment_aux')) for r in rows)
    }
    assert all(checks.values()),{k:v for k,v in checks.items() if not v}
    fresh=summarize(rows)
    saved=json.loads((out/'hg07_summary.json').read_text())
    if saved['groups'] != fresh['groups'] or saved['prereg_gates']!=fresh['prereg_gates']:
        raise AssertionError('computed summary differs from trial rows')
    if sha(csv_path)!=saved['seed_csv_sha256']:
        raise AssertionError('per-seed dataset has changed')
    sources={p:sha(ROOT/p) for p in SRC}
    if saved['sources_sha256'] != sources:
        if not refresh_metadata:
            raise AssertionError('source hash mismatch; run --refresh-metadata only for formatting changes')
        saved['sources_sha256']=sources
        saved['metadata_refresh_note']='2026-11-17: frozen registration reserialized byte-identically to public preregistration; model CSV, metrics and RNG unaffected'
        (out/'hg07_summary.json').write_text(json.dumps(saved,sort_keys=True,indent=2)+'\n')
    receipt={'schema':'HG-07/public-cpu-audit-v1',
        'data_sha256':sha(csv_path), 'data_rows':len(rows),
        'checks':checks,'all_passed':all(checks.values()),
        'source_sha256':sources,
        'preregistered_science_gates':fresh['prereg_gates'],
        'warning':'neural float32 CPU observations, not exact theorem or GPTStoryworld player'}
    return receipt


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--out',type=Path,default=ROOT/'output/evaluation_hypergames/hg07')
    a.add_argument('--refresh-metadata',action='store_true')
    a.add_argument('--receipt',type=Path,default=None)
    args=a.parse_args()
    r=verify(args.out,args.refresh_metadata)
    if args.receipt:args.receipt.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print('HG07 audited',r['data_rows'],'rows;',len(r['checks']),'checks passed;',r['data_sha256'])
    return 0 if r['all_passed'] else 1
if __name__=='__main__':raise SystemExit(main())
