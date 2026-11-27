import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {engineClass,auditWorld} from './balance.mjs';
import {pilot} from './pilot.mjs';
const load=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const reader=readFileSync(new URL('../../../storyworld_reader.html',import.meta.url));
const reader_blob=createHash('sha1').update('blob '+reader.length+'\0').update(reader).digest('hex');
const r=pilot(engineClass(reader.toString('utf8'))),summary={...r,reader_blob};delete summary.rows;
assert.deepEqual(summary,load('./summary.json'));
for(const mode of ['greedy','restart','frontier']){
 const rows=r.rows.filter(x=>x.mode===mode);
 for(let i=0;i<rows.length;i+=8)assert.deepEqual({mode,rows:rows.slice(i,i+8)},load('./receipts/'+mode+'_'+(i/8)+'.json'));
}
const audit=load('./corpus_audit.json');
assert.equal(audit.reader_blob,reader_blob);
for(const w of audit.worlds){
 const bytes=readFileSync(new URL('../../../'+w.path,import.meta.url));
 const sha=createHash('sha1').update('blob '+bytes.length+'\0').update(bytes).digest('hex');
 assert.equal(sha,w.blob);
 assert.deepEqual({path:w.path,blob:w.blob,...auditWorld(JSON.parse(bytes.toString('utf8')))},w);
}
console.log(JSON.stringify({status:'PASS',roots:r.roots,arms:3,candidate_evaluations:r.rows.reduce((s,x)=>s+x.evaluations,0),reader_transitions:r.rows.reduce((s,x)=>s+x.transitions,0),corpus_worlds:audit.worlds.length,reader_blob}));
