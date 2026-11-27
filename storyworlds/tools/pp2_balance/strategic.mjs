// PP2-BAL-02: exact finite-policy bimatrix certificates and bounded KITE-inspired search.
const api=(function strategicFactory(){
 const check=(b,m)=>{if(!b)throw new Error(m)};
 const Z=[0n,1n],O=[1n,1n],S=[1n,5n];
 const gcd=(a,b)=>{a=a<0n?-a:a;while(b){[a,b]=[b,a%b]}return a};
 function F(a,b=1n){check(b!==0n,'zero denominator');if(b<0n){a=-a;b=-b}const g=gcd(a,b);return [a/g,b/g]}
 function Q(s){check(typeof s==='string'&&/^-?\d+(\/[1-9]\d*)?$/.test(s),'rational string required');const [a,b='1']=s.split('/');return F(BigInt(a),BigInt(b))}
 const str=a=>a[0]+'/'+a[1],add=(a,b)=>F(a[0]*b[1]+b[0]*a[1],a[1]*b[1]),neg=a=>[-a[0],a[1]],sub=(a,b)=>add(a,neg(b)),mul=(a,b)=>F(a[0]*b[0],a[1]*b[1]),div=(a,b)=>F(a[0]*b[1],a[1]*b[0]),cmp=(a,b)=>{const d=a[0]*b[1]-b[0]*a[1];return d<0n?-1:d>0n?1:0};
 const sum=a=>a.reduce(add,Z),max=a=>a.reduce((u,v)=>cmp(u,v)>=0?u:v),min=a=>a.reduce((u,v)=>cmp(u,v)<=0?u:v),dot=(a,b)=>sum(a.map((u,i)=>mul(u,b[i]))),abs=a=>cmp(a,Z)<0?neg(a):a;
 const inUnit=a=>cmp(a,Z)>=0&&cmp(a,O)<=0;
 const pure=(n,i)=>Array.from({length:n},(_,j)=>i===j?O:Z),uniform=n=>Array.from({length:n},()=>F(1n,BigInt(n)));
 const mix=(a,b,t)=>a.map((v,i)=>add(mul(v,sub(O,t)),mul(b[i],t)));
 const argmax=a=>a.findIndex(v=>cmp(v,max(a))===0);
 const show=a=>a.map(str);
 function game(R,C){
  check(Array.isArray(R)&&R.length&&Array.isArray(R[0])&&R[0].length,'empty game');
  const m=R.length,n=R[0].length;
  check(Array.isArray(C)&&C.length===m&&[R,C].every(M=>M.every(r=>Array.isArray(r)&&r.length===n)),'matrix shape');
  const [r,c]=[R,C].map(M=>M.map(row=>row.map(Q)));
  check([r,c].every(M=>M.every(row=>row.every(inUnit))),'payoffs outside [0,1]');
  return {r,c,m,n};
 }
 function simplex(a,n){check(Array.isArray(a)&&a.length===n,'strategy shape');const x=a.map(Q);check(x.every(inUnit)&&cmp(sum(x),O)===0,'invalid simplex');return x}
 function reg(g,x,y){
  const ra=g.r.map(row=>dot(row,y)),ca=Array.from({length:g.n},(_,j)=>dot(x,g.c.map(row=>row[j])));
  const ur=dot(x,ra),uc=dot(y,ca),i=argmax(ra),j=argmax(ca),rr=sub(ra[i],ur),rc=sub(ca[j],uc);
  return {rr,rc,f:max([rr,rc]),ur,uc,i,j};
 }
 // Independent public verifier: reconstruct payoffs and both deviations from input.
 function certify(R,C,xs,ys){
  const g=game(R,C),x=simplex(xs,g.m),y=simplex(ys,g.n),v=reg(g,x,y);
  return {x:show(x),y:show(y),row_payoff:str(v.ur),column_payoff:str(v.uc),row_best_response:v.i,column_best_response:v.j,row_regret:str(v.rr),column_regret:str(v.rc),max_regret:str(v.f),certified:cmp(v.f,S)<=0,threshold:'1/5'};
 }
 function kite(g,x,y,v){
  // Lemma-style correction: when r>s and the other regret satisfies the kite
  // inequality, shift the high-regret player's mix toward a pure best reply.
  if(cmp(v.rr,S)>0&&cmp(add(mul(F(4n),v.rr),v.rc),O)<=0)
   return [mix(x,pure(g.m,v.i),sub(O,div(S,v.rr))),y];
  if(cmp(v.rc,S)>0&&cmp(add(v.rr,mul(F(4n),v.rc)),O)<=0)
   return [x,mix(y,pure(g.n,v.j),sub(O,div(S,v.rc)))];
  return null;
 }
 function solve(R,C,{budget=128,mode='kite',rounds=12}={}){
  const g=game(R,C);check(Number.isSafeInteger(budget)&&budget>=1&&budget<=4096&&Number.isSafeInteger(rounds)&&rounds>=0&&rounds<=64&&['support','kite'].includes(mode),'solver budget/mode');
  let best=null,kiteAttempts=0,kiteAccepted=0;const seen=new Set(),history=[];
  const ux=uniform(g.m),uy=uniform(g.n);
  // Anchors maximize the guaranteed payoff among the finite tested strategy pool.
  // These are lower bounds on true security values, not exact LP maximin values.
  let ax=ux,ay=uy,ar=min(Array.from({length:g.n},(_,j)=>dot(ax,g.r.map(r=>r[j])))),ac=min(g.c.map(r=>dot(r,ay)));
  function anchor(x,y){
   const a=min(Array.from({length:g.n},(_,j)=>dot(x,g.r.map(r=>r[j])))),b=min(g.c.map(r=>dot(r,y)));
   if(cmp(a,ar)>0){ax=x;ar=a}if(cmp(b,ac)>0){ay=y;ac=b}
  }
  function visit(x,y,source,project=true){
   if(seen.size>=budget)return;
   const k=show(x).join(',')+'|'+show(y).join(',');if(seen.has(k))return;
   seen.add(k);const v=reg(g,x,y);anchor(x,y);
   history.push({source,x:show(x),y:show(y),max_regret:str(v.f)});
   if(!best||cmp(v.f,best.v.f)<0)best={x,y,v,source};
   if(mode==='kite'&&project&&seen.size<budget){
    const k2=kite(g,x,y,v);
    if(k2){kiteAttempts++;const w=reg(g,...k2);check(cmp(w.f,S)<=0,'kite correction failed exact check');kiteAccepted++;visit(...k2,'kite_projection',false)}
   }
  }
  visit(ux,uy,'uniform');
  for(let i=0;i<g.m&&seen.size<budget;i++)for(let j=0;j<g.n&&seen.size<budget;j++)visit(pure(g.m,i),pure(g.n,j),'pure');
  // Enumerate 2x2 support faces and exact indifference intersections.
  // On a 2x2 game this includes an exact equilibrium; in larger games
  // outside-support deviations are still checked against the full matrix.
  function root(a,b){const d=sub(a,b);if(cmp(d,Z)===0)return null;const t=div(neg(b),d);return inUnit(t)?t:null}
  outer:for(let i=0;i<g.m;i++)for(let k=i+1;k<g.m;k++)for(let j=0;j<g.n;j++)for(let l=j+1;l<g.n;l++){
   if(seen.size>=budget)break outer;
   const y=root(sub(g.r[i][j],g.r[k][j]),sub(g.r[i][l],g.r[k][l]));
   const x=root(sub(g.c[i][j],g.c[i][l]),sub(g.c[k][j],g.c[k][l]));
   if(x!==null&&y!==null)visit(mix(pure(g.m,k),pure(g.m,i),x),mix(pure(g.n,l),pure(g.n,j),y),'support_2x2');
  }
  if(mode==='kite'){
   // Finite, practical multiscale search inspired by the paper, with factor-64
   // timescales and 1/4 security anchoring. No full MaximinKiteNE theorem claim.
   const steps=[F(1n,2n),F(1n,128n),F(1n,8192n)];
   let averages=steps.map(()=>[best.x,best.y]);
   for(let t=0;t<rounds&&seen.size<budget&&cmp(best.v.f,Z)>0;t++)for(let k=0;k<steps.length&&seen.size<budget;k++){
    const [x,y]=averages[k],qx=mix(x,ax,F(1n,4n)),qy=mix(y,ay,F(1n,4n)),v=reg(g,qx,qy);
    visit(qx,qy,'anchored_query');
    averages[k]=[mix(x,pure(g.m,v.i),steps[k]),mix(y,pure(g.n,v.j),steps[k])];
    visit(...averages[k],'scale_'+k);
   }
  }
  const cert=certify(R,C,show(best.x),show(best.y));
  check(cert.max_regret===str(best.v.f),'certificate mismatch');
  return {status:cert.certified?'certified':'unresolved',mode,budget,evaluations:seen.size,source:best.source,certificate:cert,security_lower_bounds:{row:str(ar),column:str(ac)},kite_attempts:kiteAttempts,kite_checked:kiteAccepted,history};
 }
 function extract(Engine,world,manifest,{maxCells=256,maxDepth=16,maxTransitions=50000}={}){
  check([maxCells,maxDepth,maxTransitions].every(x=>Number.isSafeInteger(x)&&x>0),'extraction budgets');
  const actors=manifest.actors;
  check(Array.isArray(actors)&&actors.length===2&&new Set(actors).size===2&&actors.every(a=>world.characters.some(c=>c.id===a)),'two declared actors required');
  const probe=new Engine().load(world);
  const decisions=world.encounters.filter(e=>!probe.isEnding(e.id)&&e.options?.length);
  const owners=manifest.owners,policies=manifest.policies,utilities=manifest.utilities;
  check(owners&&Object.keys(owners).length===decisions.length&&decisions.every(e=>actors.includes(owners[e.id])),'every decision requires exactly one declared owner');
  check(policies&&utilities,'policy and utility sidecars required');
  const isPerm=(rank,ids)=>Array.isArray(rank)&&rank.length===ids.length&&new Set(rank).size===ids.length&&rank.every(a=>ids.includes(a));
  for(const actor of actors){
   const ds=decisions.filter(e=>owners[e.id]===actor),ps=policies[actor];
   check(Array.isArray(ps)&&ps.length>0&&new Set(ps.map(p=>p.id)).size===ps.length,'invalid policy roster');
   for(const p of ps){
    check(typeof p.id==='string'&&p.id.length&&p.rankings&&Object.keys(p.rankings).length===ds.length,'policy must cover owned encounters');
    for(const e of ds){const ids=e.options.map(o=>o.id);check(ids.every(id=>typeof id==='string'&&id.length)&&new Set(ids).size===ids.length&&isPerm(p.rankings[e.id],ids),'policy must rank every authored option exactly once')}
   }
  }
  const [rows,cols]=actors.map(a=>policies[a]);check(rows.length*cols.length<=maxCells,'normal-form cell cap');
  const R=[],C=[],endings=[],traces=[];let transitions=0;
  for(const row of rows){
   const rr=[],cc=[],ee=[],tt=[];
   for(const col of cols){
    const e=new Engine().load(world),trace=[];let terminal;
    for(let depth=0;;depth++){
     const enc=e.getCurrentEncounter();check(enc,'dead encounter');
     if(e.isEnding(enc.id)||!enc.options?.length){terminal=enc.id;break}
     check(depth<maxDepth,'strategic horizon');const who=owners[enc.id],p=who===actors[0]?row:col;
     const visible=e.getVisibleOptions(enc);check(visible.length,'strategic dead end');
     const option=p.rankings[enc.id].find(id=>visible.some(o=>o.id===id));check(option!==undefined,'no ranked legal action');
     const r=e.selectReaction(visible.find(o=>o.id===option));check(r,'no selected reaction');
     check(++transitions<=maxTransitions,'strategic transition budget');
     trace.push({encounter:enc.id,actor:who,option,reaction:r.id});
     const before=e.state.turn;check(e.selectOption(option),'reader select failed');e.continueToNext();check(e.state.turn>before,'strategic stalled');
    }
    check(Object.hasOwn(utilities,terminal),'missing authored terminal utility: '+terminal);
    const u=utilities[terminal];check(Array.isArray(u)&&u.length===2&&u.map(Q).every(inUnit),'terminal utilities must be normalized rational pairs');
    rr.push(str(Q(u[0])));cc.push(str(Q(u[1])));ee.push(terminal);tt.push(trace);
   }
   R.push(rr);C.push(cc);endings.push(ee);traces.push(tt);
  }
  return {actors,row_policies:rows.map(p=>p.id),column_policies:cols.map(p=>p.id),R,C,endings,traces,transitions,scope:'declared encounter-priority policies; deterministic native reader; root mixture'};
 }
 function endingLaw(g,cert){
  // Recompute certificate from supplied matrices and profile; no trust in caller's regret.
  const v=certify(g.R,g.C,cert.x,cert.y),x=v.x.map(Q),y=v.y.map(Q),d=new Map();
  check(g.endings.length===x.length&&g.endings.every(row=>row.length===y.length),'ending matrix shape');
  for(let i=0;i<x.length;i++)for(let j=0;j<y.length;j++){const id=g.endings[i][j];d.set(id,add(d.get(id)||Z,mul(x[i],y[j])))}
  check(cmp(sum([...d.values()]),O)===0,'strategic probability mass');
  return Object.fromEntries([...d].filter(([,v])=>cmp(v,Z)>0).sort(([a],[b])=>a.localeCompare(b)).map(([k,v])=>[k,str(v)]));
 }
 function targetTV(a,b){
  const v=Object.values(b).map(Q);check(v.every(inUnit)&&cmp(sum(v),O)===0,'invalid strategic ending target');
  return str(mul(F(1n,2n),sum([...new Set([...Object.keys(a),...Object.keys(b)])].map(k=>abs(sub(Q(a[k]||'0'),Q(b[k]||'0')))))));
 }
 function rerank(Engine,api,world,approved,target,manifest,config={}){
  const {extraction={},solver={},...authorConfig}=config;
  const author=api.balance(Engine,world,approved,target,authorConfig);
  const rows=[];
  for(const candidate of author.history){
   const p=api.patch(world,approved,candidate.grid);
   const g=extract(Engine,p.world,manifest,extraction),s=solve(g.R,g.C,solver);
   const uniformCert=certify(g.R,g.C,show(uniform(g.R.length)),show(uniform(g.C[0].length)));
   const law=endingLaw(g,s.certificate);
   rows.push({key:candidate.key,grid:candidate.grid,author_loss:candidate.metric.loss,p_readout_tv:candidate.metric.p_readout_tv,p2_readout_tv:candidate.metric.p2_readout_tv,dead_or_horizon:candidate.metric.dead_or_horizon,edits:candidate.edits.length,game:g,solver:s,uniform_policy_certificate:uniformCert,strategic_ending_law:law,strategic_target_tv:targetTV(law,target)});
  }
  const certified=rows.filter(r=>r.solver.certificate.certified);
  const rank=(a,b)=>cmp(Q(a.author_loss),Q(b.author_loss))||cmp(Q(a.strategic_target_tv),Q(b.strategic_target_tv))||cmp(Q(a.solver.certificate.max_regret),Q(b.solver.certificate.max_regret))||a.edits-b.edits||a.key.localeCompare(b.key);
  certified.sort(rank);
  return {status:certified.length?'certified_candidate':'unresolved',author_best:rows.find(r=>r.key===author.best.key),strategic_best:certified[0]||null,candidate_evaluations:rows.length,author_transitions:author.transitions,strategic_transitions:rows.reduce((s,r)=>s+r.game.transitions,0),strategy_evaluations:rows.reduce((s,r)=>s+r.solver.evaluations,0),rows};
 }
 return {certify,solve,extract,endingLaw,targetTV,rerank};
})();
export const {certify,solve,extract,endingLaw,targetTV,rerank}=api;
