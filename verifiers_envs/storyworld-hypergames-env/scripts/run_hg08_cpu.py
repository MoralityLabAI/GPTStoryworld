"""HG-08: preregistered 32 independent world CPU parity confirmation.

Depends on unchanged HG-07 RawNet and generator; same training objective,
width, steps, optimizer and seed key. The test split is generated after all
models in a world have been trained and their calibration gates fixed.
Only public synthetic generator worlds are scored.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,time,platform,os,importlib.util
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from spiral_ln.hypergames_raw_recurrent import task_for,split_data,RawNet,seed_int,task_fingerprint
def _load_fsi():
    path=os.environ.get('EVALMATH_FSI_FILE')
    if not path or not Path(path).is_file():
        raise RuntimeError('Set EVALMATH_FSI_FILE to pinned EvalMath/src/spiral_ln/evaluation_finite_sample.py')
    spec=importlib.util.spec_from_file_location('evalmath_fsi01_for_hg08',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.evaluate_manifest


REG_REL='Hypergames/single_player/hg08_registration_v1.json'
ARMS=('flat_task','loop_task','loop_true_fragment_aux')

def gf2_fit(train,task):
    """Exact GF(2) Gaussian elimination of raw training x->parity label."""
    piv={}
    for x,y in zip(train['masks'],train['y'][:,0]):
        row=int(x);value=int(y)
        while row:
            lead=row.bit_length()-1
            if lead not in piv:
                piv[lead]=(row,value);break
            z,b=piv[lead];row^=z;value^=b
        if not row and value:raise AssertionError('inconsistent parity data')
    if len(piv)!=task.dimension:return len(piv),None
    recovered=0
    for lead in sorted(piv):
        row,value=piv[lead]
        bit=value^((row&recovered).bit_count()%2)
        recovered|=bit<<lead
    if recovered != task.goal_masks[0]:raise AssertionError('GF2 solution mismatch')
    return len(piv),recovered

def train_arm(task,arm,train,cal,cfg):
    torch.manual_seed(seed_int('model',task.seed,task.cohort,task.rank,cfg['split_counts']['train'])%(2**31))
    model=RawNet(task.dimension,task.rank,flat=(arm=='flat_task'))
    opt=torch.optim.AdamW(model.parameters(),lr=float(cfg['training']['lr']),weight_decay=float(cfg['training']['weight_decay']))
    rng=torch.Generator().manual_seed(seed_int('batches',task.seed,task.cohort,task.rank,cfg['split_counts']['train']))
    x=torch.from_numpy(train['x']);y=torch.from_numpy(train['y']);f=torch.from_numpy(train['fragment'])
    model.train()
    for _ in range(cfg['training']['steps']):
        idx=torch.randint(len(x),(cfg['training']['batch'],),generator=rng)
        goals,frag=model(x[idx]);loss=F.binary_cross_entropy_with_logits(goals,y[idx])
        if arm=='loop_true_fragment_aux':loss+=F.binary_cross_entropy_with_logits(frag,f[idx])
        opt.zero_grad(set_to_none=True);loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1.0);opt.step()
    model.eval()
    with torch.inference_mode():
        cg,cf=model(torch.from_numpy(cal['x']))
        cdir=(cg.numpy()>0)
        ccomp=np.logical_xor.reduce((cf.numpy()>0).reshape(len(cal['x']),1,3),axis=2)
    calpred=ccomp if arm=='loop_true_fragment_aux' else cdir
    calcorrect=int((calpred[:,0]==cal['y'][:,0]).sum())
    release=Q(calcorrect+1,len(cal['x'])+2)>Q(3,5)
    return model,calcorrect,release

def score_world(seed,cfg):
    task=task_for(seed,cfg['cohort'],cfg['goal_rank'])
    train=split_data(task,'train',cfg['split_counts']['train'])
    cal=split_data(task,'calibration',cfg['split_counts']['calibration'])
    fitted={arm:train_arm(task,arm,train,cal,cfg) for arm in ARMS}
    # Test labels first accessed here, after all three model arms and releases freeze.
    test=split_data(task,'test',cfg['split_counts']['test']);truth=test['y'][:,0].astype(bool)
    measured={};predictions={}
    for arm,(model,cc,release) in fitted.items():
        with torch.inference_mode():
            goals,frags=model(torch.from_numpy(test['x']))
            direct=(goals.numpy()[:,0]>0)
            composed=np.logical_xor.reduce((frags.numpy()>0).reshape(len(test['x']),1,3),axis=2)[:,0]
        result=composed if arm=='loop_true_fragment_aux' else direct
        correct=(result==truth).astype(int).tolist()
        predictions[arm]=correct
        measured[arm]={'cal_correct':cc,'test_correct':sum(correct),'released':bool(release),
            'false_releases':len(truth)-sum(correct) if release else 0,
            'test_utility':str(Q(25*sum(correct)-15*len(truth),len(truth)) if release else Q(0))}
    gf_rank, gf_mask=gf2_fit(train,task)
    gf_ok=gf_mask is not None and all(((int(x)&gf_mask).bit_count()%2)==int(y) for x,y in zip(test['masks'],truth))
    if not gf_ok:raise AssertionError('GF2 structural baseline failed in a registered world')
    return {'seed':seed,'goal_sha256':task_fingerprint(task),'gf2_rank':gf_rank,'gf2_test_correct':len(truth),
            'arms':measured},predictions

def run(cfg,limit=None):
    if cfg['schema']!='HG-08/prospective-independent-world-v1' or cfg['trained_arms']!=list(ARMS):raise ValueError('registration mismatch')
    if cfg['training']['model']!='HG07 frozen RawNet' or cfg['training']['steps']!=350:raise ValueError('architecture protocol changed')
    torch.set_num_threads(cfg['training']['threads'])
    seeds=cfg['seeds'][:limit] if limit else cfg['seeds']
    if len(set(seeds))!=len(seeds) or len(cfg['seeds'])!=32:raise ValueError('fresh world list malformed')
    worlds=[];pair1=[];pair2=[]
    for seed in seeds:
        row,pred=score_world(seed,cfg);worlds.append(row)
        for i,(x,y) in enumerate(zip(pred['loop_task'],pred['flat_task'])):
            pair1.append({'case_id':f'{seed}-{i}', 'cluster_id':str(seed),'candidate':x,'baseline':y})
        for i,(x,y) in enumerate(zip(pred['loop_true_fragment_aux'],pred['loop_task'])):
            pair2.append({'case_id':f'{seed}-{i}', 'cluster_id':str(seed),'candidate':x,'baseline':y})
        print(f'HG08 seed {seed} complete; flat {row["arms"]["flat_task"]["test_correct"]}; loop {row["arms"]["loop_task"]["test_correct"]}; aux {row["arms"]["loop_true_fragment_aux"]["test_correct"]}',flush=True)
    def inferred(name,cases):
        x={'schema_version':1,'experiment_id':f'HG08-{name}','target_population':'HG08 32 fresh synthetic goal worlds, world-macro','evaluation_mode':'sampled',
        'alpha':'0.05','minimum_effect':'0','planned_comparisons':2,'hypothesis_preregistered':True,
        'sealed_readout':True,'clusters_independent':True,'exchangeable_pair_labels':True,
        'min_independent_clusters':20,'bootstrap_resamples':cfg['analysis_policy']['cluster_bootstrap_resamples'],
        'signflip_simulations':cfg['analysis_policy']['signflip_simulations'],
        'resample_seed':cfg['analysis_policy']['resample_seed'],'cases':cases}
        return _load_fsi()(x)
    reports={}
    if limit is None:reports={'H1':inferred('H1',pair1),'H2':inferred('H2',pair2)}
    return {'schema':'HG-08/frozen-cpu-results-v1','number_worlds':len(worlds),'per_world_test':cfg['split_counts']['test'],
        'evidence':'synthetic trained neural models, GF2 family-prior comparator','worlds':worlds,
        'fsi01':reports,'control':'All arms trained before test labels; HG03 private data unused'}, pair1,pair2

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--registration',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--smoke',action='store_true');args=p.parse_args()
    cfg=json.loads(args.registration.read_text());t=time.time()
    if args.smoke:
        cfg=dict(cfg,seeds=[2026111799]+cfg['seeds'][1:]);result,a,b=run(cfg,limit=1)
    else:result,a,b=run(cfg)
    result['runtime']={'seconds':round(time.time()-t,3),'python':platform.python_version(),'torch':torch.__version__,'numpy':np.__version__}
    result['registration_sha256']=hashlib.sha256(args.registration.read_bytes()).hexdigest()
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'hg08_fsi01.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for name,rows in (('H1',a),('H2',b)):
        with (args.out/f'hg08_{name}_paired.jsonl').open('w') as f:
            for row in rows:f.write(json.dumps(row,sort_keys=True)+'\n')
    print('HG08',len(result['worlds']),'worlds',round(time.time()-t,2),'seconds',flush=True)
if __name__=='__main__':main()
