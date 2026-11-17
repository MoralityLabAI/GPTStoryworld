"""Unscored signed-in CLI summary probe; never changes the frozen HG09 runner.

Run with PYTHONPATH=src. Each create-only journal records the exact command,
public arithmetic prompt and provider events. These are capability observations,
not benchmark trials, model-level shams, or reconstructed private reasoning.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

from spiral_ln.hg09_session import Journal, read_journal, utc

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT/'Hypergames/hg09/session_20261117'
PROMPT = ('Unscored provider-capability check. Compute 27*38 + 65*17 internally, '
          'then return only a JSON object with the integer result, '
          'in the form {"result":INTEGER}. Do not use tools.')


def probe(model):
    template_path = CAMPAIGN/'traces'/f'0000_{model}_direct.jsonl'
    template = next(r for r in read_journal(template_path) if r['type']=='response')
    command = list(template['command'])
    assert command[-2:]==['--json','-'] and command[command.index('-m')+1]==model
    command[-2:-2] = ['-c','model_reasoning_summary="auto"']
    target = CAMPAIGN/'capabilities'/f'summary_auto_{model}.jsonl'
    journal = Journal(target)
    started = utc()
    begin = time.monotonic()
    try:
        journal.write({'type':'unscored_capability_request','timestamp_utc':started,
                       'model_requested':model,'summary_requested':'auto',
                       'reasoning_effort_requested':'low','command':command,
                       'prompt':PROMPT,'model_instructions':template['model_instructions'],
                       'template_trace':template_path.name,
                       'template_trace_sha256':hashlib.sha256(template_path.read_bytes()).hexdigest(),
                       'probe_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                       'scope':'Unscored arithmetic capability check, excluded from all HG09 model scores.'})
        environment = {k:v for k,v in os.environ.items() if k not in (
            'OPENAI_API_KEY','ANTHROPIC_API_KEY','GEMINI_API_KEY','OPENROUTER_API_KEY')}
        try:
            result = subprocess.run(command,input=PROMPT,text=True,encoding='utf-8',
                                    capture_output=True,timeout=180,env=environment)
            stdout,stderr,code = result.stdout,result.stderr,result.returncode
        except subprocess.TimeoutExpired as error:
            stdout,stderr,code = error.stdout or '',error.stderr or '',None
            if isinstance(stdout,bytes): stdout=stdout.decode('utf-8','replace')
            if isinstance(stderr,bytes): stderr=stderr.decode('utf-8','replace')
        events=[]
        for line in stdout.splitlines():
            try: events.append(json.loads(line))
            except ValueError: events.append({'type':'unparsed_stdout','text':line})
        items=[e['item'] for e in events if e.get('type')=='item.completed']
        reasons=[i for i in items if i.get('type')=='reasoning']
        tools=[e['item'] for e in events if e.get('item',{}).get('type') not in
               (None,'agent_message','reasoning')]
        usage=next((e.get('usage') for e in reversed(events) if e.get('type')=='turn.completed'),None)
        valid=code==0 and usage is not None and not tools
        journal.write({'type':'unscored_capability_response','timestamp_utc':utc(),
                       'model_requested':model,'exit_code':code,'valid_transport':valid,
                       'events':events,'stderr':stderr,'usage':usage,
                       'latency_s':time.monotonic()-begin,
                       'provider_exposed_reasoning':reasons,'tool_calls':tools,
                       'interpretation':'Provider-returned items only. No exposed item under this probe does not prove summaries are universally unavailable.'})
        print(json.dumps({'model':model,'valid_transport':valid,
                          'exposed_reasoning_items':len(reasons),'usage':usage}),flush=True)
    finally:
        journal.close()


if __name__=='__main__':
    for alias in ('gpt-6.1-sol','gpt-6-astra'):
        probe(alias)
