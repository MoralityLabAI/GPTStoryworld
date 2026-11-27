import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import * as B from './balance.mjs';
import * as S from './strategic.mjs';
import * as T from './strategic_target.mjs';
import {fixture} from './pilot.mjs';
const targetPilot=function targetPilot(Engine,B,S,T,fixture){
 const assert=(x,m)=>{if(!x)throw Error(m)};
 const targets=[{coalition:'3/8',defection:'3/8',hold:'1/4'},{coalition:'1/4',defection:'1/4',hold:'1/2'},{coalition:'7/16',defection:'7/16',hold:'1/8'}];
 const utilities=[{coalition:['3/4','3/4'],defection:['1','0'],hold:['1/4','1/2']},{coalition:['1/2','1'],defection:['1','1/4'],hold:['3/4','3/4']}];
 // Exact line-search test: all payoffs zero; a 1/3 target lies strictly
 // between the pure and uniform profile candidates.
 const simple={R:[['0'],['0']],C:[['0'],['0']],endings:[['a'],['b']]};
 const base=S.solve(simple.R,simple.C,{mode:'support'});
 const control=T.selectTarget(simple,base,{a:'1/3',b:'2/3'},{maxLines:0});
 const line=T.selectTarget(simple,base,{a:'1/3',b:'2/3'},{maxLines:8});
 assert(control.selected.target_tv==='1/6'&&line.selected.target_tv==='0/1','exact target crossing');
 const rows=[];
 for(let k=0;k<6;k++){
  const seed=701921+7919*k,w=fixture(seed),owners={turn1:'A',turn2:'B',turn3:'A',turn4:'B'},policies={};
  for(const actor of ['A','B']){
   const es=w.encounters.filter(e=>owners[e.id]===actor);
   policies[actor]=Array.from({length:4},(_,i)=>({id:actor+'_'+i,rankings:Object.fromEntries(es.map((e,j)=>[e.id,(i>>j)&1?e.options.map(o=>o.id).reverse():e.options.map(o=>o.id)]))}));
  }
  const target=targets[k%3],manifest={actors:['A','B'],owners,policies,utilities:utilities[k%2]};
  const r=S.rerank(Engine,B,w,B.sites(w),target,manifest,{mode:'frontier',budget:16,seed:seed^8391,solver:{budget:128,rounds:12}});
  const candidates=r.rows.map(a=>({...a,selection:T.selectTarget(a.game,a.solver,target,{maxLines:24})}));
  const original=candidates.find(a=>a.key===r.author_best.key),same=T.choose(candidates,original,'0'),slack=T.choose(candidates,original,'1/8');
  assert(same.selected&&slack.selected,'expected certified selection');
  const less=(a,b)=>B.cmp(B.parse(a),B.parse(b))<=0;
  assert(less(same.selected.selection.selected.target_tv,original.selection.selected.target_tv),'rerank worsened target');
  assert(less(slack.selected.selection.selected.target_tv,same.selected.selection.selected.target_tv),'slack worsened target');
  const slim=a=>({key:a.key,author_loss:a.author_loss,target_tv:a.selection.selected.target_tv,certificate:a.selection.selected.certificate,ending_law:a.selection.selected.ending_law,seed_target_tv:a.selection.seed_best.target_tv,p_readout_tv:a.p_readout_tv,p2_readout_tv:a.p2_readout_tv,game:{R:a.game.R,C:a.game.C,endings:a.game.endings,row_policies:a.game.row_policies,column_policies:a.game.column_policies}});
  rows.push({seed,target,utility_schedule:k%2,candidates:candidates.length,original:{key:original.key,author_loss:original.author_loss,target_tv:original.strategic_target_tv,certificate:original.solver.certificate,ending_law:original.strategic_ending_law},target_on_original:slim(original),same_author_loss:slim(same.selected),slack_1_8:slim(slack.selected),same_eligible:same.eligible,slack_eligible:slack.eligible,lines:candidates.reduce((n,x)=>n+x.selection.lines,0),improved_lines:candidates.reduce((n,x)=>n+x.selection.improvedLines,0),checked:candidates.reduce((n,x)=>n+x.selection.checked,0),seed_checked:candidates.reduce((n,x)=>n+x.selection.seedChecked,0)});
 }
 const num=s=>{const [a,b]=s.split('/').map(Number);return a/b},mean=(key,field)=>rows.reduce((n,r)=>n+num(r[key][field]),0)/rows.length;
 return {status:'development_only',scope:'same six development roots as PP2-BAL-02; exact line and seed selection, no new structural holdout',unit:{seed_target_tv:control.selected.target_tv,line_target_tv:line.selected.target_tv,certificate:line.selected.certificate},roots:rows.length,candidates:rows.reduce((n,r)=>n+r.candidates,0),lines:rows.reduce((n,r)=>n+r.lines,0),improved_lines:rows.reduce((n,r)=>n+r.improved_lines,0),checked:rows.reduce((n,r)=>n+r.checked,0),seed_checked:rows.reduce((n,r)=>n+r.seed_checked,0),means:Object.fromEntries(['original','target_on_original','same_author_loss','slack_1_8'].map(k=>[k,{target_tv:mean(k,'target_tv'),author_loss:mean(k,'author_loss')} ])),zero_target_same:rows.filter(r=>r.same_author_loss.target_tv==='0/1').length,changed_world_same:rows.filter(r=>r.same_author_loss.key!==r.original.key).length,rows};
};
const reader=readFileSync(new URL('../../../storyworld_reader.html',import.meta.url));
assert.equal(createHash('sha1').update('blob '+reader.length+'\0').update(reader).digest('hex'),'d43d9ab729206f1594ea7cee98918bc9ec92f267');
const r=targetPilot(B.engineClass(reader.toString('utf8')),B,S,T,fixture);
assert.deepEqual(r,JSON.parse(readFileSync(new URL('./strategic_target_summary.json',import.meta.url),'utf8')));
console.log(JSON.stringify({...r,rows:undefined},null,2));
