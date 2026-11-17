"""HG-09: prospective sparse GF2 causal circuit vs trained flat and tied raw networks.

Explicit parity-family inductive prior; not neural mechanistic discovery.
All neural arms train before test generation. World seeds are independent units.
"""
from __future__ import annotations
import argparse, hashlib, json, csv, math, os, random, time, platform
from pathlib import Path
from fractions import Fraction as Q
import numpy as np
import torch
from torch import nn
from torch.nn import functional as Fn
from spiral_ln.hypergames_raw_recurrent import RawNet,task_for,split_data,seed_int,task_fingerprint


def gf2_fit(masks, labels, dimension):
    """Train-only pivot elimination; returns unique parity row or abstains."""
    pivots={}
    for x,y in zip(masks,labels):
        row=int(x); y=int(y)
        while row:
            j=row.bit_length()-1
            if j not in pivots:
                pivots[j]=(row,y)
                break
            z,b=pivots[j];row^=z;y^=b
        if row==0 and y:raise AssertionError('inconsistent labels')
    if len(pivots)!=dimension:return len(pivots),None
    solution=0
    for j in sorted(pivots):
        row,y=pivots[j]
        bit=y^((row&solution).bit_count()%2)
        solution|=bit<<j
    if any((int(x)&solution).bit_count()%2 != int(y) for x,y in zip(masks,labels)):
        raise AssertionError('parity fit consistency failed')
    return len(pivots),solution


def parity_predictions(masks, support):
    return np.fromiter((((int(x)&support).bit_count()&1)!=0 for x in masks),
                       dtype=np.bool_,count=len(masks))


def train_neural(task,arm,train,cal,reg):
    assert arm in ('flat_task','loop_task')
    n=reg['train_n']; torch.manual_seed(seed_int('model',task.seed,task.cohort,task.rank,n)%(2**31))
    model=RawNet(task.dimension,task.rank,flat=(arm=='flat_task'))
    opt=torch.optim.AdamW(model.parameters(),lr=float(reg['neural_budget']['lr']),
                          weight_decay=float(reg['neural_budget']['weight_decay']))
    gen=torch.Generator().manual_seed(seed_int('batches',task.seed,task.cohort,task.rank,n))
    x=torch.from_numpy(train['x']);y=torch.from_numpy(train['y'])
    started=time.perf_counter();model.train()
    for _ in range(reg['neural_budget']['steps']):
        idx=torch.randint(n,(reg['neural_budget']['batch'],),generator=gen)
        goal,_=model(x[idx]);loss=Fn.binary_cross_entropy_with_logits(goal,y[idx])
        opt.zero_grad(set_to_none=True);loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(),1.0);opt.step()
    trained=time.perf_counter()-started
    model.eval()
    with torch.inference_mode():
        logits,_=model(torch.from_numpy(cal['x']))
    p=(logits.numpy()[:,0]>0)
    cal_correct=int(np.sum(p==cal['y'][:,0].astype(bool)))
    release=Q(cal_correct+1,len(p)+2)>Q(3,5)
    return model,{'cal_correct':cal_correct,'released':release,'train_seconds':round(trained,6)}


def forecast_neural(model,x):
    with torch.inference_mode():
        g,_=model(torch.from_numpy(x))
    return g.numpy()[:,0]>0


def get_causal_flags(base,patched_true,patched_irrelevant):
    return (base!=patched_true)&(base==patched_irrelevant)


