import * as S from './strategic.mjs';
import * as H from './strategic_robustness.mjs';
import * as C from './robust_authoring.mjs';
const api=(function factory(S,H,C){
 const ok=(v,m)=>{if(!v)throw Error(m)};
 const Z=[0n,1n],O=[1n,1n],E=[1n,5n];let meter=null;
 const tick=(k,n=1)=>{if(meter)meter[k]=(meter[k]||0)+n};
 function F(a,b=1n){tick('rational_normalizations');ok(b!==0n,'denominator');if(b<0n){a=-a;b=-b}let x=a<0n?-a:a,y=b;while(y)[x,y]=[y,x%y];return[a/x,b/x]}
 function Q(s){ok(typeof s==='string'&&/^-?\d+(\/[1-9]\d*)?$/.test(s),'rational');const [a,b='1']=s.split('/');return F(BigInt(a),BigInt(b))}
 const st=x=>x.join('/'),add=(x,y)=>F(x[0]*y[1]+y[0]*x[1],x[1]*y[1]),sub=(x,y)=>add(x,[-y[0],y[1]]),mul=(x,y)=>F(x[0]*y[0],x[1]*y[1]),cmp=(x,y)=>{tick('rational_comparisons');const v=x[0]*y[1]-y[0]*x[1];return v<0n?-1:v>0n?1:0},sum=x=>x.reduce(add,Z),max=x=>x.reduce((a,b)=>cmp(a,b)>=0?a:b),min=x=>x.reduce((a,b)=>cmp(a,b)<=0?a:b),dot=(x,y)=>sum(x.map((v,i)=>mul(v,y[i]))),eq=(x,y)=>cmp(Q(x),Q(y))===0;
 const modes=['cold','identity','early_pure','parent_transport','bank_transport'];
 const trajectoryNames=['parent','random_global'],bankLimit=8;
 const pure=(n,i)=>Array.from({length:n},(_,j)=>i===j?'1/1':'0/1');
 function alphabet(game,target){const ends=[...new Set([...game.endings.flat(),...Object.keys(target)])].sort();ok(ends.length>=2&&ends.length<=6,'ending alphabet');return ends}
 function trivial(game,target){return st(max([...new Set(game.endings.flat())].map(e=>sub(O,Q(target[e]??'0')))))}
 function exact(game,target,profile){
  const cert=S.certify(game.R,game.C,profile.x,profile.y);
  if(!cert.certified)return null;
  return {cert,tv:S.targetTV(S.endingLaw(game,cert),target)};
 }
 function matrixKey(game,target){return JSON.stringify([game.R,game.C,game.endings,game.row_policies,game.column_policies,Object.entries(target).sort(), '1/5'])}
 function rosterKey(game){return JSON.stringify([game.row_policies,game.column_policies])}
 function pool(game,screen,target){
  if(screen.kind==='transport_exact')return {roster:rosterKey(game),witnesses:[screen.witness],duals:screen.duals};
  if(screen.kind==='exact_trivial')return {roster:rosterKey(game),witnesses:[screen.witness],duals:[]};
  if(screen.kind==='unresolved_no_witness')return {roster:rosterKey(game),witnesses:[],duals:[]};
  const ends=alphabet(game,target);
  return {roster:rosterKey(game),witnesses:screen.receipt.objectives.map(o=>o.witness),duals:screen.receipt.objectives.map(o=>({subset:ends.filter((_,i)=>o.mask&(1<<i)),lambda:o.dual.lambda}))};
 }
 function model(game,target){
  const ends=alphabet(game,target),R=game.R.map(r=>r.map(Q)),C=game.C.map(r=>r.map(Q)),n=R.length,p=R[0].length;
  ok(n*p<=64&&R.every(r=>r.length===p)&&C.length===n&&C.every(r=>r.length===p),'matrix shape');
  const t=ends.map(e=>Q(target[e]??'0'));ok(t.every(v=>cmp(v,Z)>=0)&&cmp(sum(t),O)===0,'target simplex');
  const cells=[];
  for(let i=0;i<n;i++)for(let j=0;j<p;j++){
   ok(cmp(R[i][j],Z)>=0&&cmp(R[i][j],O)<=0&&cmp(C[i][j],Z)>=0&&cmp(C[i][j],O)<=0,'payoff range');
   const gaps=[...R.map(r=>sub(sub(r[j],R[i][j]),E)),...C[i].map(v=>sub(sub(v,C[i][j]),E))];
   cells.push({e:game.endings[i][j],gaps});
  }
  const subsets=Array.from({length:(1<<ends.length)-2},(_,k)=>ends.filter((_,i)=>(k+1)&(1<<i)));
  return {ends,subsets,cells,d:n+p,target};
 }
 function bound(M,subset,lambda){
  const l=lambda.map(Q);
  ok(l.length===M.d&&l.every(v=>cmp(v,Z)>=0),'invalid dual');
  const vals=M.cells.map(cell=>{tick('dual_cell_evaluations');return sub(subset.includes(cell.e)?O:Z,dot(l,cell.gaps))});
  return sub(min([O,max(vals)]),sum(subset.map(e=>Q(M.target[e]??'0'))));
 }
 function dualUpper(M,duals){
  const table=new Map();
  for(const d of duals){
   const k=JSON.stringify(d.subset);
   ok(M.subsets.some(s=>JSON.stringify(s)===k)&&!table.has(k),'invalid subset roster');
   table.set(k,d.lambda);
  }
  ok(table.size===M.subsets.length,'missing dual subset');
  return st(max([Z,...M.subsets.map(s=>bound(M,s,table.get(JSON.stringify(s))))]));
 }
 function verifyTransport(game,target,screen){
  ok(screen.kind==='transport_exact'&&screen.lower===screen.upper,'transport must close');
  ok(screen.roster===rosterKey(game),'policy roster mismatch');
  const w=exact(game,target,screen.witness);
  ok(w&&w.tv===screen.lower,'invalid witness or objective');
  const u=screen.duals.length?dualUpper(model(game,target),screen.duals):trivial(game,target);
  ok(eq(u,screen.upper),'invalid upper certificate');
 }
 function fastPure(game,target){
  const u=trivial(game,target),n=game.R.length,p=game.R[0].length;
  for(let i=0;i<n;i++)for(let j=0;j<p;j++){
   if(!eq(st(sub(O,Q(target[game.endings[i][j]]??'0'))),u))continue;
   tick('fast_pure_checks');
   const w=exact(game,target,{x:pure(n,i),y:pure(p,j)});
   if(w){ok(w.tv===u,'pure TV mismatch');return {kind:'exact_trivial',lower:u,upper:u,witness:w.cert}}
  }
  return null;
 }
 function transport(game,target,sources){
  const roster=rosterKey(game),pools=sources.filter(p=>p.roster===roster);
  if(!pools.length)return null;
  const u=trivial(game,target),seen=new Set();let best=null;
  for(const p of pools)for(const profile of p.witnesses){
   const key=profile.x.join(',')+'|'+profile.y.join(',');if(seen.has(key))continue;seen.add(key);
   tick('transport_profile_checks');
   const w=exact(game,target,profile);
   if(!w)continue;
   if(!best||cmp(Q(w.tv),Q(best.tv))>0)best=w;
   if(eq(w.tv,u))return {kind:'transport_exact',lower:u,upper:u,witness:w.cert,duals:[],roster};
  }
  if(!best||!pools.some(p=>p.duals.some(d=>d.lambda.some(v=>cmp(Q(v),Z)>0))))return null;
  const M=model(game,target),ds=[];
  for(const subset of M.subsets){
   let lambda=Array(M.d).fill('0/1'),v=bound(M,subset,lambda);
   const k=JSON.stringify(subset),used=new Set([lambda.join(',')]);
   for(const p of pools)for(const d of p.duals){
    if(JSON.stringify(d.subset)!==k||used.has(d.lambda.join(',')))continue;used.add(d.lambda.join(','));
    const w=bound(M,subset,d.lambda);if(cmp(w,v)<0){v=w;lambda=d.lambda}
   }
   ds.push({subset,lambda,bound:st(v)});
  }
  const hi=st(max([Z,...ds.map(d=>Q(d.bound))]));
  ok(cmp(Q(best.tv),Q(hi))<=0,'transport interval inverted');
  if(!eq(best.tv,hi))return null;
  return {kind:'transport_exact',lower:hi,upper:hi,witness:best.cert,duals:ds.map(({subset,lambda})=>({subset,lambda})),roster};
 }
 function runArm(steps,target,mode){
  ok(modes.includes(mode),'mode');
  const cache=new Map(),history=new Map(),recent=[],results=[],counts={queries:0,identity_hits:0,fast_hits:0,transport_hits:0,cold_fallbacks:0,transport_attempts:0,transport_dual_hits:0,unique_game_count:0,peak_bank_sources:0,peak_bank_profiles:0,peak_bank_duals:0};
  S.beginMeter();H.beginMeter();C.beginMeter();meter={};
  for(const step of steps){
   const {game,key,parent}=step,k=matrixKey(game,target);counts.queries++;
   let r=mode==='cold'?null:cache.get(k),route;
   if(r){counts.identity_hits++;route='identity'}
   else{
    if(mode==='parent_transport'||mode==='bank_transport'){
     const parentEntry=parent===null?null:history.get(parent);
     const keys=mode==='parent_transport'?(parentEntry?[parentEntry]:[]):[...new Set([...(parentEntry?[parentEntry]:[]),...recent.slice().reverse()])].slice(0,bankLimit);
     const sources=keys.map(k=>cache.get(k)?.pool).filter(Boolean);
     counts.peak_bank_sources=Math.max(counts.peak_bank_sources,sources.length);
     counts.peak_bank_profiles=Math.max(counts.peak_bank_profiles,sources.reduce((n,p)=>n+p.witnesses.length,0));
     counts.peak_bank_duals=Math.max(counts.peak_bank_duals,sources.reduce((n,p)=>n+p.duals.length,0));
     if(sources.length){
      counts.transport_attempts++;
      const proof=transport(game,target,sources);
      if(proof){verifyTransport(game,target,proof);r={screen:proof,pool:pool(game,proof,target)};counts.transport_hits++;if(proof.duals.length)counts.transport_dual_hits++;route='transport'}
     }
    }
    if(!r&&['early_pure','parent_transport','bank_transport'].includes(mode)){
     const proof=fastPure(game,target);
     if(proof){C.verifyScreen(game,target,proof);r={screen:proof,pool:pool(game,proof,target)};counts.fast_hits++;route='fast'}
    }
    if(!r){
     const screen=C.certifyScreen(game,target);C.verifyScreen(game,target,screen);r={screen,pool:pool(game,screen,target)};counts.cold_fallbacks++;route='cold';
    }
    if(mode!=='cold')cache.set(k,r);
   }
   history.set(key,k);
   if(mode!=='cold'){const i=recent.indexOf(k);if(i>=0)recent.splice(i,1);recent.push(k);if(recent.length>bankLimit)recent.shift()}
   results.push({key,route,lower:r.screen.lower,upper:r.screen.upper,has_witness:r.screen.kind!=='unresolved_no_witness',...(route==='transport'?{proof:r.screen}:{})});
  }
  counts.unique_game_count=new Set(history.values()).size;
  const work={strategic:S.endMeter(),robustness:H.endMeter(),screen:C.endMeter(),transport:meter};meter=null;
  const total=k=>Object.values(work).reduce((n,o)=>n+(o[k]||0),0);
  return {mode,counts,work,total:{rational_normalizations:total('rational_normalizations'),rational_comparisons:total('rational_comparisons'),regret_evaluations:total('regret_evaluations'),solver_calls:total('solver_calls'),envelope_calls:total('envelope_calls'),bilinear_profile_evaluations:total('bilinear_profile_evaluations'),dyadic_corner_evaluations:total('dyadic_corner_evaluations'),dual_cell_evaluations:total('dual_cell_evaluations')},results};
 }
 function benchmark(t){
  const by=new Map(t.receipt.rows.map(r=>[r.key,r])),target=t.receipt.target,trajectories=[];
  for(const name of trajectoryNames){
   const steps=t.arms[name].history.map(h=>{const row=by.get(h.key);ok(row,'missing native receipt');return {key:h.key,parent:h.parent,game:t.receipt.games[row.game].game,expected:t.receipt.games[row.game].screen}});
   ok(steps.length===64&&new Set(steps.map(x=>x.key)).size===64,'trajectory size');
   const arms=Object.fromEntries(modes.map(mode=>[mode,runArm(steps,target,mode)])),cold=arms.cold;
   for(let i=0;i<steps.length;i++){
    const ref=cold.results[i],expected=steps[i].expected;
    ok(ref.lower===expected.lower&&ref.upper===expected.upper&&ref.has_witness===(expected.kind!=='unresolved_no_witness'),'cold replay mismatch');
    for(const mode of modes.slice(1)){
     const r=arms[mode].results[i];
     ok(r.key===ref.key,'trajectory drift');
     ok(cmp(Q(r.lower),Q(ref.upper))<=0&&cmp(Q(ref.lower),Q(r.upper))<=0,'interval conflict');
     if(r.route==='transport')verifyTransport(steps[i].game,target,r.proof);
     if(ref.lower===ref.upper&&r.lower===r.upper)ok(r.lower===ref.lower,'exact mismatch');
     // Optimizations use exact certificates or original cold screen. They
     // cannot weaken a cold interval, and must preserve a known witness.
     ok(cmp(Q(r.lower),Q(ref.lower))>=0&&cmp(Q(r.upper),Q(ref.upper))<=0&&(!ref.has_witness||r.has_witness),'weakened screen');
    }
   }
   trajectories.push({name,queries:steps.length,arms,strictly_tighter:Object.fromEntries(modes.map(mode=>[mode,arms[mode].results.filter((r,i)=>r.lower!==cold.results[i].lower||r.upper!==cold.results[i].upper).length]))});
  }
  return {id:t.spec.id,family:t.spec.family,trajectories};
 }
 function summarize(roots){
  const all=roots.flatMap(r=>r.trajectories);
  const aggregate=Object.fromEntries(modes.map(mode=>{
   const a=all.map(t=>t.arms[mode]),fields=(k)=>Object.fromEntries(Object.keys(a[0][k]).map(f=>[f,a.reduce((s,r)=>s+r[k][f],0)]));
   return [mode,{counts:fields('counts'),total:fields('total'),strictly_tighter:all.reduce((s,t)=>s+t.strictly_tighter[mode],0),max_bank_sources:Math.max(...a.map(r=>r.counts.peak_bank_sources)),max_bank_profiles:Math.max(...a.map(r=>r.counts.peak_bank_profiles)),max_bank_duals:Math.max(...a.map(r=>r.counts.peak_bank_duals))}];
  }));
  return {status:'development_replay',roots:roots.length,trajectories:all.length,queries:all.reduce((s,t)=>s+t.queries,0),aggregate,by_trajectory:Object.fromEntries(trajectoryNames.map(name=>[name,Object.fromEntries(modes.map(mode=>{const a=all.filter(t=>t.name===name).map(t=>t.arms[mode]);return [mode,{cold_fallbacks:a.reduce((s,r)=>s+r.counts.cold_fallbacks,0),transport_hits:a.reduce((s,r)=>s+r.counts.transport_hits,0),regret_evaluations:a.reduce((s,r)=>s+r.total.regret_evaluations,0),rational_normalizations:a.reduce((s,r)=>s+r.total.rational_normalizations,0)}]}))])),roots_summary:roots.map(r=>({id:r.id,family:r.family,trajectories:r.trajectories.map(t=>({name:t.name,arms:Object.fromEntries(modes.map(mode=>[mode,{counts:t.arms[mode].counts,total:t.arms[mode].total}]))}))}))};
 }
 function unit(){
  const g={R:[['1'],['0']],C:[['0'],['0']],endings:[['good'],['bad']],row_policies:['g','b'],column_policies:['c']},target={good:'1',bad:'0'};
  const base=C.certifyScreen(g,target);C.verifyScreen(g,target,base);
  ok(base.lower==='1/5'&&base.upper==='1/5','unit base');
  const edit={...g,C:[['1'],['0']]},proof=transport(edit,target,[pool(g,base,target)]);
  ok(proof&&proof.duals.length>0,'dual transport test');verifyTransport(edit,target,proof);
  let rejected=0;
  for(const kind of ['lambda','witness','upper','roster','subset']){
   const bad=JSON.parse(JSON.stringify(proof));
   if(kind==='lambda')bad.duals[0].lambda[0]='-1/1';
   if(kind==='witness')bad.witness.x=['0/1','1/1'];
   if(kind==='upper')bad.upper='0/1';
   if(kind==='roster')bad.roster='changed';
   if(kind==='subset')bad.duals.pop();
   try{verifyTransport(edit,target,bad)}catch{rejected++}
  }
  ok(rejected===5,'tampered proof accepted');
  const changed={...g,row_policies:['b','g']};ok(transport(changed,target,[pool(g,base,target)])===null,'roster transport');
  return {dual_transport_exact:proof.lower,tamper_rejections:rejected,roster_rejected:true};
 }
 function beginMeter(){meter={}}
 function endMeter(){const result=meter||{};meter=null;return result}
 return {modes,trajectoryNames,benchmark,summarize,unit,verifyTransport,pool,transport,fastPure,matrixKey,rosterKey,beginMeter,endMeter};
})(S,H,C);
export const {modes,trajectoryNames,benchmark,summarize,unit,verifyTransport,pool,transport,fastPure,matrixKey,rosterKey,beginMeter,endMeter}=api;
