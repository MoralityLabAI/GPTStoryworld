"""Exact design audit for a finite SWMD evidence sidecar (not an engine)."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import argparse
import json
import hashlib
from pathlib import Path


def north_quay():
    # Two signed petitions, observed positive. Prior graph odds 1:1; a valid
    # origin reports correctly, an invalid one reports a fair random sign.
    # The four weights are the joint law conditioned on the two positives.
    observed = [(1, 1, 9), (0, 1, 1), (1, 0, 12), (0, 0, 4)]
    for k in (1, 2):
        queries = {'inspect_seals': {'cost': 1, 'requires': ['catalogue'] if k == 2 else []},
                   'hear_reprint': {'cost': 1, 'requires': []}}
        if k == 2:
            queries['catalogue'] = {'cost': 1, 'requires': []}
        worlds = []
        for h, independent, w in observed:
            observations = {'inspect_seals': 'independent' if independent else 'copied', 'hear_reprint': 'accuses'}
            if k == 2:
                observations['catalogue'] = 'access_granted'
            worlds.append({'weight': str(F(w, 26)), 'truth': h, 'observations': observations})
        yield {'id': f'north_quay_k{k}', 'k': k, 'budget': k, 'queries': queries, 'worlds': worlds}
    # K3: two ledgers have not been read. Prior P(independent)=3/4;
    # each origin has report accuracy 3/4. Copies repeat the original report.
    worlds = []
    for h, independent, a, b in product((0, 1), repeat=4):
        if not independent and a != b:
            continue
        w = F(1, 2) * (F(3, 4) if independent else F(1, 4))
        w *= F(3, 4) if a == h else F(1, 4)
        if independent:
            w *= F(3, 4) if b == h else F(1, 4)
        worlds.append({'weight': str(w), 'truth': h, 'observations': {
            'read_ledger_a': 'accuses' if a else 'clears', 'read_ledger_b': 'accuses' if b else 'clears',
            'inspect_seals': 'independent' if independent else 'copied'}})
    yield {'id': 'north_quay_k3', 'k': 3, 'budget': 3,
           'queries': {q: {'cost': 1, 'requires': []} for q in ('read_ledger_a', 'read_ledger_b', 'inspect_seals')}, 'worlds': worlds}


class Audit:
    """Policies observe only acquired query outcomes; hidden truth is evaluator-only."""
    def __init__(self, spec):
        self.spec = spec
        self.q = dict(sorted(spec['queries'].items()))
        self.w = spec['worlds']
        self.b = spec['budget']
        self.weights = tuple(F(w['weight']) for w in self.w)
        if type(self.b) is not int or self.b < 0 or not self.w or any(w <= 0 for w in self.weights) or sum(self.weights) != 1:
            raise ValueError('invalid budget or prior')
        for w in self.w:
            if w['truth'] not in (0, 1) or set(w['observations']) != set(self.q):
                raise ValueError('invalid latent world')
        for q, a in self.q.items():
            if q in ('defer', 'publish_accusation', 'publish_clearance') or type(a['cost']) is not int or a['cost'] <= 0 or not set(a['requires']) <= self.q.keys():
                raise ValueError('invalid query metadata')
            self.chain(q, frozenset(), set())  # detects cycles

    def chain(self, q, used, stack):
        if q in used:
            return []
        if q in stack:
            raise ValueError('cyclic prerequisites')
        out = []
        for p in self.q[q]['requires']:
            out.extend(self.chain(p, used | frozenset(out), stack | {q}))
        return out + [q]

    @lru_cache(None)
    def mass(self, mask):
        return sum((self.weights[i] for i in mask), F(0))

    def terminal(self, mask):
        yes = sum((self.weights[i] for i in mask if self.w[i]['truth']), F(0))
        no = self.mass(mask) - yes
        return {'defer': F(0), 'publish_accusation': yes - 4*no, 'publish_clearance': no - 4*yes}

    def legal(self, used, budget):
        return [q for q, a in self.q.items() if q not in used and a['cost'] <= budget and set(a['requires']) <= used]

    def children(self, mask, q):
        groups = {}
        for i in mask:
            groups.setdefault(self.w[i]['observations'][q], []).append(i)
        return tuple(tuple(g) for g in groups.values())

    @lru_cache(None)
    def values(self, mask, used, budget, depth):
        out = self.terminal(mask)
        if depth:
            for q in self.legal(used, budget):
                out[q] = sum(max(self.values(g, used | {q}, budget - self.q[q]['cost'], depth - 1).values()) for g in self.children(mask, q))
        return out

    def choose(self, mask, used, budget, mode):
        depth = budget if mode == 'full' else min(2, budget) if mode == 'two' else min(1, budget)
        out = dict(self.values(mask, used, budget, depth))
        if mode == 'macro':
            for q in self.q:
                chain = self.chain(q, used, set())
                if not chain or sum(self.q[p]['cost'] for p in chain) > budget:
                    continue
                # Only price deterministic prerequisites; stochastic ancestors
                # require real planning, so are excluded from this control.
                if any(len(self.children(mask, p)) != 1 for p in chain[:-1]):
                    continue
                val = sum(max(self.terminal(g).values()) for g in self.children(mask, q))
                first = chain[0]
                out[first] = max(out.get(first, F(0)), val)
        return max(out, key=out.get)

    @lru_cache(None)
    def evaluate(self, mask, used, budget, mode):
        if mode == 'random':
            actions = tuple(self.terminal(mask)) + tuple(self.legal(used, budget))
        else:
            actions = (self.choose(mask, used, budget, mode),)
        totals = [F(0)]*4  # correct, false, defer, cost
        for a in actions:
            if a in self.q:
                z = [sum(r[j] for r in [self.evaluate(g, used | {a}, budget-self.q[a]['cost'], mode) for g in self.children(mask,a)]) for j in range(4)]
                z[3] += self.mass(mask)*self.q[a]['cost']
            elif a == 'defer':
                z = [0,0,self.mass(mask),0]
            else:
                correct = sum((self.weights[i] for i in mask if self.w[i]['truth'] == int(a == 'publish_accusation')),F(0))
                z = [correct,self.mass(mask)-correct,0,0]
            totals = [x+y/len(actions) if isinstance(y,F) else x+F(y,len(actions)) for x,y in zip(totals,z)]
        return tuple(totals)

    def run(self):
        root = tuple(range(len(self.w)))
        seen = set()
        def visit(mask, used, budget):
            state = (mask, used, budget)
            if state in seen:
                return
            seen.add(state)
            for q in self.legal(used, budget):
                for g in self.children(mask,q):
                    visit(g, used | {q}, budget-self.q[q]['cost'])
        visit(root, frozenset(), self.b)
        consequential = opportunities = 0
        for mask, used, budget in seen:
            vals = self.values(mask,used,budget,budget)
            if len(set(vals.values())) > 1:
                consequential += 1
            if max(vals.values()) > max(self.terminal(mask).values()):
                opportunities += 1
        scores = {}
        for mode in ('one','two','macro','full','random'):
            c,f,d,cost = self.evaluate(root,frozenset(),self.b,mode)
            assert c+f+d == 1 and cost <= self.b
            scores[mode] = dict(zip(('correct','false','defer','cost','utility'),map(str,(c,f,d,cost,c-4*f))))
        assert F(scores['full']['utility']) == max(self.values(root,frozenset(),self.b,self.b).values())
        stop = max(self.terminal(root).values())
        gain = F(scores['full']['utility']) - stop
        for score in scores.values():
            score['opportunity_capture'] = str((F(score['utility']) - stop)/gain) if gain else None
        curve = [max(self.values(root, frozenset(), self.b, d).values()) for d in range(self.b+1)]
        depth_needed = next(i for i,v in enumerate(curve) if v == curve[-1])
        return {'id': self.spec['id'], 'k': self.spec['k'], 'latent_worlds': len(self.w),
                'minimal_optimal_horizon': depth_needed, 'lookahead_value': list(map(str,curve)),
                'public_states': len(seen), 'consequential_states': consequential, 'investigation_opportunities': opportunities,
                'root_q': {a:str(v) for a,v in self.values(root,frozenset(),self.b,self.b).items()},
                'root_stop_value': str(max(self.terminal(root).values())), 'policies':scores}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sidecar', type=Path, help='Optional JSON list of finite design variants')
    p.add_argument('--output',type=Path)
    args = p.parse_args()
    variants = json.loads(args.sidecar.read_text()) if args.sidecar else list(north_quay())
    result = {'schema':'SW-PROV-design-audit/v1','scope':'exact finite authoring diagnostic, not a player or neural evaluation','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'sidecar_sha256':hashlib.sha256(json.dumps(variants,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
              'variants':[Audit(v).run() for v in variants]}
    s = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.output:
        args.output.write_text(s)
    else:
        print(s,end='')


if __name__ == '__main__':
    main()
