import * as B from './balance.mjs';
import * as S from './strategic.mjs';
import * as C from './robust_authoring.mjs';
const api=(function gymFactory(B,S,C){
 const ok=(x,m)=>{if(!x)throw Error(m)};
 const num=s=>{const [a,b=1]=s.split('/').map(Number);return a/b},q=s=>{const [a,b='1']=s.split('/');return [BigInt(a),BigInt(b)]},gcd=(a,b)=>{a=a<0n?-a:a;while(b)[a,b]=[b,a%b];return a},cmp=(s,t)=>{const [a,b]=q(s),[c,d]=q(t),x=a*d-c*b;return x<0n?-1:x>0n?1:0},plus=(s,t)=>{const [a,b]=q(s),[c,d]=q(t),x=a*d+b*c,y=b*d,g=gcd(x,y);return x/g+'/'+y/g};
 const groups=['p_effect','p2_effect','p_read','p2_read'],actors=['A','B','C'],ends=['coalition','defection','hold'];
 const clone=x=>JSON.parse(JSON.stringify(x)),at=(o,p)=>p.reduce((x,k)=>x[k],o),one=(x,xs)=>xs.map(v=>Number(x===v)),rng=seed=>{let s=seed>>>0||1;return n=>{s^=s<<13;s^=s>>>17;s^=s<<5;return(s>>>0)%n}};
 const key=g=>g.join(','),validGrid=(g,n)=>Array.isArray(g)&&g.length===n&&g.every(x=>Number.isInteger(x)&&x>=0&&x<4);
 function blocks(world){
  const map=new Map();
  for(const site of B.sites(world)){
   const pointer=site.group.endsWith('_effect')?at(world,site.path.slice(0,-4)).Set:at(world,site.path.slice(0,-1));
   ok(pointer&&pointer.character&&Array.isArray(pointer.keyring),'site pointer');
   const id=JSON.stringify([site.group,pointer.character,pointer.keyring]);
   if(!map.has(id))map.set(id,{id,group:site.group,character:pointer.character,keyring:pointer.keyring,sites:[]});
   map.get(id).sites.push(site);
  }
  return [...map.values()].sort((a,b)=>a.id.localeCompare(b.id));
 }
 function apply(world,bs,grid){
  ok(validGrid(grid,bs.length),'grid shape');
  const out=clone(world),edits=[];
  for(let i=0;i<bs.length;i++){
   const block=bs[i],g=grid[i];
   if(g===1)continue;
   const scalar=[1,1,1,1];scalar[groups.indexOf(block.group)]=g;
   const p=B.patch(world,block.sites,scalar);
   for(const edit of p.edits){at(out,edit.path.slice(0,-1))[edit.path.at(-1)]=edit.after;edits.push(edit)}
  }
  ok(new Set(edits.map(e=>JSON.stringify(e.path))).size===edits.length,'overlapping edits');
  return {world:out,edits};
 }
 const fresh=[
  {id:'recur_chain_1',family:'chain',seed:2310173,target:1,utility:0},
  {id:'recur_chain_2',family:'chain',seed:2318092,target:0,utility:1},
  {id:'recur_fork_1',family:'fork',seed:2326011,target:2,utility:0},
  {id:'recur_fork_2',family:'fork',seed:2333930,target:0,utility:1},
  {id:'recur_veto_1',family:'veto',seed:2341849,target:2,utility:1},
  {id:'recur_veto_2',family:'veto',seed:2349768,target:1,utility:0}
 ];
 function gym(Engine,spec){
  const {world,manifest,target}=C.instance(spec),bs=blocks(world),n=bs.length;
  ok(B.auditWorld(world).admitted&&[8,9].includes(n),'unexpected block roster');
  // Verify that assigning one common scalar to every block of each group
  // exactly reproduces the old patch implementation.
  for(const g of [[1,1,1,1],[0,2,3,0],[3,0,2,3]]){
   const a=apply(world,bs,bs.map(b=>g[groups.indexOf(b.group)]));
   const b=B.patch(world,B.sites(world),g);
   ok(JSON.stringify(a.world)===JSON.stringify(b.world),'grouped patch parity');
  }
  const context={blocks:bs.map(b=>({id:b.id,group:b.group,character:b.character,keyring:b.keyring,count:b.sites.length,meanAbs:b.sites.reduce((s,x)=>s+Math.abs(x.original),0)/b.sites.length})),target:ends.map(e=>num(target[e]??'0')),utility:ends.flatMap(e=>manifest.utilities[e].map(num))};
  const cache=new Map(),games=[],gameIds=new Map();let authorTransitions=0,strategicTransitions=0;
  function evaluate(grid){
   ok(validGrid(grid,n),'invalid edit grid');
   const k=key(grid);if(cache.has(k))return cache.get(k);
   const p=apply(world,bs,grid),metric=B.measure(Engine,p.world,target,{maxDepth:16,maxTransitions:50000,influenceFloor:'1/8'});
   const g=S.extract(Engine,p.world,manifest,{maxCells:64,maxDepth:16,maxTransitions:50000});
   const game={R:g.R,C:g.C,endings:g.endings,row_policies:g.row_policies,column_policies:g.column_policies};
   const gkey=JSON.stringify(game);let id=gameIds.get(gkey);
   if(id===undefined){id=games.length;gameIds.set(gkey,id);const screen=C.certifyScreen(game,target);C.verifyScreen(game,target,screen);games.push({game,screen})}
   const screen=games[id].screen;
   authorTransitions+=metric.transitions;strategicTransitions+=g.transitions;
   const row={key:k,grid:[...grid],edits:p.edits.length,game:id,author_loss:metric.loss,p:metric.p_readout_tv,p2:metric.p2_readout_tv,bad:metric.dead_or_horizon,worst_lower:screen.lower,worst_upper:screen.upper,j_lower:plus(metric.loss,screen.lower),j_upper:plus(metric.loss,screen.upper),has_witness:screen.kind!=='unresolved_no_witness',mass:ends.map(e=>game.endings.flat().filter(x=>x===e).length/game.endings.flat().length)};
   cache.set(k,row);return row;
  }
  return {spec,n,context,base:Array(n).fill(1),evaluate,receipt:()=>({spec,context,dimensions:n,space:4**n,target,manifest,blocks:bs,rows:[...cache.values()],games,authorTransitions,strategicTransitions})};
 }
 function neighbors(g){
  const out=[];
  for(let i=0;i<g.length;i++)for(const d of [-1,1]){
   const to=g.slice();to[i]+=d;if(to[i]>=0&&to[i]<4)out.push({grid:to,key:key(to),axis:i,dir:d});
  }
  return out;
 }
 const gate=r=>cmp(r.p,'1/8')>=0&&cmp(r.p2,'1/8')>=0&&r.bad==='0/1'&&r.has_witness;
 const violation=r=>Math.max(0,.125-num(r.p))+Math.max(0,.125-num(r.p2))+num(r.bad)+(r.has_witness?0:1);
 const rank=(a,b)=>Number(!gate(a))-Number(!gate(b))||(!gate(a)?violation(a)-violation(b):0)||cmp(a.j_upper,b.j_upper)||a.edits-b.edits||a.key.localeCompare(b.key);
 function features(ctx,p,e){
  const b=ctx.blocks[e.axis],group=groups.indexOf(b.group);
  const groupMean=groups.map(g=>{const indices=ctx.blocks.flatMap((b,i)=>b.group===g?[i]:[]);return indices.reduce((s,i)=>s+p.grid[i]/3,0)/Math.max(1,indices.length)});
  return [1,...one(b.group,groups),...one(b.character,actors),...one(b.keyring[1],actors),...one(b.keyring[2],actors),e.dir,p.grid[e.axis]/3,e.grid[e.axis]/3,b.count/8,b.meanAbs,...groupMean,num(p.author_loss),num(p.worst_lower),num(p.worst_upper)-num(p.worst_lower),num(p.p),num(p.p2),num(p.bad),...p.mass,...ctx.target,...ctx.utility,ctx.blocks.length/9];
 }
 const block=(ctx,e)=>groups.indexOf(ctx.blocks[e.axis].group)*2+Number(e.dir>0);
 function sample(g,{anchors=20,perAnchor=8,seed}){
  const random=rng(seed),rows=[],seen=new Set(),as=new Set();
  for(let i=0;i<anchors;i++){
   let grid;
   do{
    grid=i===0?g.base.slice():i<anchors/2?g.base.map(()=>random(3)):g.base.map(()=>random(4));
    if(i===0&&as.has(key(grid)))throw Error('duplicate base');
   }while(as.has(key(grid)));
   as.add(key(grid));
   const p=g.evaluate(grid),ns=neighbors(grid);
   for(let j=ns.length-1;j>0;j--){const k=random(j+1);[ns[j],ns[k]]=[ns[k],ns[j]]}
   for(const e of ns.slice(0,perAnchor)){
    const pair=p.key+'>'+e.key;if(seen.has(pair))continue;seen.add(pair);
    const t=g.evaluate(e.grid),exact=cmp(p.j_lower,p.j_upper)===0&&cmp(t.j_lower,t.j_upper)===0;
    rows.push({root:g.spec.id,source:p.key,target:t.key,block:block(g.context,e),x:features(g.context,p,e),y:[gate(t)?1:-1,exact?num(t.j_lower)-num(p.j_lower):null]});
   }
  }
  return rows;
 }
 return {fresh,gym,neighbors,gate,rank,violation,features,block,sample,rng,num,cmp,key};
})(B,S,C);
export const {fresh,gym,neighbors,gate,rank,violation,features,block,sample,rng,num,cmp,key}=api;
