"""SW-PROV-02: playable public SWMD encounter-card adapter, private finite grader.

The host owns the sidecar and selected world. JSONL clients receive only public
observations, legal actions and a dynamic SWMD card, not a native engine file.
"""
import argparse
from fractions import Fraction as F
from math import lcm
import json
from pathlib import Path
import secrets
import sys
from provenance_design_audit import Audit, north_quay

TITLE = 'The North Quay Inquiry'
TERMINALS = {
    'publish_accusation': 'Publish the accusation against Vale',
    'publish_clearance': 'Publish a finding clearing Vale',
    'defer': 'Defer judgment pending further evidence',
}
LABELS = {
    'catalogue': 'Ask the registrar for access to the seals',
    'inspect_seals': 'Compare the seals and trace the petitions',
    'hear_reprint': 'Read the reprinted accusation',
    'read_ledger_a': 'Read the harbour ledger',
    'read_ledger_b': 'Read the customs ledger',
}
PROSE = {
    ('catalogue', 'access_granted'): 'The registrar opens the seal cabinet. This establishes access, not culpability.',
    ('inspect_seals', 'independent'): 'The seals trace to two independently compiled source records.',
    ('inspect_seals', 'copied'): 'The seals show the two accounts descend from a single source record.',
    ('hear_reprint', 'accuses'): 'The pamphlet repeats the accusation already in the petitions, from the same record.',
    ('read_ledger_a', 'accuses'): 'The harbour ledger implicates Vale in the leaked watch schedule.',
    ('read_ledger_a', 'clears'): 'The harbour ledger reports no involvement by Vale.',
    ('read_ledger_b', 'accuses'): 'The customs ledger implicates Vale in the leaked watch schedule.',
    ('read_ledger_b', 'clears'): 'The customs ledger reports no involvement by Vale.',
}


def sample_world(audit):
    den = lcm(*(w.denominator for w in audit.weights))
    ticket = secrets.randbelow(den)
    for i, w in enumerate(audit.weights):
        ticket -= int(w * den)
        if ticket < 0:
            return i
    raise AssertionError('prior not normalized')


class Session:
    def __init__(self, spec, world_index=None):
        self._audit = Audit(spec)
        if world_index is None:
            world_index = sample_world(self._audit)
        if type(world_index) is not int or not 0 <= world_index < len(self._audit.w):
            raise ValueError('invalid world index')
        if any(q not in LABELS for q in self._audit.q):
            raise ValueError('North Quay adapter requires authored query labels')
        if any((q, y) not in PROSE for w in self._audit.w for q, y in w['observations'].items()):
            raise ValueError('missing authored outcome text')
        self._world = self._audit.w[world_index]
        self._budget = self._audit.b
        self._used = frozenset()
        self._ledger = []
        self._ending = None

    def public(self):
        actions = [] if self._ending else [
            {'id': q, 'label': LABELS[q], 'cost': self._audit.q[q]['cost']}
            for q in self._audit.legal(self._used, self._budget)
        ] + [{'id': q, 'label': label, 'cost': 0} for q, label in TERMINALS.items()]
        opening = ('Two petitions accuse Captain Vale of leaking the harbour watch schedule. '
                   'The registrar warns that scribes sometimes copy one another.' if self._audit.spec['k'] < 3 else
                   'Two unopened ledgers may establish whether Captain Vale leaked the harbour watch schedule. '
                   'The registrar warns that the ledgers may have a common origin.')
        if self._ending:
            prose = 'The council records your decision: ' + TERMINALS[self._ending] + '. The inquiry closes without revealing the hidden truth.'
        else:
            prose = opening + f' Acquisition units remaining: {self._budget}. A false finding carries four times the benefit of a correct one.'
            if self._ledger:
                prose += ' Acquired evidence: ' + ' '.join(x['text'] for x in self._ledger)
        state = {'schema': 'SW-PROV/session/v1', 'title': TITLE, 'remaining': self._budget,
                 'turn': len(self._ledger), 'terminal': self._ending is not None,
                 'text': prose, 'ledger': [x.copy() for x in self._ledger], 'actions': actions}
        # SWMD-style live card, not a complete native SWMD world. IDs depend only on public turn.
        lines = [f'## ENC quay_{state["turn"]} | {TITLE} | turn={state["turn"]}..{state["turn"]} | spools=[inquiry]',
                 'T: ' + prose]
        lines += [f'OPT {a["id"]}: {a["label"]} (cost {a["cost"]})' for a in actions]
        state['swmd_card'] = '\n'.join(lines) + '\n'
        return state

    def act(self, action):
        if not isinstance(action, str) or action not in {a['id'] for a in self.public()['actions']}:
            raise ValueError('illegal action')
        if action in TERMINALS:
            self._ending = action
        else:
            self._budget -= self._audit.q[action]['cost']
            self._used |= {action}
            y = self._world['observations'][action]
            self._ledger.append({'query': action, 'outcome': y, 'text': PROSE[action, y]})
        return self.public()

    def grade(self):
        """Host-only result. It is never included in a player response."""
        if self._ending is None:
            raise ValueError('session still active')
        correct = int(self._ending != 'defer' and int(self._ending == 'publish_accusation') == self._world['truth'])
        false = int(self._ending != 'defer') - correct
        return {'correct': correct, 'false': false, 'defer': int(self._ending == 'defer'),
                'cost': self._audit.b - self._budget, 'utility': correct - 4 * false}


def serve(session, source, sink):
    def emit(x):
        print(json.dumps(x, sort_keys=True), file=sink, flush=True)
    emit(session.public())
    for line in source:
        try:
            obj = json.loads(line)
            if not isinstance(obj, dict) or set(obj) != {'action'}:
                raise ValueError('invalid request')
            state = session.act(obj['action'])
        except (ValueError, TypeError, KeyError):
            emit({'error': 'invalid action', 'state': session.public()})
            continue
        emit(state)
        if state['terminal']:
            return session.grade()
    return None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--k', type=int, choices=(1, 2, 3), default=3)
    p.add_argument('--sidecar', type=Path)
    p.add_argument('--jsonl', action='store_true')
    p.add_argument('--grade-file', type=Path, help='Optional host-only output; keep inaccessible to players')
    args = p.parse_args()
    variants = json.loads(args.sidecar.read_text()) if args.sidecar else list(north_quay())
    spec = next(v for v in variants if v['k'] == args.k)
    session = Session(spec)
    if args.jsonl:
        score = serve(session, sys.stdin, sys.stdout)
    else:
        score = None
        while True:
            state = session.public()
            print(state['swmd_card'])
            if state['terminal']:
                score = session.grade()
                break
            for i, a in enumerate(state['actions'], 1):
                print(f'{i}. {a["label"]} ({a["cost"]})')
            try:
                index = int(input('Choice: '))
                if not 1 <= index <= len(state['actions']):
                    raise ValueError('out of range')
                session.act(state['actions'][index - 1]['id'])
            except (ValueError, IndexError):
                print('Choose an available option.')
            except EOFError:
                break
    if score is not None and args.grade_file:
        args.grade_file.write_text(json.dumps(score, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
