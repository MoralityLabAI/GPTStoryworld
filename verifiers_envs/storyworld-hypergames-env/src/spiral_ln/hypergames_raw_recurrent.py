"""HG-07: synthetic raw-state parity training with actual CPU PyTorch models.

Task inputs contain raw public binary state only. True two-bit fragment labels
are generated solely for a declared privileged auxiliary-training arm. All
model selection and thresholding use development/training/calibration splits;
held-out test labels are accessed only by scoring.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import csv
import os
import platform
import time
from dataclasses import dataclass
from pathlib import Path
from random import Random
from fractions import Fraction as Q
import numpy as np
import torch
from torch import nn
import torch.nn.functional as Fn
from spiral_ln.evaluation_hypergames_rank import rank
from spiral_ln.evaluation_hypergames_raw import fit_raw_system, parity_mask, sparse_collision_union_bound

VERSION='HG-07/raw-state-recurrent-v1'
COHORTS=('core_140','padded_512','native_512')
RANKS=(1,2)
TRAIN=(512,2048)
SEEDS=(2026111771,2026111772,2026111773,2026111774,2026111775,2026111776)
N_CAL=256; N_TEST=256; N_MAXTRAIN=2048
STEPS=350; WIDTH=64; BATCH=128; LOOP_STEPS=3
ARMS=('linear_task','flat_task','loop_task','loop_true_fragment_aux','loop_shuffled_fragment_aux')
RANDOM_REPS=100


def seed_int(*names)->int:
    key='HG07:'+':'.join(map(str,names))
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8],'little') % (2**63)


def cohort_detail(cohort:str):
    if cohort not in COHORTS:raise ValueError('cohort')
    d=140 if cohort=='core_140' else 512
    family='core' if cohort!='native_512' else 'native512'
    return d,family


@dataclass(frozen=True)
class Task:
    seed:int; cohort:str; dimension:int; rank:int
    goal_masks:tuple[int,...]
    fragment_masks:tuple[tuple[int,int,int],...]


def task_for(seed:int,cohort:str,k:int)->Task:
    if type(seed) is not int or k not in RANKS:raise ValueError('task')
    d,family=cohort_detail(cohort)
    used=Random(seed_int('support',seed,family,k)).sample(range(140 if family=='core' else d),6*k)
    frag=tuple(tuple(sum(1<<i for i in used[6*j+2*t:6*j+2*t+2]) for t in range(3)) for j in range(k))
    goal=tuple(a^b^c for a,b,c in frag)
    assert rank(goal,d)==k and all(row.bit_count()==6 for row in goal)
    return Task(seed,cohort,d,k,goal,frag)


def split_input_masks(seed:int,split:str,count:int,dimension:int)->tuple[int,...]:
    if split not in ('train','calibration','test') or dimension not in (140,512):raise ValueError('split')
    full=(1<<dimension)-1
    return tuple(Random(seed_int('data',seed,split,i)).getrandbits(512)&full for i in range(count))


def as_bits(masks:tuple[int,...],dimension:int)->np.ndarray:
    raw=b''.join(x.to_bytes(64,'little') for x in masks)
    b=np.frombuffer(raw,dtype=np.uint8).reshape(len(masks),64)
    return np.unpackbits(b,axis=1,bitorder='little')[:,:dimension].copy().astype(np.float32)


def split_data(task:Task,split:str,n:int)->dict:
    xmask=split_input_masks(task.seed,split,n,task.dimension)
    x=as_bits(xmask,task.dimension)
    goals=np.column_stack([np.bitwise_xor.reduce(x[:,[i for i in range(task.dimension) if (mask>>i)&1]].astype(np.uint8),axis=1) for mask in task.goal_masks]).astype(np.float32)
    fragments=np.column_stack([np.bitwise_xor.reduce(x[:,[i for i in range(task.dimension) if (mask>>i)&1]].astype(np.uint8),axis=1) for trio in task.fragment_masks for mask in trio]).astype(np.float32)
    return dict(masks=xmask, x=x*2-1, y=goals,fragment=fragments)


def task_fingerprint(task:Task)->str:
    b=','.join(str(i) for i in task.goal_masks).encode()
    return hashlib.sha256(b).hexdigest()


class RawNet(nn.Module):
    def __init__(self,dimension:int,k:int,flat:bool=False):
        super().__init__()
        self.flat=flat
        self.in_proj=nn.Linear(dimension,WIDTH)
        self.cell=nn.Linear(WIDTH,WIDTH)
        self.goal=nn.Linear(WIDTH,k)
        self.fragment=nn.Linear(WIDTH,3*k)

    def forward(self,x):
        h=torch.tanh(self.in_proj(x))
        for _ in range(1 if self.flat else LOOP_STEPS):
            h=h+torch.tanh(self.cell(h))/3
        return self.goal(h), self.fragment(h)


def performance(pred:np.ndarray,truth:np.ndarray)->dict:
    if pred.shape!=truth.shape:raise ValueError('prediction shape mismatch')
    ok=(pred==truth.astype(bool))
    return {'joint':int(np.all(ok,axis=1).sum()),'bit':int(ok.sum())}


def measure_and_gate(cal:np.ndarray,test:np.ndarray,cal_truth:np.ndarray,test_truth:np.ndarray)->dict:
    a=performance(cal,cal_truth);b=performance(test,test_truth)
    release=Q(a['joint']+1,N_CAL+2)>Q(3,5)
    false_accept=(N_TEST-b['joint']) if release else 0
    value=Q(25*b['joint']-15*N_TEST,N_TEST) if release else Q(0)
    return {'cal_joint_correct':a['joint'],'test_joint_correct':b['joint'],
            'test_bit_correct':b['bit'],'release':int(release),
            'false_accept':false_accept,'true_utility':str(value)}


def f2_reference(task:Task,train:dict,cal:dict,test:dict)->dict:
    def codes(y):
        return tuple(sum(int(y[i,j])<<j for j in range(task.rank)) for i in range(len(y)))
    fit=fit_raw_system(train['masks'],codes(train['y']),task.dimension,task.rank)
    # A conservative exact-information policy: abstain until the raw training
    # design spans all input coordinates. Otherwise test inputs could remain
    # observationally ambiguous under the unrestricted parity hypothesis set.
    full=fit.rank==task.dimension
    pred=[]
    for x in test['masks']:
        code=fit.predict_if_identified(x)
        pred.append(code)
    known=sum(p is not None for p in pred)
    correct=sum(p == y for p,y in zip(pred,codes(test['y'])))
    return {'f2_rank':fit.rank,'f2_nullity':task.dimension-fit.rank,
            'f2_test_determined':known,'f2_test_correct_if_determined':correct,
            'f2_release':int(full),'f2_false_accept':0,
            'f2_utility':'10' if full else '0'}


def train_neural(task:Task,arm:str,ntrain:int,train:dict,cal:dict,test:dict)->dict:
    if arm not in ARMS or ntrain not in TRAIN:raise ValueError('registered model/size only')
    torch.set_num_threads(2)
    torch.manual_seed(seed_int('model',task.seed,task.cohort,task.rank,ntrain)%(2**31))
    if arm=='linear_task':model=nn.Linear(task.dimension,task.rank)
    else:model=RawNet(task.dimension,task.rank,flat=(arm=='flat_task'))
    opt=torch.optim.AdamW(model.parameters(),lr=.003,weight_decay=.001)
    # Every arm sees the identical train sampling sequence per condition.
    batchgen=torch.Generator().manual_seed(seed_int('batches',task.seed,task.cohort,task.rank,ntrain))
    x=torch.from_numpy(train['x'][:ntrain]);y=torch.from_numpy(train['y'][:ntrain]);f=torch.from_numpy(train['fragment'][:ntrain])
    shuffled=None
    if arm=='loop_shuffled_fragment_aux':
        p=np.random.default_rng(seed_int('shuffle',task.seed,task.cohort,task.rank,ntrain)).permutation(ntrain)
        shuffled=torch.from_numpy(train['fragment'][p].copy())
    st=time.perf_counter();last_loss=0.
    model.train()
    for _ in range(STEPS):
        idx=torch.randint(ntrain,(BATCH,),generator=batchgen)
        if arm=='linear_task':
            goal=model(x[idx]); aux=None
        else:goal,aux=model(x[idx])
        loss=Fn.binary_cross_entropy_with_logits(goal,y[idx])
        if arm in ('loop_true_fragment_aux','loop_shuffled_fragment_aux'):
            targets=f[idx] if shuffled is None else shuffled[idx]
            loss=loss+Fn.binary_cross_entropy_with_logits(aux,targets)
        opt.zero_grad(set_to_none=True);loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(),max_norm=1.0)
        opt.step();last_loss=float(loss.detach())
    train_seconds=time.perf_counter()-st
    model.eval()
    with torch.inference_mode():
        if arm=='linear_task':
            cgoal=model(torch.from_numpy(cal['x'])).numpy()
            tgoal=model(torch.from_numpy(test['x'])).numpy()
            cfrag=tfrag=None
        else:
            cgoal, cfrag=model(torch.from_numpy(cal['x']))
            tgoal, tfrag=model(torch.from_numpy(test['x']))
            cgoal=cgoal.numpy();tgoal=tgoal.numpy();cfrag=cfrag.numpy();tfrag=tfrag.numpy()
    direct=measure_and_gate(cgoal>0,tgoal>0,cal['y'],test['y'])
    extra={}
    if cfrag is not None:
        fc=cfrag>0; ft=tfrag>0
        extra['fragment_cal_correct']=int((fc==cal['fragment'].astype(bool)).sum())
        extra['fragment_test_correct']=int((ft==test['fragment'].astype(bool)).sum())
        if arm in ('loop_true_fragment_aux','loop_shuffled_fragment_aux'):
            compose_c=np.logical_xor.reduce(fc.reshape(N_CAL,task.rank,3),axis=2)
            compose_t=np.logical_xor.reduce(ft.reshape(N_TEST,task.rank,3),axis=2)
            extra['composed']=measure_and_gate(compose_c,compose_t,cal['y'],test['y'])
    return {'arm':arm,'train_loss':round(last_loss,8),'training_seconds':round(train_seconds,5),
            'param_count':sum(p.numel() for p in model.parameters()),'direct':direct,**extra}


def random_reference(task:Task,ntrain:int,train:dict,cal:dict,test:dict)->dict:
    rng=Random(seed_int('random',task.seed,task.cohort,task.rank,ntrain))
    def parity(rows,masks):
        return np.stack([np.fromiter((parity_mask(x,m) for x in masks),dtype=np.bool_,count=len(masks)) for m in rows],axis=1)
    scores=[]
    for _ in range(RANDOM_REPS):
        rows=[]
        while len(rows)<task.rank:
            mask=sum(1<<i for i in rng.sample(range(task.dimension),6))
            if rank((*rows,mask),task.dimension)>len(rows):rows.append(mask)
        ptrain=parity(rows,train['masks'][:ntrain]);pcal=parity(rows,cal['masks']);ptest=parity(rows,test['masks'])
        inverted=np.array([np.mean(ptrain[:,i] != train['y'][:ntrain,i])>.5 for i in range(task.rank)])
        m=measure_and_gate(np.logical_xor(pcal,inverted),np.logical_xor(ptest,inverted),cal['y'],test['y'])
        scores.append(m['test_joint_correct'])
    return {'random_mean_test_joint':str(Q(sum(scores),RANDOM_REPS*N_TEST)),
            'random_max_test_joint':max(scores),'random_scores':scores}


def evaluate_task(task:Task,ntrain:int)->list[dict]:
    train=split_data(task,'train',N_MAXTRAIN)
    cal=split_data(task,'calibration',N_CAL)
    test=split_data(task,'test',N_TEST)
    gf=f2_reference(task,train if ntrain==N_MAXTRAIN else {**train,'masks':train['masks'][:ntrain],'y':train['y'][:ntrain]},cal,test)
    random=random_reference(task,ntrain,train,cal,test)
    out=[]
    for arm in ARMS:
        net=train_neural(task,arm,ntrain,train,cal,test)
        p=Q(1+sum(s>=net['direct']['test_joint_correct'] for s in random['random_scores']),RANDOM_REPS+1)
        row={'seed':task.seed,'cohort':task.cohort,'dimension':task.dimension,'goal_rank':task.rank,
            'train_n':ntrain,'arm':arm,'goal_mask_sha256':task_fingerprint(task),
            'train_loss':net['train_loss'],'training_seconds':net['training_seconds'],
            'param_count':net['param_count'],
            **{'direct_'+k:v for k,v in net['direct'].items()},
            'fragment_test_correct':net.get('fragment_test_correct'),
            'composed_test_joint_correct':net.get('composed',{}).get('test_joint_correct'),
            'composed_true_utility':net.get('composed',{}).get('true_utility'),
            'composed_false_accept':net.get('composed',{}).get('false_accept'),
            'composed_release':net.get('composed',{}).get('release'),
            'f2_rank':gf['f2_rank'],'f2_nullity':gf['f2_nullity'],
            'f2_test_determined':gf['f2_test_determined'],'f2_release':gf['f2_release'],
            'f2_test_correct_if_determined':gf['f2_test_correct_if_determined'],
            'random_mean_test_joint':random['random_mean_test_joint'],
            'random_rank_p':str(p),
            'sparse_union_bound':str(sparse_collision_union_bound(task.dimension,6,ntrain))}
        out.append(row)
    return out


def run(seeds=SEEDS,cohorts=COHORTS,ranks=RANKS,train_sizes=TRAIN):
    results=[]
    for seed in seeds:
        for cohort in cohorts:
            for k in ranks:
                task=task_for(seed,cohort,k)
                for n in train_sizes:
                    results.extend(evaluate_task(task,n))
                    print(f'HG07 seed={seed} cohort={cohort} k={k} n={n} complete',flush=True)
    return results


def summarize(rows):
    out={'schema':VERSION,'rows':len(rows),'groups':[],'prereg_gates':{},'notes':[
        'CPU PyTorch synthetic learner, not a pretrained model or real storyworld evaluation',
        'random parity observers are output-rank/label-budget matched, not compute matched',
        'true auxiliary fragments are privileged training annotations; composed head is a scaffold upper bound']}
    for cohort in COHORTS:
        for k in RANKS:
            for n in TRAIN:
                for arm in ARMS:
                    data=[r for r in rows if r['cohort']==cohort and r['goal_rank']==k and r['train_n']==n and r['arm']==arm]
                    if not data:continue
                    out['groups'].append({'cohort':cohort,'goal_rank':k,'train_n':n,'arm':arm,
                        'seeds':len(data),'mean_direct_joint_accuracy':str(Q(sum(r['direct_test_joint_correct'] for r in data),N_TEST*len(data))),
                        'mean_direct_true_utility':str(sum((Q(r['direct_true_utility']) for r in data),Q(0))/len(data)),
                        'false_accepts':sum(r['direct_false_accept'] for r in data),
                        'mean_composed_joint_accuracy':None if any(r['composed_test_joint_correct'] is None for r in data) else str(Q(sum(r['composed_test_joint_correct'] for r in data),N_TEST*len(data))),
                        'mean_training_seconds':round(sum(r['training_seconds'] for r in data)/len(data),4)})
    def per(seed,cohort,k,n,arm):
        return next((r for r in rows if (r['seed'],r['cohort'],r['goal_rank'],r['train_n'],r['arm'])==(seed,cohort,k,n,arm)),None)
    pairs={}
    for seed in SEEDS:
        true=per(seed,'core_140',1,2048,'loop_true_fragment_aux')
        task=per(seed,'core_140',1,2048,'loop_task')
        flat=per(seed,'core_140',1,2048,'flat_task')
        pads={arm:per(seed,'padded_512',1,2048,arm) for arm in ARMS}
        cores={arm:per(seed,'core_140',1,2048,arm) for arm in ARMS}
        if all([true,task,flat,*pads.values(),*cores.values()]):
            pairs[str(seed)]={'H1':true['composed_test_joint_correct']>task['direct_test_joint_correct'],
                              'H2':task['direct_test_joint_correct']>flat['direct_test_joint_correct'],
                              'H3_by_arm':{arm:abs(cores[arm]['direct_test_joint_correct']-pads[arm]['direct_test_joint_correct'])/256<.05 for arm in ARMS}}
    out['pair_directions']=pairs
    out['prereg_gates']={h:{'success_count':sum(x[h] for x in pairs.values()),'total':len(pairs),'passed':len(pairs)==len(SEEDS) and sum(x[h] for x in pairs.values())>=4} for h in ('H1','H2')}
    out['prereg_gates']['H3']={'by_arm':{arm:{'success_count':sum(x['H3_by_arm'][arm] for x in pairs.values()),'total':len(pairs),'passed':len(pairs)==len(SEEDS) and sum(x['H3_by_arm'][arm] for x in pairs.values())>=4} for arm in ARMS}}
    out['prereg_gates']['H3']['passed']=all(z['passed'] for z in out['prereg_gates']['H3']['by_arm'].values())
    f2=all(r['f2_rank']==r['dimension'] and r['f2_test_determined']==N_TEST and r['f2_test_correct_if_determined']==N_TEST for r in rows if r['train_n']==2048)
    out['prereg_gates']['H4']={'passed':f2}
    return out


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--smoke',action='store_true')
    args=parser.parse_args()
    out=args.out;out.mkdir(parents=True,exist_ok=True)
    cfg=json.loads((Path(__file__).resolve().parents[2]/'Hypergames/single_player/hg07_registration_v1.json').read_text())
    if cfg['schema']!=VERSION or cfg['training_steps']!=STEPS or cfg['training_sizes']!=list(TRAIN):raise ValueError('registration changed')
    started=time.time()
    rows=run(seeds=(2026111701,) if args.smoke else SEEDS,
             cohorts=('core_140',) if args.smoke else COHORTS,
             ranks=(1,) if args.smoke else RANKS,train_sizes=(512,) if args.smoke else TRAIN)
    summary=summarize(rows)
    summary['runtime']={'torch':torch.__version__,'numpy':np.__version__,'python':platform.python_version(),
                        'cpu':platform.processor(),'requested_threads':2,'seconds':round(time.time()-started,3)}
    summary['sources_sha256']={p:hashlib.sha256((Path(__file__).resolve().parents[2]/p).read_bytes()).hexdigest()
           for p in ['src/spiral_ln/evaluation_hypergames_raw.py','src/spiral_ln/hypergames_raw_recurrent.py','Hypergames/single_player/hg07_registration_v1.json']}
    dest=out/('hg07_smoke_seed_rows.csv' if args.smoke else 'hg07_public_seed_rows.csv')
    with dest.open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
    summary['seed_csv_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest()
    (out/('hg07_smoke_summary.json' if args.smoke else 'hg07_summary.json')).write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print('HG07',len(rows),'rows','runtime',round(time.time()-started,2),'scientific gates',summary['prereg_gates'])

if __name__=='__main__':main()
