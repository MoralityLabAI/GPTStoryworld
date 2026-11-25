"""SW-PROV-05: exact social access chain with actor-local evidence.

Public development fixture. The isolated host holds truth and unobserved evidence.
This is an authoring/session model, not a native SWMD runtime.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
from functools import lru_cache
from math import lcm
import argparse
import json
from pathlib import Path
import secrets
import sys
from provenance_characters import LAW as COUNCIL_LAW
from provenance_session import TERMINALS, serve

TITLE = 'The North Quay Inquiry: the sealed register'
# The dispatch is an independent noisy report conditional on truth, not a copy.
LAW = tuple((w * (F(2, 3) if c == x['truth'] else F(1, 3)), {**x, 'C': c})
            for w, x in COUNCIL_LAW for c in (0, 1))
assert sum(w for w, _ in LAW) == 1
COST = {'consult': 1, 'seals': 1, 'brief': 1, 'apply': 1, 'registry': 1, 'dispatch': 2}
FIELDS = {'consult': 'B', 'seals': 'shared', 'registry': 'valid_A', 'dispatch': 'C'}
LABELS = {'consult': 'Consult the magistrate about the customs report',
          'seals': 'Trace the harbour and customs seals',
          'brief': 'Show the registrar the documented lineage and acquired reports',
          'apply': 'File the one permitted application for sealed records',
          'registry': 'Read the opened registry of source validity',
          'dispatch': 'Obtain the independent watch dispatch'}
SIGNS = {0: 'clears', 1: 'accuses'}
MODES = ('social', 'blocked', 'ungated')


@dataclass(frozen=True)
class State:
    evidence: tuple
    used: frozenset = frozenset()
    granted: bool = False
    budget: int = 0

    @property
    def trust(self):
        # Public documented behaviour, independent of the truth of the accusation.
        return F(1, 4) if 'brief' in self.used else F(0)


def root(a, budget):
    if type(budget) is not int or budget < 0 or a not in (0, 1):
        raise ValueError('invalid root')
    return State((('A', a),), budget=budget)


@lru_cache(None)
def mass(evidence):
    matches = [(w, x) for w, x in LAW if all(x[k] == v for k, v in evidence)]
    return tuple(sum((w for w, x in matches if x['truth'] == h), F(0)) for h in (0, 1))


def posterior(evidence):
    no, yes = mass(tuple(sorted(evidence)))
    if not no+yes:
        raise ValueError('impossible evidence')
    return yes/(no+yes)


def grant(trust):
    # Refuse on ties. Exactly the calibrated SW-PROV-04 desirability rule.
    return trust - F(1, 8) > 0


def legal(s, mode='social'):
    if mode not in MODES:
        raise ValueError('invalid mode')
    out = []
    for q, cost in COST.items():
        if q in s.used or cost > s.budget:
            continue
        if q in ('brief', 'apply') and mode != 'social':
            continue
        if q == 'brief' and 'seals' not in s.used:
            continue
        if q == 'registry' and (mode == 'blocked' or (mode == 'social' and not s.granted)):
            continue
        out.append(q)
    return tuple(out) + tuple(TERMINALS)


def step(s, action, observation, mode='social'):
    """Public-state transition. No latent world required after observing outcome."""
    if action not in legal(s, mode) or action not in COST:
        raise ValueError('illegal acquisition')
    evidence = dict(s.evidence)
    granted = s.granted
    if action in FIELDS:
        if type(observation) is not int or observation not in (0, 1):
            raise ValueError('invalid observation')
        evidence[FIELDS[action]] = observation
    elif action == 'brief':
        if observation != 'documented':
            raise ValueError('invalid briefing')
    elif action == 'apply':
        granted = grant(s.trust)
        if observation != ('granted' if granted else 'refused'):
            raise ValueError('invalid application reaction')
    new = State(tuple(sorted(evidence.items())), s.used | {action}, granted, s.budget-COST[action])
    if not sum(mass(new.evidence)):
        raise ValueError('impossible observation')
    return new


@lru_cache(None)
def children(s, q, mode):
    if q in FIELDS:
        outcomes = (0, 1)
    elif q == 'brief':
        outcomes = ('documented',)
    else:
        outcomes = ('granted' if grant(s.trust) else 'refused',)
    out = []
    for y in outcomes:
        try:
            new = step(s, q, y, mode)
        except ValueError as err:
            if str(err) == 'impossible observation':
                continue
            raise
        p = sum(mass(new.evidence))/sum(mass(s.evidence))
        out.append((p, new))
    assert sum(p for p, _ in out) == 1
    return tuple(out)


def stop(s, q):
    p = posterior(s.evidence)
    c = p if q == 'publish_accusation' else 1-p if q == 'publish_clearance' else F(0)
    f = 1-c if q != 'defer' else F(0)
    return (c, f, 1-c-f, F(0), F(0))  # correct, false, defer, cost, registry acquisitions


def utility(row):
    return row[0]-4*row[1]


def terminal(s):
    return max(TERMINALS, key=lambda q: (utility(stop(s,q)), q=='defer'))


@lru_cache(None)
def values(s, depth, mode='social'):
    """Values of legal first actions with at most depth acquisitions."""
    v = {q: utility(stop(s,q)) for q in TERMINALS}
    if depth:
        for q in legal(s, mode):
            if q in COST:
                v[q] = sum(p*max(values(n, depth-1, mode).values()) for p,n in children(s,q,mode))
    return v


def archive_route(s, mode):
    """One complete advertised route to the registry, possibly stochastic seals."""
    if mode != 'social' or 'registry' in s.used or ('apply' in s.used and not s.granted):
        return ()
    route = tuple(q for q in ('seals','brief','apply','registry') if q not in s.used)
    # If already granted, the application route is unnecessary.
    return ('registry',) if s.granted else route


@lru_cache(None)
def route_value(s, route, mode):
    if not route:
        return utility(stop(s,terminal(s)))
    q = route[0]
    if q not in legal(s,mode):
        return None
    parts = [(p,route_value(n,route[1:],mode)) for p,n in children(s,q,mode)]
    if any(v is None for _,v in parts):
        return None
    return sum(p*v for p,v in parts)


def choose(s, policy='full', mode='social'):
    depth = {'stop':0, 'one':1, 'two':2, 'route':1, 'full':s.budget}[policy]
    v = dict(values(s,min(s.budget,depth),mode))
    if policy == 'route':
        route = archive_route(s,mode)
        if route and sum(COST[q] for q in route)<=s.budget:
            score = route_value(s,route,mode)
            if score is not None:
                v[route[0]]=max(v.get(route[0],F(-5)),score)
    # Prefer stopping on exact ties; prefer defer among terminal ties.
    return max(v,key=lambda q:(v[q],q in TERMINALS,q=='defer'))


@lru_cache(None)
def evaluate(s, policy='full', mode='social'):
    q=choose(s,policy,mode)
    if q in TERMINALS:
        return stop(s,q)
    out=[F(0),F(0),F(0),F(COST[q]),F(q=='registry')]
    for p,n in children(s,q,mode):
        out=[a+p*b for a,b in zip(out,evaluate(n,policy,mode))]
    return tuple(out)


class AccessSession:
    def __init__(self,budget=5,world_index=None,mode='social'):
        if mode not in MODES:
            raise ValueError('invalid mode')
        if world_index is None:
            den=lcm(*(w.denominator for w,_ in LAW)); ticket=secrets.randbelow(den)
            for i,(w,_) in enumerate(LAW):
                ticket-=int(w*den)
                if ticket<0:
                    world_index=i; break
        if type(world_index) is not int or not 0<=world_index<len(LAW):
            raise ValueError('invalid world index')
        self._world=LAW[world_index][1]
        self._mode=mode
        self._initial_budget=budget
        self._s=root(self._world['A'],budget)
        self._registrar=(('A',self._world['A']),)
        self._history=[]; self._ending=None

    def legal(self):
        return () if self._ending else legal(self._s,self._mode)

    def public(self):
        s=self._s
        text=(f'The harbour report {SIGNS[dict(s.evidence)["A"]]} Captain Vale. '
              f'You have {s.budget} research units left. '
              'The independent watch dispatch costs two units. Correct judgment pays one, false judgment costs four; defer pays zero. ')
        if self._mode=='social':
            text+='The registrar requires a documented seal comparison before a briefing can establish trust. One application is allowed; applying before the briefing will be refused. An opened register can be read at a further cost. '
        if self._mode=='blocked': text+='The sealed registry is closed for this hearing. '
        if self._mode=='ungated': text+='The sealed registry is already accessible for this hearing. '
        text+=f'Registrar trust: {s.trust}. '+ ' '.join(x['text'] for x in self._history)
        if self._ending: text+=' The council records your judgment: '+TERMINALS[self._ending]+'. The hidden truth remains undisclosed.'
        actions=[{'id':q,'label':LABELS.get(q,TERMINALS.get(q)),'cost':COST.get(q,0)} for q in self.legal()]
        turn=len(self._history)
        card=[f'## ENC access_{turn} | {TITLE} | turn={turn}..{turn} | spools=[inquiry]','T: '+text]
        card += [f'OPT {a["id"]}: {a["label"]} (cost {a["cost"]})' for a in actions]
        return {'schema':'SW-PROV/session/v1','title':TITLE,'remaining':s.budget,'turn':turn,
                'terminal':self._ending is not None,'text':text,'ledger':[x.copy() for x in self._history],
                'actions':actions,'swmd_card':'\n'.join(card)+'\n'}

    def act(self,q):
        if not isinstance(q,str) or q not in self.legal():
            raise ValueError('illegal action')
        if q in TERMINALS:
            self._ending=q
        else:
            if q in FIELDS:
                y=self._world[FIELDS[q]]
                text={'consult':f'The customs report {SIGNS[y]} Vale.',
                      'seals':'The seal comparison establishes '+('shared origin.' if y else 'independent origins.'),
                      'registry':'The registry declares the harbour source '+('valid.' if y else 'invalid; its report is fair noise under the declared law.'),
                      'dispatch':f'The independent watch dispatch {SIGNS[y]} Vale.'}[q]
            elif q=='brief':
                y='documented'; self._registrar=self._s.evidence
                text='The registrar accepts your documented provenance, increasing trust to 1/4.'
            else:
                y='granted' if grant(self._s.trust) else 'refused'
                text='The registrar '+('opens the sealed registry.' if y=='granted' else 'refuses the sole application.')
            self._s=step(self._s,q,y,self._mode)
            self._history.append({'query':q,'outcome':str(y),'text':text})
        return self.public()

    def private_projection(self):
        return {'editor':str(2*posterior(self._s.evidence)-1), 'registrar':str(2*posterior(self._registrar)-1),
                'trust':str(self._s.trust),'editor_ledger':dict(self._s.evidence),'registrar_ledger':dict(self._registrar)}

    def grade(self):
        if self._ending is None: raise ValueError('active session')
        correct=int(self._ending!='defer' and int(self._ending=='publish_accusation')==self._world['truth'])
        false=int(self._ending!='defer')-correct
        return {'correct':correct,'false':false,'defer':int(self._ending=='defer'),'utility':correct-4*false,
                'cost':self._initial_budget-self._s.budget,'registry':int('registry' in self._s.used)}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--budget',type=int,default=5)
    p.add_argument('--mode',choices=MODES,default='social');p.add_argument('--grade-file',type=Path);a=p.parse_args()
    result=serve(AccessSession(a.budget,mode=a.mode),sys.stdin,sys.stdout)
    if result is not None and a.grade_file:a.grade_file.write_text(json.dumps(result,sort_keys=True)+'\n')


if __name__=='__main__':main()
