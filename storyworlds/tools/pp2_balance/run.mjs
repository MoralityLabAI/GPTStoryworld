import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {engineClass,auditWorld,sites,balance,patch} from './balance.mjs';
import {pilot} from './pilot.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const raw=readFileSync(path.join(root,'storyworld_reader.html'));
assert.equal(createHash('sha1').update('blob '+raw.length+'\0').update(raw).digest('hex'),'d43d9ab729206f1594ea7cee98918bc9ec92f267','reader source changed; re-audit before using');
const Engine=engineClass(raw.toString('utf8'));
if(process.argv[2]==='audit'){
 const p=process.argv[3],w=JSON.parse(readFileSync(p,'utf8'));console.log(JSON.stringify({audit:auditWorld(w),available_sites:sites(w)},null,2));
}else if(process.argv[2]==='balance'){
 const m=JSON.parse(readFileSync(process.argv[3],'utf8')),out=path.resolve(process.argv[4]);assert(!existsSync(out),'new output directory required');
 const bytes=readFileSync(m.source);assert.equal(createHash('sha256').update(bytes).digest('hex'),m.source_sha256,'source changed');const w=JSON.parse(bytes);
 assert(Array.isArray(m.approved_sites)&&m.approved_sites.length>0,'author approval required');
 const r=balance(Engine,w,m.approved_sites,m.target,m.config||{}),p=patch(w,m.approved_sites,r.best.grid);
 mkdirSync(out,{recursive:true});writeFileSync(path.join(out,'candidate.json'),JSON.stringify(p.world,null,2)+'\n');writeFileSync(path.join(out,'receipt.json'),JSON.stringify({manifest:m,result:r},null,2)+'\n');console.log(JSON.stringify({before:r.initial.metric.loss,after:r.best.metric.loss,evaluations:r.evaluations,transitions:r.transitions}));
}else{
 const r=pilot(Engine);console.log(JSON.stringify({status:r.status,unit:r.unit,roots:r.roots,summary:r.summary,paired:r.paired},null,2));
 if(process.argv[2])writeFileSync(process.argv[2],JSON.stringify(r)+'\n');
}
