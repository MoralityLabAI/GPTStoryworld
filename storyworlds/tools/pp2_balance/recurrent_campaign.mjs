import * as G from './coordinate_gym.mjs';
import * as M from './recurrent_ranker.mjs';
const api=(function runFactory(G,M){
 const ok=(v,m)=>{if(!v)throw Error(m)},budgets=[8,16,32,64];
 const modes=['frontier','parent','direction','T1','T3','T3_shuffled','random_local','random_global'];
 const sum=(a,f)=>a.reduce((s,r,i)=>s+f(r,i),0);
 function directions(rows){
  return Array.from({length:8},(_,k)=>{
   const rs=rows.filter(r=>r.block===k),ds=rs.filter(r=>r.y[1]!==null);
   return [rs.length?sum(rs,r=>Number(r.y[0]>0))/rs.length:.5,ds.length?sum(ds,r=>r.y[1])/ds.length:0];
  });
 }
 function search(g,mode,fit,dir,seed){
  const random=G.rng(seed),seen=new Map(),history=[],snapshots={};let best=null;
  function visit(grid,parent){
   const k=G.key(grid);ok(!seen.has(k),'duplicate candidate');
   const r=g.evaluate(grid);seen.set(k,r);
   if(G.gate(r)&&(!best||G.rank(r,best)<0))best=r;
   history.push({key:k,parent,admitted:G.gate(r),j_lower:r.j_lower,j_upper:r.j_upper});
   if(budgets.includes(seen.size))snapshots[seen.size]={key:best?.key??null,j_lower:best?.j_lower??null,j_upper:best?.j_upper??null,admitted_seen:[...seen.values()].filter(G.gate).length};
  }
  visit(g.base,null);
  while(seen.size<64){
   const known=[...seen.values()].sort(G.rank);
   if(mode==='frontier'){
    const from=known.find(r=>G.neighbors(r.grid).some(e=>!seen.has(e.key)));
    ok(from,'frontier exhausted');
    for(const e of G.neighbors(from.grid))if(!seen.has(e.key)&&seen.size<64)visit(e.grid,from.key);
    continue;
   }
   if(mode==='random_global'){
    let grid;do{grid=g.base.map(()=>random(4))}while(seen.has(G.key(grid)));visit(grid,null);continue;
   }
   const by=new Map();
   for(const p of known)for(const e of G.neighbors(p.grid))if(!seen.has(e.key)){
    let score=G.num(p.j_upper)+(G.gate(p)?0:1+G.violation(p));
    if(mode==='direction'||mode.startsWith('T')){
     const pred=mode==='direction'?dir[G.block(g.context,e)]:M.predict(fit,G.features(g.context,p,e));
     score=G.num(p.j_upper)+pred[1]+1-pred[0];
    }
    // Quantization only affects search ordering, not verifier certificates.
    score=Math.round(score*1e9)/1e9;
    const z={...e,parent:p.key,score},old=by.get(e.key);
    if(!old||score<old.score||(score===old.score&&z.parent<old.parent))by.set(e.key,z);
   }
   const open=[...by.values()];ok(open.length>0,'proposal frontier exhausted');
   const p=mode==='random_local'?open[random(open.length)]:open.sort((a,b)=>a.score-b.score||a.key.localeCompare(b.key)||a.parent.localeCompare(b.parent))[0];
   visit(p.grid,p.parent);
  }
  return {mode,history,snapshots};
 }
 function training(Engine,C){
  return C.roster.map(spec=>{const gym=G.gym(Engine,spec),samples=G.sample(gym,{seed:spec.seed^70183});return {spec,samples,receipt:gym.receipt()}});
 }
 function fitFold(training,family){
  const roots=training.filter(r=>r.spec.family!==family),rows=roots.flatMap(r=>r.samples);
  ok(roots.length===4&&roots.every(r=>r.spec.family!==family),'family split');
  const T1=M.train(rows,{passes:1}),T3=M.train(rows,{passes:3}),T3_shuffled=M.train(rows,{passes:3,shuffle:true});
  ok(T1.L.n===T3.L.n&&T3.L.n===T3_shuffled.L.n,'parameter count mismatch');
  return {family,training_roots:roots.map(r=>r.spec.id),examples:rows.length,exact_delta_examples:rows.filter(r=>r.y[1]!==null).length,dir:directions(rows),models:{T1,T3,T3_shuffled}};
 }
 function test(Engine,spec,fold){
  ok(spec.family===fold.family&&!fold.training_roots.includes(spec.id),'test split');
  const g=G.gym(Engine,spec),arms={};
  for(const mode of modes)arms[mode]=search(g,mode,fold.models[mode],fold.dir,spec.seed^91991);
  // Independent probe edges generated after all search trajectories; no
  // feedback to fitted models or search. Also constitute a reference sample.
  const probes=G.sample(g,{anchors:12,perAnchor:6,seed:spec.seed^18821});
  const all=g.receipt(),admitted=all.rows.filter(G.gate).sort(G.rank),best=admitted[0]||null;
  const diag=M.diagnostics(fold.models.T3,probes);
  return {spec,arms,probes,diagnostics:diag,reference:best?{key:best.key,j_lower:best.j_lower,j_upper:best.j_upper}:null,receipt:all};
 }
 function summarize(tests){
  const scores=Object.fromEntries(budgets.map(n=>[n,Object.fromEntries(modes.map(m=>{
   const rows=tests.map(t=>t.arms[m].snapshots[n]),valid=rows.filter(r=>r.key),ref=tests.map(t=>t.reference),paired=tests.map(t=>[t.arms[m].snapshots[n],t.arms.frontier.snapshots[n]]);
   const wins={wins:0,losses:0,ties:0,unresolved:0};
   for(const [a,b] of paired){
    if(Boolean(a.key)!==Boolean(b.key))wins[a.key?'wins':'losses']++;
    else if(!a.key)wins.ties++;
    else if(G.cmp(a.j_upper,b.j_lower)<0)wins.wins++;
    else if(G.cmp(a.j_lower,b.j_upper)>0)wins.losses++;
    else if(a.j_lower===a.j_upper&&b.j_lower===b.j_upper&&a.j_lower===b.j_lower)wins.ties++;
    else wins.unresolved++;
   }
   return [m,{admitted:valid.length,roots:rows.length,mean_j_upper:valid.length?sum(valid,r=>G.num(r.j_upper))/valid.length:null,mean_reference_upper_gap:valid.length?sum(rows,(r,i)=>r.key?G.num(r.j_upper)-G.num(ref[i].j_upper):0)/valid.length:null,paired_vs_frontier:wins}];
  }))]));
  const comparison=(a,b,n)=>{
   const out={wins:0,losses:0,ties:0,unresolved:0};
   for(const t of tests){const x=t.arms[a].snapshots[n],y=t.arms[b].snapshots[n];if(Boolean(x.key)!==Boolean(y.key))out[x.key?'wins':'losses']++;else if(!x.key)out.ties++;else if(G.cmp(x.j_upper,y.j_lower)<0)out.wins++;else if(G.cmp(x.j_lower,y.j_upper)>0)out.losses++;else if(x.j_lower===x.j_upper&&y.j_lower===y.j_upper&&x.j_lower===y.j_lower)out.ties++;else out.unresolved++}return out;
  };
  const mean=(a,f)=>sum(a,f)/a.length,ds=tests.map(t=>t.diagnostics);
  const interventions=[0,1,2,-1].flatMap(pass=>['mean','null'].map(kind=>({pass,kind,mean_gate_accuracy:mean(ds,d=>d.interventions.find(r=>r.pass===pass&&r.kind===kind).gate_accuracy),mean_delta_mse:mean(ds,d=>d.interventions.find(r=>r.pass===pass&&r.kind===kind).delta_mse),mean_output_shift:mean(ds,d=>d.interventions.find(r=>r.pass===pass&&r.kind===kind).mean_output_shift)})));
  return {scores,comparisons:Object.fromEntries(budgets.map(n=>[n,Object.fromEntries(['T1','direction','T3_shuffled','parent'].map(m=>[m,comparison('T3',m,n)]))])),diagnostics:{clean:{mean_gate_accuracy:mean(ds,d=>d.clean.gate_accuracy),mean_delta_mse:mean(ds,d=>d.clean.delta_mse)},interventions},test_unique_candidates:sum(tests,t=>t.receipt.rows.length),test_distinct_games:sum(tests,t=>t.receipt.games.length),test_native_transitions:sum(tests,t=>t.receipt.authorTransitions+t.receipt.strategicTransitions),roots:tests.length};
 }
 return {budgets,modes,training,fitFold,test,summarize};
})(G,M);
export const {budgets,modes,training,fitFold,test,summarize}=api;
