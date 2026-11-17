"""Reconstruct HG-09 world-level FSI-01 claims from frozen packed public outcomes.

Zero training; inspects source-hashed 64-world CSV and original registration.
Works with pinned EvalMath FSI imported by file path to avoid package collisions.
"""
from __future__ import annotations
import argparse,csv,json,hashlib,importlib.util,os
from pathlib import Path
from fractions import Fraction as Q


def unpack(x):
    raw=bytes.fromhex(x)
    if len(raw)!=32:raise ValueError('packed HG09 outcome must be exactly 256 bits')
    return [int(bool(raw[i//8]&(1<<(i%8)))) for i in range(256)]


def load_fsi():
    file=os.getenv('EVALMATH_FSI_FILE')
    if not file or not Path(file).is_file():raise RuntimeError('Set EVALMATH_FSI_FILE to pinned EvalMath source')
    spec=importlib.util.spec_from_file_location('fsi09_evalmath',file)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def audit(reg_file,paired_file,worlds_file=None):
    reg_bytes=Path(reg_file).read_bytes();csv_bytes=Path(paired_file).read_bytes()
    reg=json.loads(reg_bytes)
    if reg['schema']!='HG-09/prospective-sparse-causal-v1' or reg['goal_rank']!=1:
        raise ValueError('registration mismatch')
    data=list(csv.DictReader(csv_bytes.decode().splitlines()))
    expected=reg['world_seeds']
    if len(expected)!=64 or [int(r['seed']) for r in data]!=expected:
        raise ValueError('incomplete/reordered 64 independent-world roster')
    arms=['flat_task','loop_task','sparse_gf2_compiled','scrambled_six_support']
    for row in data:
        for arm in arms:
            for suffix in ['correct_hex','causal_hex']:
                unpack(row[f'{arm}_{suffix}'])
        if unpack(row['sparse_gf2_compiled_correct_hex'])!=[1]*256:
            raise ValueError('compiled learner misses a synthetic parity label')
        if unpack(row['sparse_gf2_compiled_causal_hex'])!=[1]*256:
            raise ValueError('compiled learner fails target/irrelevant causal discrimination')
    fsi=load_fsi()
    def make_cases(metric,cand,control):
        return [{'case_id':f'{row["seed"]}:{i}','cluster_id':row['seed'],
             'candidate':a,'baseline':b}
             for row in data for i,(a,b) in enumerate(zip(unpack(row[f'{cand}_{metric}_hex']),
                                                           unpack(row[f'{control}_{metric}_hex'])))]
    def score(hypothesis,cases,minimum):
        return fsi.evaluate_manifest({'schema_version':1,
             'experiment_id':'HG09-'+hypothesis,
             'target_population':'new 64 independent core-140 six-sparse parity worlds',
             'evaluation_mode':'sampled','alpha':'0.05','minimum_effect':minimum,
             'planned_comparisons':2,'hypothesis_preregistered':True,
             'sealed_readout':True,'clusters_independent':True,'exchangeable_pair_labels':True,
             'min_independent_clusters':20,'signflip_simulations':20000,
             'bootstrap_resamples':4096,'resample_seed':20261117,'cases':cases})
    h1=score('H1-sparse-task-vs-loop',make_cases('correct','sparse_gf2_compiled','loop_task'),'0.10')
    h2=score('H2-target-irrelevant-selectivity-vs-sham',make_cases('causal','sparse_gf2_compiled','scrambled_six_support'),'0.50')
    sums={arm:{'correct':sum(sum(unpack(r[f'{arm}_correct_hex'])) for r in data),
                'selective':sum(sum(unpack(r[f'{arm}_causal_hex'])) for r in data)} for arm in arms}
    output={'schema':'HG09/FSI01-audit-v1','worlds':64,'states_per_world':256,
       'source_sha256':{'registration':hashlib.sha256(reg_bytes).hexdigest(),
                        'paired_bits':hashlib.sha256(csv_bytes).hexdigest()},
       'totals':sums,'H1':h1,'H2':h2,
       'scientific_scope':'Programmatically compiled known-parity-family prior. No emergent neural mechanistic discovery or native storyworld gameplay.'}
    if worlds_file:
        worlds=json.loads(Path(worlds_file).read_text())['worlds']
        if [w['seed'] for w in worlds]!=expected:raise ValueError('world summaries mismatch roster')
        for w,r in zip(worlds,data):
            for arm in arms:
                if w['arms'][arm]['test_correct']!=sum(unpack(r[f'{arm}_correct_hex'])):raise ValueError('world archive has inconsistent test count')
                if w['arms'][arm]['causal_selectivity']!=sum(unpack(r[f'{arm}_causal_hex'])):raise ValueError('world archive has inconsistent causal count')
        output['world_archive_sha256']=hashlib.sha256(Path(worlds_file).read_bytes()).hexdigest()
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registration',type=Path,required=True)
    parser.add_argument('--paired',type=Path,required=True)
    parser.add_argument('--worlds',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    a=parser.parse_args()
    x=audit(a.registration,a.paired,a.worlds)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
    print('HG09 scored',x['worlds'],'worlds; H1',x['H1']['verdict'],'H2',x['H2']['verdict'])
if __name__=='__main__':main()