def score_world(seed,reg):
    task=task_for(seed,reg['cohort'],reg['goal_rank'])
    train=split_data(task,'train',reg['train_n'])
    cal=split_data(task,'calibration',reg['cal_n'])
    trained={arm:train_neural(task,arm,train,cal,reg) for arm in reg['neural_arms']}
    t0=time.perf_counter()
    rank,mask=gf2_fit(train['masks'],train['y'][:,0],task.dimension)
    support_seconds=time.perf_counter()-t0
    if rank!=reg['dimension'] or mask is None or mask.bit_count()!=reg['goal_width']:
        raise AssertionError('frozen full-rank six-sparse gate failed')
    # The true goal mask is available only to the audit here, NEVER the trained support selector.
    if mask!=task.goal_masks[0]:raise AssertionError('structural recovery differs from task oracle')
    support=[i for i in range(task.dimension) if mask&(1<<i)]
    rest=[i for i in range(task.dimension) if not mask&(1<<i)]
    rng=random.Random(seed_int('hg09_null_and_interventions',seed))
    false_support=rng.sample(rest,reg['goal_width'])
    false_mask=sum(1<<i for i in false_support)
    target_bit=support[rng.randrange(len(support))]
    irrelevant_bit=rest[rng.randrange(len(rest))]
    # All models, support selection and release decisions freeze before test data is constructed.
    test=split_data(task,'test',reg['test_n'])
    truth=test['y'][:,0].astype(bool)
    masks=test['masks']
    tx=tuple(x^(1<<target_bit) for x in masks)
    nx=tuple(x^(1<<irrelevant_bit) for x in masks)
    correct={};selectivity={};scores={}
    for arm,(model,info) in trained.items():
        p=forecast_neural(model,test['x'])
        truth_x=test['x'].copy();truth_x[:,target_bit]*=-1
        null_x=test['x'].copy();null_x[:,irrelevant_bit]*=-1
        pt=forecast_neural(model,truth_x); pn=forecast_neural(model,null_x)
        correct[arm]=(p==truth).astype(np.uint8)
        selectivity[arm]=get_causal_flags(p,pt,pn).astype(np.uint8)
        scores[arm]={**info,'test_correct':int(correct[arm].sum()),
          'causal_selectivity':int(selectivity[arm].sum()),
          'flip_true_fraction':float(np.mean(p!=pt)),
          'flip_irrelevant_fraction':float(np.mean(p!=pn))}
    for arm,prior in (('sparse_gf2_compiled',mask),('scrambled_six_support',false_mask)):
        p=parity_predictions(masks,prior)
        pt=parity_predictions(tx,prior);pn=parity_predictions(nx,prior)
        correct[arm]=(p==truth).astype(np.uint8)
        selectivity[arm]=get_causal_flags(p,pt,pn).astype(np.uint8)
        cal_pred=parity_predictions(cal['masks'],prior)
        cal_correct=int(np.sum(cal_pred==cal['y'][:,0].astype(bool)))
        release=Q(cal_correct+1,len(cal['masks'])+2)>Q(3,5)
        scores[arm]={'cal_correct':cal_correct,'released':release,
         'test_correct':int(correct[arm].sum()),
         'causal_selectivity':int(selectivity[arm].sum()),
         'flip_true_fraction':float(np.mean(p!=pt)),
         'flip_irrelevant_fraction':float(np.mean(p!=pn))}
    for arm in scores:
        release=scores[arm]['released'];k=scores[arm]['test_correct']
        scores[arm]['false_releases']=reg['test_n']-k if release else 0
        scores[arm]['true_utility']=str(Q(25*k-15*reg['test_n'],reg['test_n']) if release else Q(0))
    return {'seed':seed,'goal_sha256':task_fingerprint(task),
       'sparse_support_mask_sha256':hashlib.sha256(str(mask).encode()).hexdigest(),
       'GF2_rank':rank,'support_size':mask.bit_count(),
       'compiled_CPU_seconds':round(support_seconds,6),
       'target_bit':target_bit,'irrelevant_bit':irrelevant_bit,
       'random_sham_support':false_support,
       'arms':scores},correct,selectivity


def pack_bits(values):
    return int.from_bytes(np.packbits(values,bitorder='little').tobytes(),'little').to_bytes(32,'little').hex()


def run(reg,limit=0,start=0):
    if reg['schema']!='HG-09/prospective-sparse-causal-v1' or len(reg['world_seeds'])!=64:
        raise ValueError('registered HG09 world suite changed')
    if reg['train_n']!=2048 or reg['cal_n']!=256 or reg['test_n']!=256 or reg['dimension']!=140:
        raise ValueError('registered task shape changed')
    torch.set_num_threads(reg['neural_budget']['torch_threads'])
    worlds=[];raw=[]
    seeds=reg['world_seeds'][start:start+limit] if limit else reg['world_seeds'][start:]
    for seed in seeds:
        world,correct,causal=score_world(seed,reg)
        worlds.append(world)
        raw.append({'seed':seed,'goal_sha256':world['goal_sha256'],
          **{f'{arm}_correct_hex':pack_bits(a) for arm,a in correct.items()},
          **{f'{arm}_causal_hex':pack_bits(a) for arm,a in causal.items()}})
        print(f'HG09 {seed}: flat={world["arms"]["flat_task"]["test_correct"]} '
              f'loop={world["arms"]["loop_task"]["test_correct"]} '
              f'compiled={world["arms"]["sparse_gf2_compiled"]["test_correct"]}',flush=True)
    return worlds,raw


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--registration',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--limit',type=int,default=0);p.add_argument('--start',type=int,default=0)
    args=p.parse_args()
    reg=json.loads(args.registration.read_text());start=time.time()
    worlds,packed=run(reg,args.limit,args.start)
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'hg09_worlds.json').write_text(json.dumps({'schema':'HG09/worlds-v1','worlds':worlds,
      'registration_sha256':hashlib.sha256(args.registration.read_bytes()).hexdigest(),
      'seconds':round(time.time()-start,3),'world_index_start':args.start},indent=2,sort_keys=True)+'\n')
    with (args.out/'hg09_paired_bits.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(packed[0]));w.writeheader();w.writerows(packed)
    print('HG09',len(worlds),'worlds',round(time.time()-start,2),'s')
if __name__=='__main__':main()
