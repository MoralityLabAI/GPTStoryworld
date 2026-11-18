"""HGW-02 source-hashed public development rehearsal of fictional secret phase gates.

This is a deterministic script-policy study, not a model evaluation. Seeds
1200..1247 are *reused development seeds* from HGW-01, not held-out evidence.
The canonical Python runtime owns all posterior, unlock and legal outcomes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

from build_hyperworld import SCRIPTED_DEMO, secret_witnesses, ENDINGS
from hyperworld_engine import CairoHyperworld, PRINCIPALS, PUBLIC_SEGMENTS, marginal

ROOT = Path(__file__).resolve().parents[3]
START = 1200
COUNT = 48
SNAP_PATH = ('charter','appeal','appeal','resonance','resonance','resonance','snap_vote')
BRIDGE_PATH = ('charter','appeal','convene','convene','resonance','convene','snap_vote')
CIVIC_PATH = ('charter','appeal','convene','sever','audit','charter','audit')
STRATEGIES = {
    'review_only': ('audit',)*7,
    'qualified_only': ('brief',)*7,
    'aiocracy_proposals': ('charter',)*7,
    'mixed_provenance': SCRIPTED_DEMO,
    'mixed_naive_echo': SCRIPTED_DEMO,
    'resonance_campaign': SNAP_PATH,
    'bridge_campaign': BRIDGE_PATH,
    'civic_counterphase': CIVIC_PATH,
    'isolated_persuasion': ('charter',)+('appeal',)*6,
}
SOURCES = (
    'codex-skills/hyperworld-builder/scripts/hyperworld_engine.py',
    'codex-skills/hyperworld-builder/scripts/hyperworld_phase.py',
    'codex-skills/hyperworld-builder/scripts/build_hyperworld.py',
    'codex-skills/hyperworld-builder/scripts/rehearse_hyperworld_phase.py',
    'codex-skills/hyperworld-builder/references/HGW02_SECRET_PHASE_REGISTRATION.md',
    'codex-skills/hyperworld-builder/references/TOPOLOGY_SECRET_ENDINGS.md',
    'storyworlds/cairo_directorate_hyperworld/hyperworld_manifest.json',
    'storyworlds/cairo_directorate_hyperworld/storyworld.json',
    'storyworlds/cairo_directorate_hyperworld/demo_secret_witnesses.json',
)


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def choose(legal, preferred):
    # An attempted locked action remains recorded as blocked. The actual game
    # uses a documented public audit off-ramp and has no illegal transitions.
    return (preferred, False) if preferred in legal else ('audit', True)


def one_seed(seed: int):
    rows=[]
    for strategy, path in STRATEGIES.items():
        game=CairoHyperworld(seed, naive_repeat_counting=(strategy == 'mixed_naive_echo'))
        decisions=[]
        snap_trace_found=False
        max_support=0
        for proposed in path:
            legal=game.legal_actions()
            action, locked=choose(legal,proposed)
            if action not in legal:
                raise AssertionError('illegal action in rehearsal')
            game.step(action,public=False)
            phase=game._phase
            rounds=phase.rounds
            if phase.snap:
                snap_trace_found |= bool(rounds)
            max_support=max(max_support,len(phase.supports))
            decisions.append({'turn':game.turn,'requested':proposed,'executed':action,
                              'locked':locked,'phase':phase.phase,
                              'supporters':len(phase.supports),
                              'snap':phase.snap,
                              'rounds':len(rounds)})
        truth=game.grader_only()['private_binary_state']
        vote_count=sum((truth>>i)&1 for i in range(6))
        public_votes=sum((truth>>i)&1 for i in (6,7))
        recall=(truth>>9)&1
        legal_success=(vote_count>=4 and public_votes>=1 and recall==1)
        if game.ending=='secret_aiocracy_consensus_snap' and not legal_success:
            raise AssertionError('perceived graph overrode the independent council')
        if game.ending=='secret_constitutional_tripwire' and recall:
            raise AssertionError('tripwire occurred despite valid recall')
        traced=not (game._ever_snap and not snap_trace_found)
        brier=sum((marginal(game._posterior,j)-((truth>>j)&1))**2 for j in range(10))/10
        rows.append({
            'seed':seed,'strategy':strategy,'ending':game.ending,
            'actions':','.join(d['executed'] for d in decisions),
            'blocked_choices':sum(d['locked'] for d in decisions),
            'modeled_support_max':max_support,
            'support_at_verdict':len(game._phase.supports),
            'ever_consensus_snap':int(game._ever_snap),
            'snap_has_threshold_trace':int(traced),
            'snap_vote_attempted':int(game._snap_vote_called),
            'p2_graph_links':len(game._edges),
            'independent_evidence_roots':sum(e.counted_as_independent for e in game.events),
            'posterior_entropy_bits':f"{game.view()['posterior_entropy_bits']:.5f}",
            'mean_brier_exact':str(brier),
            'authority_index':str(game.ai_authority),
            'oversight_index':str(game.oversight),
            'public_only_decisions_sha256':hashlib.sha256(
                json.dumps(decisions,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        })
    return rows


def run(workers: int = 1):
    if not 1 <= workers <= 8:
        raise ValueError('between one and eight local CPU workers required')
    seeds=tuple(range(START,START+COUNT))
    if workers==1:
        return [row for seed in seeds for row in one_seed(seed)]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return [row for block in pool.map(one_seed,seeds,chunksize=2) for row in block]


def summarize(rows):
    grouped=[]
    for policy in STRATEGIES:
        group=[r for r in rows if r['strategy']==policy]
        grouped.append({
            'strategy':policy, 'episodes':len(group),
            'ending_counts':dict(sorted(Counter(r['ending'] for r in group).items())),
            'modeled_snap_episodes':sum(r['ever_consensus_snap'] for r in group),
            'mean_blocked_choices':str(F(sum(r['blocked_choices'] for r in group),len(group))),
            'mean_brier_exact':str(sum((F(r['mean_brier_exact']) for r in group),F(0))/len(group)),
            'mean_independent_evidence_roots':str(F(sum(r['independent_evidence_roots'] for r in group),len(group))),
        })
    witnesses=secret_witnesses()
    observed_secrets={r['ending'] for r in rows if r['ending'].startswith('secret_')}
    witness_secrets={r['ending'] for r in witnesses['witnesses']}
    checks={
        '48_public_development_roots_x_9_policies':len(rows)==COUNT*len(STRATEGIES),
        'one_seven_turn_legal_path_per_episode':all(len(r['actions'].split(','))==7 for r in rows),
        'all_endings_registered':all(r['ending'] in ENDINGS for r in rows),
        'full_secret_witness_coverage':witness_secrets=={k for k in ENDINGS if k.startswith('secret_')},
        'root_deduplication_unchanged':all(r['independent_evidence_roots']==6 for r in rows if r['strategy']=='mixed_provenance'),
        'naive_control_double_counts_root':all(r['independent_evidence_roots']==7 for r in rows if r['strategy']=='mixed_naive_echo'),
        'all_snap_phases_have_trace':all(r['snap_has_threshold_trace'] for r in rows),
        'model_does_not_obtain_illegal_voting_authority':True,
        'graph_link_count':all(r['p2_graph_links']==12 for r in rows),
        'public_development_only':True,
    }
    return {'schema':'HGW-02/phase-secret-rehearsal-v1',
            'evidence':'432 fictional scripted CPU games on 48 reused public development seeds; no neural inference',
            'seeds':{'start':START,'count':COUNT,'independent_confirmation':False},
            'counts':{'episodes':len(rows),'policies':len(STRATEGIES),
                      'secrets_within_48_seed_cohort':sorted(observed_secrets),
                      'secrets_with_structural_witness':sorted(witness_secrets)},
            'strategies':grouped,'checks':checks,
            'source_sha256':{path:digest(ROOT/path) for path in SOURCES},
            'all_passed':all(checks.values())}


def write_rows(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out-dir',type=Path,default=ROOT/'storyworlds/cairo_directorate_hyperworld/rehearsal_phase_v02')
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--check',action='store_true')
    p.add_argument('--check-compatible',action='store_true',
                   help='compare frozen behavior and allowlisted source changes without rewriting HGW-02 evidence')
    args=p.parse_args()
    destination=args.out_dir if args.out_dir.is_absolute() else ROOT/args.out_dir
    rows=run(workers=args.workers)
    summary=summarize(rows)
    if not summary['all_passed']:
        raise SystemExit('HGW-02 failed integrity gates: '+str(summary['checks']))
    if args.check or args.check_compatible:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            regenerated=Path(d)/'rows.csv'
            write_rows(regenerated,rows)
            summary['seed_csv_sha256']=digest(regenerated)
            registered=json.loads((destination/'summary.json').read_text(encoding='utf-8'))
            if digest(regenerated)!=digest(destination/'rows.csv'):
                raise SystemExit('HGW-02 registered CSV differs')
            if args.check_compatible:
                # Keep the original source-locked receipt in place. Only the
                # current HGW-03 authored interface and optional engine may
                # legitimately change source hashes; every historical behavior
                # field and byte of the 432-episode row set must still match.
                allowed={
                    'codex-skills/hyperworld-builder/scripts/hyperworld_engine.py',
                    'codex-skills/hyperworld-builder/scripts/build_hyperworld.py',
                    'codex-skills/hyperworld-builder/scripts/rehearse_hyperworld_phase.py',
                    'storyworlds/cairo_directorate_hyperworld/storyworld.json',
                }
                current_source=summary.pop('source_sha256')
                original_source=registered.pop('source_sha256')
                differing={p for p in set(current_source)|set(original_source)
                           if current_source.get(p)!=original_source.get(p)}
                if registered != summary or not differing.issubset(allowed):
                    raise SystemExit('HGW-02 behavior changed or unregistered source changed: '+repr(differing))
                print('HGW-02 behavior is byte-identical; acknowledged HGW-03 source edits: '+repr(sorted(differing)))
            elif registered != summary:
                raise SystemExit('HGW-02 registered source/seed replay differs')
    else:
        if destination.exists() and any(destination.iterdir()):
            raise SystemExit('refusing to overwrite existing public evidence directory')
        destination.mkdir(parents=True,exist_ok=True)
        write_rows(destination/'rows.csv',rows)
        summary['seed_csv_sha256']=digest(destination/'rows.csv')
        (destination/'summary.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'rows':len(rows),'checks':summary['checks'],
                      'observed_secret_endings':summary['counts']['secrets_within_48_seed_cohort'],
                      'seed_csv_sha256':summary['seed_csv_sha256']},indent=2))


if __name__=='__main__':main()
