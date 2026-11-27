const api=(function proposalFactory(){
 const ok=(v,m)=>{if(!v)throw Error(m)};
 const num=s=>{const [a,b=1]=s.split('/').map(Number);return a/b};
 const q=s=>s.split('/').map(BigInt),cmp=(s,t)=>{const [a,b]=q(s),[c,d]=q(t),x=a*d-c*b;return x<0n?-1:x>0n?1:0};
 const gcd=(a,b)=>{a=a<0n?-a:a;while(b)[a,b]=[b,a%b];return a};
 const plus=(s,t)=>{const [a,b]=q(s),[c,d]=q(t),x=a*d+b*c,y=b*d,g=gcd(x,y);return x/g+'/'+y/g};
 const minus=(s,t)=>{const [a,b]=q(t);return plus(s,(-a)+'/'+b)};
 const min=a=>a.reduce((x,y)=>cmp(x,y)<=0?x:y),max=a=>a.reduce((x,y)=>cmp(x,y)>=0?x:y);
 const budgets=[8,16,32],modes=['frontier','parent','direction','learned','shuffled','random_local','random_global'];
 const fresh=[
  {id:'test_chain_1',family:'chain',seed:1199227,target:2,utility:1},
  {id:'test_chain_2',family:'chain',seed:1207146,target:1,utility:0},
  {id:'test_fork_1',family:'fork',seed:1215065,target:0,utility:1},
  {id:'test_fork_2',family:'fork',seed:1222984,target:2,utility:0},
  {id:'test_veto_1',family:'veto',seed:1230903,target:1,utility:1},
  {id:'test_veto_2',family:'veto',seed:1238822,target:0,utility:0}
 ];
 const rng=seed=>{let s=seed>>>0||1;return n=>{s^=s<<13;s^=s>>>17;s^=s<<5;return(s>>>0)%n}};
 const gate=r=>cmp(r.p,'1/8')>=0&&cmp(r.p2,'1/8')>=0&&r.bad==='0/1';
 const admit=r=>gate(r)&&r.has_witness;
 function context(receipt){
  const t=receipt.summary.target,u=receipt.manifest.utilities;
  return {target:['coalition','defection','hold'].map(e=>num(t[e]??'0/1')),utility:['coalition','defection','hold'].flatMap(e=>u[e].map(num)),sites:['p_effect','p2_effect','p_read','p2_read'].map(g=>receipt.approved_sites.filter(s=>s.group===g).length/32)};
 }
 function observation(receipt,row){
  const game=receipt.games[row.game],screen=game.screen;
  return {key:row.key,grid:row.grid.slice(),edits:row.edits,author_loss:row.author_loss,p:row.p,p2:row.p2,bad:row.bad,worst_lower:screen.lower,worst_upper:screen.upper,j_lower:plus(row.author_loss,screen.lower),j_upper:plus(row.author_loss,screen.upper),has_witness:screen.kind!=='unresolved_no_witness',mass:['coalition','defection','hold'].map(e=>game.game.endings.flat().filter(x=>x===e).length/game.game.endings.flat().length)};
 }
 function neighbors(grid){
  const out=[];
  for(let k=0;k<4;k++)for(const d of [-1,1]){const g=grid.slice();g[k]+=d;if(g[k]>=0&&g[k]<4)out.push({key:g.join(','),grid:g,axis:k,dir:d,block:k*2+(d>0?1:0)})}
  return out;
 }
 function features(ctx,p,e){
  // The source has already been evaluated; the target has only its proposed grid.
  // All static features derive from the authored sidecar, not a test receipt label.
  return [1,...p.grid.map(v=>v/3),e.grid[e.axis]/3,num(p.author_loss),num(p.worst_lower),num(p.worst_upper)-num(p.worst_lower),num(p.p),num(p.p2),num(p.bad),...p.mass,...ctx.target,...ctx.utility,...ctx.sites];
 }
 function samples(receipt){
  const rows=new Map(receipt.rows.map(r=>[r.key,r])),ctx=context(receipt),out=[];
  for(const p of receipt.rows){
   const obs=observation(receipt,p);
   for(const e of neighbors(p.grid)){
    const t=rows.get(e.key);
    const exact=p.j_lower===p.j_upper&&t.j_lower===t.j_upper;
    // Only exact finite-grid intervals give a numeric change label.
    // A gate label is exact regardless of the worst-TV certificate width.
    out.push({root:receipt.spec.id,block:e.block,x:features(ctx,obs,e),y:[gate(t)?1:0,exact?num(minus(t.j_lower,p.j_lower)):null]});
   }
  }
  return out;
 }
 function ridge(rows,head,dim,reg=4){
  const A=Array.from({length:dim},(_,i)=>Array.from({length:dim+1},(_,j)=>i===j?reg:0));let count=0;
  for(const r of rows){const y=r.y[head];if(y===null)continue;count++;for(let i=0;i<dim;i++){for(let j=0;j<dim;j++)A[i][j]+=r.x[i]*r.x[j];A[i][dim]+=r.x[i]*y}}
  // Deterministic partial-pivoted solve. Coefficients are proposal-only.
  for(let i=0;i<dim;i++){
   let p=i;for(let k=i+1;k<dim;k++)if(Math.abs(A[k][i])>Math.abs(A[p][i]))p=k;
   [A[i],A[p]]=[A[p],A[i]];const z=A[i][i];ok(Math.abs(z)>1e-12,'singular ridge');
   for(let j=i;j<=dim;j++)A[i][j]/=z;
   for(let k=0;k<dim;k++)if(k!==i){const v=A[k][i];for(let j=i;j<=dim;j++)A[k][j]-=v*A[i][j]}
  }
  return {w:A.map(r=>r[dim]),count};
 }
 function train(receipts,{shuffle=false,seed=19472}={}){
  ok(receipts.length>0,'training roots required');
  const data=receipts.flatMap(samples),dim=data[0].x.length;
  if(shuffle){
   // Permute the joint gate/change labels within each root and edit block.
   // Preserve directional marginals and missing-label counts.
   const random=rng(seed);
   for(const root of receipts.map(r=>r.spec.id))for(let block=0;block<8;block++){
    const group=data.filter(r=>r.root===root&&r.block===block);
    const ys=group.map(r=>r.y);
    for(let i=ys.length-1;i>0;i--){const j=random(i+1);[ys[i],ys[j]]=[ys[j],ys[i]]}
    group.forEach((r,i)=>r.y=ys[i]);
   }
  }
  const blocks=Array.from({length:8},(_,block)=>{
   const group=data.filter(r=>r.block===block),heads=[0,1].map(i=>ridge(group,i,dim));
   const means=[0,1].map(i=>{const ys=group.map(r=>r.y[i]).filter(y=>y!==null);return ys.length?ys.reduce((s,y)=>s+y,0)/ys.length:0});
   return {block,heads,means};
  });
  return {kind:shuffle?'shuffled':'trained',roots:receipts.map(r=>r.spec.id),families:[...new Set(receipts.map(r=>r.spec.family))].sort(),directed_examples:data.length,exact_delta_examples:data.filter(r=>r.y[1]!==null).length,dim,blocks};
 }
 const all=()=>Array.from({length:256},(_,i)=>[i>>6,(i>>4)&3,(i>>2)&3,i&3]);
 const violation=r=>Math.max(0,0.125-num(r.p))+Math.max(0,0.125-num(r.p2))+num(r.bad)+(r.has_witness?0:1);
 const rank=(a,b)=>Number(!admit(a))-Number(!admit(b))||(!admit(a)?violation(a)-violation(b):0)||cmp(a.j_upper,b.j_upper)||a.edits-b.edits||a.key.localeCompare(b.key);
 const dot=(x,w)=>x.reduce((s,v,i)=>s+v*w[i],0);
 const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
 function runSearch(ctx,oracle,{mode,model,seed=1,budget=32}){
  ok(modes.includes(mode)&&Number.isSafeInteger(budget)&&budget>=1&&budget<=256,'search config');
  if(['learned','shuffled','direction'].includes(mode))ok(model?.blocks?.length===8,'model required');
  const random=rng(seed),seen=new Map(),history=[],snaps={};
  let best=null;
  function visit(key,parent,block){
   ok(!seen.has(key),'repeat evaluation');
   const r=oracle(key);ok(r.key===key,'oracle mismatch');
   seen.set(key,r);history.push({key,parent,block,admitted:admit(r),screen_j_upper:r.j_upper});
   if(admit(r)&&(!best||rank(r,best)<0))best=r;
   if(budgets.includes(seen.size))snaps[seen.size]={key:best?.key??null,evaluated:seen.size,admitted_seen:[...seen.values()].filter(admit).length};
  }
  visit('1,1,1,1',null,null);
  while(seen.size<budget){
   const known=[...seen.values()].sort(rank);
   if(mode==='frontier'){
    const from=known.find(r=>neighbors(r.grid).some(e=>!seen.has(e.key)));
    ok(from,'frontier exhausted');
    for(const e of neighbors(from.grid)){if(seen.size>=budget)break;if(!seen.has(e.key))visit(e.key,from.key,e.block)}
    continue;
   }
   if(mode==='random_global'){
    const open=all().map(g=>g.join(',')).filter(k=>!seen.has(k));visit(open[random(open.length)],null,null);continue;
   }
   const proposals=[];
   for(const p of known)for(const e of neighbors(p.grid))if(!seen.has(e.key)){
    let score=num(p.j_upper)+(!admit(p)?1+violation(p):0);
    if(['learned','shuffled','direction'].includes(mode)){
     const b=model.blocks[e.block],x=features(ctx,p,e);
     const [pg,delta]=mode==='direction'?b.means:b.heads.map(h=>dot(x,h.w));
     score=num(p.j_upper)+clamp(delta,-2,2)+(1-clamp(pg,0,1));
    }
    proposals.push({key:e.key,parent:p.key,block:e.block,score});
   }
   ok(proposals.length>0,'no proposal');
   const byKey=new Map();
   for(const p of proposals){const old=byKey.get(p.key);if(!old||p.score<old.score||(p.score===old.score&&p.parent<old.parent))byKey.set(p.key,p)}
   const unique=[...byKey.values()];
   const next=mode==='random_local'?unique[random(unique.length)]:unique.sort((a,b)=>a.score-b.score||a.key.localeCompare(b.key)||a.parent.localeCompare(b.parent))[0];
   visit(next.key,next.parent,next.block);
  }
  return {mode,history,snapshots:snaps};
 }
 function evaluate(receipt,model,sham){
  const ctx=context(receipt),map=new Map(receipt.rows.map(r=>[r.key,r]));
  const valid=receipt.rows.filter(r=>gate(r)&&receipt.games[r.game].screen.kind!=='unresolved_no_witness');
  const optimum=valid.length?{lower:min(valid.map(r=>r.j_lower)),upper:min(valid.map(r=>r.j_upper))}:null;
  const arms={};
  for(const mode of modes){
   const active=mode==='shuffled'?sham:model;
   const observed=new Set(),oracle=key=>{ok(!observed.has(key),'repeated oracle call');observed.add(key);const r=map.get(key);ok(r,'unknown key');return observation(receipt,r)};
   const run=runSearch(ctx,oracle,{mode,model:active,seed:receipt.spec.seed^72819});
   ok(observed.size===32,'evaluation budget');
   const score={};
   for(const b of budgets){
    const s=run.snapshots[b];
    if(!s.key){score[b]={...s,status:'no_admitted_incumbent'};continue}
    const r=map.get(s.key);ok(gate(r),'returned prohibited candidate');
    // Refined interval is used exclusively for post-hoc scoring.
    const gap={lower:max(['0/1',minus(r.j_lower,optimum.upper)]),upper:minus(r.j_upper,optimum.lower)};
    score[b]={...s,status:'admitted',j_lower:r.j_lower,j_upper:r.j_upper,author_loss:r.author_loss,worst_lower:r.worst_lower,worst_upper:r.worst_upper,p:r.p,p2:r.p2,gap,exact_optimum:gap.upper==='0/1'};
   }
   arms[mode]={...run,score};
  }
  return {id:receipt.spec.id,family:receipt.spec.family,seed:receipt.spec.seed,training_roots:model.roots,training_families:model.families,optimum,admitted_grid_points:valid.length,arms};
 }
 function summary(rows){
  return Object.fromEntries(budgets.map(b=>[b,Object.fromEntries(modes.map(m=>{
   const a=rows.map(r=>r.arms[m].score[b]),v=a.filter(r=>r.status==='admitted'),paired=rows.map(r=>[r.arms[m].score[b],r.arms.frontier.score[b]]);
   const mean=(f)=>v.length?v.reduce((s,r)=>s+f(r),0)/v.length:null;
   let wins=0,losses=0,ties=0,unresolved=0;
   for(const [x,y] of paired){
    if(x.status!==y.status){if(x.status==='admitted')wins++;else losses++}
    else if(x.status!=='admitted')ties++;
    else if(cmp(x.j_upper,y.j_lower)<0)wins++;
    else if(cmp(x.j_lower,y.j_upper)>0)losses++;
    else if(x.j_lower===x.j_upper&&y.j_lower===y.j_upper&&x.j_lower===y.j_lower)ties++;
    else unresolved++;
   }
   return [m,{admitted:v.length,roots:a.length,exact_optima:v.filter(r=>r.exact_optimum).length,mean_j_upper:mean(r=>num(r.j_upper)),mean_gap_upper:mean(r=>num(r.gap.upper)),mean_worst_upper:mean(r=>num(r.worst_upper)),paired_vs_frontier:{wins,losses,ties,unresolved}}];
  }))]));
 }
 function experiment(trainReceipts,testReceipts){
  const families=['chain','fork','veto'],folds=[],rows=[];
  ok(new Set([...trainReceipts,...testReceipts].map(r=>r.spec.seed)).size===trainReceipts.length+testReceipts.length,'seed leakage');
  for(const family of families){
   const tr=trainReceipts.filter(r=>r.spec.family!==family),te=testReceipts.filter(r=>r.spec.family===family);
   ok(tr.length===4&&te.length===2,'fold roster');
   const model=train(tr),sham=train(tr,{shuffle:true});
   ok(!model.families.includes(family),'family leakage');
   folds.push({family,model,sham,test_ids:te.map(r=>r.spec.id)});
   for(const r of te)rows.push(evaluate(r,model,sham));
  }
  const transfer=train(trainReceipts),sham=train(trainReceipts,{shuffle:true});
  const seenFamily=testReceipts.map(r=>evaluate(r,transfer,sham));
  return {status:'development_transfer_test',protocol:{budgets,modes,hard_gate:'p,p2>=1/8; dead/horizon=0; screen has feasible strategy witness',reg:4,shuffle_seed:19472,score:'parent_screen_J+clipped predicted delta+(1-clipped predicted gate probability)',test:'fresh coefficient seeds; held-out generator family for each fit; seen-family transfer secondary'},folds,held_family:{summary:summary(rows),rows},seen_family:{model:transfer,sham,summary:summary(seenFamily),rows:seenFamily}};
 }
 return {fresh,budgets,modes,train,context,observation,runSearch,evaluate,experiment};
})();
export const {fresh,budgets,modes,train,context,observation,runSearch,evaluate,experiment}=api;
