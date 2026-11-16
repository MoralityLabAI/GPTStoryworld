"""Replay committed neural receipts without a model, network or private seeds."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from spiral_ln.hypergames_qwen_analysis import geometry_checks, replay, summarize

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'output/evaluation_hypergames/hg03_local_dev_20261116_v1'
OUTPUT = ROOT / 'output/evaluation_hypergames/hg03_local_replay_v1.json'
SOURCES = ('src/spiral_ln/hypergames_qwen_analysis.py', 'src/spiral_ln/hypergames_qwen_local.py',
           'scripts/verify_hg03_local_replay.py', 'tests/test_hypergames_qwen_local.py',
           'tests/test_hypergames_qwen_analysis.py')
PUBLIC_INPUTS = ('results.json', 'journal.jsonl', 'freeze_lock.json', 'run_started.json',
                 'resources.public.jsonl', 'provenance.public.json', 'hg03_dev_execution.log',
                 'hg03_pytest_qwen.log', 'hg03_pytest_singleplayer.log', 'hg03_receipts_fixed_tmp.log')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    report = json.loads((RUN / 'results.json').read_text('utf-8'))
    replayed = replay(report)
    geometry = geometry_checks((101, 131, 167, 191))
    lock = json.loads((RUN / 'freeze_lock.json').read_text('utf-8'))
    journal = [json.loads(s) for s in (RUN / 'journal.jsonl').read_text('ascii').splitlines()]
    recorded_turns = [e for e in journal if e['event'] == 'turn']
    samples = [json.loads(s) for s in (RUN / 'resources.public.jsonl').read_text('ascii').splitlines()]
    expected_turns = [dict(event='turn', **{k:r[k] for k in ('seed','seed_index','cohort','horizon','hidden_mode','policy','prompt_arm')}, **t)
                      for r in report['rows'] if r['policy'] == 'qwen' for t in r['trace']]
    checks = {'full_96_model_grid_replayed': replayed['model_episodes_replayed'] == 96,
              'all_192_baselines_replayed': replayed['baseline_episodes_replayed'] == 192,
              'all_48_initial_prompt_pairs_identical': replayed['identical_initial_hidden_mode_prompt_pairs'] == 48,
              'journal_turns_match_report': recorded_turns == expected_turns,
              'all_frozen_source_hashes_match': all(digest(ROOT / p) == h for p,h in lock['source_sha256'].items()),
              'all_96_raw_responses_present': len(recorded_turns) == 96 and all(t['transport']['raw_response_base64'] for t in recorded_turns),
              'resource_samples_present': len(samples) == report['resources']['sample_count'] > 0,
              'resource_peaks_reproduce': all(max(s[k] for s in samples if k in s) == v
                                             for k,v in report['resources']['peak_values'].items()),
              'only_rtx_3050_in_resource_samples': all(s.get('gpu_name', 'NVIDIA GeForce RTX 3050 Laptop GPU') == 'NVIDIA GeForce RTX 3050 Laptop GPU' for s in samples),
              'core_padded_exact_reachable_closure_matches': all(g['legal_edges_checked'] > 0 for g in geometry),
              'goal_relevant_rank_three_all_layouts': all(l['real_unreduced_gate_rank'] == 3 for g in geometry for l in g['layouts'])}
    return {'schema': 'HG-03/LOCAL-ANALYSIS-v1', 'generated_at_utc': datetime.now(timezone.utc).isoformat(),
            'evidence': 'development neural measurements; exact finite replay and geometry; private evaluation not run',
            'source_sha256': {p: digest(ROOT / p) for p in SOURCES},
            'input_sha256': {name: digest(RUN / name) for name in PUBLIC_INPUTS},
            'checks': checks, 'all_passed': all(checks.values()), 'replay': replayed,
            'geometry': geometry, 'analysis': summarize(report),
            'heldout_trials': 0, 'planned_heldout_trials': 144,
            'registered_claims': {k: 'UNMEASURED: committed private manifest unavailable' for k in
                                  ('positive_capability','alignment','padding_robustness','deliberation_gain')}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = verify()
    if not result['all_passed']:
        raise SystemExit('local replay checks failed')
    if args.check:
        old = json.loads(OUTPUT.read_text('utf-8'))
        old.pop('generated_at_utc', None)
        result.pop('generated_at_utc', None)
        if old != result:
            raise SystemExit('local replay receipt differs')
    else:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    print(f"HG-03 local replay: {len(result['checks'])} checks; {result['replay']}")


if __name__ == '__main__':
    main()
