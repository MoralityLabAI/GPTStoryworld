import * as B from './balance.mjs';
import * as S from './strategic.mjs';
import * as H from './strategic_robustness.mjs';
import * as C from './robust_authoring.mjs';
import * as A from './amortized_verification.mjs';
import {createProofBank} from './proof_component_memory.mjs';
function campaign(B,S,H,C,A,createProofBank){
 const ok=(v,m)=>{if(!v)throw Error(m)},clone=x=>JSON.parse(JSON.stringify(x)),lex=(a,b)=>a<b?-1:a>b?1:0;
 const bytes=s=>{let n=0;for(const ch of s){const c=ch.codePointAt(0);n+=c<128?1:c<2048?2:c<65536?3:4}return n};
 const size=x=>bytes(JSON.stringify(x));
 const num=s=>{const [a,b='1']=s.split('/');return Number(a)/Number(b)};
 const add=(a,b)=>{for(const [k,v] of Object.entries(b))a[k]=(a[k]||0)+v};
 const cmp=(a,b)=>B.cmp(B.parse(a),B.parse(b));
 const modes=['identity','whole_feasible','component_lru','component_frequency'];
 const config={totalBytes:8192,identityCeiling:8,packetWitnesses:6,packetDuals:12,attempts:1,policy:'one packet on miss after early pure'};
 function measure(fn){
  for(const a of [S,H,C,A])a.beginMeter();
  try{const value=fn(),work={};for(const a of [S,H,C,A])add(work,a.endMeter());return {value,work}}
  catch(e){for(const a of [S,H,C,A])a.endMeter();throw e}
 }
 function cold(g,t){const p=C.certifyScreen(g,t);C.verifyScreen(g,t,p);return p}
 function verify(g,t,p){if(p.kind==='transport_exact')A.verifyTransport(g,t,p);else C.verifyScreen(g,t,p)}
 function lru(limit,ceiling=Infinity){
  // Array order is the LRU metadata and is itself charged.
  let list=[],peak=2,evictions=0,oversize=0,serializedBytes=0,serializations=0;
  function cost(x){const n=size(x);serializedBytes+=n;serializations++;return n}
  function get(k){const i=list.findIndex(e=>e.key===k);if(i<0)return null;const [e]=list.splice(i,1);list.push(e);return e.value}
  function put(k,v){
   const e={key:k,value:v},i=list.findIndex(e=>e.key===k);if(i>=0)list.splice(i,1);
   if(cost([e])>limit){oversize++;return}
   list.push(e);
   let n=cost(list);while(n>limit||list.length>ceiling){list.shift();evictions++;n=cost(list)}
   peak=Math.max(peak,n);
  }
  return {get,put,recent:()=>list.slice().reverse().map(e=>e.value),stats:()=>({bytes:size(list),peak,entries:list.length,evictions,oversize,serializedBytes,serializations})};
 }
 function cleanPool(g,t,p){
  const x=A.pool(g,p,t),w=new Map(),d=new Map();
  for(const a of x.witnesses){const z={x:a.x,y:a.y};w.set(JSON.stringify(z),z)}
  for(const a of x.duals){const z={subset:a.subset,lambda:a.lambda};if(a.lambda.some(v=>num(v)!==0))d.set(JSON.stringify(z),z)}
  return {roster:x.roster,witnesses:[...w.values()],duals:[...d.values()]};
 }
 function score(g,t,p,meter){
  const R=g.R.map(r=>r.map(num)),C=g.C.map(r=>r.map(num));let best=-1e6;
  for(const w of p.witnesses.slice(0,config.packetWitnesses)){
   const x=w.x.map(num),y=w.y.map(num),n=x.length,m=y.length,ra=Array(n).fill(0),ca=Array(m).fill(0),law={};
   for(let i=0;i<n;i++)for(let j=0;j<m;j++){
    ra[i]+=R[i][j]*y[j];ca[j]+=C[i][j]*x[i];const e=g.endings[i][j];law[e]=(law[e]||0)+x[i]*y[j];meter.approxCells++;
   }
   const u=ra.reduce((z,a,i)=>z+a*x[i],0),v=ca.reduce((z,a,i)=>z+a*y[i],0);
   const regret=Math.max(Math.max(...ra)-u,Math.max(...ca)-v);
   const tv=.5*[...new Set([...Object.keys(law),...Object.keys(t)])].reduce((s,e)=>s+Math.abs((law[e]||0)-num(t[e]??'0')),0);
   best=Math.max(best,(regret<=.2+1e-12?1:0)+tv-.25*regret);
  }
  return Math.round((best+.01*Math.min(p.duals.length,config.packetDuals))*1e9)/1e9;
 }
 function controller(mode){
  const split=mode!=='identity',limit=split?config.totalBytes/2:config.totalBytes;
  const identities=lru(limit,config.identityCeiling),whole=mode==='whole_feasible'?lru(limit):null;
  const components=mode.startsWith('component_')?createProofBank({byteLimit:limit,policy:mode.slice(10)}):null;
  const counts={queries:0,identity:0,pure:0,transport:0,cold:0,attempts:0,failed:0,packets:0,packetWitnesses:0,packetDuals:0,approxCells:0,wholeScans:0};
  const work={};let peakTotal=0;
  function query(g,t){
   counts.queries++;const k=A.matrixKey(g,t),old=identities.get(k);
   if(old){counts.identity++;return old}
   let r=measure(()=>{const p=A.fastPure(g,t);if(p)C.verifyScreen(g,t,p);return p});add(work,r.work);
   let p=r.value;if(p)counts.pure++;
   if(!p&&split){
    const roster=A.rosterKey(g);let packet=null;
    if(whole){
     let best=null,bestScore=-Infinity;
     for(const pool of whole.recent()){
      counts.wholeScans++;if(pool.roster!==roster||!pool.witnesses.length)continue;
      const s=score(g,t,pool,counts);if(s>bestScore){bestScore=s;best=pool}
     }
     if(best)packet={roster,witnesses:best.witnesses.slice(0,config.packetWitnesses),duals:best.duals.slice(0,config.packetDuals)};
    }else packet=components.packet(roster,{maxWitnesses:config.packetWitnesses,maxDuals:config.packetDuals,perSubset:2});
    if(packet?.witnesses.length){
     counts.attempts++;counts.packets++;counts.packetWitnesses+=packet.witnesses.length;counts.packetDuals+=packet.duals.length;
     r=measure(()=>{const v=A.transport(g,t,[packet]);if(v)A.verifyTransport(g,t,v);return v});add(work,r.work);p=r.value;
     if(p){counts.transport++;if(components)components.recordUse(p)}else counts.failed++;
    }
   }
   if(!p){r=measure(()=>cold(g,t));add(work,r.work);p=r.value;counts.cold++}
   identities.put(k,p);
   if(split){
    const pool=cleanPool(g,t,p);
    if(whole){if(pool.witnesses.length)whole.put(JSON.stringify(pool),pool)}
    else components.ingest(pool);
   }
   const n=identities.stats().bytes+(whole?.stats().bytes??components?.stats().bytes??0);ok(n<=config.totalBytes,'total byte cap');peakTotal=Math.max(peakTotal,n);
   return p;
  }
  return {query,stats:()=>({counts,work,identity:identities.stats(),pool:whole?.stats()??components?.stats()??null,peakTotal})};
 }
 function run(root){
  const trajectories=[];
  for(const tr of root.trajectories){
   const controllers=Object.fromEntries(modes.map(m=>[m,controller(m)])),answers=[];
   // Only game and target enter a controller. Historical answers are audit-only.
   for(const step of tr.steps)answers.push(Object.fromEntries(modes.map(m=>[m,controllers[m].query(step.game,tr.target)])));
   const stats=Object.fromEntries(modes.map(m=>[m,controllers[m].stats()]));
   const audit={queries:0,outputs:0,exact:0,strictlyTighter:0,work:{}};
   for(let i=0;i<tr.steps.length;i++){
    const g=tr.steps[i].game,t=tr.target,r=measure(()=>cold(g,t)),ref=r.value;add(audit.work,r.work);audit.queries++;
    const old=tr.steps[i].answers.cache.screen;
    ok(cmp(ref.lower,old.lower)<=0&&cmp(ref.upper,old.upper)>=0,'historical reference incompatible');
    for(const m of modes){
     const p=answers[i][m];verify(g,t,p);
     ok(cmp(p.lower,ref.lower)>=0&&cmp(p.upper,ref.upper)<=0&&(ref.kind==='unresolved_no_witness'||p.kind!=='unresolved_no_witness'),'weaker screen '+m);
     audit.outputs++;if(p.lower===ref.lower&&p.upper===ref.upper)audit.exact++;else audit.strictlyTighter++;
    }
   }
   for(const m of modes){const q=stats[m].counts;ok(q.queries===tr.steps.length&&q.identity+q.pure+q.transport+q.cold===q.queries,'route conservation');ok(q.attempts<=q.queries&&stats[m].peakTotal<=config.totalBytes,'cap')}
   trajectories.push({name:tr.name,stats,audit});
  }
  return {spec:root.spec,config,trajectories};
 }
 function summarize(roots){
  const ts=roots.flatMap(r=>r.trajectories),agg=Object.fromEntries(modes.map(m=>{
   const counts={},work={};let peakTotal=0;
   for(const t of ts){const s=t.stats[m];add(counts,s.counts);add(work,s.work);peakTotal=Math.max(peakTotal,s.peakTotal)}
   return [m,{counts,work,peakTotal}];
  }));
  return {status:'spent_development_only',config,roots:roots.length,trajectories:ts.length,queries:ts.reduce((n,t)=>n+t.audit.queries,0),auditedOutputs:ts.reduce((n,t)=>n+t.audit.outputs,0),parity:ts.reduce((n,t)=>n+t.audit.exact,0),aggregate:agg};
 }
 return {config,modes,run,summarize};
}
export const {config,modes,run,summarize}=campaign(B,S,H,C,A,createProofBank);
