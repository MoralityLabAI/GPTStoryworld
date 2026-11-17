"""HG-06 public CPU exact replay, deterministic source/census hashes.

Run from verifiers_envs/storyworld-hypergames-env (PYTHONPATH=src):
    python scripts/run_hg06_cpu.py --out output/evaluation_hypergames/hg06
    python scripts/run_hg06_cpu.py --out output/evaluation_hypergames/hg06 --check
    python scripts/run_hg06_cpu.py --seed-count 2 --out /tmp/hg06_smoke

The full census uses 24 public development seeds. Private HG-03 seeds stay sealed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from time import perf_counter

from spiral_ln.hypergames_composition import (
    VERSION,COHORTS,RANKS,POOLS,TRAIN_SIZES,SEED_START,SEED_COUNT,N_CAL,N_TEST,N_RANDOM,ARMS,
    instance,run,aggregate,write_csv)

ROOT=Path(__file__).resolve().parents[1]
REGISTRATION=ROOT/'Hypergames/single_player/hg06_registration_v1.json'
SOURCES=(
  'src/spiral_ln/evaluation_hypergames_composition.py',
  'src/spiral_ln/hypergames_composition.py',
  'scripts/run_hg06_cpu.py',
  'tests/test_hypergames_composition.py',
  'Hypergames/single_player/hg06_registration_v1.json',
)


def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_registration(cfg):
    assert (cfg['schema']==VERSION and cfg['seed_start']==SEED_START and cfg['seed_count']==SEED_COUNT)
    assert tuple(cfg['cohorts'])==COHORTS and tuple(cfg['goal_ranks'])==RANKS
    assert tuple(cfg['dictionary_pools'])==POOLS and tuple(cfg['train_sizes'])==TRAIN_SIZES
    assert cfg['calibration_size']==N_CAL and cfg['test_size']==N_TEST and cfg['random_triples']==N_RANDOM
    assert cfg['goal_width']==6 and cfg['fragments_per_goal']==3 and cfg['fragment_width']==2
    assert tuple(cfg['arms'])==ARMS+('random_rank_matched_100',)
    assert cfg['fixed_decoy_formula']=='6*k' and cfg['ambient_decoy_formula']=='max(6*k, floor(d/32))'


def _one_seed(seed):
    return run(seeds=(seed,))


def seed_rows(seeds,workers=1):
    if workers==1:
        return [row for seed in seeds for row in _one_seed(seed)]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return [row for part in pool.map(_one_seed,seeds) for row in part]


def compact_receipt(rows,summary,csv_sha):
    counts=summary['counts']
    science=summary['registered_science_gates']
    unique={(r['seed'],r['cohort'],r['goal_rank'],r['pool']) for r in rows}
    expected_conditions=SEED_COUNT*len(COHORTS)*len(RANKS)*len(POOLS)
    checks={
      'registration_shape': len(unique)==expected_conditions,
      'seed_roster':sorted(set(r['seed'] for r in rows))==list(range(SEED_START,SEED_START+SEED_COUNT)),
      'all_five_cohorts':len({r['cohort'] for r in rows})==5,
      'four_goal_ranks':set(r['goal_rank'] for r in rows)==set(RANKS),
      'two_feature_pools':set(r['pool'] for r in rows)==set(POOLS),
      'four_training_budgets':set(r['train_n'] for r in rows)==set(TRAIN_SIZES),
      'six_deterministic_arms':set(r['arm'] for r in rows)==set(ARMS),
      'expected_23040_rows':len(rows)==23040,
      'expected_96000_random_controls':counts['random_composite_draws']==96000,
      'full_census_padding_invariant':science['fixed_pool_padding_identity'],
      'oracle_all_128_128':science['oracle_perfect'],
      'missing_component_rank_deficit':science['all_missing_component_target_deficient'],
      'n64_registered_recovery_gate':science['n64_xor3_exact_and_beats_xor2_20of24_each_rank'],
      'source_hashes_recorded':len(SOURCES)==5,
      'five_public_seed_csv_sha256':len(csv_sha)==5,
    }
    return {'schema':'HG-06/compact-receipt-v1','evidence':'public synthetic CPU enumeration',
      'counts':counts,'directions':summary['directions'],'science_gates':science,
      'checks':checks,'all_passed':all(checks.values()),
      'source_sha256':{p:sha(ROOT/p) for p in SOURCES},
      'seed_csv_sha256':csv_sha}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=Path('output/evaluation_hypergames/hg06'))
    parser.add_argument('--workers',type=int,default=1)
    parser.add_argument('--seed-count',type=int,default=SEED_COUNT,help='smoke subsets only; full=24')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if not (1<=args.seed_count<=SEED_COUNT) or not (1<=args.workers<=16):
        parser.error('seed-count 1..24 and workers 1..16 required')
    if args.check and args.seed_count!=SEED_COUNT:
        parser.error('--check requires the full 24-seed registration')
    cfg=json.loads(REGISTRATION.read_text('utf8'))
    validate_registration(cfg)
    rootout=args.out if args.out.is_absolute() else ROOT/args.out
    if rootout.exists() and not args.check and any(rootout.iterdir()):
        raise SystemExit('refusing to overwrite a nonempty output folder')
    import tempfile
    begin=perf_counter()
    seeds=tuple(range(SEED_START,SEED_START+args.seed_count))
    rows=seed_rows(seeds,args.workers)
    result=aggregate(rows) if args.seed_count==SEED_COUNT else None
    if args.check:
        with tempfile.TemporaryDirectory() as temp:
            files=write_csv(rows,Path(temp))
            csv_sha={p.name:sha(p) for p in files}
            for p in files:
                target=rootout/p.name
                if not target.exists() or sha(target)!=sha(p):
                    raise SystemExit('CSV hash discrepancy: '+str(target))
            report=compact_receipt(rows,result,csv_sha)
            expected=json.loads((rootout/'hg06_compact_receipt_v1.json').read_text('utf8'))
            if report!=expected:
                raise SystemExit('regenerated source-hashed compact receipt differs')
            print('HG-06 verified',report['checks'], 'seconds',round(perf_counter()-begin,2))
            return 0 if report['all_passed'] else 1
    rootout.mkdir(parents=True,exist_ok=True)
    paths=write_csv(rows,rootout)
    if result:
        (rootout/'hg06_group_summary_v1.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n','utf8')
        report=compact_receipt(rows,result,{p.name:sha(p) for p in paths})
        (rootout/'hg06_compact_receipt_v1.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n','utf8')
        print('HG-06 generated',report['counts'],report['science_gates'],report['directions'],flush=True)
        if not report['all_passed']:
            return 1
    else:
        print('HG-06 smoke subset, not a preregistered result')
    print('Elapsed seconds',round(perf_counter()-begin,2),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
