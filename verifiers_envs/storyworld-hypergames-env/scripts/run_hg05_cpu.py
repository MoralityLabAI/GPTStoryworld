"""Run HG-05 registered public synthetic CPU census and source-hash receipt.

From the repo's Hypergames environment subfolder:
    PYTHONPATH=src python scripts/run_hg05_cpu.py --out output/evaluation_hypergames/hg05
The committed receipt uses only standard Python modules; no hidden test data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from spiral_ln.hypergames_rank import run, report, write_seed_csv

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    'src/spiral_ln/evaluation_hypergames_rank.py',
    'src/spiral_ln/hypergames_rank.py',
    'scripts/run_hg05_cpu.py',
    'Hypergames/single_player/hg05_registration_v1.json',
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=Path('output/evaluation_hypergames/hg05'))
    parser.add_argument('--check',action='store_true',help='compare regenerated seed rows/receipt to existing output')
    args=parser.parse_args()
    out=(args.out if args.out.is_absolute() else ROOT/args.out)
    cfg=json.loads((ROOT/'Hypergames/single_player/hg05_registration_v1.json').read_text('utf8'))
    start=time.perf_counter()
    rows=run(reg=cfg)
    result=report(rows)
    result['source_sha256']={p:sha(ROOT/p) for p in SOURCES}
    result['checks']={
        'registered_24_seed_roster':len({r['seed'] for r in rows})==24,
        'registered_5_cohorts':len({r['cohort'] for r in rows})==5,
        'registered_5_goal_ranks':len({r['goal_rank'] for r in rows})==5,
        'registered_2_pools':len({r['pool'] for r in rows})==2,
        'registered_3_training_sizes':len({r['train_n'] for r in rows})==3,
        'all_observer_rank_equal_goal_rank':result['gates']['all_basis_rank_matched'],
        'fixed_pool_padding_identical':result['gates']['fixed_pool_padding_invariance'],
        'expected_14400_seed_arm_rows':len(rows)==14400,
        'registered_120000_random_basis_draws':result['counts']['random_base_draws']==120000,
        'oracle_perfect_at_all_scales':all(r['test_correct']==64 and r['false_accept']==0 for r in rows if r['arm']=='oracle_task'),
    }
    result['all_passed']=all(result['checks'].values())
    # Preserve scientific results separately from integrity checks.
    result['scientific_gate_results']=result['gates']
    if args.check:
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)
            paths=write_seed_csv(rows,dest)
            for path in paths:
                original=out/Path(path).name
                if not original.is_file() or sha(Path(path))!=sha(original):
                    raise SystemExit(f'REGENERATED CSV DIFFERS: {original}')
            result['seed_csv_sha256']={Path(p).name:sha(Path(p)) for p in paths}
            saved=json.loads((out/'hg05_summary_v1.json').read_text('utf8'))
            if saved!=result:
                raise SystemExit('REGENERATED SUMMARY DIFFERS')
    else:
        if out.exists() and any(out.iterdir()):
            raise SystemExit('refusing to overwrite an existing output directory')
        out.mkdir(parents=True, exist_ok=True)
        paths=write_seed_csv(rows,out)
        result['seed_csv_sha256']={Path(p).name:sha(Path(p)) for p in paths}
        (out/'hg05_summary_v1.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n','utf8')
    print(f"HG-05 rows={len(rows)} random bases={result['counts']['random_base_draws']} elapsed={time.perf_counter()-start:.2f}s",flush=True)
    print('integrity:',result['checks'],flush=True)
    print('registered science gates:',result['registered_direction_counts'],flush=True)
    return 0 if result['all_passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
