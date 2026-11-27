import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import * as S from './strategic.mjs';
import * as H from './strategic_robustness.mjs';
const robustPilot=function robustPilot(S,H,previous){
 const ok=(x,m)=>{if(!x)throw Error(m)};
 // Dominant row action forces probability of the bad ending <= epsilon.
 const dom={R:[['1'],['0']],C:[['0'],['0']],endings:[['good'],['bad']]},tar={good:'1',bad:'0'};
 const unit=H.envelope(dom,tar,[],{maxSplits:0});
 ok(unit.verified.worst_tv.lower==='1/5'&&unit.verified.worst_tv.upper==='1/5','dominance bound not exact');
 let rejected=0;
 for(const field of ['dual','witness','cover']){
  const bad=JSON.parse(JSON.stringify(unit));
  if(field==='dual'){bad.objectives[0].dual.lambda[0]='-1/1'}else if(field==='witness'){bad.objectives[0].witness.x=['0/1','1/1']}else bad.cover='x';
  try{H.verify(dom,tar,bad)}catch{rejected++}
 }
 ok(rejected===3,'tampered proof accepted');
 // Anti-coordination: both players prefer different actions. A correlated
 // relaxation can put all mass on off-diagonal outcomes, independent NE
 // must still be witnessed. Cover refinement tested on a game with a gap.
 const mp={R:[['1','0'],['0','1']],C:[['0','1'],['1','0']],endings:[['match','diff'],['diff','match']]};
 const mp0=H.envelope(mp,{match:'1/2',diff:'1/2'},[],{maxSplits:0});
 const mp1=H.envelope(mp,{match:'1/2',diff:'1/2'},[],{maxSplits:256});
 const n=s=>{const [a,b]=s.split('/').map(Number);return a/b};
 ok(n(mp1.verified.worst_tv.upper)<=n(mp0.verified.worst_tv.upper),'refinement worsened outer upper');
 const rows=[];
 for(const row of previous.rows){
  const fields=['target_on_original','same_author_loss'];
  const byKey=new Map();
  const arms={};
  for(const field of fields){
   const a=row[field];
   if(!byKey.has(a.key))byKey.set(a.key,H.envelope(a.game,row.target,[a.certificate],{maxSplits:256,depthLimit:14,dualSweeps:4,witnessSweeps:4}));
   arms[field]={key:a.key,author_loss:a.author_loss,target_aligned_tv:a.target_tv,receipt:byKey.get(a.key)};
  }
  rows.push({seed:row.seed,target:row.target,arms});
 }
 const selected=rows.map(r=>r.arms.same_author_loss);
 const mean=(arr,fn)=>arr.reduce((a,r)=>a+fn(r),0)/arr.length;
 const summary={status:'development_only',roots:rows.length,unique_games:rows.reduce((n,r)=>n+new Set(Object.values(r.arms).map(a=>a.key)).size,0),unit:{dominance:unit.verified,tamper_rejections:rejected,matching_pennies:{root:mp0.verified,refined:mp1.verified}},means:{selected_target_tv:mean(selected,r=>n(r.target_aligned_tv)),selected_worst_tv_lower:mean(selected,r=>n(r.receipt.verified.worst_tv.lower)),selected_worst_tv_upper:mean(selected,r=>n(r.receipt.verified.worst_tv.upper)),original_worst_tv_lower:mean(rows,r=>n(r.arms.target_on_original.receipt.verified.worst_tv.lower)),original_worst_tv_upper:mean(rows,r=>n(r.arms.target_on_original.receipt.verified.worst_tv.upper))},exact_selected_worst_tv:selected.filter(r=>r.receipt.verified.worst_tv.lower===r.receipt.verified.worst_tv.upper).length,selected_splits:selected.reduce((n,r)=>n+r.receipt.verified.cover.splits,0),rows};
 return summary;
};
const read=f=>JSON.parse(readFileSync(new URL(f,import.meta.url),'utf8'));
const previous=read('./strategic_target_summary.json');
const expected=read('./strategic_robustness_summary.json');
for(const r of expected.rows){const p=previous.rows.find(v=>v.seed===r.seed);for(const [field,a] of Object.entries(r.arms))assert.deepEqual(H.verify(p[field].game,r.target,a.receipt),a.receipt.verified)}
const actual=robustPilot(S,H,previous);
assert.deepEqual(actual,expected);
console.log(JSON.stringify({...actual,rows:undefined},null,2));
