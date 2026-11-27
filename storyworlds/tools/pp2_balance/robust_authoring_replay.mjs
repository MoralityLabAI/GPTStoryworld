import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {engineClass} from './balance.mjs';
import {roster,runRoot,verifyScreen} from './robust_authoring.mjs';
const raw=readFileSync(new URL('../../../storyworld_reader.html',import.meta.url));
assert.equal(createHash('sha1').update('blob '+raw.length+'\0').update(raw).digest('hex'),'d43d9ab729206f1594ea7cee98918bc9ec92f267');
const Engine=engineClass(raw.toString('utf8'));
const write=process.argv.includes('--write'),filter=process.argv.find(x=>roster.some(r=>r.id===x));
const rows=[];
for(const spec of roster.filter(r=>!filter||r.id===filter)){
 const path=new URL('./robust_authoring_receipts/'+spec.id+'.json',import.meta.url);
 const result=runRoot(Engine,spec);
 if(write){mkdirSync(new URL('./robust_authoring_receipts/',import.meta.url),{recursive:true});writeFileSync(path,JSON.stringify(result)+'\n')}
 else {
  const expected=JSON.parse(readFileSync(path,'utf8'));
  for(const e of expected.games){verifyScreen(e.game,expected.summary.target,e.screen);if(e.refined)verifyScreen(e.game,expected.summary.target,e.refined)}
  assert.deepEqual(result,expected);
 }
 rows.push(result.summary);
}
console.log(JSON.stringify(rows,null,2));
