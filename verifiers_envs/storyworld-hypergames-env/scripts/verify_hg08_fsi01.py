"""Reproduce FSI-01 from HG-08's compact 32-world per-case correctness archive.

The packed bits retain every paired 0/1 result without storing 16,384 JSONL
records in Git. This script has no neural dependencies. For an independent
neural replay, use --replay-dir to compare the CPU runner's emitted JSONL.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,os,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'Hypergames/single_player/hg08_registration_v1.json'
BITS=ROOT/'output/evaluation_hypergames/hg08/hg08_paired_bits_v1.csv'

def load_fsi():
    f=os.environ.get('EVALMATH_FSI_FILE')
    if not f or not Path(f).is_file():raise RuntimeError('Set EVALMATH_FSI_FILE to a pinned EvalMath FSI source file')
    spec=importlib.util.spec_from_file_location('hg08_pinned_fsi',f)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def decode(hex64):
    if not re.fullmatch('[0-9a-f]{64}',hex64):raise ValueError('expected 256 packed bits as 64 lowercase hex digits')
    return list(map(int,bin(int(hex64,16))[2:].zfill(256)))

def audit(reg_path=REG,bits_path=BITS,replay_dir=None):
    reg_bytes=reg_path.read_bytes();bit_bytes=bits_path.read_bytes();reg=json.loads(reg_bytes)
    if reg['schema']!='HG-08/prospective-independent-world-v1' or reg['split_counts']['test']!=256:raise ValueError('registration mismatch')
    with bits_path.open(newline='') as f: rows=list(csv.DictReader(f))
    if len(rows)!=32 or [int(x['seed']) for x in rows]!=reg['seeds']:raise ValueError('expected exactly 32 frozen independent world seeds')
    a={k:[] for k in ('H1','H2')};worlds=[]
    for row in rows:
        seed=row['seed'];flat=decode(row['flat_correct_bits_hex']);loop=decode(row['loop_correct_bits_hex']);aux=decode(row['aux_correct_bits_hex'])
        cal=[int(row[f'{name}_cal']) for name in ('flat','loop','aux')]
        if any((c+1)*5 > 3*258 for c in cal):raise ValueError('a released arm conflicts with the frozen no-release archive')
        if int(row['gf2_correct'])!=256:raise ValueError('structural GF2 comparator failed')
        if not re.fullmatch('[0-9a-f]{64}',row['goal_sha256']):raise ValueError('missing goal fingerprint')
        worlds.append({'seed':int(seed),'correct':[sum(flat),sum(loop),sum(aux)],'calibration':cal})
        for i,(f,l,u) in enumerate(zip(flat,loop,aux)):
            base={'case_id':f'{seed}-{i}','cluster_id':seed}
            a['H1'].append({**base,'candidate':l,'baseline':f})
            a['H2'].append({**base,'candidate':u,'baseline':l})
    if replay_dir:
        for tag in ('H1','H2'):
            lines=[json.loads(line) for line in (Path(replay_dir)/f'hg08_{tag}_paired.jsonl').read_text().splitlines() if line]
            if lines!=a[tag]:raise ValueError(f'{tag} independent CPU replay differs from archived outcomes')
    fsi=load_fsi();reports={}
    for tag,cases in a.items():
        args={'schema_version':1,'experiment_id':'HG08-'+tag,
              'target_population':'HG08 32 fresh synthetic goal worlds, world-macro',
              'evaluation_mode':'sampled','alpha':'0.05','minimum_effect':'0','planned_comparisons':2,
              'hypothesis_preregistered':True,'sealed_readout':True,
              'clusters_independent':True,'exchangeable_pair_labels':True,'min_independent_clusters':20,
              'bootstrap_resamples':reg['analysis_policy']['cluster_bootstrap_resamples'],
              'signflip_simulations':reg['analysis_policy']['signflip_simulations'],
              'resample_seed':reg['analysis_policy']['resample_seed'],'cases':cases}
        reports[tag]=fsi.evaluate_manifest(args)
    return {'schema':'HG08/fsi01-independent-source-audit-v1','n_worlds':32,'n_case_rows_per_test':8192,
            'source_sha256':{'registration':hashlib.sha256(reg_bytes).hexdigest(),'packed_pairs':hashlib.sha256(bit_bytes).hexdigest()},
            'worlds':worlds,'fsi01':reports,
            'scope':'Public 32-world synthetic parity; no HG03 private seeds or narrative model evaluation.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--registration',type=Path,default=REG)
    p.add_argument('--bits',type=Path,default=BITS);p.add_argument('--replay-dir',type=Path)
    p.add_argument('--out',type=Path);x=p.parse_args()
    r=audit(x.registration,x.bits,x.replay_dir);s=json.dumps(r,sort_keys=True,indent=2)+'\n'
    if x.out:x.out.parent.mkdir(parents=True,exist_ok=True);x.out.write_text(s)
    else:print(s)
    print('HG08 audit:',r['n_worlds'],'worlds; H1 p_adj',r['fsi01']['H1']['p_bonferroni'],'H2 p_adj',r['fsi01']['H2']['p_bonferroni'])
if __name__=='__main__':main()
