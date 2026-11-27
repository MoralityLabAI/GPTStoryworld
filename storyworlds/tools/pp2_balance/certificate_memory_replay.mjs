import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {engineClass} from './balance.mjs';
import * as M from './certificate_memory.mjs';
const raw=readFileSync(new URL('../../../storyworld_reader.html',import.meta.url));
assert.equal(createHash('sha1').update('blob '+raw.length+'\0').update(raw).digest('hex'),'d43d9ab729206f1594ea7cee98918bc9ec92f267');
const Engine=engineClass(raw.toString('utf8')),read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8')),write=process.argv.includes('--write');
const base='./certificate_memory_receipts/';
// Native Array.sort comparator counts depend on the JS engine's sorting implementation.
// Compare all other receipt fields exactly, and report original and replayed counts.
function compareReceipt(id,actual,expected){
 const a=JSON.parse(JSON.stringify(actual)),e=JSON.parse(JSON.stringify(expected)),deltas=[];
 function count(ar,er,path){
  const x=ar.sort_comparisons,y=er.sort_comparisons;
  assert(Number.isSafeInteger(x)&&x>=0&&Number.isSafeInteger(y)&&y>=0,'invalid sort counter');
  if(x!==y)deltas.push({path,recorded:y,replayed:x});
  delete ar.sort_comparisons;delete er.sort_comparisons;
 }
 if(id==='summary'){
  for(const m of M.modes)count(a.aggregate[m].retrieval,e.aggregate[m].retrieval,'aggregate/'+m);
  for(const t of Object.keys(e.by_trajectory))for(const m of M.modes)count(a.by_trajectory[t][m].retrieval,e.by_trajectory[t][m].retrieval,t+'/'+m);
 }else if(M.fresh.some(s=>s.id===id)){
  for(let i=0;i<e.trajectories.length;i++)for(const m of M.modes)count(a.trajectories[i].stats[m].retrieval,e.trajectories[i].stats[m].retrieval,i+'/'+m);
 }
 assert.deepEqual(a,e);
 if(deltas.length)console.log(JSON.stringify({receipt:id,runtime_sort_comparison_deltas:deltas}));
}
function record(id,v){const url=new URL(base+id+'.json',import.meta.url);if(write){mkdirSync(new URL(base,import.meta.url),{recursive:true});writeFileSync(url,JSON.stringify(v)+'\n')}else compareReceipt(id,v,read(base+id+'.json'))}
const training=M.trainIds.map(id=>{const r=M.collect(read('./nash_witness_receipts/'+id+'.json'));record('train_'+id,r);return r});
const folds=['chain','fork','veto'].map(f=>M.fold(training,f));
for(const f of folds)record('fold_'+f.family,f);
const tests=M.fresh.map(spec=>{const t=M.test(Engine,spec,folds.find(f=>f.family===spec.family));record(spec.id,t);return t});
const summary=M.summarize(training,folds,tests);record('summary',summary);console.log(JSON.stringify(summary,null,2));
