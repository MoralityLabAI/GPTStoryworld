import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {engineClass} from './balance.mjs';
import {roster,runRoot,verifyScreen} from './robust_authoring.mjs';
import {fresh,experiment} from './proposal_learning.mjs';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const raw=readFileSync(new URL('../../../storyworld_reader.html',import.meta.url));
assert.equal(createHash('sha1').update('blob '+raw.length+'\0').update(raw).digest('hex'),'d43d9ab729206f1594ea7cee98918bc9ec92f267');
const Engine=engineClass(raw.toString('utf8')),write=process.argv.includes('--write');
const training=roster.map(r=>read('./robust_authoring_receipts/'+r.id+'.json'));
const testing=[];
for(const spec of fresh){
 const path='./proposal_learning_receipts/'+spec.id+'.json';
 const actual=runRoot(Engine,spec);
 if(write){mkdirSync(new URL('./proposal_learning_receipts/',import.meta.url),{recursive:true});writeFileSync(new URL(path,import.meta.url),JSON.stringify(actual)+'\n')}
 else {
  const expected=read(path);
  for(const e of expected.games){verifyScreen(e.game,expected.summary.target,e.screen);if(e.refined)verifyScreen(e.game,expected.summary.target,e.refined)}
  assert.deepEqual(actual,expected);
 }
 testing.push(actual);
}
const result=experiment(training,testing);
const path='./proposal_learning_summary.json';
if(write)writeFileSync(new URL(path,import.meta.url),JSON.stringify(result)+'\n');
else assert.deepEqual(result,read(path));
console.log(JSON.stringify({held_family:result.held_family.summary,seen_family:result.seen_family.summary},null,2));
