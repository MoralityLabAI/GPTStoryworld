"""Exact public transcript and scoring audit for the North Quay session adapter."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from provenance_design_audit import Audit, north_quay
from provenance_session import Session


def verify(spec):
    audit = Audit(spec)
    seen = {}
    prefixes = endings = 0
    for i in range(len(audit.w)):
        def walk(path):
            nonlocal prefixes, endings
            session = Session(spec, i)
            for a in path:
                session.act(a)
            state = session.public()
            history = tuple((x['query'], x['outcome']) for x in state['ledger'])
            key = (tuple(path), history)
            blob = json.dumps(state, sort_keys=True)
            assert seen.setdefault(key, blob) == blob
            prefixes += 1
            endings += state['terminal']
            for a in state['actions']:
                walk(path + [a['id']])
        walk([])
    policies = {}
    root = tuple(range(len(audit.w)))
    for mode in ('one', 'two', 'macro', 'full'):
        total = [F(0)] * 4
        for i, weight in enumerate(audit.weights):
            s = Session(spec, i)
            mask, used = root, frozenset()
            while not s.public()['terminal']:
                q = audit.choose(mask, used, s.public()['remaining'], mode)
                state = s.act(q)
                if q in audit.q:
                    y = state['ledger'][-1]['outcome']
                    mask = tuple(j for j in mask if audit.w[j]['observations'][q] == y)
                    used |= {q}
            grade = s.grade()
            total = [x + weight * grade[k] for x, k in zip(total, ('correct', 'false', 'defer', 'cost'))]
        assert tuple(total) == audit.evaluate(root, frozenset(), audit.b, mode)
        policies[mode] = dict(zip(('correct','false','defer','cost','utility'), map(str, (*total, total[0]-4*total[1]))))
    return {'id': spec['id'], 'worlds': len(audit.w), 'prefixes': prefixes,
            'endings': endings, 'unique_public_histories': len(seen), 'policies': policies}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    root = Path(__file__).resolve().parent
    sources = ['provenance_design_audit.py', 'provenance_session.py', 'test_provenance_session.py',
               'verify_provenance_session.py', 'provenance_client.ts', 'test_provenance_client.cjs']
    receipt = {'schema': 'SW-PROV/session-audit/v1', 'scope': 'exact public development fixture, no neural evaluation',
               'source_sha256': {x: hashlib.sha256((root/x).read_bytes()).hexdigest() for x in sources},
               'variants': [verify(spec) for spec in north_quay()]}
    out = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(out)
    else:
        print(out, end='')


if __name__ == '__main__':
    main()
