import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {run,summarize} from './proof_component_pilot.mjs';
const roots=process.argv.includes('--all')?['mem_chain_1','mem_chain_2','mem_fork_1','mem_fork_2','mem_veto_1','mem_veto_2']:['mem_chain_1'];
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const results=roots.map(id=>run(read('./certificate_memory_receipts/'+id+'.json')));
const summary=summarize(results);
if(!process.argv.includes('--all'))assert.deepEqual(summary,read('./proof_component_pilot_summary.json'));
console.log(JSON.stringify({summary,results},null,2));
