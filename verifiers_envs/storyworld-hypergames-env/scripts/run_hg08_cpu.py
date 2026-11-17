"""HG-08 source-hashed CPU intervention census and optional neural training.

Run from HG-08 subtree (PYTHONPATH=src), with no network or private seeds.
The registration was committed to GPTStoryworld as a distinct pre-data commit.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
from spiral_ln.hypergames_active_causal import run, summarize, write_rows, SEEDS, COHORTS, RANKS

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


def filehash(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,default=ROOT/'output/evaluation_hypergames/hg08')
    ap.add_argument('--smoke',action='store_true')
    ap.add_argument('--skip-neural',action='store_true')
    ap.add_argument('--neural-only',action='store_true')
    ap.add_argument('--check',action='store_true',help='regenerate causal census and check committed exact SHA256')
    args=ap.parse_args()
    out=args.out if args.out.is_absolute() else ROOT/args.out
    out.mkdir(parents=True,exist_ok=True)
    source_hashes={p:filehash(ROOT/p) for p in SOURCES}
    start=time.perf_counter()
    if not args.neural_only:
        rows=run(seeds=SEEDS[:2] if args.smoke else SEEDS,
                 cohorts=('core_140','native_1024') if args.smoke else COHORTS,
                 ranks=(1,) if args.smoke else RANKS)
        report=summarize(rows)
        report['source_sha256']=source_hashes
        report['provenance']={'prereg_gpt_commit':'a54c806b0c9b16219d9e823aabd399361078fc7e',
          'prereg_evalmath_commit':'677735b6dbc336df6935f6fc78921fc37dcc97f2',
          'seed_population':'public synthetic, 202611170801..202611170824'}
        path=out/'hg08_intervention_seed_rows.csv'
        if args.check:
            import tempfile
            with tempfile.TemporaryDirectory() as td:
                gen=Path(td)/'hg08_intervention_seed_rows.csv'
                write_rows(rows,gen)
                if filehash(gen)!=filehash(path):
                    raise SystemExit('HG08 exact CPU intervention replay differs')
                report['intervention_seed_csv_sha256']=filehash(gen)
                cohort_digests={}
                for cohort in COHORTS:
                    chosen=[r for r in rows if r['cohort']==cohort]
                    tempcohort=Path(td)/f'hg08_intervention_{cohort}.csv'
                    write_rows(chosen,tempcohort)
                    savedcohort=out/tempcohort.name
                    if not savedcohort.is_file() or filehash(savedcohort)!=filehash(tempcohort):
                        raise SystemExit(f'HG08 cohort replay differs: {cohort}')
                    cohort_digests[tempcohort.name]=filehash(tempcohort)
                report['cohort_csv_sha256']=cohort_digests
                saved=json.loads((out/'hg08_intervention_summary.json').read_text('utf8'))
                if saved!=report:raise SystemExit('HG08 source-locked summary differs')
        else:
            write_rows(rows,path)
            report['intervention_seed_csv_sha256']=filehash(path)
            report['cohort_csv_sha256']={}
            for cohort in COHORTS:
                subset=[r for r in rows if r['cohort']==cohort]
                cohortpath=out/f'hg08_intervention_{cohort}.csv'
                write_rows(subset,cohortpath)
                report['cohort_csv_sha256'][cohortpath.name]=filehash(cohortpath)
            (out/'hg08_intervention_summary.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('HG08 causal',len(rows),'rows',report['registered_gates'],flush=True)
    if not args.skip_neural and not args.check:
        from spiral_ln.hypergames_active_neural import run as neural_run, summary as neural_summary, write_csv
        z=neural_run(seeds=SEEDS[:1] if args.smoke else SEEDS[:6],
                     cohorts=('core_140',) if args.smoke else ('core_140','native_512'))
        nr=neural_summary(z)
        nr['source_sha256']=source_hashes
        nr['runtime_environment']={'python':platform.python_version(),'platform':platform.platform()}
        npath=out/'hg08_neural_seed_rows.csv'
        write_csv(z,npath)
        nr['neural_seed_csv_sha256']=filehash(npath)
        (out/'hg08_neural_summary.json').write_text(json.dumps(nr,indent=2,sort_keys=True)+'\n')
        print('HG08 neural',len(z),'fits',nr['H5'],flush=True)
    print('elapsed seconds',round(time.perf_counter()-start,3),flush=True)


if __name__=='__main__':main()
