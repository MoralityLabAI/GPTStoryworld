"""SW-PROV-04 reproducible council-derived support and exact finite audit."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from provenance_characters import LAW, posterior, reaction
from reaction_sensitivity_audit import audit, choose, parse_swmd

ROOT = Path(__file__).resolve().parent
B = 'magistrate.Culpability[vale]'
T = 'magistrate.Trust[editor]'
A = 'magistrate.Access'


def ledgers():
    return sorted({tuple(sorted((k,x[k]) for k in ('A','B')+extra)) for _,x in LAW
                   for extra in (('shared',),('valid_A',),('shared','valid_A'))})


def spec(calibrated):
    return {'entry':'hearing','horizon':1,'max_effect':'1/4',
            'initial_states':[{B:str(2*posterior(dict(x))-1),T:str(t),A:'0'}
                              for x in ledgers() for t in (F(0),F(1,4))],
            'perturbations':{B:['-1','-2/3','0','2/3','1'],T:['0','1/4']},
            'guards':{'end_archive':[[A,'>=','1/4' if calibrated else '5/4']]}}


def run():
    rows = {}; sources = ['reaction_sensitivity_audit.py','verify_reaction_sensitivity.py',
                          'test_reaction_sensitivity.py','provenance_characters.py',
                          'provenance_session.py','provenance_design_audit.py']
    led = ledgers()
    for cal in (False,True):
        name = 'calibrated' if cal else 'bad'
        file = f'north_quay_reaction_{name}.swmd.min.md'; sources.append(file)
        text = (ROOT/file).read_text(); model = spec(cal)
        rows[name] = audit(text, model)
        rs = parse_swmd(text)['hearing']['options']['verdict']
        mapping = {'defer':'defer','accuse':'publish_accusation','clear':'publish_clearance'}
        # Both versions reproduce the actual prior fixture verdict on all 26
        # factual ledgers and both trust values, not just the projected support.
        for x in led:
            for t in (F(0),F(1,4)):
                s={B:2*posterior(dict(x))-1,T:t,A:F(0)}
                assert mapping[rs[choose(rs,s)[0]]['id']] == reaction(dict(x),t)
    bad,good = rows['bad'],rows['calibrated']
    trust_flips=sum(reaction(dict(x),F(0))!=reaction(dict(x),F(1,4)) for x in led)
    checks={'original_council_reaction_parity':True,'26_ledger_regression':len(led)==26 and trust_flips==0,
            'bad_trust_inert':bad['options']['hearing/verdict']['variables'][T]['winner_flips']==0,
            'bad_duplicate':bool(bad['options']['hearing/verdict']['mechanically_equivalent_pairs']),
            'bad_gate_blocked':bad['endings']['end_archive']['status']=='UNREACHED_WITHIN_HORIZON' and bad['endings']['end_archive']['incoming_attempts']>0,
            'bad_effect_clips':any(v['clipped'] and v['large_applied'] for v in bad['effects'].values()),
            'good_trust_access_active':good['options']['hearing/archive']['variables'][T]['winner_flips']>0,
            'good_gate_reached':good['endings']['end_archive']['status']=='REACHED',
            'good_effects_in_range':all(not(v['clipped'] or v['large_applied']) for v in good['effects'].values()),
            'all_calibrated_reactions_selected':all(not v['never_selected'] for v in good['options'].values())}
    assert all(checks.values()),checks
    return {'schema':'SW-PROV-04/v1','evidence':'exact finite authoring regression; paired synthetic fixtures, no model experiment',
            'source_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in sources},
            'factual_ledgers':len(led),'original_trust_flips':trust_flips,'checks':checks,
            'sidecars':{k:spec(k=='calibrated') for k in rows},'variants':rows}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'reaction_receipt.json');p.add_argument('--compact',action='store_true');a=p.parse_args()
    r=run()
    if a.compact:
        digest=hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
        r={k:v for k,v in r.items() if k not in ('variants','sidecars')}
        r['full_receipt_canonical_sha256']=digest
    a.output.write_text(json.dumps(r,sort_keys=True,indent=2,default=str)+'\n');print(json.dumps(r['checks'],indent=2))


if __name__=='__main__':main()
