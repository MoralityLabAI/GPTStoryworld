import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {engineClass} from './balance.mjs';
import * as M from './certificate_memory.mjs';
const raw=readFileSync(new URL('../../../storyworld_reader.html',import.meta.url));
assert.equal(createHash('sha1').update('blob '+raw.length+'\0').update(raw).digest('hex'),'d43d9ab729206f1594ea7cee98918bc9ec92f267');
const Engine=engineClass(raw.toString('utf8')),read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8')),write=process.argv.includes('--write');
const base='./certificate_memory_receipts/';
function record(id,v){const url=new URL(base+id+'.json',import.meta.url);if(write){mkdirSync(new URL(base,import.meta.url),{recursive:true});writeFileSync(url,JSON.stringify(v)+'\n')}else assert.deepEqual(v,read(base+id+'.json'))}
const training=M.trainIds.map(id=>{const r=M.collect(read('./nash_witness_receipts/'+id+'.json'));record('train_'+id,r);return r});
const folds=['chain','fork','veto'].map(f=>M.fold(training,f));
for(const f of folds)record('fold_'+f.family,f);
const tests=M.fresh.map(spec=>{const t=M.test(Engine,spec,folds.find(f=>f.family===spec.family));record(spec.id,t);return t});
const summary=M.summarize(training,folds,tests);record('summary',summary);console.log(JSON.stringify(summary,null,2));
