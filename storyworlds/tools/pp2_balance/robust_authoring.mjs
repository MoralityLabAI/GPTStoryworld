import * as B from './balance.mjs';
import * as S from './strategic.mjs';
import * as H from './strategic_robustness.mjs';
import {fixture} from './pilot.mjs';
const api=(function campaignFactory(B,S,H,fixture){
 const ok=(v,m)=>{if(!v)throw Error(m)};
 const gcd=(x,y)=>{x=x<0n?-x:x;while(y)[x,y]=[y,x%y];return x};
 const f=(x,y=1n)=>{ok(y>0n,'denominator');const g=gcd(x,y);return [x/g,y/g]};
 const q=s=>f(...s.split('/').map(BigInt)),st=x=>x.join('/'),a=(x,y)=>f(x[0]*y[1]+y[0]*x[1],x[1]*y[1]),b=(x,y)=>a(x,[-y[0],y[1]]),cmp=B.cmp,cs=(x,y)=>cmp(q(x),q(y)),min=xs=>xs.reduce((x,y)=>cs(x,y)<=0?x:y),max=xs=>xs.reduce((x,y)=>cs(x,y)>=0?x:y);
 const plus=(x,y)=>st(a(q(x),q(y))),minus=(x,y)=>st(b(q(x),q(y)));
 const p0='0/1',p1='1/1';
 const roster=[
  {id:'chain_a',family:'chain',seed:812021,target:0,utility:0},
  {id:'chain_b',family:'chain',seed:819940,target:1,utility:1},
  {id:'fork_a',family:'fork',seed:827859,target:1,utility:0},
  {id:'fork_b',family:'fork',seed:835778,target:2,utility:1},
  {id:'veto_a',family:'veto',seed:843697,target:2,utility:0},
  {id:'veto_b',family:'veto',seed:851616,target:0,utility:1}
 ];
 const targets=[{coalition:'3/8',defection:'3/8',hold:'1/4'},{coalition:'1/4',defection:'1/4',hold:'1/2'},{coalition:'7/16',defection:'7/16',hold:'1/8'}];
 const utilities=[{coalition:['3/4','3/4'],defection:['1','0'],hold:['1/4','1/2']},{coalition:['1/2','1'],defection:['1','1/4'],hold:['3/4','3/4']}];
 const c=value=>({pointer_type:'Bounded Number Constant',value});
 const ptr=(character,keyring,coefficient=1)=>({pointer_type:'Bounded Number Pointer',character,keyring,coefficient});
 const op=(operator_type,...operands)=>({operator_type,operands});
 const effect=(actor,keyring,delta)=>({effect_type:'Bounded Number Effect',Set:ptr(actor,keyring),to:op('Nudge',ptr(actor,keyring),c(delta))});
 const react=(id,consequence_id,desirability_script,after_effects=[])=>({id,consequence_id,desirability_script,after_effects});
 function newWorld(family,seed){
  let s=seed>>>0;const rnd=n=>{s^=s<<13;s^=s>>>17;s^=s<<5;return (s>>>0)%n},amp=()=> (2+rnd(7))/20,offset=()=> (rnd(5)-2)/20;
  const P=['Trust','B'],Q=['Trust','C'],M=['Trust','B','C'],N=['Trust','A','C'],BA=['Trust','A'];
  const [aa,bb,dd,ff,gg,hh]=Array.from({length:6},amp),shift=offset(),hold=amp();
  const rw=(id,sign,to,fx)=>({id:id+'_'+(sign>0?1:0),visibility_script:true,reactions:[react(id+'_r'+sign,to,c(0),fx)]});
  const mk=(id,to,fn)=>({id,options:[-1,1].map(sign=>rw(id,sign,to,fn(sign)))});
  const final=(id)=>({id,options:[-1,1].map((sign,i)=>({id:id+'_'+i,visibility_script:i===0?true:op('GreaterThanOrEqualTo',ptr('A',P),c(-0.25)),reactions:[
   react(id+'_c'+i,'coalition',op('Addition',ptr('A',P,1),ptr('A',Q,0.5),ptr('A',M,1),ptr('B',N,0.5),c(sign*shift))),
   react(id+'_d'+i,'defection',op('Addition',ptr('A',P,-1),ptr('A',Q,-0.5),ptr('A',M,-1),ptr('B',N,-0.5),c(-sign*shift))),
   react(id+'_h'+i,'hold',c(hold))
  ]}))});
  let encounters,owners;
  if(family==='fork'){
   const first={id:'offer',options:[-1,1].map(sign=>rw('offer',sign,sign<0?'west':'east',[effect('A',P,sign*aa),effect('B',N,sign*bb)]))};
   const west=mk('west','closing',sign=>[effect('A',Q,sign*dd),effect('A',M,sign*ff),effect('B',BA,-sign*gg)]);
   const east=mk('east','closing',sign=>[effect('A',Q,-sign*gg),effect('A',M,sign*hh),effect('B',BA,sign*ff)]);
   encounters=[first,west,east,final('closing')];owners={offer:'A',west:'B',east:'B',closing:'A'};
  }else{
   ok(family==='veto','unknown structural family');
   const first=mk('proposal','review',sign=>[effect('A',P,sign*aa),effect('B',N,sign*bb),effect('A',M,sign*dd)]);
   const review={id:'review',options:[
    {id:'review_0',visibility_script:true,reactions:[
     react('veto','defection',op('Addition',ptr('A',P,-1),ptr('B',N,-1),c(shift))),
     react('continue','amend',c(hold),[effect('A',M,-ff),effect('A',Q,gg)])
    ]},
    rw('review',1,'amend',[effect('A',M,ff),effect('A',Q,-gg),effect('B',BA,hh)])
   ]};
   const amend=mk('amend','ratify',sign=>[effect('A',P,sign*dd),effect('A',M,sign*hh),effect('B',N,-sign*gg)]);
   encounters=[first,review,amend,final('ratify')];owners={proposal:'A',review:'B',amend:'A',ratify:'B'};
  }
  const world={storyworld_title:'PP2 '+family+' '+seed,characters:['A','B','C'].map(id=>({id,name:id,bnumber_properties:{Trust:0.1}})),authored_properties:[{id:'Trust',property_name:'Trust',default_value:0}],spools:[{id:'main',spool_name:'Main',starts_active:true,encounters:encounters.map(e=>e.id)},{id:'ending',spool_name:'Endings',starts_active:false,encounters:['coalition','defection','hold']}],encounters:[...encounters,...['coalition','defection','hold'].map(id=>({id,options:[]}))]};
  return {world,owners};
 }
 function instance(spec){
  const {world,owners}=spec.family==='chain'?{world:fixture(spec.seed),owners:{turn1:'A',turn2:'B',turn3:'A',turn4:'B'}}:newWorld(spec.family,spec.seed);
  const policies={};
  for(const actor of ['A','B']){
   const es=world.encounters.filter(e=>owners[e.id]===actor);
   ok(es.length===2&&es.every(e=>e.options.length===2),'binary roster shape');
   policies[actor]=Array.from({length:4},(_,i)=>({id:actor+'_'+i,rankings:Object.fromEntries(es.map((e,k)=>[e.id,(i>>k)&1?e.options.map(o=>o.id).reverse():e.options.map(o=>o.id)]))}));
  }
  return {world,manifest:{actors:['A','B'],owners,policies,utilities:utilities[spec.utility]},target:targets[spec.target]};
 }
 function trivialUpper(game,target){
  return max([...new Set(game.endings.flat())].map(e=>minus(p1,target[e]||p0)));
 }
 function certifyScreen(game,target){
  const m=game.R.length,n=game.R[0].length,upper=trivialUpper(game,target);
  const pure=(n,i)=>Array.from({length:n},(_,j)=>i===j?p1:p0),uniform=n=>Array(n).fill('1/'+n);
  let best=null,checks=0;
  function visit(x,y){
   const cert=S.certify(game.R,game.C,x,y);checks++;
   if(!cert.certified)return;
   const law=S.endingLaw(game,cert),tv=S.targetTV(law,target);
   if(!best||cs(tv,best.tv)>0)best={tv,cert};
  }
  for(let i=0;i<m;i++)for(let j=0;j<n;j++)visit(pure(m,i),pure(n,j));
  visit(uniform(m),uniform(n));
  if(best&&cs(best.tv,upper)===0)return {kind:'exact_trivial',lower:upper,upper,witness:best.cert,screen_checks:checks};
  const sol=S.solve(game.R,game.C,{mode:'support',budget:128,rounds:12});
  for(const p of [sol.certificate,...sol.history])visit(p.x,p.y);
  if(best&&cs(best.tv,upper)===0)return {kind:'exact_trivial',lower:upper,upper,witness:best.cert,screen_checks:checks};
  // A valid lower witness seeds the full verifier. If the bounded solver
  // cannot certify any equilibrium, fail closed and retain the trivial
  // outer upper bound with no fabricated feasible witness.
  if(!best)return {kind:'unresolved_no_witness',lower:p0,upper,witness:null,screen_checks:checks};
  const cert=H.envelope(game,target,[best.cert],{maxSplits:0,depthLimit:14,dualSweeps:2,witnessSweeps:2});
  return {kind:'relaxation',lower:cert.verified.worst_tv.lower,upper:cert.verified.worst_tv.upper,receipt:cert,screen_checks:checks};
 }
 function verifyScreen(game,target,screen){
  const upper=trivialUpper(game,target);
  if(screen.kind==='relaxation'||screen.kind==='refined'){
   const r=H.verify(game,target,screen.receipt).worst_tv;
   ok(r.lower===screen.lower&&r.upper===screen.upper,'robust proof mismatch');
  }else if(screen.kind==='exact_trivial'){
   const cert=S.certify(game.R,game.C,screen.witness.x,screen.witness.y);
   ok(cert.certified&&S.targetTV(S.endingLaw(game,cert),target)===upper&&screen.lower===upper&&screen.upper===upper,'trivial certificate invalid');
  }else ok(screen.kind==='unresolved_no_witness'&&screen.lower===p0&&screen.upper===upper&&screen.witness===null,'invalid unresolved screen');
  ok(cs(screen.lower,screen.upper)<=0,'inverted interval');
 }
 const allGrid=()=>{const r=[];for(let a=0;a<4;a++)for(let b=0;b<4;b++)for(let c=0;c<4;c++)for(let d=0;d<4;d++)r.push([a,b,c,d]);return r};
 const rank=(a,b,key)=>cs(a[key],b[key])||a.edits-b.edits||a.key.localeCompare(b.key);
 function frontier(rows,key,budget=16){
  const map=new Map(rows.map(r=>[r.key,r])),seen=new Map(),history=[];
  let best=map.get('1,1,1,1');
  function visit(r,parent){ok(!seen.has(r.key),'duplicate frontier visit');seen.set(r.key,r);history.push([r.key,parent]);if(rank(r,best,key)<0)best=r}
  function neighbors(r){const out=[];for(let i=0;i<4;i++)for(const d of [-1,1]){const g=r.grid.slice();g[i]+=d;const k=g.join(',');if(map.has(k)&&!seen.has(k))out.push(map.get(k))}return out}
  visit(best,null);
  while(seen.size<budget){
   let from=best,ns=neighbors(best);
   if(!ns.length){from=[...seen.values()].sort((a,b)=>rank(a,b,key)).find(r=>neighbors(r).length);ns=from?neighbors(from):[]}
   if(!ns.length)break;
   for(const r of ns){if(seen.size>=budget)break;visit(r,from.key)}
  }
  return {key:best.key,evaluations:history.length,history};
 }
 function runRoot(Engine,spec){
  const {world,manifest,target}=instance(spec),audit=B.auditWorld(world),approved=B.sites(world);
  ok(audit.admitted&&approved.length>0,'fixture audit');
  const rows=[],games=[],gameIds=new Map();let authorTransitions=0,strategicTransitions=0;
  for(const grid of allGrid()){
   const p=B.patch(world,approved,grid),metric=B.measure(Engine,p.world,target,{maxDepth:16,maxTransitions:50000,influenceFloor:'1/8'});
   const g=S.extract(Engine,p.world,manifest,{maxCells:256,maxDepth:16,maxTransitions:50000});
   const game={R:g.R,C:g.C,endings:g.endings,row_policies:g.row_policies,column_policies:g.column_policies};
   const key=JSON.stringify(game);let gi=gameIds.get(key);
   if(gi===undefined){gi=games.length;gameIds.set(key,gi);const screen=certifyScreen(game,target);verifyScreen(game,target,screen);games.push({game,screen})}
   const screen=games[gi].screen;
   authorTransitions+=metric.transitions;strategicTransitions+=g.transitions;
   rows.push({key:grid.join(','),grid,game:gi,edits:p.edits.length,author_loss:metric.loss,p:metric.p_readout_tv,p2:metric.p2_readout_tv,bad:metric.dead_or_horizon,worst_lower:screen.lower,worst_upper:screen.upper,j_lower:plus(metric.loss,screen.lower),j_upper:plus(metric.loss,screen.upper)});
  }
  ok(rows.length===256,'grid incomplete');
  const old=frontier(rows,'author_loss'),robust=frontier(rows,'j_upper');
  const checkOld=B.balance(Engine,world,approved,target,{mode:'frontier',budget:16,seed:spec.seed^8391,influenceFloor:'1/8'});
  ok(checkOld.best.key===old.key&&JSON.stringify(checkOld.history.map(h=>[h.key,h.parent]))===JSON.stringify(old.history),'frontier parity failed');
  const map=new Map(rows.map(r=>[r.key,r]));
  const order=(key,rs=rows)=>rs.slice().sort((a,b)=>rank(a,b,key));
  const authorGrid=order('author_loss')[0];
  // Refine at most four distinct competitive games AFTER the budget-matched
  // searches. This is an exhaustive-grid arm, not information supplied to
  // the online frontier. Each screen remains frozen for baseline parity.
  const refinementIds=[];
  for(const r of [order('j_upper')[0],map.get(old.key),map.get(robust.key),authorGrid,...order('j_lower')]){
   if(refinementIds.length===4)break;
   if(refinementIds.includes(r.game)||cs(games[r.game].screen.lower,games[r.game].screen.upper)===0||games[r.game].screen.kind==='unresolved_no_witness')continue;
   const e=games[r.game],seed=e.screen.receipt?.objectives?.map(o=>o.witness)||[e.screen.witness];
   const receipt=H.envelope(e.game,target,seed,{maxSplits:128,depthLimit:14,dualSweeps:4,witnessSweeps:4});
   // If one side of a new certificate is looser, keep both proofs and
   // intersect their intervals; never silently replace a stronger bound.
   const refined={kind:'refined',lower:receipt.verified.worst_tv.lower,upper:receipt.verified.worst_tv.upper,receipt};
   verifyScreen(e.game,target,refined);e.refined=refined;refinementIds.push(r.game);
  }
  const finalRows=rows.map(r=>{
   const e=games[r.game],low=e.refined?max([e.screen.lower,e.refined.lower]):e.screen.lower,up=e.refined?min([e.screen.upper,e.refined.upper]):e.screen.upper;
   ok(cs(low,up)<=0,'certificate intersection');
   return {...r,worst_lower:low,worst_upper:up,j_lower:plus(r.author_loss,low),j_upper:plus(r.author_loss,up)};
  });
  const finals=new Map(finalRows.map(r=>[r.key,r]));
  const robustGrid=order('j_upper',finalRows)[0],gridLower=min(finalRows.map(r=>r.j_lower));
  const constrained=order('worst_upper',finalRows.filter(r=>cs(r.author_loss,authorGrid.author_loss)<=0))[0];
  const slim=r=>({key:r.key,game:r.game,author_loss:r.author_loss,worst_lower:r.worst_lower,worst_upper:r.worst_upper,j_lower:r.j_lower,j_upper:r.j_upper,p:r.p,p2:r.p2,bad:r.bad});
  const label=(r,t,low,up)=>{
   if(cs(t[up],r[low])<0)return 'improves';
   if(cs(t[low],r[up])>0)return 'degrades';
   if(cs(r[low],r[up])===0&&cs(t[low],t[up])===0&&cs(r[low],t[low])===0)return 'tie';
   return 'unresolved';
  };
  const edges=[],counts={improves:0,degrades:0,tie:0,unresolved:0};
  for(const r of finalRows)for(let k=0;k<4;k++)if(r.grid[k]<3){
   const g=r.grid.slice();g[k]++;const t=finals.get(g.join(',')),j=label(r,t,'j_lower','j_upper'),w=label(r,t,'worst_lower','worst_upper');
   edges.push([r.key,t.key,B.groups[k],j,w]);counts[j]++;
  }
  ok(edges.length===768,'grid edge count');
  const summary={id:spec.id,family:spec.family,seed:spec.seed,target,utility_schedule:spec.utility,approved_sites:approved.length,grid:rows.length,distinct_games:games.length,screen_exact_games:games.filter(e=>cs(e.screen.lower,e.screen.upper)===0).length,refined_games:refinementIds.length,final_exact_candidates:finalRows.filter(r=>cs(r.worst_lower,r.worst_upper)===0).length,unresolved_no_witness:games.filter(e=>e.screen.kind==='unresolved_no_witness').length,author_transitions:authorTransitions,strategic_transitions:strategicTransitions,author_frontier:slim(finals.get(old.key)),robust_frontier:slim(finals.get(robust.key)),author_grid:slim(finals.get(authorGrid.key)),robust_grid:slim(robustGrid),zero_author_slack:slim(constrained),global_j_lower:gridLower,global_j_upper:robustGrid.j_upper,global_j_gap:minus(robustGrid.j_upper,gridLower),frontier_robust_certified_win:cs(finals.get(robust.key).j_upper,finals.get(old.key).j_lower)<0,frontier_robust_certified_loss:cs(finals.get(robust.key).j_lower,finals.get(old.key).j_upper)>0,grid_robust_certified_win:cs(robustGrid.j_upper,finals.get(authorGrid.key).j_lower)<0,edge_labels:counts};
  return {status:'development_only',spec,summary,approved_sites:approved,manifest,screen_config:{maxSplits:0,dualSweeps:2,witnessSweeps:2},refinement_config:{maxSplits:128,maxGames:4,dualSweeps:4,witnessSweeps:4},games,rows:finalRows,frontier:{author:old,robust},edge_columns:['from','to','group','joint_loss_label','worst_tv_label'],edges};
 }
 return {roster,instance,runRoot,verifyScreen};
})(B,S,H,fixture);
export const {roster,instance,runRoot,verifyScreen}=api;
