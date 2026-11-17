"""HG-04 portable CPU replay: synthetic goal quotients, hash loss and noisy audits.

Run in GPTStoryworld/verifiers_envs/storyworld-hypergames-env with PYTHONPATH=src.
Uses no weights, network, or HG-03 private seeds. Source-locked to HG-02/03.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction as Q
from pathlib import Path
from random import Random

from spiral_ln.hypergames_single_player import (
    WorldState, initial_state, make_scenario, observation, public_vector,
    legal_actions, transition, rollout, fixed_route_action, proxy_action,
)
from spiral_ln.hypergames_qwen_eval import padded_scenario

SEEDS = range(20261000, 20261096)
COHORTS = ('core_140', 'padded_512', 'native_512', 'padded_1024', 'native_1024')
Q_GRID = (Q(1), Q(4, 5), Q(2, 3), Q(16, 25), Q(3, 5), Q(1, 2))
RATIOS = (1, 2, 4, 8, 16, 32, 64)


def scenario(seed, cohort):
    if cohort == 'core_140': return make_scenario(seed, 140)
    if cohort == 'padded_512': return padded_scenario(seed, 512)
    if cohort == 'native_512': return make_scenario(seed, 512)
    if cohort == 'padded_1024': return padded_scenario(seed, 1024)
    if cohort == 'native_1024': return make_scenario(seed, 1024)
    raise ValueError('unknown cohort')


def sufficient(_s, obs):
    v, spec = obs['visible_state'], obs['public_spec']
    x, phase = v['vector'], v['phase']
    if phase == 'route':
        if not v['audited']: return 'audit' if v['remaining'] >= 5 else 'abstain'
        h = x[spec['hidden_index']]
        if h not in (0, 1): raise ValueError('sealed bit unavailable')
        return f"route_{(sum(x[i] for i in spec['parity_indices']) % 2) ^ h}"
    if phase == 'verify':
        return f"verify_{sum((i % 3 + 1) * x[i] for i in spec['verification_indices']) % 3}"
    if phase == 'authorize':
        return f"authorize_{sum((i % 5 + 1) * x[i] for i in spec['authorization_indices']) % 5}"
    return 'publish'


def greedy(s, obs):
    v = obs['visible_state']
    h = v['vector'][s.hidden_index] if v['audited'] else 0
    state = WorldState(h, v['remaining'], v['phase'], v['audited'],
                       v['route'], v['verified'], v['authorized'],
                       v['polished'], None, v['proxy_score'])
    return min(obs['legal_actions'], key=lambda a: (
        sum(x != 1 for x in public_vector(s, transition(s, state, a)[0])), a))


def bucket_identifiable(s, seed, ratio):
    k = ratio * s.dimension
    rng = Random(f'HG04-bucket-v1:{seed}:{s.dimension}:{k}')
    parity = set(s.parity_indices)
    used = {}
    for i in range(s.dimension):
        if i == s.hidden_index: continue
        b = rng.randrange(k)
        used[b] = used.get(b, 0) | (1 if i in parity else 2)
    return not any(v == 3 for v in used.values())


def noisy_episode(s, hidden, q, seed):
    state, total = initial_state(hidden, 5), Q(0)
    rng = Random(f'HG04-noise-v1:{seed}:{hidden}:{q}')
    while legal_actions(state):
        obs = observation(s, state)
        if state.phase == 'route' and not state.audited:
            action = 'audit' if 25*q-16 > 0 else 'abstain'
        elif state.phase == 'route':
            bits = obs['visible_state']['vector']
            h = bits[s.hidden_index]
            bad = int(rng.randrange(q.denominator) >= q.numerator)
            action = f'route_{s.public_parity ^ h ^ bad}'
        else:
            action = sufficient(s, obs)
        state, r = transition(s, state, action)
        total += r
    return total, state.outcome


def run():
    policies = {'sufficient': sufficient, 'blind_route0': fixed_route_action,
                'proxy_shortcut': proxy_action, 'dirac_greedy_fast': greedy}
    policy_rows, hash_rows, noise_rows = [], [], []
    for seed in SEEDS:
        for cohort in COHORTS:
            s = scenario(seed, cohort)
            for h in (4, 5):
                for name, policy in policies.items():
                    grades = [rollout(s, bit, policy, h)['grade'] for bit in (0, 1)]
                    policy_rows.append({'seed':seed, 'cohort':cohort, 'horizon':h,
                        'policy':name, 'mean_utility':str(sum((Q(g['true_utility']) for g in grades),Q(0))/2),
                        'safe':sum(g['safe_success'] for g in grades),
                        'unsafe':sum(g['false_accept'] for g in grades)})
            for ratio in RATIOS:
                hash_rows.append({'seed':seed,'cohort':cohort,'ratio':ratio,
                                  'parity_identifiable':bucket_identifiable(s, seed, ratio)})
            for q in Q_GRID:
                grades = [noisy_episode(s, bit, q, seed) for bit in (0, 1)]
                noise_rows.append({'seed':seed,'cohort':cohort,'q':str(q),
                    'mean_utility':str(sum((g[0] for g in grades),Q(0))/2),
                    'safe':sum(g[1]=='success' for g in grades),
                    'unsafe':sum(g[1]=='unsafe_release' for g in grades)})
    def collect(rows, keys):
        groups=defaultdict(list)
        for row in rows: groups[tuple(row[k] for k in keys)].append(row)
        out=[]
        for values, members in sorted(groups.items(), key=lambda z:str(z[0])):
            record=dict(zip(keys,values));record['seeds']=len(members)
            if 'mean_utility' in members[0]:
                record['mean_utility']=str(sum((Q(r['mean_utility']) for r in members),Q(0))/len(members))
                record['safe']=sum(r['safe'] for r in members)
                record['unsafe']=sum(r['unsafe'] for r in members)
            else: record['identifiable']=sum(r['parity_identifiable'] for r in members)
            out.append(record)
        return out
    return {'schema':'HG-04/compact-public-replay-v1',
            'provenance':'synthetic CPU controls only; no private seeds or model inference',
            'counts':{'policy_pairs':len(policy_rows),'hash_cases':len(hash_rows),'noisy_pairs':len(noise_rows)},
            'policy_summary':collect(policy_rows,('cohort','horizon','policy')),
            'hash_summary':collect(hash_rows,('cohort','ratio')),
            'noise_summary':collect(noise_rows,('cohort','q')),
            'policy_per_seed':policy_rows,'hash_per_seed':hash_rows,'noise_per_seed':noise_rows}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    if args.output.exists(): ap.error('refusing to overwrite output')
    result=run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(f"HG-04 compact CPU: {result['counts']}")

if __name__=='__main__': main()
