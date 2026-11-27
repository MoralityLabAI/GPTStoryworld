import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {run,summarize} from './proof_component_study.mjs';
const ids=["mem_chain_1","mem_chain_2","mem_fork_1","mem_fork_2","mem_veto_1","mem_veto_2"];
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const results=ids.map(id=>run(read('./certificate_memory_receipts/'+id+'.json')));
const summary=summarize(results);
assert.deepEqual({summary,results},read('./proof_component_study_receipt.json'));
console.log(JSON.stringify(summary,null,2));
