import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {engineClass} from './balance.mjs';
import {roster,smoke,stream} from './proof_component_prospective.mjs';
import {run,summarize} from './proof_component_study.mjs';
const raw=readFileSync(new URL('../../../storyworld_reader.html',import.meta.url));
assert.equal(createHash('sha1').update('blob '+raw.length+'\0').update(raw).digest('hex'),'d43d9ab729206f1594ea7cee98918bc9ec92f267');
const Engine=engineClass(raw.toString('utf8'));
if(process.argv.includes('--smoke')){console.log(JSON.stringify(smoke(Engine),null,2));}
else{
 assert(process.argv.includes('--evaluate-frozen'),'explicit frozen evaluation required');
 const streams=roster.map(spec=>stream(Engine,spec));
 const results=streams.map(run),summary={...summarize(results),status:'prospective_frozen_structural_families',readerTransitions:streams.flatMap(x=>x.trajectories).reduce((n,t)=>n+t.readerTransitions,0)};
 const receipt={summary,results};
 if(process.argv.includes('--write'))writeFileSync(new URL('./proof_component_prospective_receipt.json',import.meta.url),JSON.stringify(receipt,null,2)+'\n',{flag:'wx'});
 console.log(JSON.stringify(receipt,null,2));
}
