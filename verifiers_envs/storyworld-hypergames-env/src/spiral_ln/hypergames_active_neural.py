"""HG-08 actual CPU PyTorch recurrent ablation with intervention-informed masks.

All neural arms are the same 3-loop RawNet with identical initialization,
training batches, number of updates, and feature dimension per cohort.
The masked input subset is obtained from a separate causal intervention oracle;
the privileged arm receives ground truth support as an explicit ceiling.
"""
from __future__ import annotations
import csv
import hashlib
import json
import platform
import time
from fractions import Fraction as Q
from pathlib import Path
from random import Random

import numpy as np
import torch
from torch.nn import functional as F

from spiral_ln.hypergames_active_causal import (
    SEEDS, make_problem, _private_goal, discover, seed_int,
)
from spiral_ln.hypergames_raw_recurrent import RawNet

NEURAL_SEEDS = SEEDS[:6]
NEURAL_COHORTS = ('core_140','native_512')
NEURAL_ARMS = ('raw_loop','causal_masked_loop',
               'privileged_true_support_masked_loop','random_six_masked_loop')
N_TRAIN=512
N_CAL=256
N_TEST=256
STEPS=350
BATCH=128


def data(seed:int,dim:int,goal_mask:int,split:str,n:int) -> tuple[np.ndarray,np.ndarray]:
    if split not in ('train','cal','test') or dim not in (140,512):
        raise ValueError('invalid data request')
    bitrows=[]; labels=[]
    for i in range(n):
        v=Random(seed_int('neuraldata',seed,split,i)).getrandbits(1024) & ((1<<dim)-1)
        bitrows.append(v.to_bytes((dim+7)//8,'little'))
        labels.append((v & goal_mask).bit_count()&1)
    bytearr=np.frombuffer(b''.join(bitrows),dtype=np.uint8).reshape(n,(dim+7)//8)
    X=np.unpackbits(bytearr,bitorder='little',axis=1)[:,:dim].copy().astype(np.float32)*2-1
    Y=np.array(labels,dtype=np.float32).reshape(n,1)
    return X,Y


def choose_support(problem, arm:str, budget:int=512) -> tuple[set[int],bool,int]:
    if arm == 'raw_loop': return set(range(problem.dimension)),True,0
    if arm == 'causal_masked_loop':
        result=discover(problem,budget,'adaptive_hash')
        return set(result.known[0]),result.completed,result.queries
    if arm == 'privileged_true_support_masked_loop':
        mask=_private_goal(problem)[0]
        return {i for i in range(problem.dimension) if (mask>>i)&1},True,0
    if arm == 'random_six_masked_loop':
        rng=Random(seed_int('neuralrandom',problem.seed,problem.cohort))
        return set(rng.sample(range(problem.dimension),6)),True,0
    raise ValueError('invalid registered model arm')


def train_one(problem, arm:str)->dict:
    torch.set_num_threads(2)
    dim=problem.dimension
    goal=_private_goal(problem)[0]
    support,certified,queries=choose_support(problem,arm)
    Xtr,Ytr=data(problem.seed,dim,goal,'train',N_TRAIN)
    Xcal,Ycal=data(problem.seed,dim,goal,'cal',N_CAL)
    Xte,Yte=data(problem.seed,dim,goal,'test',N_TEST)
    if arm!='raw_loop':
        gate=np.zeros(dim,dtype=np.float32)
        gate[list(support)]=1
        Xtr*=gate;Xcal*=gate;Xte*=gate
    torch.manual_seed(seed_int('neural_init',problem.seed,problem.cohort)%(2**31))
    model=RawNet(dim,1,flat=False)
    opt=torch.optim.AdamW(model.parameters(),lr=.003,weight_decay=.001)
    rng=torch.Generator().manual_seed(seed_int('neural_batches',problem.seed,problem.cohort)%(2**63))
    xx=torch.from_numpy(Xtr);yy=torch.from_numpy(Ytr)
    start=time.perf_counter()
    for _ in range(STEPS):
        sample=torch.randint(N_TRAIN,(BATCH,),generator=rng)
        pred,_=model(xx[sample]);loss=F.binary_cross_entropy_with_logits(pred,yy[sample])
        opt.zero_grad(set_to_none=True);loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(),max_norm=1.0)
        opt.step()
    elapsed=time.perf_counter()-start
    model.eval()
    with torch.inference_mode():
        pc=(model(torch.from_numpy(Xcal))[0].numpy()>0)
        pt=(model(torch.from_numpy(Xte))[0].numpy()>0)
    cc=int((pc==Ycal.astype(bool)).sum());tc=int((pt==Yte.astype(bool)).sum())
    release=Q(cc+1,N_CAL+2)>Q(3,5) and (certified or arm!='causal_masked_loop')
    return {'seed':problem.seed,'cohort':problem.cohort,'dimension':dim,'goal_rank':1,
            'arm':arm,'n_train':N_TRAIN,'training_steps':STEPS,
            'input_features_visible':len(support),'support_complete':int(certified),
            'causal_query_count':queries,'parameter_count':sum(p.numel() for p in model.parameters()),
            'final_train_loss':round(float(loss.detach()),7),
            'training_seconds':round(elapsed,5),'cal_correct':cc,'test_correct':tc,
            'released':int(release),'false_accept':(N_TEST-tc) if release else 0,
            'true_utility':str(Q(25*tc-15*N_TEST,N_TEST) if release else Q(0))}


def run(seeds=NEURAL_SEEDS,cohorts=NEURAL_COHORTS)->list[dict]:
    rows=[]
    for seed in seeds:
        for cohort in cohorts:
            public=make_problem(seed,cohort,1)
            for arm in NEURAL_ARMS:
                rows.append(train_one(public,arm))
            print('HG08 neural trained',seed,cohort,flush=True)
    return rows


def summary(rows:list[dict])->dict:
    groups=[]
    for cohort in NEURAL_COHORTS:
        for arm in NEURAL_ARMS:
            sub=[r for r in rows if r['cohort']==cohort and r['arm']==arm]
            if not sub:continue
            groups.append({'cohort':cohort,'arm':arm,'n':len(sub),
                 'test_accuracy':str(Q(sum(r['test_correct'] for r in sub),N_TEST*len(sub))),
                 'mean_true_utility':str(sum((Q(r['true_utility']) for r in sub),Q(0))/len(sub)),
                 'false_accepts':sum(r['false_accept'] for r in sub),
                 'released':sum(r['released'] for r in sub),
                 'mean_training_seconds':round(sum(r['training_seconds'] for r in sub)/len(sub),4)})
    wins=[]
    for seed in NEURAL_SEEDS:
        raw=next((r for r in rows if (r['seed'],r['cohort'],r['arm'])==(seed,'core_140','raw_loop')),None)
        causal=next((r for r in rows if (r['seed'],r['cohort'],r['arm'])==(seed,'core_140','causal_masked_loop')),None)
        if raw and causal:wins.append({'seed':seed,'causal_beats_raw':causal['test_correct']>raw['test_correct'],
                       'delta_test_correct':causal['test_correct']-raw['test_correct']})
    return {'schema':'HG-08/neural-causal-v1','rows':len(rows),'groups':groups,
            'H5':{'paired_wins':sum(x['causal_beats_raw'] for x in wins),'n':len(wins),
                  'passes':len(wins)==6 and sum(x['causal_beats_raw'] for x in wins)>=4,
                  'pairs':wins},
            'runtime_versions':{'torch':torch.__version__,'numpy':np.__version__,'python':platform.python_version()},
            'scope':'actual synthetic CPU training; intervention-derived feature masking, not end-to-end causal learning'}


def write_csv(rows,path:Path):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--smoke',action='store_true')
    args=ap.parse_args()
    result=run(seeds=NEURAL_SEEDS[:1] if args.smoke else NEURAL_SEEDS,
               cohorts=NEURAL_COHORTS[:1] if args.smoke else NEURAL_COHORTS)
    write_csv(result,args.out/'hg08_neural_seed_rows.csv')
    (args.out/'hg08_neural_summary.json').write_text(json.dumps(summary(result),indent=2,sort_keys=True)+'\n')
    print(summary(result)['H5'],flush=True)
