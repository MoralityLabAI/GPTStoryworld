"""Source-hashed exact authoring receipt and session/oracle agreement checks."""
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import argparse
import hashlib
import json
from provenance_access import (LAW, MODES, COST, TERMINALS, AccessSession, root,
                               choose, evaluate, utility, values, mass, legal,
                               posterior, grant)
from reaction_sensitivity_audit import audit

ROOT=Path(__file__).resolve().parent
ARMS=(('stop','social'),('one','social'),('two','social'),('route','social'),
      ('full','social'),('full','blocked'),('full','ungated'))
METRICS=('correct','false','defer','cost','registry')
SOURCES=('provenance_access.py','test_provenance_access.py','verify_provenance_access.py',
         'provenance_characters.py','provenance_session.py','provenance_design_audit.py',
         'reaction_sensitivity_audit.py','north_quay_access.swmd.min.md','north_quay_access.sidecar.json')


def scores(b):
    out={}
    for pol,mode in ARMS:
        total=[F(0)]*len(METRICS)
        for i,(w,_) in enumerate(LAW):
            session=AccessSession(b,i,mode)
            while not session.public()['terminal']:
                action=choose(session._s,pol,mode)
                # Oracle's decision uses only the public sufficient state.
                assert action in [a['id'] for a in session.public()['actions']]
                session.act(action)
            g=session.grade()
            total=[a+w*g[k] for a,k in zip(total,METRICS)]
        independent_total=tuple(sum(sum(mass(root(sign,b).evidence))*evaluate(root(sign,b),pol,mode)[j] for sign in (0,1)) for j in range(len(METRICS)))
        assert tuple(total)==independent_total
        assert sum(total[:3])==1 and total[3]<=b
        out[f'{pol}_{mode}']={**dict(zip(METRICS,map(str,total))),'utility':str(utility(total))}
    return out


def brute(b, mode, reverse=False):
    """Separate policy-tree oracle: group actual session packets across worlds.

    No mass(), values(), choose(), or posterior() calls. The session dynamics
    are shared; terminal scores and public equivalence classes drive the tree.
    """
    @lru_cache(None)
    def replay(i,path):
        s=AccessSession(b,i,mode)
        for q in path:s.act(q)
        return s
    def group(ids,path):
        g={}
        for i in ids:
            packet=json.dumps(replay(i,path).public(),sort_keys=True)
            g.setdefault(packet,[]).append(i)
        return tuple(tuple(x) for x in g.values())
    @lru_cache(None)
    def walk(ids,path):
        choices=replay(ids[0],path).public()['actions']
        best=F(-5)
        for a in choices:
            q=a['id']; nxt=path+(q,)
            if q in TERMINALS:
                v=sum(LAW[i][0]*replay(i,nxt).grade()['utility'] for i in ids)
            else:
                v=sum(walk(g,nxt) for g in group(ids,nxt))
            best=max(best,v)
        return best
    ids=tuple(range(len(LAW)))
    if reverse:ids=tuple(reversed(ids))
    return sum(walk(g,()) for g in group(ids,()))


def privacy(b):
    """Enumerate every legal sequence; compare packets by factual history only."""
    seen={}; prefixes=0; terminals=0
    for i,(_,w) in enumerate(LAW):
        def walk(path):
            nonlocal prefixes,terminals
            s=AccessSession(b,i)
            for q in path:s.act(q)
            packet=s.public(); factual=tuple((x['query'],x['outcome']) for x in packet['ledger'] if x['query'] in ('consult','seals','registry','dispatch'))
            key=(w['A'],path,factual)
            blob=json.dumps(packet,sort_keys=True)
            assert seen.setdefault(key,blob)==blob
            prefixes+=1;terminals+=packet['terminal']
            if packet['terminal']:return
            for a in packet['actions']:walk(path+(a['id'],))
        walk(())
    return {'budget':b,'world_prefixes':prefixes,'terminal_prefixes':terminals,'public_histories':len(seen)}


def run():
    rows={str(b):scores(b) for b in range(2,8)}
    for row in rows.values():
        full=F(row['full_social']['utility'])
        assert all(full>=F(row[k]['utility']) for k in ('stop_social','one_social','two_social','route_social','full_blocked'))
        assert F(row['full_ungated']['utility'])>=full
    # Independent decision tree on a budget where the gate is active.
    assert brute(4,'social')==brute(4,'social',True)==F(rows['4']['full_social']['utility'])
    # Verify explicit SWMD mechanism, without giving the player latent truth.
    spec=json.loads((ROOT/'north_quay_access.sidecar.json').read_text())
    mechanical=audit((ROOT/'north_quay_access.swmd.min.md').read_text(),spec)
    assert all(e['status']=='REACHED' for e in mechanical['endings'].values())
    assert all(not(e['clipped'] or e['large_applied']) for e in mechanical['effects'].values())
    assert mechanical['options']['application/apply']['variables']['registrar.Trust[editor]']['winner_flips']==2
    assert all(not v['never_selected'] for v in mechanical['options'].values())
    # Witness: invalid harbour source, independent contrary customs evidence.
    i=next(i for i,(_,w) in enumerate(LAW) if w['A']==1 and w['B']==0 and w['shared']==0 and w['valid_A']==0)
    s=AccessSession(5,i); path=[]
    for a in ('consult','seals','brief','apply','registry'):
        s.act(a); path.append({'action':a,**s.private_projection()})
    assert path[-2]['editor']=='0' and path[-1]['editor']=='-2/3'
    assert path[-1]['registrar']=='0'
    assert path[-1]['trust']=='1/4'
    assert F(rows['5']['full_social']['utility'])>F(rows['5']['full_blocked']['utility'])
    return {'schema':'SW-PROV-05/v1','evidence':'exact finite authoring fixture, no neural or independent sample claim',
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES},
            'latent_assignments':len(LAW),'budgets':rows,'privacy':privacy(5),'witness':path,
            'mechanical':mechanical,'checks':{'session_oracle_parity':True,'dominance_and_budget':True,
                    'independent_packet_tree':True,'public_history_equivalence':True,'all_mechanical_endings_reached':True,
                    'effects_bounded':True,'trust_changes_access':True,'local_belief_revision':True,'all_mechanical_reactions_selected':True,'reverse_world_order_oracle':True}}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'access_receipt.json');a=p.parse_args()
    r=run();a.output.write_text(json.dumps(r,sort_keys=True,indent=2,default=str)+'\n')
    print(json.dumps({k:r[k] for k in ('latent_assignments','privacy','checks')},indent=2))


if __name__=='__main__':main()
