import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {engineClass} from './balance.mjs';
import * as C from './robust_authoring.mjs';
import * as G from './coordinate_gym.mjs';
import * as M from './recurrent_ranker.mjs';
import * as R from './recurrent_campaign.mjs';
const raw=readFileSync(new URL('../../../storyworld_reader.html',import.meta.url));
assert.equal(createHash('sha1').update('blob '+raw.length+'\0').update(raw).digest('hex'),'d43d9ab729206f1594ea7cee98918bc9ec92f267');
const Engine=engineClass(raw.toString('utf8')),write=process.argv.includes('--write');
const base='./recurrent_receipts/';
function record(name,value){
 const url=new URL(base+name+'.json',import.meta.url);
 if(write){mkdirSync(new URL(base,import.meta.url),{recursive:true});writeFileSync(url,JSON.stringify(value)+'\n')}
 else assert.deepEqual(value,JSON.parse(readFileSync(url,'utf8')));
}
const unit=M.gradientCheck();
const training=R.training(Engine,C);
for(const row of training)record(row.spec.id,row);
const folds=['chain','fork','veto'].map(f=>R.fitFold(training,f));
for(const f of folds)record('fold_'+f.family,f);
const tests=G.fresh.map(spec=>R.test(Engine,spec,folds.find(f=>f.family===spec.family)));
for(const t of tests)record(t.spec.id,t);
const report={status:'development_only',unit,folds:folds.map(f=>({family:f.family,training_roots:f.training_roots,examples:f.examples,exact_delta_examples:f.exact_delta_examples,parameters:f.models.T3.L.n,losses:Object.fromEntries(Object.entries(f.models).map(([k,m])=>[k,m.losses]))})),training_unique_candidates:training.reduce((n,r)=>n+r.receipt.rows.length,0),training_native_transitions:training.reduce((n,r)=>n+r.receipt.authorTransitions+r.receipt.strategicTransitions,0),...R.summarize(tests)};
record('summary',report);console.log(JSON.stringify(report,null,2));
