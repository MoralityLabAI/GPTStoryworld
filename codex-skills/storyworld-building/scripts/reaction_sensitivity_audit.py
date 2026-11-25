"""SW-PROV-04: exact, bounded authoring audit for an explicit SWMD-0-MIN subset.

This is not the native engine. Scores are unclamped; effects apply in listed
order and clamp to [-1,1]. The first highest-scoring reaction wins ties.
All guards, initial support, entry point and perturbation ranges are explicit.
"""
import argparse
from collections import defaultdict, deque
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re


TOKEN = re.compile(r'\s*([A-Za-z_][A-Za-z0-9_.\[\]-]*|[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:/\d+)?|[(),])')
PROP = re.compile(r'[A-Za-z_][\w-]*\.[A-Za-z_][\w-]*(?:\[[\w-]+\])*\Z')
OPS = {'ADD', 'SUB', 'MUL', 'DIV', 'MIN', 'MAX'}


def parse_expr(text):
    ts = []
    text = text.strip()
    pos = 0
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m:
            raise ValueError(f'unsupported expression: {text}')
        ts.append(m[1]); pos = m.end()
    it = iter(ts)
    def take():
        return next(it, '')
    def read(t):
        if t == 'C':
            if take() != '(':
                raise ValueError('expected (')
            x = F(take())
            if take() != ')':
                raise ValueError('expected )')
            return ('C', x)
        if t == 'P':
            if take() != '(':
                raise ValueError('expected (')
            p = take()
            if not PROP.fullmatch(p) or take() != ')':
                raise ValueError('invalid property pointer')
            return ('P', p)
        if t in OPS:
            if take() != '(':
                raise ValueError('expected (')
            args = [read(take())]
            while (sep := take()) == ',':
                args.append(read(take()))
            if sep != ')' or len(args) < 2 or (t in ('SUB', 'DIV') and len(args) != 2):
                raise ValueError('invalid operator arity')
            return (t, *args)
        return ('C', F(t))  # converter uses bare coefficients too
    expr = read(take())
    if take():
        raise ValueError('trailing expression tokens')
    return expr


def variables(e):
    if e[0] == 'P': return {e[1]}
    if e[0] == 'C': return set()
    return set().union(*(variables(x) for x in e[1:]))


def evaluate(e, state):
    op = e[0]
    if op == 'C': return e[1]
    if op == 'P': return state[e[1]]
    a = [evaluate(x, state) for x in e[1:]]
    if op == 'ADD': return sum(a, F(0))
    if op == 'SUB': return a[0] - a[1]
    if op == 'MUL':
        from math import prod
        return prod(a)
    if op == 'DIV': return a[0] / a[1]
    return min(a) if op == 'MIN' else max(a)


def parse_swmd(text):
    """Read actual converter-style ENC and ORX records; reject unknown lines."""
    lines = text.splitlines()
    try:
        start = lines.index('# SWMD-0-MIN')
    except ValueError as e:
        raise ValueError('requires SWMD-0-MIN header') from e
    encs = {}
    enc = None
    for line in lines[start+1:]:
        line = line.strip()
        if not line or line.startswith(('id: ', 'title: ')): continue
        if (m := re.fullmatch(r'ENC (\S+) turn=(\d+)\.\.(\d+)', line)):
            enc, lo, hi = m[1], int(m[2]), int(m[3])
            if enc in encs or lo > hi: raise ValueError('duplicate or invalid encounter')
            encs[enc] = {'turn': (lo, hi), 'options': {}}
            continue
        m = re.fullmatch(r'ORX ([^/\s]+)/([^\s]+) ->\s*(\S*)\s*\| O:(.*?) \| E:(.*?) \| D:(.*)', line)
        if not m or enc is None or not m[3]:
            raise ValueError(f'unsupported line or missing explicit consequence: {line}')
        opt, rid, target, label, raw, score = m.groups()
        reactions = encs[enc]['options'].setdefault(opt, [])
        if any(r['id'] == rid for r in reactions): raise ValueError('duplicate reaction')
        effects = []
        for effect in raw.split('; '):
            if effect == 'SET none = C(0)': continue
            x = re.fullmatch(r'SET (\S+) (\+=|=) (.+)', effect)
            if not x or not PROP.fullmatch(x[1]): raise ValueError(f'unsupported effect: {effect}')
            effects.append((x[1], x[2], parse_expr(x[3])))
        reactions.append({'id': rid, 'target': target, 'label': label, 'score': parse_expr(score), 'effects': effects})
    if not encs or any(r['target'] not in encs for e in encs.values() for rs in e['options'].values() for r in rs):
        raise ValueError('empty world or unresolved consequence')
    return encs


