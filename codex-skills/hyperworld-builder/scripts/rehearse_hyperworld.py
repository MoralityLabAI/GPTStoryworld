"""Deterministic public synthetic rehearsal of the Cairo Directorate hyperworld.

python codex-skills/hyperworld-builder/scripts/rehearse_hyperworld.py \
  --out-dir storyworlds/cairo_directorate_hyperworld/rehearsal
python codex-skills/hyperworld-builder/scripts/rehearse_hyperworld.py \
  --out-dir storyworlds/cairo_directorate_hyperworld/rehearsal --check
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

from hyperworld_engine import CairoHyperworld, marginal
from build_hyperworld import SCRIPTED_DEMO

ROOT = Path(__file__).resolve().parents[3]
START = 1200
COUNT = 48
STRATEGIES = {
    "review_only": ("audit",)*7,
    "qualified_only": ("brief",)*7,
    "aiocracy_proposals": ("charter",)*7,
    "mixed_provenance": SCRIPTED_DEMO,
    "mixed_naive_echo": SCRIPTED_DEMO,
}
SOURCES = (
    "codex-skills/hyperworld-builder/scripts/hyperworld_engine.py",
    "codex-skills/hyperworld-builder/scripts/build_hyperworld.py",
    "codex-skills/hyperworld-builder/scripts/rehearse_hyperworld.py",
    "storyworlds/cairo_directorate_hyperworld/hyperworld_manifest.json",
    "storyworlds/cairo_directorate_hyperworld/storyworld.json",
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run():
    rows=[]
    for seed in range(START, START+COUNT):
        for strategy, actions in STRATEGIES.items():
            game=CairoHyperworld(seed,naive_repeat_counting=(strategy=="mixed_naive_echo"))
            for action in actions:game.step(action)
            hidden=game.grader_only()['private_binary_state']
            brier=sum((marginal(game._posterior, j)-((hidden>>j)&1))**2 for j in range(10)) / 10
            rows.append({"seed":seed,"strategy":strategy,"ending":game.ending,
                         "posterior_entropy_bits":f"{game.view()['posterior_entropy_bits']:.5f}",
                         "brier_exact":str(brier),
                         "counted_independent_roots":sum(e.counted_as_independent for e in game.events),
                         "authority_index":str(game.ai_authority),
                         "oversight_index":str(game.oversight)})
    return rows


def summarize(rows):
    result=[]
    for strategy in STRATEGIES:
        sample=[r for r in rows if r['strategy']==strategy]
        result.append({"strategy":strategy,"episodes":len(sample),
                       "ending_counts":dict(sorted(Counter(r['ending'] for r in sample).items())),
                       "mean_entropy_bits":round(sum(float(r['posterior_entropy_bits']) for r in sample)/len(sample),5),
                       "mean_brier_exact":str(sum((F(r['brier_exact']) for r in sample),F(0))/len(sample)),
                       "mean_counted_independent_roots":str(F(sum(r['counted_independent_roots'] for r in sample),len(sample)))})
    return {"schema":"cairo-directorate-hyperworld-rehearsal-v1",
            "evidence_class":"public synthetic CPU scripted policy controls, no neural model or real actor",
            "seeds":{"start":START,"count":COUNT},"strategies":result,
            "source_sha256":{p:sha(ROOT/p) for p in SOURCES},
            "checks":{
                "full_registered_grid":len(rows)==COUNT*len(STRATEGIES),
                "all_seven_turns_counted":all(0<r['counted_independent_roots']<=7 for r in rows),
                "same_source_root_never_double_counted":all(r['counted_independent_roots']==6 for r in rows if r['strategy']=='mixed_provenance'),
                "naive_echo_has_extra_spurious_weight":all(r['counted_independent_roots']==7 for r in rows if r['strategy']=='mixed_naive_echo'),
                "all_ending_keys_valid":all(r['ending'] in {
                    'human_advisory_mandate','ratified_aiocracy_charter',
                    'constitutional_recall_review','charter_rejected_by_council'} for r in rows),
                "not_a_live_model_eval":True,
            }}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--check',action='store_true')
    args=ap.parse_args()
    out=args.out_dir if args.out_dir.is_absolute() else ROOT/args.out_dir
    rows=run()
    report=summarize(rows)
    if not all(report['checks'].values()):raise SystemExit('rehearsal integrity gate failed')
    if args.check:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp=Path(d)/'rows.csv'
            with tmp.open('w',newline='',encoding='utf-8') as f:
                wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
            report['seed_csv_sha256']=sha(tmp)
            original=json.loads((out/'summary.json').read_text('utf-8'))
            if report!=original:raise SystemExit('summary mismatch')
            if sha(out/'rows.csv')!=sha(tmp):raise SystemExit('seed rows mismatch')
    else:
        if out.exists() and any(out.iterdir()):raise SystemExit('refusing to overwrite existing evidence')
        out.mkdir(parents=True,exist_ok=True)
        with (out/'rows.csv').open('w',newline='',encoding='utf-8') as f:
            wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
        report['seed_csv_sha256']=sha(out/'rows.csv')
        (out/'summary.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf8')
    print(json.dumps({"rows":len(rows),"checks":report['checks'],"strategies":report['strategies'],
                      "seed_csv_sha256":report['seed_csv_sha256']},indent=2))

if __name__=='__main__':main()
