import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {roster} from './robust_authoring.mjs';
const guardrails=function guardrails(receipts){
 const ok=(v,m)=>{if(!v)throw Error(m)};
 const gcd=(x,y)=>{x=x<0n?-x:x;while(y)[x,y]=[y,x%y];return x},F=(x,y)=>{const g=gcd(x,y);return [x/g,y/g]};
 const q=s=>s.split('/').map(BigInt),st=x=>x.join('/'),add=(x,y)=>F(x[0]*y[1]+y[0]*x[1],x[1]*y[1]),sub=(x,y)=>add(x,[-y[0],y[1]]),mul=(x,y)=>F(x[0]*y[0],x[1]*y[1]),cmp=(x,y)=>{const z=x[0]*y[1]-y[0]*x[1];return z<0n?-1:z>0n?1:0},cs=(x,y)=>cmp(q(x),q(y)),min=xs=>xs.reduce((a,b)=>cs(a,b)<=0?a:b),num=s=>{const [a,b]=s.split('/').map(Number);return a/b};
 const p0='0/1',floor='1/8',weights=['0/1','1/2','1/1','2/1','4/1'];
 const admitted=r=>cs(r.p,floor)>=0&&cs(r.p2,floor)>=0&&r.bad===p0;
 function solve(rows,w,gate){
  const rs=(gate?rows.filter(admitted):rows).map(r=>({...r,score_lower:st(add(q(r.author_loss),mul(q(w),q(r.worst_lower)))),score_upper:st(add(q(r.author_loss),mul(q(w),q(r.worst_upper))))}));
  if(!rs.length)return {status:'no_admitted_grid_point',admitted:0};
  rs.sort((a,b)=>cs(a.score_upper,b.score_upper)||a.edits-b.edits||a.key.localeCompare(b.key));
  const r=rs[0],lo=min(rs.map(r=>r.score_lower)),gap=st(sub(q(r.score_upper),q(lo)));
  return {status:gap===p0?'exact_grid_optimum':'bounded_grid_optimum',admitted:rs.length,key:r.key,author_loss:r.author_loss,worst_lower:r.worst_lower,worst_upper:r.worst_upper,p:r.p,p2:r.p2,bad:r.bad,score_lower:lo,score_upper:r.score_upper,gap,passes_floor:admitted(r)};
 }
 const rows=receipts.map(r=>{
  ok(r.rows.length===256,'incomplete grid');
  const variants=weights.map(weight=>({weight,unconstrained:solve(r.rows,weight,false),hard_gate:solve(r.rows,weight,true)}));
  const existing=variants.find(v=>v.weight==='1/1').unconstrained;
  ok(existing.key===r.summary.robust_grid.key&&existing.score_upper===r.summary.global_j_upper,'prior minimax parity');
  return {id:r.spec.id,family:r.spec.family,seed:r.spec.seed,variants};
 });
 const summaries=weights.map(weight=>{
  const rs=rows.map(r=>r.variants.find(v=>v.weight===weight));
  const ag=key=>{const a=rs.map(r=>r[key]),valid=a.filter(r=>r.admitted>0),mean=f=>valid.length?valid.reduce((z,r)=>z+num(r[f]),0)/valid.length:null;return {roots:valid.length,exact_grid_optima:valid.filter(r=>r.gap===p0).length,passes_floor:valid.filter(r=>r.passes_floor).length,mean_author_loss:mean('author_loss'),mean_worst_lower:mean('worst_lower'),mean_worst_upper:mean('worst_upper'),mean_score_upper:mean('score_upper'),mean_grid_gap:mean('gap'),admitted_points:a.reduce((n,r)=>n+r.admitted,0)}};
  return {weight,unconstrained:ag('unconstrained'),hard_gate:ag('hard_gate')};
 });
 return {status:'posthoc_development_diagnostic',floor,weights,definition:'p and p2 read-ablation TV >=1/8 and zero uniform dead/horizon mass; same committed finite grids; no native training',summaries,rows};
};
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const report=guardrails(roster.map(r=>read('./robust_authoring_receipts/'+r.id+'.json')));
assert.deepEqual(report,read('./robust_authoring_guardrails.json'));
console.log(JSON.stringify(report.summaries,null,2));
