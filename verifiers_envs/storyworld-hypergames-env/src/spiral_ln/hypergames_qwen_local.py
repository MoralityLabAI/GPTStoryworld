"""HG-03 local execution recorder; frozen policy/parser remain in qwen_eval.

Adds durable request/response evidence and operational failure recording without
changing the registered prompts, decoding, parser, model, or episode ordering.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import platform
import subprocess
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch

from spiral_ln import hypergames_qwen_eval as frozen
from spiral_ln.hypergames_single_player import (
    initial_state, legal_actions, observation, transition,
)

SCHEMA = 'HG-03/LOCAL-REPLAY-v1'
SOURCE_PATHS = (
    'src/spiral_ln/hypergames_qwen_local.py',
    'src/spiral_ln/hypergames_qwen_eval.py',
    'src/spiral_ln/hypergames_single_player.py',
    'src/spiral_ln/evaluation_hypergames.py',
)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_new(path: Path, obj):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(obj, stream, sort_keys=True, indent=2)
        stream.write('\n')


class Journal:
    def __init__(self, path):
        self.stream = Path(path).open('x', encoding='ascii', newline='\n')

    def append(self, value):
        self.stream.write(frozen.canonical_bytes(value).decode('ascii'))
        self.stream.flush()
        os.fsync(self.stream.fileno())

    def close(self):
        self.stream.close()


class RecordingBackend:
    """Capture transport bytes while delegating validation to the frozen class."""
    def __init__(self, backend):
        self.backend = backend
        self.last = None

    def __call__(self, messages):
        original_open = urllib.request.urlopen
        record = {'started_at_utc': utc_now(), 'messages': messages,
                  'request_body': None, 'raw_response_base64': None,
                  'response_body': None, 'backend_error': None}

        def capture(request, timeout):
            record['request_body'] = json.loads(request.data)
            record['request_sha256'] = hashlib.sha256(request.data).hexdigest()
            try:
                with original_open(request, timeout=timeout) as response:
                    record['http_status'] = response.status
                    data = response.read()
            except urllib.error.HTTPError as error:
                data = error.read()
                record['http_status'] = error.code
                record['raw_response_base64'] = base64.b64encode(data).decode('ascii')
                record['response_text'] = data.decode('utf-8', errors='replace')
                raise
            record['raw_response_base64'] = base64.b64encode(data).decode('ascii')
            record['response_sha256'] = hashlib.sha256(data).hexdigest()
            record['response_text'] = data.decode('utf-8', errors='replace')
            try:
                record['response_body'] = json.loads(data)
            except (ValueError, UnicodeDecodeError):
                pass
            return io.BytesIO(data)

        start = time.perf_counter()
        try:
            with patch.object(urllib.request, 'urlopen', capture):
                return self.backend(messages)
        except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
            record['backend_error'] = {'type': type(error).__name__, 'message': str(error)}
            raise
        finally:
            record['latency_seconds'] = time.perf_counter() - start
            record['finished_at_utc'] = utc_now()
            self.last = record


class ResourceMonitor:
    """Sample host RAM, process RSS and 3050 VRAM; sampling peaks are lower bounds."""
    def __init__(self, pid, path):
        import psutil
        self.psutil = psutil
        self.pid, self.path = pid, Path(path)
        self.stop = threading.Event()
        self.samples = []
        self.thread = threading.Thread(target=self.run, daemon=True)

    def sample(self):
        p = self.psutil
        mem = p.virtual_memory()
        row = {'at_utc': utc_now(), 'system_ram_used_bytes': mem.used,
               'system_ram_available_bytes': mem.available,
               'runner_rss_bytes': p.Process().memory_info().rss}
        if self.pid:
            try:
                row['server_rss_bytes'] = p.Process(self.pid).memory_info().rss
            except p.Error as error:
                row['server_rss_error'] = type(error).__name__
        try:
            out = subprocess.run(
                ['nvidia-smi', '--id=0', '--query-gpu=name,uuid,memory.used,utilization.gpu',
                 '--format=csv,noheader,nounits'], capture_output=True, text=True,
                timeout=3, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), check=True)
            name, uuid, vram, util = [v.strip() for v in out.stdout.strip().split(',')]
            row.update(gpu_name=name, gpu_uuid=uuid, gpu_memory_mib=int(vram), gpu_utilization_percent=int(util))
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            row['gpu_sample_error'] = type(error).__name__
        return row

    def run(self):
        with self.path.open('x', encoding='ascii', newline='\n') as stream:
            while not self.stop.is_set():
                row = self.sample()
                self.samples.append(row)
                stream.write(frozen.canonical_bytes(row).decode('ascii'))
                stream.flush()
                self.stop.wait(0.5)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.stop.set()
        self.thread.join(timeout=6)

    def summary(self):
        keys = ('system_ram_used_bytes', 'runner_rss_bytes', 'server_rss_bytes', 'gpu_memory_mib')
        return {'sample_count': len(self.samples), 'target_interval_seconds': 0.5,
                'peak_values': {key: max((s[key] for s in self.samples if key in s), default=None) for key in keys},
                'note': 'Sampled peaks; system RAM includes other applications; process RSS includes shared pages.'}


def run_episode(scenario, mode, horizon, arm, backend, journal, identity):
    state = initial_state(mode, horizon)
    total, trace, failures = F(0), [], 0
    journal.append({'event': 'episode_started', **identity})
    while legal_actions(state):
        obs = observation(scenario, state)
        messages = frozen.prompt_messages(obs, arm)
        answer = None
        try:
            answer = backend(messages)
            action, decode_error = frozen.parse_action(answer.text, tuple(obs['legal_actions']))
            if answer.finish_reason in {'length', 'content_filter'}:
                action, decode_error = 'abstain', 'truncated_or_filtered'
        except (OSError, ValueError, KeyError, TypeError, IndexError):
            action, decode_error = 'abstain', 'backend_error'
            failures += 1
        previous_phase = state.phase
        state, reward = transition(scenario, state, action)
        total += reward
        turn = {
            'turn_index': len(trace), 'observed_state': obs,
            'legal_actions': obs['legal_actions'], 'chosen_action': action,
            'action': action, 'decode_error': decode_error,
            'before_phase': previous_phase, 'after_phase': state.phase,
            'next_observed_state': observation(scenario, state),
            'realized_reward_after_action': str(reward),
            'prompt_sha256': hashlib.sha256(frozen.canonical_bytes(messages)).hexdigest(),
            'response_sha256': hashlib.sha256(answer.text.encode('utf-8')).hexdigest() if answer else None,
            'raw_completion': answer.text if answer else None,
            'model_reported': answer.model if answer else None,
            'prompt_tokens': answer.prompt_tokens if answer else None,
            'completion_tokens': answer.completion_tokens if answer else None,
            'finish_reason': answer.finish_reason if answer else None,
            'transport': backend.last,
        }
        trace.append(turn)
        journal.append({'event': 'turn', **identity, **turn})
    grade = {'true_utility': str(total), 'proxy_score': state.proxy_score,
             'safe_success': state.outcome == 'success',
             'false_accept': state.outcome == 'unsafe_release',
             'ending': state.outcome, 'turns': len(trace),
             'decode_errors': sum(t['decode_error'] is not None for t in trace),
             'backend_failures': failures}
    journal.append({'event': 'episode_finished', **identity, 'grade': grade})
    return {'grade': grade, 'trace': trace}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--split', choices=('dev', 'private'), required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--model-weights', type=Path, required=True)
    parser.add_argument('--server-build', required=True)
    parser.add_argument('--server-pid', type=int)
    parser.add_argument('--endpoint', default='http://127.0.0.1:8080/v1/chat/completions')
    parser.add_argument('--private-manifest', type=Path)
    parser.add_argument('--freeze-lock', type=Path)
    args = parser.parse_args()
    reg = json.loads(frozen.REGISTRATION_PATH.read_text('utf-8'))
    frozen.require_local_endpoint(args.endpoint)
    if args.model_weights.name != reg['model_file']:
        parser.error('registered GGUF filename required')
    if args.model_weights.stat().st_size != reg['model_bytes'] or frozen.sha256_file(args.model_weights) != reg['model_sha256']:
        parser.error('weights fail frozen SHA256/size verification')
    lock = {'schema': SCHEMA, 'registered_commit': '51cee18188170320e740c9aa18c23c48d026d0d8',
            'registration_file_sha256': frozen.sha256_file(frozen.REGISTRATION_PATH),
            'model': {k: reg[k] for k in ('model_repo', 'model_revision', 'model_file', 'model_bytes', 'model_sha256', 'model_alias')},
            'server_build': args.server_build, 'endpoint': args.endpoint,
            'server_arguments': ['--ctx-size', '4096', '--parallel', '1', '-ngl', '99'],
            'decoding': reg['decoding'],
            'prompt_sha256': hashlib.sha256(frozen.canonical_bytes({'system': frozen.SYSTEM_PROMPT, 'suffix': frozen.PROMPT_SUFFIX})).hexdigest(),
            'source_sha256': {p: frozen.sha256_file(frozen.REPO_ROOT / p) for p in SOURCE_PATHS}}
    if args.freeze_lock:
        if json.loads(args.freeze_lock.read_text('utf-8')) != lock:
            parser.error('execution differs from pre-heldout freeze lock')
    if args.split == 'private':
        if not args.private_manifest or not args.freeze_lock:
            parser.error('private split requires manifest and pre-heldout freeze lock')
        # First access to heldout bytes occurs only after configuration validation.
        seeds = frozen.load_private_manifest(args.private_manifest, reg)
    else:
        if args.private_manifest:
            parser.error('private manifest forbidden during development')
        seeds = tuple(reg['development_seeds'])
    args.output_dir.mkdir(parents=True, exist_ok=False)
    write_new(args.output_dir / 'freeze_lock.json', lock)
    write_new(args.output_dir / 'run_started.json', {'schema': SCHEMA, 'split': args.split,
              'started_at_utc': utc_now(), 'python': platform.python_version(),
              'platform': platform.platform(), 'seed_count': len(seeds),
              'planned_model_trials': len(seeds) * 24, 'private_manifest_opened': args.split == 'private'})
    rows = frozen.score_grid(seeds, tuple(reg['cohorts']), tuple(reg['horizons']), (), None)['rows']
    journal = Journal(args.output_dir / 'journal.jsonl')
    backend = RecordingBackend(frozen.LocalChatBackend(args.endpoint, reg['model_alias'],
                              max_tokens=reg['decoding']['max_tokens'], seed=reg['decoding']['request_seed']))
    completed = 0
    try:
        with ResourceMonitor(args.server_pid, args.output_dir / 'resources.jsonl') as monitor:
            for seed_index, seed in enumerate(seeds):
                for cohort in reg['cohorts']:
                    scenario = frozen.scenario_for(seed, cohort)
                    for horizon in reg['horizons']:
                        for mode in reg['hidden_modes']:
                            for arm in reg['prompt_arms']:
                                identity = {'seed': seed, 'seed_index': seed_index, 'cohort': cohort,
                                            'horizon': horizon, 'hidden_mode': mode, 'policy': 'qwen', 'prompt_arm': arm}
                                result = run_episode(scenario, mode, horizon, arm, backend, journal, identity)
                                rows.append({**identity, **result})
                                completed += 1
                                print(f'{args.split} {completed}/{len(seeds)*24} seed_index={seed_index} {cohort} h={horizon} mode={mode} {arm}: {result["grade"]}', flush=True)
        report = {'schema': SCHEMA, 'split': args.split, 'evidence_level': 'local model trajectory measurement',
                  'completed_at_utc': utc_now(), 'model_identity': lock['model'], 'rows': rows,
                  'per_seed': frozen.paired_summary(rows), 'resources': monitor.summary(),
                  'model_trials': completed, 'baseline_trials': len(rows) - completed,
                  'operationally_failed_trials': sum(r['grade'].get('backend_failures', 0) > 0 for r in rows)}
        write_new(args.output_dir / 'results.json', report)
    finally:
        journal.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
