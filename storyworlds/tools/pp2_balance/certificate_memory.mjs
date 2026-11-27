import * as B from './balance.mjs';
import * as S from './strategic.mjs';
import * as H from './strategic_robustness.mjs';
import * as C from './robust_authoring.mjs';
import * as G from './coordinate_gym.mjs';
import * as A from './amortized_verification.mjs';
const api=(function factory(B,S,H,C,G,A){
 const ok=(v,m)=>{if(!v)throw Error(m)},num=G.num,cmp=G.cmp;
 const modes=['cache','recency','similarity','feasibility','learned','shuffled'];
 const cap=8,k=2,budget=64,trajectories=['parent','random_global'];
 const fresh=[
  {id:'mem_chain_1',family:'chain',seed:4610201,target:0,utility:0},
  {id:'mem_chain_2',family:'chain',seed:4618120,target:2,utility:1},
  {id:'mem_fork_1',family:'fork',seed:4626039,target:1,utility:0},
  {id:'mem_fork_2',family:'fork',seed:4633958,target:0,utility:1},
  {id:'mem_veto_1',family:'veto',seed:4641877,target:2,utility:0},
  {id:'mem_veto_2',family:'veto',seed:4649796,target:1,utility:1}
 ];
 const trainIds=['geo_chain_1','geo_chain_2','geo_fork_1','geo_fork_2','geo_veto_1','geo_veto_2'];
 const workKeys=['rational_normalizations','rational_comparisons','regret_evaluations','solver_calls','envelope_calls','bilinear_profile_evaluations','dyadic_corner_evaluations','dual_cell_evaluations','transport_profile_checks','fast_pure_checks','cold_screen_calls','cold_screen_verifier_calls','cover_verifier_calls','public_certify_calls'];
 const zeroWork=()=>Object.fromEntries(workKeys.map(k=>[k,0]));
 function addWork(a,b){for(const k of workKeys)a[k]+=b[k]||0}
 function measure(f){
  S.beginMeter();H.beginMeter();C.beginMeter();A.beginMeter();
  let value,error;
  try{value=f()}catch(e){error=e}
  const work=zeroWork();
  for(const v of [S.endMeter(),H.endMeter(),C.endMeter(),A.endMeter()])addWork(work,v);
  if(error)throw error;
  return {value,work};
 }
 function cold(game,target){
  const screen=C.certifyScreen(game,target);C.verifyScreen(game,target,screen);return screen;
 }
 function early(game,target){
  const p=A.fastPure(game,target);if(p)C.verifyScreen(game,target,p);return p;
 }
 function attempt(game,target,source){
  const p=A.transport(game,target,[source.pool]);
  if(p)A.verifyTransport(game,target,p);return p;
 }
 function entry(game,target,screen){return {game,screen,pool:A.pool(game,screen,target),key:A.matrixKey(game,target)}}
 function memory(){
  const bank=new Map();let evictions=0,peak=0;
  function get(key){const v=bank.get(key);if(v){bank.delete(key);bank.set(key,v)}return v}
  function put(e){bank.delete(e.key);bank.set(e.key,e);if(bank.size>cap){bank.delete(bank.keys().next().value);evictions++}peak=Math.max(peak,bank.size);ok(bank.size<=cap,'bank overflow')}
  return {get,put,recent:()=>[...bank.values()].reverse(),stats:()=>({evictions,peak})};
 }
 function approximate(game,p,target,cost){
  cost.approx_profiles++;
  const x=p.x.map(num),y=p.y.map(num),R=game.R,C=game.C,n=x.length,m=y.length;
  const ra=Array(n).fill(0),ca=Array(m).fill(0),law={};
  for(let i=0;i<n;i++)for(let j=0;j<m;j++){
   ra[i]+=num(R[i][j])*y[j];ca[j]+=num(C[i][j])*x[i];
   const e=game.endings[i][j];law[e]=(law[e]||0)+x[i]*y[j];cost.profile_cells++;
  }
  const ur=ra.reduce((s,v,i)=>s+v*x[i],0),uc=ca.reduce((s,v,i)=>s+v*y[i],0);
  const r=Math.max(Math.max(...ra)-ur,Math.max(...ca)-uc);
  const tv=.5*[...new Set([...Object.keys(law),...Object.keys(target)])].reduce((s,e)=>s+Math.abs((law[e]||0)-num(target[e]??'0')),0);
  return {r,tv};
 }
 const retrievalCost=()=>({pair_features:0,matrix_cells:0,approx_profiles:0,profile_cells:0,linear_terms:0,sort_comparisons:0});
 function features(game,target,source,age,cost){
  ok(A.rosterKey(game)===source.pool.roster,'source roster');
  cost.pair_features++;
  const a=source.game,n=game.R.length,m=game.R[0].length;
  let changed=0,delta=0,maxDelta=0;
  for(let i=0;i<n;i++)for(let j=0;j<m;j++){
   const d=Math.abs(num(a.R[i][j])-num(game.R[i][j]))+Math.abs(num(a.C[i][j])-num(game.C[i][j]));
   changed+=Number(a.endings[i][j]!==game.endings[i][j]);delta+=d;maxDelta=Math.max(maxDelta,d);cost.matrix_cells++;
  }
  const ws=new Map();for(const p of source.pool.witnesses)ws.set(p.x.join(',')+'|'+p.y.join(','),p);
  const preds=[...ws.values()].map(p=>approximate(game,p,target,cost)),best=preds.filter(p=>p.r<=.2+1e-12);
  const feasible=best.length?Math.max(...best.map(p=>p.tv)):0;
  const upper=Math.max(...game.endings.flat().map(e=>1-num(target[e]??'0')));
  const bestR=preds.length?Math.min(...preds.map(p=>p.r)):1;
  const duals=source.pool.duals.filter(d=>d.lambda.some(x=>num(x)>0));
  const norm=duals.length?Math.max(...duals.map(d=>d.lambda.reduce((s,x)=>s+num(x),0))):0;
  const x=[1,age/(cap-1),changed/(n*m),delta/(2*n*m),maxDelta/2,ws.size/6,best.length/6,Math.min(1,bestR),feasible,upper-feasible,duals.length/6,Math.min(1,norm/8),num(source.screen.upper),num(source.screen.upper)-num(source.screen.lower),upper];
  ok(x.every(Number.isFinite),'feature nonfinite');return x;
 }
 function rankSources(game,target,available,mode,fit,cost){
  const eligible=available.filter(s=>s.pool.roster===A.rosterKey(game));
  if(mode==='recency')return eligible.slice(0,k);
  if(mode==='similarity'){
   const rs=eligible.map(s=>{
    let d=0;for(let i=0;i<game.R.length;i++)for(let j=0;j<game.R[0].length;j++){d+=Number(s.game.endings[i][j]!==game.endings[i][j]);cost.matrix_cells++}
    return {s,d};
   });
   rs.sort((a,b)=>{cost.sort_comparisons++;return a.d-b.d||a.s.key.localeCompare(b.s.key)});return rs.slice(0,k).map(r=>r.s);
  }
  const rs=eligible.map((s,age)=>{
   const x=features(game,target,s,age,cost);
   let score;
   if(mode==='feasibility')score=(x[6]>0?1:0)+x[8]-.25*x[9]+.03*x[10]-.02*x[2];
   else {ok(fit&&fit.w.length===x.length,'missing retrieval model');score=x.reduce((z,v,i)=>z+v*fit.w[i],0);cost.linear_terms+=x.length}
   return {s,score:Math.round(score*1e9)/1e9};
  });
  rs.sort((a,b)=>{cost.sort_comparisons++;return b.score-a.score||a.s.key.localeCompare(b.s.key)});
  return rs.slice(0,k).map(r=>r.s);
 }
 function controller(mode,fit){
  ok(modes.includes(mode),'mode');
  const bank=memory(),work=zeroWork(),retrieval=retrievalCost(),counts={queries:0,identity:0,pure:0,transport:0,dual_transport:0,attempts:0,failed_attempts:0,cold:0,peak_profiles:0,peak_duals:0};
  function query(game,target){
   counts.queries++;const id=A.matrixKey(game,target),old=bank.get(id);
   if(old){counts.identity++;return {screen:old.screen,route:'identity',attempted:[]}}
   const fast=measure(()=>early(game,target));addWork(work,fast.work);
   let screen=fast.value,route=screen?'pure':null;const attempted=[];
   if(screen)counts.pure++;
   if(!screen&&mode!=='cache'){
    const sources=rankSources(game,target,bank.recent(),mode,fit,retrieval);
    for(const s of sources){
     counts.attempts++;
     const r=measure(()=>attempt(game,target,s));addWork(work,r.work);
     attempted.push({source:s.key,hit:Boolean(r.value),normalizations:r.work.rational_normalizations});
     if(r.value){screen=r.value;route='transport';counts.transport++;if(screen.duals.length)counts.dual_transport++;break}
     counts.failed_attempts++;
    }
   }
   if(!screen){const r=measure(()=>cold(game,target));addWork(work,r.work);screen=r.value;route='cold';counts.cold++}
   bank.put(entry(game,target,screen));
   const resident=bank.recent();
   counts.peak_profiles=Math.max(counts.peak_profiles,resident.reduce((s,e)=>s+e.pool.witnesses.length,0));
   counts.peak_duals=Math.max(counts.peak_duals,resident.reduce((s,e)=>s+e.pool.duals.length,0));
   return {screen,route,attempted};
  }
  return {query,stats:()=>({counts,work,retrieval,...bank.stats()})};
 }
 // Training pairs are generated only on prior spent trajectories. Each
 // target's cold proof is available to label work, never as a feature.
 function collect(t){
  const rows=new Map(t.receipt.rows.map(r=>[r.key,r])),target=t.receipt.target;
  const data=[],memo=new Map();let coldCalls=0,attemptCalls=0,exactHits=0;
  const cost=retrievalCost(),work=zeroWork();
  for(const name of trajectories){
   const bank=memory();
   for(const h of t.arms[name].history){
    const e=t.receipt.games[rows.get(h.key).game],id=A.matrixKey(e.game,target);
    if(bank.get(id))continue;
    let baseline=memo.get(id);
    if(!baseline){
     const f=measure(()=>early(e.game,target));addWork(work,f.work);
     if(f.value)baseline={fast:true,screen:f.value,cost:0};
     else{
      const r=measure(()=>cold(e.game,target));addWork(work,r.work);coldCalls++;
      baseline={fast:false,screen:r.value,cost:r.work.rational_normalizations};
      ok(r.value.lower===e.screen.lower&&r.value.upper===e.screen.upper,'training cold parity');
     }
     memo.set(id,baseline);
    }
    if(!baseline.fast){
     const sources=bank.recent().filter(s=>s.pool.roster===A.rosterKey(e.game));
     for(let age=0;age<sources.length;age++){
      const s=sources[age],x=features(e.game,target,s,age,cost);
      const r=measure(()=>attempt(e.game,target,s));addWork(work,r.work);attemptCalls++;
      if(r.value){exactHits++;ok(cmp(r.value.lower,baseline.screen.upper)<=0&&cmp(r.value.upper,baseline.screen.lower)>=0,'train interval conflict')}
      const saved=(r.value?baseline.cost:0)-r.work.rational_normalizations;
      data.push({root:t.spec.id,trajectory:name,query:h.key,source:s.key,x,hit:Boolean(r.value),baseline_cost:baseline.cost,transport_cost:r.work.rational_normalizations,y:saved/100000});
     }
    }
    bank.put(entry(e.game,target,baseline.screen));
   }
  }
  return {spec:t.spec,data,coldCalls,attemptCalls,exactHits,work,cost};
 }
 function fit(rows,shuffled=false){
  ok(rows.length>0,'no training pairs');const d=rows[0].x.length,ys=rows.map(r=>r.y);
  if(shuffled){
   const rng=G.rng(74121);
   for(const root of new Set(rows.map(r=>r.root))){
    const ids=rows.flatMap((r,i)=>r.root===root?[i]:[]);
    for(let i=ids.length-1;i>0;i--){const j=rng(i+1),a=ids[i],b=ids[j];[ys[a],ys[b]]=[ys[b],ys[a]]}
   }
  }
  const A0=Array.from({length:d},(_,i)=>Array.from({length:d+1},(_,j)=>i===j?4:0));
  for(let n=0;n<rows.length;n++){const x=rows[n].x,y=ys[n];for(let i=0;i<d;i++){for(let j=0;j<d;j++)A0[i][j]+=x[i]*x[j];A0[i][d]+=x[i]*y}}
  for(let i=0;i<d;i++){
   let p=i;for(let j=i+1;j<d;j++)if(Math.abs(A0[j][i])>Math.abs(A0[p][i]))p=j;
   [A0[i],A0[p]]=[A0[p],A0[i]];const z=A0[i][i];ok(Math.abs(z)>1e-12,'ridge singular');
   for(let j=i;j<=d;j++)A0[i][j]/=z;
   for(let j=0;j<d;j++)if(j!==i){const v=A0[j][i];for(let k=i;k<=d;k++)A0[j][k]-=v*A0[i][k]}
  }
  const w=A0.map(r=>r[d]);ok(w.every(Number.isFinite),'fit nonfinite');
  return {w,examples:rows.length,shuffled};
 }
 function fold(training,family){
  const roots=training.filter(r=>r.spec.family!==family),rows=roots.flatMap(r=>r.data);
  ok(roots.length===4,'family split');
  return {family,roots:roots.map(r=>r.spec.id),pairs:rows.length,hits:rows.filter(r=>r.hit).length,learned:fit(rows),shuffled:fit(rows,true)};
 }
 function test(Engine,spec,fit){
  ok(spec.family===fit.family&&!fit.roots.includes(spec.id),'test split');
  const {world,manifest,target}=C.instance(spec),bs=G.blocks(world),out=[];
  ok(B.auditWorld(world).admitted,'world audit');
  // Raw extraction for each prospective candidate, one copy of the matrix
  // streamed to every controller. Only baseline observations choose the next
  // edit, never another controller's result or the post-run cold oracle.
  for(const name of trajectories){
   const cs=Object.fromEntries(modes.map(mode=>[mode,controller(mode,fit[mode])])),seen=new Map(),steps=[],rng=G.rng(spec.seed^82271);
   let authorTransitions=0,strategicTransitions=0;
   function visit(grid,parent){
    const key=G.key(grid);ok(!seen.has(key),'repeat candidate');
    const patch=G.apply(world,bs,grid),metric=B.measure(Engine,patch.world,target,{maxDepth:16,maxTransitions:50000,influenceFloor:'1/8'});
    const x=S.extract(Engine,patch.world,manifest,{maxCells:64,maxDepth:16,maxTransitions:50000});
    authorTransitions+=metric.transitions;strategicTransitions+=x.transitions;
    const game={R:x.R,C:x.C,endings:x.endings,row_policies:x.row_policies,column_policies:x.column_policies};
    const answers=Object.fromEntries(modes.map(mode=>[mode,cs[mode].query(game,target)])),s=answers.cache.screen;
    const add=(a,b)=>{const [x,y]=B.parse(a),[z,w]=B.parse(b);const n=x*w+z*y,d=y*w;return B.parse(n+'/'+d).join('/')};
    const r={key,grid,edits:patch.edits.length,author_loss:metric.loss,p:metric.p_readout_tv,p2:metric.p2_readout_tv,bad:metric.dead_or_horizon,has_witness:s.kind!=='unresolved_no_witness',j_lower:add(metric.loss,s.lower),j_upper:add(metric.loss,s.upper)};
    seen.set(key,r);steps.push({key,parent,game,answers});
   }
   visit(Array(bs.length).fill(1),null);
   while(seen.size<budget){
    if(name==='random_global'){
     let g;do{g=Array.from({length:bs.length},()=>rng(4))}while(seen.has(G.key(g)));visit(g,null);continue;
    }
    const proposals=new Map();
    for(const p of [...seen.values()].sort(G.rank))for(const e of G.neighbors(p.grid))if(!seen.has(e.key)){
     const score=Math.round((num(p.j_upper)+(G.gate(p)?0:1+G.violation(p)))*1e9)/1e9,z={...e,parent:p.key,score},old=proposals.get(e.key);
     if(!old||score<old.score||(score===old.score&&p.key<old.parent))proposals.set(e.key,z);
    }
    const a=[...proposals.values()].sort((a,b)=>a.score-b.score||a.key.localeCompare(b.key)||a.parent.localeCompare(b.parent));ok(a.length,'frontier exhausted');visit(a[0].grid,a[0].parent);
   }
   const stats=Object.fromEntries(modes.map(m=>[m,cs[m].stats()]));
   // Audit each query independently AFTER the entire trajectory.
   let coldWork=zeroWork(),narrower=Object.fromEntries(modes.map(m=>[m,0])),exactParity=Object.fromEntries(modes.map(m=>[m,0]));
   for(const step of steps){
    const r=measure(()=>cold(step.game,target));addWork(coldWork,r.work);
    const ref=r.value;
    for(const m of modes){
     const v=step.answers[m].screen;
     if(v.kind==='transport_exact')A.verifyTransport(step.game,target,v);else C.verifyScreen(step.game,target,v);
     ok(cmp(v.lower,ref.lower)>=0&&cmp(v.upper,ref.upper)<=0&&(ref.kind==='unresolved_no_witness'||v.kind!=='unresolved_no_witness'),'weaker online screen');
     if(v.lower===ref.lower&&v.upper===ref.upper)exactParity[m]++;else narrower[m]++;
    }
   }
   for(const m of modes){ok(stats[m].peak<=cap,'memory cap');ok(stats[m].counts.queries===budget,'query budget');ok(stats[m].counts.identity+stats[m].counts.pure+stats[m].counts.transport+stats[m].counts.cold===budget,'route count');ok(stats[m].counts.attempts<=k*budget,'retrieval cap')}
   out.push({name,target,steps,stats,coldWork,narrower,exactParity,authorTransitions,strategicTransitions,reference_best:[...seen.values()].filter(G.gate).sort(G.rank)[0]??null});
  }
  return {spec,dimensions:bs.length,trajectories:out};
 }
 function summarize(training,folds,tests){
  const ts=tests.flatMap(t=>t.trajectories),sum=(a,f)=>a.reduce((s,r)=>s+f(r),0);
  const ag=ts=>Object.fromEntries(modes.map(m=>{const ss=ts.map(t=>t.stats[m]),fields=k=>Object.fromEntries(Object.keys(ss[0][k]).map(x=>[x,sum(ss,r=>r[k][x])]));return [m,{counts:fields('counts'),work:fields('work'),retrieval:fields('retrieval'),evictions:sum(ss,r=>r.evictions),peak_entries:Math.max(...ss.map(r=>r.peak)),max_profiles:Math.max(...ss.map(r=>r.counts.peak_profiles)),max_duals:Math.max(...ss.map(r=>r.counts.peak_duals)),parity:sum(ts,t=>t.exactParity[m]),narrower:sum(ts,t=>t.narrower[m])}]}));
  const per=ts.map(t=>Object.fromEntries(modes.map(m=>[m,t.stats[m].work.rational_normalizations])));
  return {status:'prospective_development',cap,k,budget,training:{pairs:sum(training,r=>r.data.length),hits:sum(training,r=>r.exactHits),cold_calls:sum(training,r=>r.coldCalls),attempts:sum(training,r=>r.attemptCalls),normalizations:sum(training,r=>r.work.rational_normalizations)},folds:folds.map(f=>({family:f.family,roots:f.roots,pairs:f.pairs,hits:f.hits})),roots:tests.length,trajectories:ts.length,queries:sum(ts,t=>t.steps.length),native_transitions:sum(ts,t=>t.authorTransitions+t.strategicTransitions),cold_audit_work:sum(ts,t=>t.coldWork.rational_normalizations),aggregate:ag(ts),by_trajectory:Object.fromEntries(trajectories.map(name=>[name,ag(ts.filter(t=>t.name===name))])),learned_pairwise:Object.fromEntries(modes.filter(m=>m!=='learned').map(m=>[m,{wins:per.filter(r=>r.learned<r[m]).length,losses:per.filter(r=>r.learned>r[m]).length,ties:per.filter(r=>r.learned===r[m]).length}]))};
 }
 return {fresh,trainIds,modes,collect,fold,test,summarize};
})(B,S,H,C,G,A);
export const {fresh,trainIds,modes,collect,fold,test,summarize}=api;
