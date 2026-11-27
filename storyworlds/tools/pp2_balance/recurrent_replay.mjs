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

// Transcendental/optimizer floats can differ between V8 builds. Keep every
// other field (in particular choices, counts, ranks and certificates) exact.
const floatPaths={
 fold:[
  /^models\.(T1|T3|T3_shuffled)\.(w|losses|strength)\.\d+$/,
  /^models\.(T1|T3|T3_shuffled)\.means\.\d+\.\d+$/,
 ],
 root:[/^diagnostics\.(clean\.delta_mse|interventions\.\d+\.(delta_mse|mean_output_shift))$/],
 summary:[
  /^folds\.\d+\.losses\.(T1|T3|T3_shuffled)\.\d+$/,
  /^diagnostics\.(clean\.mean_delta_mse|interventions\.\d+\.(mean_delta_mse|mean_output_shift))$/,
 ],
};
const FLOAT_ABS_TOL=1e-12;
function compareReceipt(actual,expected,kind,label,path=''){
 const at=path?label+'.'+path:label;
 if(typeof actual==='number'&&typeof expected==='number'&&floatPaths[kind].some(r=>r.test(path))){
  assert.ok(Number.isFinite(actual)&&Number.isFinite(expected)&&Math.abs(actual-expected)<=FLOAT_ABS_TOL,
   at+': numeric drift beyond '+FLOAT_ABS_TOL+' ('+actual+' vs '+expected+')');
  return;
 }
 if(actual!==null&&expected!==null&&typeof actual==='object'&&typeof expected==='object'){
  assert.equal(Array.isArray(actual),Array.isArray(expected),at);
  if(Array.isArray(actual))assert.equal(actual.length,expected.length,at);
  const keys=Object.keys(expected).sort();
  assert.deepEqual(Object.keys(actual).sort(),keys,at);
  for(const k of keys)compareReceipt(actual[k],expected[k],kind,label,path?path+'.'+k:k);
  return;
 }
 assert.deepEqual(actual,expected,at);
}
function checkComparator(){
 const fixture={models:{T3:{w:[0.125],column:4}},reference:{key:'a',j_upper:'1/3'}};
 const verify=value=>compareReceipt(value,fixture,'fold','comparator fixture');
 let candidate=structuredClone(fixture);
 candidate.models.T3.w[0]+=Number.EPSILON;
 verify(candidate);
 candidate.models.T3.w[0]+=1e-8;
 assert.throws(()=>verify(candidate),/numeric drift beyond/);
 candidate=structuredClone(fixture);
 candidate.models.T3.w[0]=Infinity;
 assert.throws(()=>verify(candidate),/numeric drift beyond/);
 candidate=structuredClone(fixture);
 candidate.models.T3.column=5;
 assert.throws(()=>verify(candidate),/models.T3.column/);
 candidate=structuredClone(fixture);
 candidate.reference.j_upper='1/4';
 assert.throws(()=>verify(candidate),/reference.j_upper/);
 candidate=structuredClone(fixture);
 candidate.reference.key='b';
 assert.throws(()=>verify(candidate),/reference.key/);
 candidate=structuredClone(fixture);
 candidate.models.T3.w.push(0);
 assert.throws(()=>verify(candidate),/models.T3.w/);
}
checkComparator();
function record(name,value,kind='root'){
 const url=new URL(base+name+'.json',import.meta.url);
 if(write){mkdirSync(new URL(base,import.meta.url),{recursive:true});writeFileSync(url,JSON.stringify(value)+'\n')}
 else compareReceipt(value,JSON.parse(readFileSync(url,'utf8')),kind,name);
}
const unit=M.gradientCheck();
const training=R.training(Engine,C);
for(const row of training)record(row.spec.id,row);
const folds=['chain','fork','veto'].map(f=>R.fitFold(training,f));
for(const f of folds)record('fold_'+f.family,f,'fold');
const tests=G.fresh.map(spec=>R.test(Engine,spec,folds.find(f=>f.family===spec.family)));
for(const t of tests)record(t.spec.id,t);
const report={status:'development_only',unit,folds:folds.map(f=>({family:f.family,training_roots:f.training_roots,examples:f.examples,exact_delta_examples:f.exact_delta_examples,parameters:f.models.T3.L.n,losses:Object.fromEntries(Object.entries(f.models).map(([k,m])=>[k,m.losses]))})),training_unique_candidates:training.reduce((n,r)=>n+r.receipt.rows.length,0),training_native_transitions:training.reduce((n,r)=>n+r.receipt.authorTransitions+r.receipt.strategicTransitions,0),...R.summarize(tests)};
record('summary',report,'summary');console.log(JSON.stringify(report,null,2));