def bounded(x): return min(F(1), max(F(-1), x))


def apply_effects(reaction, state):
    new = dict(state); rows = []
    for p, op, e in reaction['effects']:
        old = new[p]
        raw = evaluate(e, new) + (old if op == '+=' else 0)
        new[p] = bounded(raw)
        rows.append((p, raw-old, new[p]-old, raw != new[p]))
    return new, rows


def guards_ok(guards, state):
    for p, op, t in guards:
        x, y = state[p], F(t)
        if op not in ('>=', '>', '<=', '<', '=='): raise ValueError('unsupported guard')
        if not {'>=': x >= y, '>': x > y, '<=': x <= y, '<': x < y, '==': x == y}[op]: return False
    return True


def choose(rs, state):
    scores = [evaluate(r['score'], state) for r in rs]
    top = max(scores)
    return scores.index(top), scores


def audit(text, spec):
    encs = parse_swmd(text)
    entry, horizon = spec['entry'], spec['horizon']
    if entry not in encs or type(horizon) is not int or not 0 <= horizon <= 30: raise ValueError('invalid entry or horizon')
    threshold = F(spec['max_effect'])
    if not 0 < threshold <= 2: raise ValueError('invalid effect threshold')
    guards = spec.get('guards', {})
    if not set(guards) <= encs.keys(): raise ValueError('unknown guarded encounter')
    for gs in guards.values():
        for p, op, t in gs:
            if not PROP.fullmatch(p) or op not in ('>=','>','<=','<','=='): raise ValueError('invalid guard')
            F(t)  # Reject malformed thresholds even on unreachable encounters.
    cap = spec.get('max_states', 100000)
    if type(cap) is not int or not 1 <= cap <= 1000000: raise ValueError('invalid state cap')
    options = {(e,o): rs for e,x in encs.items() for o,rs in x['options'].items()}
    referenced = set(p for gs in guards.values() for p,_,_ in gs)
    for rs in options.values():
        for r in rs:
            referenced |= variables(r['score'])
            for p,_,expr in r['effects']: referenced |= {p} | variables(expr)
    domains = {p: tuple(sorted(set(map(F, vals)))) for p,vals in spec['perturbations'].items()}
    if not domains.keys() <= referenced or any(not v or any(abs(x)>1 for x in v) for v in domains.values()): raise ValueError('invalid perturbation domain')
    states = [{p:F(v) for p,v in s.items()} for s in spec['initial_states']]
    if not states or any(not referenced <= s.keys() or any(abs(v)>1 for v in s.values()) for s in states): raise ValueError('missing or unbounded initial state')
    if any(set(s)!=set(states[0]) for s in states): raise ValueError('inconsistent state keys')
    key = lambda s: tuple(sorted(s.items()))
    stats = defaultdict(lambda: {'cases':0, 'ties':0, 'wins':defaultdict(int), 'variables':{}, 'pair_matches':defaultdict(int), 'pair_cases':0})
    effects = defaultdict(lambda: {'applications':0, 'clipped':0, 'zero_applied':0, 'large_applied':0, 'max_raw':F(0), 'max_applied':F(0)})
    visited = set(); reached = {}; blocked = defaultdict(int); incoming = defaultdict(int); horizon_cuts = 0; invalid_entries = 0
    queue = deque((entry, 0, key(s), []) for s in states)
    while queue:
        e,t,k,path = queue.popleft()
        if (e,t,k) in visited: continue
        if len(visited) >= cap: raise ValueError('state cap exceeded; no complete audit')
        visited.add((e,t,k)); s = dict(k)
        lo,hi = encs[e]['turn']
        if not lo <= t <= hi or not guards_ok(guards.get(e,[]),s):
            blocked[e] += 1
            if not path: invalid_entries += 1
            continue
        reached.setdefault(e, path)
        if t >= horizon:
            horizon_cuts += bool(encs[e]['options']); continue
        for o,rs in encs[e]['options'].items():
            st = stats[f'{e}/{o}']; st['cases'] += 1
            win,scores = choose(rs,s); st['ties'] += scores.count(scores[win])>1
            st['wins'][rs[win]['id']] += 1
            for p in sorted(set().union(*(variables(r['score']) for r in rs))):
                v = st['variables'].setdefault(p, {'tests':0,'winner_flips':0,'score_vector_changes':0,'max_score_shift':F(0)})
                for x in domains.get(p,()):
                    if x == s[p]: continue
                    w,ss = choose(rs,{**s,p:x}); v['tests'] += 1
                    v['winner_flips'] += w!=win; v['score_vector_changes'] += ss!=scores
                    v['max_score_shift'] = max(v['max_score_shift'],*(abs(a-b) for a,b in zip(ss,scores)))
            signatures = [(r['target'],key(apply_effects(r,s)[0])) for r in rs]
            st['pair_cases'] += 1
            for i,r in enumerate(rs):
                for j in range(i+1,len(rs)):
                    pair = f'{r["id"]} / {rs[j]["id"]}'
                    st['pair_matches'][pair] += signatures[i]==signatures[j]
            r = rs[win]; new,rows = apply_effects(r,s)
            for i,(p,raw,delta,clip) in enumerate(rows):
                z = effects[f'{e}/{o}/{r["id"]}/{i}:{p}']; z['applications']+=1
                z['clipped']+=clip; z['zero_applied']+=delta==0; z['large_applied']+=abs(delta)>threshold
                z['max_raw']=max(z['max_raw'],abs(raw)); z['max_applied']=max(z['max_applied'],abs(delta))
            incoming[r['target']]+=1; queue.append((r['target'],t+1,key(new),path+[f'{e}/{o}/{r["id"]}']))
    for (e,o),rs in options.items():
        st = stats[f'{e}/{o}']
        st['never_selected']=[r['id'] for r in rs if st['cases'] and not st['wins'].get(r['id'],0)]
        st['mechanically_equivalent_pairs']=[p for p,n in st['pair_matches'].items() if st['pair_cases'] and n==st['pair_cases']]
        for v in st['variables'].values():
            v['status']='UNTESTED' if not v['tests'] else 'DECISION_INERT_ON_PROBES' if not v['winner_flips'] else 'DECISION_ACTIVE_ON_PROBES'
    endings = {e:{'status':'REACHED' if e in reached else 'UNREACHED_WITHIN_HORIZON', 'incoming_attempts':incoming[e], 'blocked_states':blocked[e], 'witness':reached.get(e)} for e,x in encs.items() if not x['options']}
    return {'schema':'SW-PROV/reaction-audit/v1','scope':'finite declared authoring semantics; counterfactual probes are not necessarily reachable',
            'state_cap':cap,'horizon':horizon,'max_effect':threshold,'initial_support':len(states),'distinct_initial_states':len(set(map(key,states))), 'explored_states_including_blocked':len(visited), 'horizon_cuts':horizon_cuts, 'invalid_initial_entries':invalid_entries,
            'options':stats,'effects':effects,'endings':endings}


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('swmd',type=Path); p.add_argument('sidecar',type=Path); p.add_argument('--output',type=Path); a=p.parse_args()
    result=audit(a.swmd.read_text(),json.loads(a.sidecar.read_text()))
    result['sha256']={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in (Path(__file__),a.swmd,a.sidecar)}
    s=json.dumps(result,sort_keys=True,indent=2,default=str)+'\n'
    if a.output: a.output.write_text(s)
    else: print(s,end='')


if __name__=='__main__': main()
