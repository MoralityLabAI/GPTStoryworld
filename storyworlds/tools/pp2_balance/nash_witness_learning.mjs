import * as G from './coordinate_gym.mjs';
import * as S from './strategic.mjs';
const api=(function factory(G,S){
 const ok=(v,m)=>{if(!v)throw Error(m)},Z=[0n,1n],O=[1n,1n],E=[1n,5n];
 const gcd=(a,b)=>{a=a<0n?-a:a;while(b)[a,b]=[b,a%b];return a};
 function F(a,b=1n){ok(b!==0n,'zero denominator');if(b<0n){a=-a;b=-b}const g=gcd(a,b);return[a/g,b/g]}
 const Q=s=>{ok(typeof s==='string'&&/^-?\d+(\/[1-9]\d*)?$/.test(s),'rational');const [a,b='1']=s.split('/');return F(BigInt(a),BigInt(b))};
 const st=x=>x.join('/'),a=(x,y)=>F(x[0]*y[1]+y[0]*x[1],x[1]*y[1]),b=(x,y)=>a(x,[-y[0],y[1]]),m=(x,y)=>F(x[0]*y[0],x[1]*y[1]),c=(x,y)=>{const d=x[0]*y[1]-y[0]*x[1];return d<0n?-1:d>0n?1:0},sum=x=>x.reduce(a,Z),max=x=>x.reduce((u,v)=>c(u,v)>=0?u:v),min=x=>x.reduce((u,v)=>c(u,v)<=0?u:v),num=x=>Number(x[0])/Number(x[1]),dot=(x,y)=>sum(x.map((v,i)=>m(v,y[i]))),clamp=(x,lo=0,hi=1)=>Math.max(lo,Math.min(hi,x));
 const ends=['coalition','defection','hold'],budgets=[8,16,32,64],modes=['frontier','parent','direction','scalar','geometry_scalar','factored','factored_sham','random_global'];
 const fresh=[
  {id:'geo_chain_1',family:'chain',seed:3510191,target:2,utility:0},
  {id:'geo_chain_2',family:'chain',seed:3518110,target:0,utility:1},
  {id:'geo_fork_1',family:'fork',seed:3526029,target:1,utility:1},
  {id:'geo_fork_2',family:'fork',seed:3533948,target:2,utility:0},
  {id:'geo_veto_1',family:'veto',seed:3541867,target:0,utility:0},
  {id:'geo_veto_2',family:'veto',seed:3549786,target:1,utility:1}
 ];
 const masks=[1,2,3,4,5,6],pure=(n,i)=>Array.from({length:n},(_,j)=>i===j?'1/1':'0/1');
 const mean=xs=>xs.length?xs.reduce((s,x)=>s+x,0)/xs.length:0;
 function gaps(game,p){
  const R=game.R.map(r=>r.map(Q)),C=game.C.map(r=>r.map(Q)),x=p.x.map(Q),y=p.y.map(Q);
  const ra=R.map(row=>dot(row,y)),ca=Array.from({length:y.length},(_,j)=>dot(x,C.map(row=>row[j])));
  const ur=dot(x,ra),uc=dot(y,ca);
  const row=ra.map(v=>b(b(v,ur),E)),col=ca.map(v=>b(b(v,uc),E));
  const cert=S.certify(game.R,game.C,p.x,p.y);
  ok(c(a(max([...row,...col]),E),Q(cert.max_regret))===0,'gap parity');
  return {row,col,cert};
 }
 function screenWitnesses(entry){
  const {screen}=entry;
  if(screen.kind==='exact_trivial')return [screen.witness];
  if(screen.kind==='unresolved_no_witness')return [];
  return screen.receipt.objectives.map(o=>o.witness);
 }
 const cache=new WeakMap();
 function prepare(entry,target){
  const k=JSON.stringify(target);if(cache.has(entry)){const x=cache.get(entry);ok(x.target===k,'changed target for cached game');return x}
  const {game,screen}=entry,ws=new Map();
  for(const p of screenWitnesses(entry)){
   const cert=S.certify(game.R,game.C,p.x,p.y);ok(cert.certified,'source witness rejected');
   const tv=S.targetTV(S.endingLaw(game,cert),target),id=cert.x.join(',')+'|'+cert.y.join(',');
   ws.set(id,{cert,tv});
  }
  const witnesses=[...ws.values()].sort((u,v)=>c(Q(v.tv),Q(u.tv)));
  if(witnesses.length)ok(witnesses[0].tv===screen.lower,'screen lower lacks matching witness');
  const worst=witnesses[0]||null,gs=worst?gaps(game,worst.cert):null;
  const pureCounts=[0,0,0],pureGaps=[];
  for(let i=0;i<game.R.length;i++)for(let j=0;j<game.R[0].length;j++){
   const cert=S.certify(game.R,game.C,pure(game.R.length,i),pure(game.R[0].length,j));
   pureGaps.push(G.num(cert.max_regret));
   if(cert.certified)pureCounts[ends.indexOf(game.endings[i][j])]++;
  }
  const n=game.endings.flat().length;
  const uniform=S.certify(game.R,game.C,Array(game.R.length).fill('1/'+game.R.length),Array(game.R[0].length).fill('1/'+game.R[0].length));
  const duals=screen.receipt?.objectives??[];
  const gapFeatures=vs=>[num(max(vs)),num(min(vs)),mean(vs.map(num)),vs.filter(v=>c(v,Z)===0).length/vs.length,vs.filter(v=>c(v,F(-1n,20n))>=0).length/vs.length];
  const features=[
   Number(Boolean(worst)),...pureCounts.map(v=>v/n),mean(pureGaps),Math.min(...pureGaps),Math.max(...pureGaps),
   G.num(uniform.row_regret),G.num(uniform.column_regret),
   ...(gs?[...gapFeatures(gs.row),...gapFeatures(gs.col)]:Array(10).fill(0)),
   ...(worst?ends.map(e=>G.num(S.endingLaw(game,worst.cert)[e]??'0')):[0,0,0]),
   ...(worst?[worst.cert.x.filter(v=>G.num(v)>0).length/game.R.length,worst.cert.y.filter(v=>G.num(v)>0).length/game.R[0].length]:[0,0]),
   mean(duals.map(d=>clamp(d.dual.lambda.reduce((s,v)=>s+G.num(v),0)/4))),
   G.num(screen.upper)-G.num(screen.lower)
  ];
  ok(features.every(Number.isFinite),'geometry features');
  const x={target:k,witnesses,worst,gs,features};cache.set(entry,x);return x;
 }
 // Every parent multiplier vector is nonnegative. Recalculate its upper
 // envelope on the edited cells instead of assuming the old bound survives.
 function transportUpper(source,edited,target){
  const game=edited.game,R=game.R.map(r=>r.map(Q)),C=game.C.map(r=>r.map(Q)),n=R.length,p=R[0].length;
  const parent=source.screen.receipt?.objectives??[];
  const bounds=masks.map(mask=>{
   const prev=parent.find(o=>o.mask===mask);
   const lambda=prev?prev.dual.lambda.map(Q):Array(n+p).fill(Z);
   ok(lambda.length===n+p&&lambda.every(x=>c(x,Z)>=0),'bad multiplier');
   const values=[];
   for(let i=0;i<n;i++)for(let j=0;j<p;j++){
    const gap=[...R.map(r=>b(b(r[j],R[i][j]),E)),...C[i].map(v=>b(b(v,C[i][j]),E))];
    values.push(b(mask&(1<<ends.indexOf(game.endings[i][j]))?O:Z,dot(lambda,gap)));
   }
   const qt=sum(ends.flatMap((e,i)=>mask&(1<<i)?[Q(target[e]??'0')]:[]));
   return b(min([O,max(values)]),qt);
  });
  return st(max([Z,...bounds]));
 }
 function counterfactual(source,edited,target){
  const before=prepare(source,target),u=source.game,v=edited.game;
  ok(JSON.stringify(u.row_policies)===JSON.stringify(v.row_policies)&&JSON.stringify(u.column_policies)===JSON.stringify(v.column_policies),'policy roster changed');
  const changed=u.endings.flat().filter((e,i)=>e!==v.endings.flat()[i]).length;
  const gameChanged=JSON.stringify(u)!==JSON.stringify(v);
  const payoffChanged=u.R.flat().some((r,i)=>r!==v.R.flat()[i])||u.C.flat().some((r,i)=>r!==v.C.flat()[i]);
  let lower=Z,survived=0,bind=0,newBind=0,broken=0,oldWorstSurvives=null,oldWorstTargetTv=null,oldWorstRegret=null,maxGapChange=null;
  for(let k=0;k<before.witnesses.length;k++){
   const p=before.witnesses[k],ng=gaps(v,p.cert),tv=S.targetTV(S.endingLaw(v,ng.cert),target);
   if(ng.cert.certified){survived++;lower=max([lower,Q(tv)])}
   if(k===0){
    const g0=[...before.gs.row,...before.gs.col],g1=[...ng.row,...ng.col];
    bind=g0.filter(z=>c(z,Z)===0).length;
    newBind=g1.filter((z,i)=>c(z,Z)===0&&c(g0[i],Z)!==0).length;
    broken=g1.filter((z,i)=>c(z,Z)>0&&c(g0[i],Z)<=0).length;
    maxGapChange=st(max(g1.map((z,i)=>b(z,g0[i]))));
    oldWorstSurvives=ng.cert.certified;oldWorstTargetTv=tv;oldWorstRegret=ng.cert.max_regret;
   }
  }
  const upper=transportUpper(source,edited,target),l=st(lower);
  ok(c(lower,Q(upper))<=0&&c(lower,Q(edited.screen.upper))<=0&&c(Q(upper),Q(edited.screen.lower))>=0,'transport proof inconsistent');
  if(!gameChanged)ok(survived===before.witnesses.length&&(!before.worst||oldWorstTargetTv===before.worst.tv),'unchanged game witness mismatch');
  return {game_changed:gameChanged,payoff_changed:payoffChanged,changed_ending_cells:changed,witnesses:before.witnesses.length,survived,binding_before:bind,new_binding:newBind,violated_after:broken,old_worst_survives:oldWorstSurvives,old_worst_target_tv:oldWorstTargetTv,old_worst_regret:oldWorstRegret,max_gap_change:maxGapChange,transport_lower:l,transport_upper:upper};
 }
 function example(ctx,target,p,t,source,edited,e,root){
  const cf=counterfactual(source,edited,target),exact=p.worst_lower===p.worst_upper&&t.worst_lower===t.worst_upper;
  const dl=st(b(Q(t.author_loss),Q(p.author_loss))),dw=exact?st(b(Q(t.worst_lower),Q(p.worst_lower))):null;
  if(!cf.game_changed&&exact)ok(dw==='0/1','identical game, unequal exact W');
  const dj=dw===null?null:st(a(Q(dl),Q(dw)));
  return {root,source:p.key,target:t.key,block:G.block(ctx,e),x:G.features(ctx,p,e),geometry:prepare(source,target).features,cf,delta_author:dl,delta_worst:dw,delta_joint:dj,gate:G.gate(t)?1:0,labels:[G.gate(t)?1:0,dj===null?null:G.num(dj),G.num(dl),cf.game_changed?1:0,cf.game_changed&&dw!==null?G.num(dw):null,G.num(cf.transport_lower),cf.old_worst_survives===null?null:Number(cf.old_worst_survives)]};
 }
 function convert(receipt,samples){
  const map=new Map(receipt.rows.map(r=>[r.key,r]));
  return samples.map(r=>{
   const p=map.get(r.source),t=map.get(r.target);ok(p&&t,'missing edge endpoint');
   const e=G.neighbors(p.grid).find(e=>e.key===t.key);ok(e,'edge is not local');
   return example(receipt.context,receipt.target,p,t,receipt.games[p.game],receipt.games[t.game],e,receipt.spec.id);
  });
 }
 function audit(rows){
  return {edges:rows.length,game_changed:rows.filter(r=>r.cf.game_changed).length,payoff_changed:rows.filter(r=>r.cf.payoff_changed).length,exact_worst_delta:rows.filter(r=>r.delta_worst!==null).length,worst_changed:rows.filter(r=>r.delta_worst!==null&&r.delta_worst!=='0/1').length,author_only:rows.filter(r=>!r.cf.game_changed&&r.delta_author!=='0/1').length,old_worst_invalidated:rows.filter(r=>r.cf.old_worst_survives===false).length,invalidated_without_certified_improvement:rows.filter(r=>r.cf.old_worst_survives===false&&(r.delta_worst===null||G.cmp(r.delta_worst,'0/1')>=0)).length,new_binding_edges:rows.filter(r=>r.cf.new_binding>0).length,transport_exact:rows.filter(r=>r.cf.transport_lower===r.cf.transport_upper).length};
 }
 function ridge(rows,features,head,reg=4){
  const dim=features(rows[0]).length,A=Array.from({length:dim},(_,i)=>Array.from({length:dim+1},(_,j)=>i===j?reg:0));let count=0;
  for(const r of rows){const y=r.labels[head];if(y===null)continue;const x=features(r);count++;for(let i=0;i<dim;i++){for(let j=0;j<dim;j++)A[i][j]+=x[i]*x[j];A[i][dim]+=x[i]*y}}
  for(let i=0;i<dim;i++){
   let p=i;for(let k=i+1;k<dim;k++)if(Math.abs(A[k][i])>Math.abs(A[p][i]))p=k;
   [A[i],A[p]]=[A[p],A[i]];const d=A[i][i];ok(Math.abs(d)>1e-12,'singular ridge');
   for(let j=i;j<=dim;j++)A[i][j]/=d;
   for(let k=0;k<dim;k++)if(k!==i){const v=A[k][i];for(let j=i;j<=dim;j++)A[k][j]-=v*A[i][j]}
  }
  return {w:A.map(r=>r[dim]),count};
 }
 const fBase=r=>r.x,fGeo=r=>[...r.x,...r.geometry];
 function fitModel(rows,kind,sham=false){
  const data=rows.map(r=>({...r,labels:r.labels.slice()}));
  if(sham){
   const random=G.rng(19729);
   for(const root of new Set(data.map(r=>r.root)))for(let block=0;block<8;block++){
    const rs=data.filter(r=>r.root===root&&r.block===block),ys=rs.map(r=>r.labels);
    for(let i=ys.length-1;i>0;i--){const j=random(i+1);[ys[i],ys[j]]=[ys[j],ys[i]]}
    rs.forEach((r,i)=>r.labels=ys[i]);
   }
  }
  const heads=kind==='factored'?[0,2,3,4,5,6]:[0,1],feat=kind==='scalar'?fBase:fGeo;
  return {kind,sham,blocks:Array.from({length:8},(_,block)=>{
   const rs=data.filter(r=>r.block===block);ok(rs.length,'empty direction block');
   return Object.fromEntries(heads.map(h=>[h,ridge(rs,feat,h)]));
  })};
 }
 function predict(fit,row,parentWorst){
  const x=fit.kind==='scalar'?fBase(row):fGeo(row),heads=fit.blocks[row.block],v=h=>x.reduce((s,z,i)=>s+z*heads[h].w[i],0);
  if(fit.kind!=='factored')return {gate:clamp(v(0)),delta:clamp(v(1),-2,2)};
  const gate=clamp(v(0)),deltaL=clamp(v(2),-2,2),pChange=clamp(v(3)),deltaW=clamp(v(4),-1,1),lowerProxy=clamp(v(5)),survive=clamp(v(6));
  // Predicted counterfactual lower bound is only a ranking heuristic.
  const predictedW=Math.max(clamp(parentWorst+pChange*deltaW),lowerProxy);
  return {gate,delta:deltaL+predictedW-parentWorst,deltaL,pChange,deltaW,lowerProxy,survive};
 }
 function fold(training,family){
  const rs=training.filter(t=>t.spec.family!==family),rows=rs.flatMap(t=>t.examples);
  ok(rs.length===4&&rs.every(r=>r.spec.family!==family),'family split');
  const directions=Array.from({length:8},(_,k)=>{const a=rows.filter(r=>r.block===k);return {gate:mean(a.map(r=>r.labels[0])),delta:mean(a.flatMap(r=>r.labels[1]===null?[]:[r.labels[1]]))}});
  return {family,roots:rs.map(r=>r.spec.id),audit:audit(rows),directions,models:{scalar:fitModel(rows,'scalar'),geometry_scalar:fitModel(rows,'geometry_scalar'),factored:fitModel(rows,'factored'),factored_sham:fitModel(rows,'factored',true)}};
 }
 function search(g,target,mode,fit,seed){
  const rng=G.rng(seed),seen=new Map(),history=[],snapshots={},predCache=new Map();let best=null;
  function visit(grid,parent){
   const k=G.key(grid);ok(!seen.has(k),'repeat evaluation');const row=g.evaluate(grid);seen.set(k,row);
   if(G.gate(row)&&(!best||G.rank(row,best)<0))best=row;
   history.push({key:k,parent,admitted:G.gate(row),j_lower:row.j_lower,j_upper:row.j_upper});
   if(budgets.includes(seen.size))snapshots[seen.size]={key:best?.key??null,j_lower:best?.j_lower??null,j_upper:best?.j_upper??null};
  }
  visit(g.base,null);
  while(seen.size<64){
   const known=[...seen.values()].sort(G.rank);
   if(mode==='frontier'){
    const p=known.find(r=>G.neighbors(r.grid).some(e=>!seen.has(e.key)));ok(p,'frontier');
    for(const e of G.neighbors(p.grid))if(seen.size<64&&!seen.has(e.key))visit(e.grid,p.key);continue;
   }
   if(mode==='random_global'){let grid;do{grid=g.base.map(()=>rng(4))}while(seen.has(G.key(grid)));visit(grid,null);continue}
   const by=new Map();
   for(const p of known)for(const e of G.neighbors(p.grid))if(!seen.has(e.key)){
    let score=G.num(p.j_upper)+(G.gate(p)?0:1+G.violation(p));
    if(mode!=='parent'){
     const id=p.key+'>'+e.key;let pred=predCache.get(id);
     if(!pred){
      const block=G.block(g.context,e);
      pred=mode==='direction'?fit.directions[block]:predict(fit.models[mode],{block,x:G.features(g.context,p,e),geometry:mode==='scalar'?[]:prepare(g.gameFor(p),target).features},G.num(p.worst_upper));
      predCache.set(id,pred);
     }
     score=G.num(p.j_upper)+pred.delta+1-pred.gate;
    }
    score=Math.round(score*1e9)/1e9;const z={...e,score,parent:p.key},old=by.get(e.key);
    if(!old||score<old.score||(score===old.score&&z.parent<old.parent))by.set(e.key,z);
   }
   const open=[...by.values()].sort((a,b)=>a.score-b.score||a.key.localeCompare(b.key)||a.parent.localeCompare(b.parent));ok(open.length,'proposal frontier');
   visit(open[0].grid,open[0].parent);
  }
  return {mode,history,snapshots};
 }
 function test(Engine,spec,fit){
  ok(spec.family===fit.family&&!fit.roots.includes(spec.id),'test split');const g=G.gym(Engine,spec),target=g.receipt().target,arms={};
  for(const mode of modes)arms[mode]=search(g,target,mode,fit,spec.seed^52991);
  const probes=G.sample(g,{anchors:12,perAnchor:6,seed:spec.seed^61321}),receipt=g.receipt(),examples=convert(receipt,probes);
  const known=new Map(receipt.rows.map(r=>[r.key,r])),diagnostics={};
  for(const mode of ['direction','scalar','geometry_scalar','factored','factored_sham']){
   const predictions=examples.map(r=>{const parent=known.get(r.source);return mode==='direction'?fit.directions[r.block]:predict(fit.models[mode],r,G.num(parent.worst_upper))});
   const exact=examples.flatMap((r,i)=>r.labels[1]===null?[]:[(predictions[i].delta-r.labels[1])**2]);
   const base={gate_accuracy:mean(examples.map((r,i)=>Number((predictions[i].gate>=.5)===(r.labels[0]===1)))),delta_mse:mean(exact),exact:exact.length};
   if(mode.startsWith('factored')){
    base.change_accuracy=mean(examples.map((r,i)=>Number((predictions[i].pChange>=.5)===(r.labels[3]===1))));
    base.witness_survival_accuracy=mean(examples.flatMap((r,i)=>r.labels[6]===null?[]:[Number((predictions[i].survive>=.5)===(r.labels[6]===1))]));
   }
   diagnostics[mode]=base;
  }
  const best=receipt.rows.filter(G.gate).sort(G.rank)[0]??null;
  return {spec,arms,examples,audit:audit(examples),diagnostics,reference:best?{key:best.key,j_upper:best.j_upper}:null,receipt};
 }
 function summarize(training,folds,tests){
  const pair=(x,y)=>!x.key&&!y.key?'ties':!x.key?'losses':!y.key?'wins':G.cmp(x.j_upper,y.j_lower)<0?'wins':G.cmp(x.j_lower,y.j_upper)>0?'losses':x.j_lower===x.j_upper&&y.j_lower===y.j_upper&&x.j_lower===y.j_lower?'ties':'unresolved';
  const scores=Object.fromEntries(budgets.map(n=>[n,Object.fromEntries(modes.map(mode=>{
   const rows=tests.map(t=>t.arms[mode].snapshots[n]),valid=rows.filter(r=>r.key),vs={wins:0,losses:0,ties:0,unresolved:0};
   tests.forEach(t=>vs[pair(t.arms[mode].snapshots[n],t.arms.direction.snapshots[n])]++);
   return [mode,{admitted:valid.length,roots:rows.length,mean_j_upper:valid.length?mean(valid.map(r=>G.num(r.j_upper))):null,mean_sampled_reference_gap:valid.length?mean(rows.flatMap((r,i)=>r.key?[G.num(r.j_upper)-G.num(tests[i].reference.j_upper)]:[])):null,vs_direction:vs}];
  }))]));
  const diagnostics=Object.fromEntries(Object.keys(tests[0].diagnostics).map(mode=>[mode,Object.fromEntries(Object.keys(tests[0].diagnostics[mode]).map(k=>[k,mean(tests.map(t=>t.diagnostics[mode][k]))]))]));
  return {status:'development_only',training_audit:audit(training.flatMap(t=>t.examples)),probe_audit:audit(tests.flatMap(t=>t.examples)),folds:folds.map(f=>({family:f.family,roots:f.roots,audit:f.audit})),scores,diagnostics,test_candidates:tests.reduce((n,t)=>n+t.receipt.rows.length,0),test_games:tests.reduce((n,t)=>n+t.receipt.games.length,0),test_native_transitions:tests.reduce((n,t)=>n+t.receipt.authorTransitions+t.receipt.strategicTransitions,0),roots:tests.length};
 }
 function unit(){
  const target={coalition:'1/2',defection:'1/2',hold:'0/1'};
  const make=(R,C,endings,witness)=>{const game={R,C,endings,row_policies:['a','b'],column_policies:['c']},cert=S.certify(R,C,witness,['1']);ok(cert.certified,'unit cert');const tv=S.targetTV(S.endingLaw(game,cert),target);return {game,screen:{kind:'exact_trivial',witness:cert,lower:tv,upper:tv}}};
  const p=make([['1'],['0']],[['0'],['0']],[['coalition'],['defection']],['1','0']);
  const t=make([['0'],['1']],[['0'],['0']],[['coalition'],['defection']],['0','1']);
  const x=counterfactual(p,t,target);ok(x.old_worst_survives===false&&x.violated_after===1&&x.transport_lower==='0/1'&&x.transport_upper==='1/2','transport control');
  const y=counterfactual(p,p,target);ok(y.old_worst_survives&&y.transport_lower==='1/2'&&y.transport_upper==='1/2'&&!y.game_changed,'identity control');
  return {invalidated:x,identity:y};
 }
 return {fresh,budgets,modes,convert,audit,fold,test,summarize,unit,counterfactual};
})(G,S);
export const {fresh,budgets,modes,convert,audit,fold,test,summarize,unit,counterfactual}=api;
