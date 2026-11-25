"""Exact social/epistemic design audit over all legal public histories."""
import argparse
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from provenance_characters import CouncilSession, LAW, LABELS, TERMINALS, posterior, reaction

MODES = ('stop', 'one', 'two', 'full', 'no_brief')
METRICS = ('correct', 'false', 'defer', 'endorsed_correct', 'cost', 'utility')


def audit(budget):
    prefixes, endings, opportunity = 0, 0, 0
    public_histories = {}

    @lru_cache(None)
    def replay(i, path):
        s = CouncilSession(budget, i)
        for a in path:
            s.act(a)
        return s

    def groups(ids, path):
        out = {}
        for i in ids:
            blob = json.dumps(replay(i, path).public(), sort_keys=True)
            out.setdefault(blob, []).append(i)
        return tuple(tuple(x) for x in out.values())

    def mass(ids):
        return sum((LAW[i][0] for i in ids), F(0))

    def actions(ids, path, allow_brief=True):
        a = replay(ids[0], path).legal()
        assert all(replay(i, path).legal() == a for i in ids)
        return [q for q in a if allow_brief or q != 'brief']

    def terminal(ids, path, q):
        rows = [(LAW[i][0], replay(i, path+(q,)).grade()) for i in ids]
        return tuple(sum((w*F(row[k]) for w, row in rows), F(0)) for k in METRICS)

    @lru_cache(None)
    def values(ids, path, horizon, allow_brief=True):
        out = {q: terminal(ids, path, q)[-1] for q in TERMINALS}
        if horizon:
            for q in actions(ids, path, allow_brief):
                if q in LABELS:
                    nxt = path+(q,)
                    out[q] = sum(max(values(g, nxt, horizon-1, allow_brief).values()) for g in groups(ids, nxt))
        return out

    @lru_cache(None)
    def play(ids, path, mode):
        remaining = replay(ids[0], path).public()['remaining']
        horizon = {'stop': 0, 'one': 1, 'two': 2}.get(mode, remaining)
        out = values(ids, path, min(remaining, horizon), mode != 'no_brief')
        q = max(out, key=out.get)
        if q in TERMINALS:
            return terminal(ids, path, q)
        nxt = path+(q,)
        return tuple(map(sum, zip(*(play(g, nxt, mode) for g in groups(ids, nxt)))))

    def walk(ids, path):
        nonlocal prefixes, endings, opportunity
        blob = json.dumps(replay(ids[0], path).public(), sort_keys=True)
        assert all(json.dumps(replay(i, path).public(), sort_keys=True) == blob for i in ids)
        # Group by *all* public observations; separately ensure no hidden state
        # affects public packets on identical initial report and acquired factual outcomes.
        # Exclude briefing reactions from the key: they must be derived from those facts.
        for i in ids:
            s = replay(i, path)
            state = s.public()
            key = (LAW[i][1]['A'], path, tuple((e['query'], e['outcome']) for e in state['ledger'] if e['query'] != 'brief'))
            assert public_histories.setdefault(key, blob) == blob
            prefixes += 1
        if path and path[-1] in TERMINALS:
            endings += len(ids)
            return
        remaining = replay(ids[0], path).public()['remaining']
        opportunity += max(values(ids, path, remaining).values()) > max(values(ids, path, 0).values())
        for q in actions(ids, path):
            nxt = path+(q,)
            for g in groups(ids, nxt):
                walk(g, nxt)

    roots = groups(tuple(range(len(LAW))), ())
    for g in roots:
        walk(g, ())
    results = {m: tuple(map(sum, zip(*(play(g, (), m) for g in roots)))) for m in MODES}
    curve = [sum(max(values(g, (), d).values()) for g in roots) for d in range(budget+1)]
    assert results['full'][-1] == curve[-1]
    assert all(r[-1] <= results['full'][-1] for r in results.values())
    assert all(sum(r[:3]) == 1 and r[3] <= r[0] and r[4] <= budget for r in results.values())
    return {'budget': budget, 'worlds': len(LAW), 'world_prefixes': prefixes, 'terminal_prefixes': endings,
            'public_histories': len(public_histories), 'investigation_opportunities': opportunity,
            'lookahead_utility': list(map(str, curve)),
            'policies': {m: dict(zip(METRICS, map(str, r))) for m, r in results.items()}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=Path('character_receipt.json'))
    args = p.parse_args()
    root = Path(__file__).resolve().parent
    sources = ('provenance_characters.py', 'verify_provenance_characters.py', 'test_provenance_characters.py', 'provenance_session.py', 'provenance_design_audit.py')
    out = {'schema': 'SW-PROV/characters-audit/v1', 'scope': 'exact finite public development design, not neural or independent samples',
           'source_sha256': {n: hashlib.sha256((root/n).read_bytes()).hexdigest() for n in sources},
           'variants': [audit(b) for b in (2, 3, 4)]}
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2)+'\n')
    print(json.dumps(out['variants'], indent=2))


if __name__ == '__main__':
    main()
