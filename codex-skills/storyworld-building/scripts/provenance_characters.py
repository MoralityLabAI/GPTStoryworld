"""SW-PROV-03: character-local evidence, pValues and authored reactions.

Private host state; compatible with the SW-PROV-02 public session protocol.
A toy authored finite law, not a native SWMD engine or a learned policy.
"""
from fractions import Fraction as F
from itertools import product
from math import lcm
import argparse
import json
from pathlib import Path
import secrets
import sys
from provenance_session import serve, TERMINALS

TITLE = 'The North Quay Inquiry: council edition'
ACTORS = ('editor', 'magistrate', 'registrar')
LABELS = {'consult': 'Ask the magistrate to show the customs report',
          'seals': 'Trace the seals to their source records',
          'registry': 'Check the validity of the harbour source',
          'brief': 'Present the acquired evidence to both councillors'}
WORDS = {0: 'clears', 1: 'accuses'}
EVIDENCE_FIELDS = frozenset(('A', 'B', 'shared', 'valid_A'))


def worlds():
    """Uniform truth and shared/independent prior; origin validity 2/3.

    Valid origins report truth, invalid ones report a fair bit. Shared
    labels share validity AND report. Enumerate positive-mass assignments.
    """
    for h, shared in product((0, 1), repeat=2):
        n = 1 if shared else 2
        for vs in product((0, 1), repeat=n):
            for rs in product((0, 1), repeat=n):
                w = F(1, 4)
                for v, r in zip(vs, rs):
                    w *= F(2, 3) if v else F(1, 3)
                    w *= F(int(r == h)) if v else F(1, 2)
                if w:
                    yield w, {'truth': h, 'A': rs[0], 'B': rs[-1],
                              'shared': shared, 'valid_A': vs[0]}


LAW = tuple(worlds())
assert sum(w for w, _ in LAW) == 1


def posterior(ledger):
    if not set(ledger) <= EVIDENCE_FIELDS or any(type(v) is not int or v not in (0, 1) for v in ledger.values()):
        raise ValueError('invalid evidence ledger')
    compatible = [(w, x) for w, x in LAW if all(x[k] == v for k, v in ledger.items())]
    mass = sum((w for w, _ in compatible), F(0))
    if not mass:
        raise ValueError('impossible evidence history')
    return sum((w for w, x in compatible if x['truth']), F(0)) / mass


def desirability(b, trust):
    """b = pValue of Vale culpability. Trust is a distinct social axis."""
    return {'defer': F(0), 'publish_accusation': (5*b-3)/2 + trust/8,
            'publish_clearance': (-5*b-3)/2 + trust/8}


def reaction(ledger, trust=F(0)):
    b = 2*posterior(ledger)-1
    scores = desirability(b, trust)
    return max(scores, key=scores.get)


def transfer(target, evidence):
    """Idempotent merge of authenticated observations, never latent truth."""
    if not set(evidence) <= EVIDENCE_FIELDS or any(type(v) is not int or v not in (0, 1) for v in evidence.values()):
        raise ValueError('invalid evidence')
    if any(k in target and target[k] != v for k, v in evidence.items()):
        raise ValueError('inconsistent observation')
    result = {**target, **evidence}
    posterior(result)
    return result


