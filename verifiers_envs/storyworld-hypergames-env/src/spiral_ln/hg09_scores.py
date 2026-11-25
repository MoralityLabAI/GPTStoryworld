"""Summarize HG-09 model episodes; preserve failures, denominators and provider metadata."""
from __future__ import annotations
import argparse, csv, json
from collections import defaultdict
from pathlib import Path


def summarize(receipt):
    if receipt.get('schema')!='HG-09/frontier-crossmodel-v1':raise ValueError('unknown schema')
    groups=defaultdict(list)
    for r in receipt['results']:
        groups[(r['model_tag'],r['provider'],r['model'],r['task'])].append(r)
    out=[]
    for (tag,provider,model,task),rows in sorted(groups.items()):
        n=len(rows);valid=[r for r in rows if not r['errors'] and all(t.get('format_valid',False) for t in r['turns'])]
        calls=sum(len(r['turns']) for r in rows)
        toks=lambda key:sum(r['usage'].get(key,0) for r in rows)
        out.append({'model':tag,'provider':provider,'model_id':model,'task':task,'episodes':n,'valid_episodes':len(valid),'turns':calls,
                    'mean_true_utility_valid':sum(r['true_utility'] for r in valid)/len(valid) if valid else None,
                    'safe_success_or_certified_release_valid':sum(r.get('safe_success',r.get('released',False)) for r in valid),
                    'false_accepts_valid':sum(r.get('false_accept',0) for r in valid),
                    'episodes_with_errors':sum(bool(r['errors']) for r in rows),
                    'reasoning_artifacts':sum(bool(t['provider_output']['reasoning_summary']) for r in rows for t in r['turns']),
                    'input_tokens':toks('input_tokens'),'output_tokens':toks('output_tokens')})
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('receipt',type=Path);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();report=summarize(json.loads(args.receipt.read_text('utf8')))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(report[0]) if report else ['model','episodes']);w.writeheader();w.writerows(report)
    print('model groups:',len(report))
if __name__=='__main__':main()
