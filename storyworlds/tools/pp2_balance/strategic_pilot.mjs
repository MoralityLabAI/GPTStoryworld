import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import * as B from './balance.mjs';
import * as S from './strategic.mjs';
import {fixture} from './pilot.mjs';
const runPilot=function runPilot(Engine,B,S,fixture){
 const assert=(x,m)=>{if(!x)throw Error(m)};
 const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 const lopsidedR=[['1','0'],['0','1/2']],lopsidedC=[['0','1'],['1','0']];
 const exact=S.certify(lopsidedR,lopsidedC,['1/2','1/2'],['1/3','2/3']);
 assert(exact.max_regret==='0/1','lopsided exact equilibrium');
 const corner=S.certify(lopsidedR,lopsidedC,['1/2','1/2'],['0','1']);
 assert(corner.row_regret==='1/4'&&corner.column_regret==='0/1','kite corner');
 const projected=S.certify(lopsidedR,lopsidedC,['2/5','3/5'],['0','1']);
 assert(projected.max_regret==='1/5'&&projected.certified,'kite boundary');
 const solved=S.solve(lopsidedR,lopsidedC);assert(solved.certificate.max_regret==='0/1','exact support solve');
 let rejected=0;for(const bad of [[['1/2','1/3'],['0','1']], [['-1/2','3/2'],['0','1']]]){try{S.certify(lopsidedR,lopsidedC,...bad)}catch{rejected++}}assert(rejected===2,'invalid simplex accepted');
 const fail=S.solve(lopsidedR,lopsidedC,{budget:1});assert(fail.evaluations===1,'budget');
 const unit={exact_lopsided:exact,corner,projected,solver:solved.certificate,invalid_simplex_rejections:rejected,budget_one:fail.evaluations};
 const targets=[{coalition:'3/8',defection:'3/8',hold:'1/4'},{coalition:'1/4',defection:'1/4',hold:'1/2'},{coalition:'7/16',defection:'7/16',hold:'1/8'}];
 const utilitySets=[{coalition:['3/4','3/4'],defection:['1','0'],hold:['1/4','1/2']},{coalition:['1/2','1'],defection:['1','1/4'],hold:['3/4','3/4']}];
 const makeManifest=(w,utilities)=>{
  const owners={turn1:'A',turn2:'B',turn3:'A',turn4:'B'},policies={};
  for(const actor of ['A','B']){
   const es=w.encounters.filter(e=>owners[e.id]===actor);
   policies[actor]=Array.from({length:4},(_,i)=>({id:actor+'_'+i,rankings:Object.fromEntries(es.map((e,k)=>[e.id,(i>>k)&1?e.options.map(o=>o.id).reverse():e.options.map(o=>o.id)]))}));
  }
  return {actors:['A','B'],owners,policies,utilities};
 };
 const num=s=>{const [a,b]=s.split('/').map(Number);return a/b};
 const rows=[];
 for(let k=0;k<6;k++){
  const seed=701921+7919*k,w=fixture(seed),manifest=makeManifest(w,utilitySets[k%2]);
  assert(B.auditWorld(w).admitted,'native fixture rejected');
  const target=targets[k%3],r=S.rerank(Engine,B,w,B.sites(w),target,manifest,{mode:'frontier',budget:16,seed:seed^8391,solver:{budget:128,rounds:12}});
  // Independent certificate replay for every matrix, plus same-budget support-only comparison.
  let supportCert=0,kiteCert=0,kiteWins=0,supportWins=0,ties=0,supportEvaluations=0,uniformCert=0;
  for(const a of r.rows){
   assert(same(a.solver.certificate,S.certify(a.game.R,a.game.C,a.solver.certificate.x,a.solver.certificate.y)),'certificate replay');
   const b=S.solve(a.game.R,a.game.C,{mode:'support',budget:128,rounds:12});
   supportEvaluations+=b.evaluations;
   if(b.certificate.certified)supportCert++;
   if(a.uniform_policy_certificate.certified)uniformCert++;
   if(a.solver.certificate.certified)kiteCert++;
   const d=B.cmp(B.parse(a.solver.certificate.max_regret),B.parse(b.certificate.max_regret));if(d<0)kiteWins++;else if(d>0)supportWins++;else ties++;
  }
  const slim=x=>x?{key:x.key,author_loss:x.author_loss,strategic_target_tv:x.strategic_target_tv,uniform_regret:x.uniform_policy_certificate.max_regret,certified_regret:x.solver.certificate.max_regret,strategic_ending_law:x.strategic_ending_law,p_readout_tv:x.p_readout_tv,p2_readout_tv:x.p2_readout_tv}:null;
  rows.push({seed,utility_schedule:k%2,target,candidates:r.candidate_evaluations,author_transitions:r.author_transitions,strategic_transitions:r.strategic_transitions,kite_evaluations:r.strategy_evaluations,support_evaluations:supportEvaluations,uniform_certified:uniformCert,kite_certified:kiteCert,support_certified:supportCert,kite_wins:kiteWins,support_wins:supportWins,ties,author_best:slim(r.author_best),strategic_best:slim(r.strategic_best),kite_projections:r.rows.reduce((s,x)=>s+x.solver.kite_checked,0)});
 }
 const avg=(xs,key)=>xs.reduce((s,x)=>s+num(x[key]),0)/xs.length;
 const selected=rows.filter(x=>x.strategic_best);
 const report={status:'development_only',scope:'six new coefficient roots, one synthetic structural family; explicit synthetic terminal utility schedules; restricted policies',unit,roots:rows.length,candidates:rows.reduce((s,x)=>s+x.candidates,0),author_transitions:rows.reduce((s,x)=>s+x.author_transitions,0),strategic_transitions:rows.reduce((s,x)=>s+x.strategic_transitions,0),uniform_certified:rows.reduce((s,x)=>s+x.uniform_certified,0),kite_certified:rows.reduce((s,x)=>s+x.kite_certified,0),support_certified:rows.reduce((s,x)=>s+x.support_certified,0),kite_evaluations:rows.reduce((s,x)=>s+x.kite_evaluations,0),support_evaluations:rows.reduce((s,x)=>s+x.support_evaluations,0),kite_wins:rows.reduce((s,x)=>s+x.kite_wins,0),support_wins:rows.reduce((s,x)=>s+x.support_wins,0),ties:rows.reduce((s,x)=>s+x.ties,0),kite_projections:rows.reduce((s,x)=>s+x.kite_projections,0),certified_roots:selected.length,changed_incumbent:selected.filter(x=>x.author_best.key!==x.strategic_best.key).length,means:{author_best_loss:avg(rows.map(x=>x.author_best),'author_loss'),strategic_best_loss:selected.length?avg(selected.map(x=>x.strategic_best),'author_loss'):null,author_best_strategic_tv:avg(rows.map(x=>x.author_best),'strategic_target_tv'),strategic_best_tv:selected.length?avg(selected.map(x=>x.strategic_best),'strategic_target_tv'):null},rows};
 return report;
};
const reader=readFileSync(new URL('../../../storyworld_reader.html',import.meta.url));
assert.equal(createHash('sha1').update('blob '+reader.length+'\0').update(reader).digest('hex'),'d43d9ab729206f1594ea7cee98918bc9ec92f267');
const result=runPilot(B.engineClass(reader.toString('utf8')),B,S,fixture);
assert.deepEqual(result,JSON.parse(readFileSync(new URL('./strategic_summary.json',import.meta.url),'utf8')));
console.log(JSON.stringify(result,null,2));