class CouncilSession:
    def __init__(self, budget=4, world_index=None):
        if type(budget) is not int or budget < 0:
            raise ValueError('invalid budget')
        if world_index is None:
            den = lcm(*(w.denominator for w, _ in LAW))
            ticket = secrets.randbelow(den)
            for i, (w, _) in enumerate(LAW):
                ticket -= int(w*den)
                if ticket < 0:
                    world_index = i
                    break
        if type(world_index) is not int or not 0 <= world_index < len(LAW):
            raise ValueError('invalid world')
        self._world = LAW[world_index][1]
        self._initial_budget = self._budget = budget
        self._knowledge = {'editor': {'A': self._world['A']},
                           'magistrate': {'B': self._world['B']},
                           'registrar': {'A': self._world['A']}}
        self._trust = dict.fromkeys(ACTORS[1:], F(0))
        self._endorsement = {}
        self._history = []
        self._used = set()
        self._ending = None

    def private_projection(self):
        """Host-only mapping to depth-1 pValue and depth-1 trust pointers."""
        return {a: {'keyring': ['Culpability', 'char_vale'],
                    'value': str(2*posterior(self._knowledge[a])-1),
                    'evidence': dict(self._knowledge[a]),
                    'trust_keyring': ['Trust', 'char_editor'],
                    'trust_editor': str(self._trust.get(a, F(0)))} for a in ACTORS}

    def legal(self):
        if self._ending:
            return []
        queries = [q for q in LABELS if self._budget and q not in self._used
                   and (q != 'brief' or 'consult' in self._used)]
        return queries + list(TERMINALS)

    def public(self):
        actions = [{'id': q, 'label': LABELS[q] if q in LABELS else TERMINALS[q],
                    'cost': int(q in LABELS)} for q in self.legal()]
        text = (f'The harbour report {WORDS[self._world["A"]]} Captain Vale. '
                'The magistrate has a customs report; the registrar warns about copied sources. '
                f'Research units left: {self._budget}. Correct judgment pays one, false judgment costs four; '
                'a correct judgment endorsed by the magistrate gains a quarter. '
                'Defer is always possible.')
        if self._history:
            text += ' ' + ' '.join(x['text'] for x in self._history)
        if self._ending:
            text += ' The council records your decision: ' + TERMINALS[self._ending] + '. The hidden truth remains undisclosed.'
        turn = len(self._history)
        card = [f'## ENC council_{turn} | {TITLE} | turn={turn}..{turn} | spools=[inquiry]', 'T: '+text]
        card += [f'OPT {a["id"]}: {a["label"]} (cost {a["cost"]})' for a in actions]
        return {'schema': 'SW-PROV/session/v1', 'title': TITLE, 'remaining': self._budget,
                'turn': turn, 'terminal': self._ending is not None, 'text': text,
                'ledger': [x.copy() for x in self._history], 'actions': actions,
                'swmd_card': '\n'.join(card)+'\n'}

    def act(self, q):
        if not isinstance(q, str) or q not in self.legal():
            raise ValueError('illegal action')
        if q in TERMINALS:
            self._ending = q
        else:
            self._budget -= 1
            self._used.add(q)
            if q == 'brief':
                for actor in ACTORS[1:]:
                    self._knowledge[actor] = transfer(self._knowledge[actor], self._knowledge['editor'])
                    if {'shared', 'valid_A'} & self._knowledge['editor'].keys():
                        self._trust[actor] = F(1, 4)  # documented provenance, regardless of sign
                    self._endorsement[actor] = reaction(self._knowledge[actor], self._trust[actor])
                y = '|'.join(self._endorsement[a] for a in ACTORS[1:])
                text = 'After the briefing, ' + '; '.join(f'{a}: {TERMINALS[self._endorsement[a]]}' for a in ACTORS[1:]) + '.'
            else:
                field = {'consult': 'B', 'seals': 'shared', 'registry': 'valid_A'}[q]
                v = self._world[field]
                self._knowledge['editor'] = transfer(self._knowledge['editor'], {field: v})
                y = str(v)
                text = {'consult': f'The customs report {WORDS[v]} Vale.',
                        'seals': 'The reports descend from ' + ('one origin.' if v else 'independent origins.'),
                        'registry': 'The harbour source is ' + ('valid.' if v else 'invalid; its report is uninformative under the declared law.')}[q]
            self._history.append({'query': q, 'outcome': y, 'text': text})
        return self.public()

    def grade(self):
        if not self._ending:
            raise ValueError('active session')
        correct = int(self._ending != 'defer' and int(self._ending == 'publish_accusation') == self._world['truth'])
        false = int(self._ending != 'defer')-correct
        endorsed = int(correct and self._endorsement.get('magistrate') == self._ending)
        return {'correct': correct, 'false': false, 'defer': int(self._ending == 'defer'),
                'endorsed_correct': endorsed, 'cost': self._initial_budget-self._budget,
                'utility': str(F(correct-4*false)+F(endorsed, 4))}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--budget', type=int, default=4)
    p.add_argument('--grade-file', type=Path)
    args = p.parse_args()
    grade = serve(CouncilSession(args.budget), sys.stdin, sys.stdout)
    if grade is not None and args.grade_file:
        args.grade_file.write_text(json.dumps(grade, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
