// Reader-backed, bounded authoring search. No live belief or corpus writes.
const assert=(x,m)=>{if(!x)throw Error(m)};
const copy=x=>JSON.parse(JSON.stringify(x));
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const sum=a=>a.reduce((x,y)=>x+y,0n);
function gcd(a,b){if(a<0n)a=-a;while(b){[a,b]=[b,a%b]}return a}
function frac(a,b=1n){assert(b>0n,'denominator');const g=gcd(a,b);return [a/g,b/g]}
const add=(a,b)=>frac(a[0]*b[1]+b[0]*a[1],a[1]*b[1]);
const sub=(a,b)=>frac(a[0]*b[1]-b[0]*a[1],a[1]*b[1]);
const cmp=(a,b)=>{const x=a[0]*b[1]-b[0]*a[1];return x<0n?-1:x>0n?1:0};
const abs=a=>[a[0]<0n?-a[0]:a[0],a[1]];
const mul=(a,b)=>frac(a[0]*b[0],a[1]*b[1]);
const str=a=>a.map(String).join('/');
const parse=s=>frac(...s.split('/').map(BigInt));
const zero=()=>frac(0n);
const groups=['p_effect','p2_effect','p_read','p2_read'];
const scales=[0.5,1,1.5,2];
const base=[1,1,1,1];
const allowedOps={GreaterThan:2,GreaterThanOrEqualTo:2,'Arithmetic Comparator':2,And:null,Or:null,Addition:null,Multiplication:null,'Absolute Value':1,Nudge:2};
const compareTypes=new Set(['Greater Than','GT','Greater Than or Equal To','GTE','Less Than','LT','Less Than or Equal To','LTE','Equal To','EQ','Not Equal To','NEQ']);
function engineClass(html){
 const a=html.indexOf('class StoryworldEngine {'),b=html.indexOf('// ========== UI CONTROLLER ==========',a);
 assert(a>=0&&b>a,'reader class boundaries');
 return Function(html.slice(a,b)+'\nreturn StoryworldEngine;')();
}
function auditWorld(world){
 const issues=[],reads=new Map(),writes=new Map(),aliases=new Map(),operators={},effects={},pointers={};
 const bad=(path,why)=>issues.push({path:path.join('.'),why});
 const ids=new Set((world.characters||[]).map(c=>c.id)),encIds=new Set((world.encounters||[]).map(e=>e.id));
 const propIds=new Set((world.authored_properties||[]).flatMap(p=>[p.id,p.property_name].filter(Boolean)));
 const coords=(v,path,usage)=>{
  const k=v.keyring;
  if(!Array.isArray(k)||k.length<1||k.length>3||k.some(x=>typeof x!=='string'||!x||x.includes('::'))||!ids.has(v.character)){bad(path,'invalid coordinate');return}
  if(!propIds.has(k[0]))bad(path,'unregistered property id/name');
  if(k.slice(1).some(x=>!ids.has(x)))bad(path,'unknown perceived character');
  const full=JSON.stringify([v.character,...k]),old=JSON.stringify([v.character,k[0]]);
  if(!aliases.has(old))aliases.set(old,new Set());aliases.get(old).add(full);
  (usage==='write'?writes:reads).set(full,k.length-1);
 };
 function script(v,path,usage='read'){
  if(typeof v==='boolean'||finite(v)||typeof v==='string')return;
  if(v==null)return;
  if(typeof v!=='object'||Array.isArray(v)){bad(path,'unsupported script shape');return}
  if(v.pointer_type){
   pointers[v.pointer_type]=(pointers[v.pointer_type]||0)+1;
   if(v.pointer_type==='Bounded Number Pointer'||v.pointer_type==='Bounded Number Property'){
    coords(v,path,usage);
    if(v.pointer_type!=='Bounded Number Pointer')bad(path,'legacy pointer ignored by browser reader');
    if(v.coefficient!==undefined&&!finite(v.coefficient))bad(path,'nonfinite pointer coefficient');
   }else if(v.pointer_type==='Bounded Number Constant'){
    if(!finite(v.value))bad(path,'numeric constant missing finite value');
   }else if(v.pointer_type==='String Constant'){if(typeof v.value!=='string')bad(path,'invalid string constant')}
   else if(v.pointer_type==='Boolean Constant'){if(typeof v.value!=='boolean')bad(path,'invalid boolean constant')}
   else bad(path,'unsupported pointer '+v.pointer_type);
   return;
  }
  if(v.operator_type){
   const o=v.operator_type;operators[o]=(operators[o]||0)+1;
   if(!Object.prototype.hasOwnProperty.call(allowedOps,o))bad(path,'unsupported reader operator '+o);
   const n=allowedOps[o];if(!Array.isArray(v.operands)||(n!==undefined&&n!==null&&v.operands.length!==n))bad(path,'operator arity');
   if(o==='Arithmetic Comparator'&&!compareTypes.has(v.operator_subtype))bad(path,'unsupported comparator');
   for(const [i,x] of (v.operands||[]).entries())script(x,[...path,'operands',i],usage);
   return;
  }
  bad(path,'unsupported expression');
 }
 if(!Array.isArray(world.characters)||ids.size!==world.characters.length||!Array.isArray(world.encounters)||encIds.size!==world.encounters.length||!Array.isArray(world.spools))bad([],'invalid world ids or collections');
 for(const [ci,c] of (world.characters||[]).entries()){
  if(typeof c.id!=='string'||c.id.includes('::'))bad(['characters',ci],'invalid character id');
  for(const [k,v] of Object.entries(c.bnumber_properties||{})){if(typeof v==='number'&&(!finite(v)||Math.abs(v)>1))bad(['characters',ci,k],'initial bnumber out of bounds')}
 }
 const spools=new Set((world.spools||[]).map(s=>s.id));
 for(const [i,e] of (world.encounters||[]).entries()){
  const ep=['encounters',i];
  for(const k of ['acceptability_script','desirability_script'])script(e[k],[...ep,k]);
  for(const [j,o] of (e.options||[]).entries()){
   const op=[...ep,'options',j];script(o.visibility_script,[...op,'visibility_script']);
   if(!o.reactions?.length)bad(op,'option missing reactions');
   for(const [k,r] of (o.reactions||[]).entries()){
    const rp=[...op,'reactions',k];script(r.desirability_script,[...rp,'desirability_script']);
    const target=r.consequence_id;if(target&&target!=='wild'&&!encIds.has(target))bad(rp,'unknown consequence');
    for(const z of [...(r.activate_spools||[]),...(r.deactivate_spools||[])])if(!spools.has(z))bad(rp,'unknown spool');
    for(const [l,f] of (r.after_effects||[]).entries()){
     const fp=[...rp,'after_effects',l];effects[f.effect_type]=(effects[f.effect_type]||0)+1;
     if(f.effect_type!=='Bounded Number Effect')bad(fp,'effect ignored by browser reader');
     if(f.Set)script(f.Set,[...fp,'Set'],'write');else bad(fp,'missing Set');
     script(f.to,[...fp,'to']);
    }
   }
  }
 }
 for(const [i,s] of (world.spools||[]).entries())if((s.encounters||[]).some(x=>!encIds.has(x)))bad(['spools',i],'unknown encounter');
 const count=m=>[0,1,2].map(i=>[...m.values()].filter(x=>x===i).length);
 return {admitted:issues.length===0,issue_count:issues.length,issues:issues.slice(0,16),pointers,effects,operators,distinct_read_coords:count(reads),distinct_write_coords:count(writes),legacy_alias_groups:[...aliases.values()].filter(s=>s.size>1).length,legacy_aliased_coordinates:[...aliases.values()].filter(s=>s.size>1).reduce((z,s)=>z+s.size,0)};
}
const at=(o,p)=>p.reduce((x,k)=>x[k],o);
function sites(world){
 const result=[];
 function scan(v,p){
  if(!v||typeof v!=='object')return;
  if(v.pointer_type==='Bounded Number Pointer'&&[2,3].includes(v.keyring?.length)){
   const value=v.coefficient??1;if(value!==0)result.push({group:v.keyring.length===2?'p_read':'p2_read',path:[...p,'coefficient'],original:value,implicit:v.coefficient===undefined});
  }
  for(const [k,x] of Object.entries(v))if(typeof x==='object')scan(x,[...p,Array.isArray(v)?Number(k):k]);
 }
 for(const [i,e] of world.encounters.entries())for(const [j,o] of (e.options||[]).entries())for(const [k,r] of (o.reactions||[]).entries()){
  const p=['encounters',i,'options',j,'reactions',k];
  scan(r.desirability_script,[...p,'desirability_script']);
  for(const [l,f] of (r.after_effects||[]).entries()){
   const set=f.Set,to=f.to;
   if(f.effect_type!=='Bounded Number Effect'||![2,3].includes(set?.keyring?.length)||!['Nudge','Addition'].includes(to?.operator_type)||to.operands?.length!==2)continue;
   const [x,d]=to.operands;
   if(x.pointer_type!=='Bounded Number Pointer'||x.character!==set.character||JSON.stringify(x.keyring)!==JSON.stringify(set.keyring)||(x.coefficient??1)!==1||d.pointer_type!=='Bounded Number Constant'||!finite(d.value)||d.value===0)continue;
   result.push({group:set.keyring.length===2?'p_effect':'p2_effect',path:[...p,'after_effects',l,'to','operands',1,'value'],original:d.value,implicit:false});
  }
 }
 return result;
}
function patch(world,approved,grid){
 assert(grid.length===groups.length&&grid.every(i=>Number.isInteger(i)&&i>=0&&i<scales.length),'grid');
 const available=new Map(sites(world).map(s=>[JSON.stringify(s.path),s])),out=copy(world),seen=new Set(),edits=[];
 for(const s of approved){
  const k=JSON.stringify(s.path),actual=available.get(k);
  assert(actual&&JSON.stringify(actual)===JSON.stringify(s)&&!seen.has(k),'site approval mismatch');seen.add(k);
  const gain=scales[grid[groups.indexOf(s.group)]],v=s.original*gain;
  assert(finite(v)&&Math.sign(v)===Math.sign(s.original),'effect sign changed');
  if(s.group.endsWith('_effect'))assert(Math.abs(v)<=1,'effect dose exceeds one');
  else assert(Math.abs(v)<=4,'read coefficient exceeds four');
  if(gain===1)continue;
  const parent=at(out,s.path.slice(0,-1));parent[s.path.at(-1)]=v;
  edits.push({path:s.path,group:s.group,before:s.original,after:v});
 }
 return {world:out,edits};
}
function cloneState(s){return {...copy({...s,visitedEncounters:[],activeSpools:[]}),visitedEncounters:new Set(s.visitedEncounters),activeSpools:new Set(s.activeSpools)}}
function decisionAblation(Engine,order){
 const e=new Engine();if(!order)return e;
 for(const name of ['getVisibleOptions','selectReaction','selectNextAcceptableEncounter']){
  const f=e[name].bind(e);e[name]=(...args)=>{
   const get=e.getBNumber;e.getBNumber=function(c,k){return k.length===order+1?0:get.call(this,c,k)};
   try{return f(...args)}finally{e.getBNumber=get}
  };
 }
 return e;
}
function enumerate(Engine,world,{maxDepth=16,maxTransitions=50000,ablate=0}={}){
 const e=decisionAblation(Engine,ablate);e.load(world);
 let transitions=0,leaves=0;const dist=new Map(),trace=[];
 function terminal(id,mass){dist.set(id,add(dist.get(id)||zero(),mass));leaves++}
 function walk(mass,depth){
  const enc=e.getCurrentEncounter();
  if(!enc){terminal('__dead__',mass);return}
  if(e.isEnding(enc.id)||!(enc.options||[]).length){terminal(enc.id,mass);return}
  if(depth>=maxDepth){terminal('__horizon__',mass);return}
  const options=e.getVisibleOptions(enc);if(!options.length){terminal('__dead__',mass);return}
  const saved=cloneState(e.state),branch=frac(mass[0],mass[1]*BigInt(options.length));
  for(const o of options){
   assert(++transitions<=maxTransitions,'transition budget exceeded');
   e.state=cloneState(saved);
   // Independently select using reader code; effects and routing are executed by reader.
   const r=e.selectReaction(o);assert(r,'no selected reaction');
   const pending=e.selectOption(o.id);assert(pending,'reader option failed');
   const before=e.state.currentEncounterId,turn=e.state.turn;
   e.continueToNext();
   if(e.state.currentEncounterId===before&&e.state.turn===turn){terminal('__dead__',branch);continue}
   walk(branch,depth+1);
  }
  e.state=saved;
 }
 walk(frac(1n),0);
 assert(cmp([...dist.values()].reduce(add,zero()),frac(1n))===0,'mass not conserved');
 return {dist:Object.fromEntries([...dist.entries()].sort((a,b)=>a[0].localeCompare(b[0])).map(([k,v])=>[k,str(v)])),transitions,leaves};
}
function tv(a,b){const keys=new Set([...Object.keys(a),...Object.keys(b)]);return mul(frac(1n,2n),[...keys].map(k=>abs(sub(parse(a[k]||'0/1'),parse(b[k]||'0/1')))).reduce(add,zero()))}
function measure(Engine,world,target,opts){
 const normal=enumerate(Engine,world,opts),p=enumerate(Engine,world,{...opts,ablate:1}),p2=enumerate(Engine,world,{...opts,ablate:2});
 const diff=tv(normal.dist,target),effectP=tv(normal.dist,p.dist),effectP2=tv(normal.dist,p2.dist),bad=add(parse(normal.dist.__dead__||'0/1'),parse(normal.dist.__horizon__||'0/1')),floor=parse(opts.influenceFloor||'1/8');
 const short=v=>cmp(v,floor)<0?sub(floor,v):zero();
 const loss=add(add(diff,mul(frac(2n),bad)),add(short(effectP),short(effectP2)));
 return {loss:str(loss),target_tv:str(diff),p_readout_tv:str(effectP),p2_readout_tv:str(effectP2),dead_or_horizon:str(bad),normal,p_ablated:p,p2_ablated:p2,transitions:normal.transitions+p.transitions+p2.transitions};
}
function validateTarget(world,target){
 const ends=new Set(world.encounters.filter(e=>!e.options?.length).map(e=>e.id));
 assert(Object.keys(target).length>0&&Object.keys(target).every(k=>ends.has(k)),'target must name terminal encounters');
 const probs=Object.values(target).map(parse);
 assert(probs.every(x=>x[0]>=0n)&&cmp(probs.reduce(add,zero()),frac(1n))===0,'invalid target distribution');
}
function balance(Engine,world,approved,target,{mode='frontier',budget=16,maxDepth=16,maxTransitions=50000,influenceFloor='1/8',seed=1}={}){
 const audit=auditWorld(world);assert(audit.admitted,'world failed reader admission: '+JSON.stringify(audit.issues));validateTarget(world,target);
 assert(['greedy','frontier','restart'].includes(mode)&&Number.isInteger(budget)&&budget>=1&&budget<=256,'search config');
 const known=new Map(),history=[];let calls=0,s=seed>>>0;
 const gkey=g=>g.join(',');
 function random(n){s^=s<<13;s^=s>>>17;s^=s<<5;return (s>>>0)%n}
 function rank(a,b){return cmp(parse(a.metric.loss),parse(b.metric.loss))||a.edits.length-b.edits.length||a.key.localeCompare(b.key)}
 function evaluate(g,parent){
  const k=gkey(g);assert(!known.has(k),'duplicate candidate');
  const p=patch(world,approved,g),metric=measure(Engine,p.world,target,{maxDepth,maxTransitions,influenceFloor});
  const r={key:k,grid:[...g],parent,edits:p.edits,metric};known.set(k,r);history.push(r);calls+=metric.transitions;return r;
 }
 function neighbours(g){const a=[];for(let i=0;i<g.length;i++)for(const d of [-1,1]){const x=[...g];x[i]+=d;if(x[i]>=0&&x[i]<scales.length&&!known.has(gkey(x)))a.push(x)}return a}
 const all=[];for(let a=0;a<4;a++)for(let b=0;b<4;b++)for(let c=0;c<4;c++)for(let d=0;d<4;d++)all.push([a,b,c,d]);
 let best=evaluate(base,null),stop='budget';
 while(known.size<budget){
  let from=best,opts=neighbours(best.grid);
  if(!opts.length&&mode==='frontier'){const sorted=[...known.values()].sort(rank);from=sorted.find(r=>neighbours(r.grid).length);opts=from?neighbours(from.grid):[]}
  if(!opts.length&&mode==='restart'){const unseen=all.filter(g=>!known.has(gkey(g)));if(unseen.length)opts=[unseen[random(unseen.length)]];from=null}
  if(!opts.length){stop='local_exhausted';break}
  for(const g of opts){if(known.size>=budget)break;const r=evaluate(g,from?.key??null);if(rank(r,best)<0)best=r}
 }
 return {mode,budget,target,influenceFloor,initial:history[0],best,evaluations:known.size,transitions:calls,stop,history};
}
export {engineClass,auditWorld,sites,patch,enumerate,measure,balance,tv,groups,scales,base,parse,cmp};
