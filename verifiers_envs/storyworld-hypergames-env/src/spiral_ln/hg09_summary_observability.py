"""Separately registered summary-enabled repeats, excluded from primary scores.

Uses the frozen run_episode observation boundary, parser and grader unchanged.
The only inference configuration change is model_reasoning_summary="auto".
These public, already-observed worlds supply no new independent generator roots.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

from spiral_ln.hg09_session import CONDITIONS, INTRO, read_journal, run_episode, utc

ROOT=Path(__file__).resolve().parents[2]
CAMPAIGN=ROOT/'Hypergames/hg09/session_20261117'


class SummaryDispatch:
    def __call__(self,model,effort,prompt):
        if effort!='low': raise ValueError('Extension registered low effort only')
        template=next(r for r in read_journal(CAMPAIGN/'traces'/f'0000_{model}_direct.jsonl')
                      if r['type']=='response')
        command=list(template['command'])
        if command[-2:]!=['--json','-'] or command[command.index('-m')+1]!=model:
            raise ValueError('Unexpected frozen command template')
        command[-2:-2]=['-c','model_reasoning_summary="auto"']
        environment={k:v for k,v in os.environ.items() if k not in (
            'OPENAI_API_KEY','ANTHROPIC_API_KEY','GEMINI_API_KEY','OPENROUTER_API_KEY')}
        started=utc(); begin=time.monotonic()
        try:
            result=subprocess.run(command,input=prompt,text=True,encoding='utf-8',
                                  capture_output=True,timeout=180,env=environment)
            stdout,stderr,code=result.stdout,result.stderr,result.returncode
        except subprocess.TimeoutExpired as error:
            stdout,stderr,code=error.stdout or '',error.stderr or '',None
            if isinstance(stdout,bytes): stdout=stdout.decode('utf-8','replace')
            if isinstance(stderr,bytes): stderr=stderr.decode('utf-8','replace')
        events=[]
        for line in stdout.splitlines():
            try: events.append(json.loads(line))
            except ValueError: events.append({'type':'unparsed_stdout','text':line})
        items=[e['item'] for e in events if e.get('type')=='item.completed']
        answers=[i.get('text','') for i in items if i.get('type')=='agent_message']
        reasons=[i for i in items if i.get('type')=='reasoning']
        tools=[e['item'] for e in events if e.get('item',{}).get('type') not in
               (None,'agent_message','reasoning')]
        usage=next((e.get('usage') for e in reversed(events) if e.get('type')=='turn.completed'),None)
        return {'answer':answers[-1] if answers else '', 'events':events,'stderr':stderr,
                'exit_code':code,'valid_transport':code==0 and usage is not None and len(answers)==1 and not tools,
                'started_utc':started,'finished_utc':utc(),'latency_s':time.monotonic()-begin,
                'usage':usage,'model_requested':model,'backend_snapshot':None,
                'reasoning_effort_requested':effort,'reasoning_summary_requested':'auto',
                'max_output_tokens':None,'model_instructions':INTRO+'\n',
                'reasoning_provenance':'cli_exposed_reasoning_item' if reasons else 'unavailable',
                'provider_exposed_reasoning':reasons,'tool_calls':tools,'command':command}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true',help='Consumes ordinary signed-in allowance')
    args=parser.parse_args()
    if not args.execute: parser.error('Use offline hg09_replay to reproduce grades; inference requires --execute')
    folder=CAMPAIGN/'summary_extension'
    registration=json.loads((folder/'registration.json').read_text('utf-8'))
    for name,digest in registration['source_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Registered source changed: '+name)
    if hashlib.sha256((CAMPAIGN/'registration.json').read_bytes()).hexdigest()!=registration['primary_registration_sha256']:
        raise ValueError('Primary registration changed')
    dispatch=SummaryDispatch()
    for index,spec in enumerate(registration['episodes']):
        for model in registration['models']:
            for condition in CONDITIONS:
                path=folder/'traces'/f'{index:04d}_{model}_{condition}.jsonl'
                result=run_episode(spec,model,condition,path,dispatch,registration['effort'])
                print(json.dumps({'case':index,'model':model,'condition':condition,
                                  'status':result['status'],'utility':result.get('true_utility')}),flush=True)
                if result['status']!='complete': raise RuntimeError('Extension transport failure; preserve immutable attempt')


if __name__=='__main__': main()
