import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {engineClass} from './balance.mjs';
import {roster,verifyScreen} from './robust_authoring.mjs';
import * as N from './nash_witness_learning.mjs';
const raw=readFileSync(new URL('../../../storyworld_reader.html',import.meta.url));
assert.equal(createHash('sha1').update('blob '+raw.length+'\0').update(raw).digest('hex'),'d43d9ab729206f1594ea7cee98918bc9ec92f267');
const Engine=engineClass(raw.toString('utf8')),read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8')),write=process.argv.includes('--write');
const base='./nash_witness_receipts/';
function record(name,v){
 const url=new URL(base+name+'.json',import.meta.url);
 if(write){mkdirSync(new URL(base,import.meta.url),{recursive:true});writeFileSync(url,JSON.stringify(v)+'\n')}
 else assert.deepEqual(v,JSON.parse(readFileSync(url,'utf8')));
}
const training=roster.map(spec=>{const r=read('./recurrent_receipts/'+spec.id+'.json');for(const e of r.receipt.games)verifyScreen(e.game,r.receipt.target,e.screen);return {spec,examples:N.convert(r.receipt,r.samples)}});
for(const t of training)record(t.spec.id,t);
const folds=['chain','fork','veto'].map(f=>N.fold(training,f));
for(const f of folds)record('fold_'+f.family,f);
const tests=N.fresh.map(spec=>N.test(Engine,spec,folds.find(f=>f.family===spec.family)));
for(const t of tests)record(t.spec.id,t);
const report={unit:N.unit(),...N.summarize(training,folds,tests)};
record('summary',report);console.log(JSON.stringify(report,null,2));
