import * as B from './balance.mjs';
import * as S from './strategic.mjs';
import * as H from './strategic_robustness.mjs';
import * as C from './robust_authoring.mjs';
import * as A from './amortized_verification.mjs';
function study(B,S,H,C,A){
 const ok=(v,m)=>{if(!v)throw Error(m)},lex=(a,b)=>a<b?-1:a>b?1:0;
 const config={totalBytes:8192,identityBytes:4096,bankBytes:4096,identityCeiling:8,witnessLimit:2,dualLimit:12,attemptLimit:1,seed:741093};
 const modes=['identity','whole_single','whole_pooled','component_lru','component_random','component_frequency','component_utility','component_lru_6'];
 const add=(a,b)=>{for(const [k,v] of Object.entries(b))a[k]=(a[k]||0)+v};
 const bytes=s=>{let n=0;for(const ch of s){const c=ch.codePointAt(0);n+=c<128?1:c<2048?2:c<65536?3:4}return n};
 const num=s=>{const [a,b='1']=s.split('/');return Number(a)/Number(b)};
 const cmp=(a,b)=>B.cmp(B.parse(a),B.parse(b));
 const qkey=w=>JSON.stringify([w.x,w.y]),dkey=d=>JSON.stringify([d.subset,d.lambda]);
 function measure(fn){
  for(const a of [S,H,C,A])a.beginMeter();
  try{const value=fn(),work={};for(const a of [S,H,C,A])add(work,a.endMeter());return {value,work}}
  catch(e){for(const a of [S,H,C,A])a.endMeter();throw e}
 }
 function cold(g,t){const p=C.certifyScreen(g,t);C.verifyScreen(g,t,p);return p}
 function verify(g,t,p){if(p.kind==='transport_exact')A.verifyTransport(g,t,p);else C.verifyScreen(g,t,p)}
 function manager(mode,seed){
  const m={serializations:0,serializedBytes:0,rankComparisons:0,lookupComparisons:0,scans:0,approxCells:0,approxProfiles:0,dualSelectionScans:0,evictions:0,identityEvictions:0,oversize:0,creditUpdates:0,randomDraws:0};
  const count=(k,n=1)=>m[k]+=n;
  function encode(v){const s=JSON.stringify(v);count('serializations');count('serializedBytes',bytes(s));return s}
  const size=v=>bytes(encode(v)),equal=(a,b)=>{count('lookupComparisons');return a===b};
  function order(a,compare){
   const out=[];
   for(const v of a){let i=out.length;while(i){count('rankComparisons');if(compare(out[i-1],v)<=0)break;i--}out.splice(i,0,v)}
   return out;
  }
  const split=mode!=='identity',isWhole=mode.startsWith('whole_'),utility=mode==='component_utility',random=mode==='component_random',frequency=mode==='component_frequency';
  const cap=split?config.identityBytes:config.totalBytes,bc=split?config.bankBytes:0;
  let ids=[],bank={clock:0,seed:random?seed:0,coldN:0,coldMean:0,entries:[]},peak=0;
  function footprint(){return size(ids)+(split?size(bank):0)}
  function mark(){const n=footprint();ok(n<=config.totalBytes,'total capacity');peak=Math.max(peak,n)}
  function get(k){const i=ids.findIndex(e=>equal(e.key,k));if(i<0)return null;const [e]=ids.splice(i,1);ids.push(e);return e.screen}
  function put(k,p){
   const v={key:k,screen:p};
   if(size([v])>cap){count('oversize');return}
   ids.push(v);while(ids.length>config.identityCeiling||size(ids)>cap){ids.shift();count('identityEvictions')}
  }
  const ek=e=>encode([e.roster,e.kind,e.payload]);
  function nextRandom(){let x=bank.seed|0;x^=x<<13;x^=x>>>17;x^=x<<5;bank.seed=x>>>0;count('randomDraws');return bank.seed}
  function evict(){
   while(size(bank)>bc){
    ok(bank.entries.length,'bank header overflow');
    let i=0;
    if(random)i=nextRandom()%bank.entries.length;
    else{
     const rank=e=>utility?e.credit/Math.max(1,size(e)):frequency?e.uses:0;
     let low=rank(bank.entries[0]);
     for(let j=1;j<bank.entries.length;j++){
      const z=rank(bank.entries[j]);count('rankComparisons');
      if(z<low||(z===low&&bank.entries[j].last<bank.entries[i].last)){i=j;low=z}
     }
    }
    bank.entries.splice(i,1);count('evictions');
   }
  }
  function observeCold(cost){
   if(!utility)return;
   // Running estimate, using only completed online cold fallbacks.
   bank.coldN=Math.min(65535,bank.coldN+1);
   bank.coldMean=Math.round(bank.coldMean+(cost-bank.coldMean)/bank.coldN);
   evict();
  }
  function ingest(g,t,p){
   if(!split)return;
   const raw=A.pool(g,p,t),ws=new Map(),ds=new Map();
   for(const w of raw.witnesses){const v={x:w.x,y:w.y};ws.set(encode(v),v)}
   for(const d of raw.duals){if(d.lambda.some(x=>num(x)!==0)){const v={subset:d.subset,lambda:d.lambda};ds.set(encode(v),v)}}
   const pool={witnesses:[...ws.values()],duals:[...ds.values()]};
   bank.clock++;
   const candidates=isWhole?(pool.witnesses.length?[['pool',pool]]:[]):[...pool.witnesses.map(w=>['witness',w]),...pool.duals.map(d=>['dual',d])];
   for(const [kind,payload] of candidates){
    const e={roster:raw.roster,kind,payload,last:bank.clock,uses:0,credit:0},k=ek(e);
    const old=bank.entries.find(x=>equal(ek(x),k));
    if(old){old.last=bank.clock;evict();continue}
    if(size({...bank,entries:[e]})>bc){count('oversize');continue}
    bank.entries.push(e);evict();
   }
   evict();
  }
  function ranking(g,t,w,R,C){
   count('approxProfiles');const x=w.x.map(num),y=w.y.map(num),n=x.length,m=y.length,ra=Array(n).fill(0),ca=Array(m).fill(0),law={};
   for(let i=0;i<n;i++)for(let j=0;j<m;j++){
    ra[i]+=R[i][j]*y[j];ca[j]+=C[i][j]*x[i];const e=g.endings[i][j];law[e]=(law[e]||0)+x[i]*y[j];count('approxCells');
   }
   const u=ra.reduce((z,a,i)=>z+a*x[i],0),v=ca.reduce((z,a,i)=>z+a*y[i],0);
   const r=Math.max(Math.max(...ra)-u,Math.max(...ca)-v),tv=.5*[...new Set([...Object.keys(law),...Object.keys(t)])].reduce((s,e)=>s+Math.abs((law[e]||0)-num(t[e]??'0')),0);
   return Math.round(((r<=.2+1e-12?1:0)+tv-.25*r)*1e9);
  }
  function packet(g,t){
   const roster=A.rosterKey(g),eligible=[];
   for(const e of bank.entries){count('scans');if(e.roster===roster)eligible.push(e)}
   const R=g.R.map(r=>r.map(num)),C=g.C.map(r=>r.map(num)),scoreCache=new Map(),limit=mode==='component_lru_6'?6:config.witnessLimit;
   function build(w,d){
    const uniqueW=new Map(),uniqueD=new Map();
    for(const item of w){const k=encode(item.v);if(!uniqueW.has(k))uniqueW.set(k,item)}
    for(const item of d){const k=encode(item.v);if(!uniqueD.has(k))uniqueD.set(k,item)}
    const ws=order([...uniqueW].map(([k,item])=>{
     if(!scoreCache.has(k))scoreCache.set(k,ranking(g,t,item.v,R,C));
     return {...item,k,score:scoreCache.get(k)};
    }),(a,b)=>b.score-a.score||lex(a.k,b.k)).slice(0,limit);
    const ds=order([...uniqueD].map(([k,item])=>({...item,k})),(a,b)=>b.e.last-a.e.last||lex(a.k,b.k)),picked=[],coverage=new Map();
    for(let pass=0;pass<2&&picked.length<config.dualLimit;pass++){
     for(const item of ds){count('dualSelectionScans');if(picked.length>=config.dualLimit)break;const k=encode(item.v.subset);
      if((coverage.get(k)||0)!==pass||picked.includes(item))continue;
      picked.push(item);coverage.set(k,pass+1);
     }
    }
    return {pool:{roster,witnesses:ws.map(x=>x.v),duals:picked.map(x=>x.v)},ws,ds:picked,score:(ws[0]?.score??-1e12)+10000000*picked.length};
   }
   if(mode==='whole_single'){
    let best=null;
    for(const e of eligible){const z=build(e.payload.witnesses.map(v=>({v,e})),e.payload.duals.map(v=>({v,e})));
     count('rankComparisons');if(z.ws.length&&(!best||z.score>best.score))best=z}
    return best;
   }
   const w=[],d=[];
   for(const e of eligible){
    if(e.kind==='pool'){w.push(...e.payload.witnesses.map(v=>({v,e})));d.push(...e.payload.duals.map(v=>({v,e})))}
    else (e.kind==='witness'?w:d).push({v:e.payload,e});
   }
   return build(w,d);
  }
  function feedback(z,p,cost){
   if(isWhole||!split)return;
   const used=new Set();
   if(p){
    const k=qkey(p.witness),ds=new Set(p.duals.map(dkey));
    for(const item of z.ws)if(qkey(item.v)===k)used.add(item.e);
    for(const item of z.ds)if(ds.has(dkey(item.v)))used.add(item.e);
   }
   const proposed=new Set([...z.ws,...z.ds].map(x=>x.e));
   if(p)for(const e of used){e.uses=Math.min(65535,e.uses+1);e.last=bank.clock;count('creditUpdates')}
   if(utility){
    // Charge the attempted packet, credit only vectors in the returned proof.
    const penalty=Math.ceil(cost/Math.max(1,proposed.size)),bonus=p?Math.floor(bank.coldMean/Math.max(1,used.size)):0;
    for(const e of proposed){e.credit=Math.max(-1e9,Math.min(1e9,e.credit-penalty+(used.has(e)?bonus:0)));count('creditUpdates')}
   }
   evict();
  }
  function stats(){return {peak,retainedBytes:footprint(),identityEntries:ids.length,bankEntries:bank.entries.length,work:{...m}}}
  mark();
  return {get,put,observeCold,ingest,packet,feedback,mark,stats};
 }
 function controller(mode,seed){
  const mem=manager(mode,seed),counts={queries:0,identity:0,pure:0,transport:0,cold:0,attempts:0,failed:0,packetWitnesses:0,packetDuals:0},work={};
  function query(g,t){
   counts.queries++;const k=A.matrixKey(g,t),old=mem.get(k);
   if(old){counts.identity++;mem.mark();return old}
   let r=measure(()=>{const p=A.fastPure(g,t);if(p)C.verifyScreen(g,t,p);return p});add(work,r.work);let p=r.value;
   if(p)counts.pure++;
   if(!p&&mode!=='identity'){
    const z=mem.packet(g,t);
    if(z?.pool.witnesses.length){counts.attempts++;counts.packetWitnesses+=z.pool.witnesses.length;counts.packetDuals+=z.pool.duals.length;
     r=measure(()=>{const v=A.transport(g,t,[z.pool]);if(v)A.verifyTransport(g,t,v);return v});add(work,r.work);p=r.value;
     if(p)counts.transport++;else counts.failed++;
     mem.feedback(z,p,r.work.rational_normalizations||0);
    }
   }
   if(!p){r=measure(()=>cold(g,t));add(work,r.work);p=r.value;counts.cold++;mem.observeCold(r.work.rational_normalizations||0)}
   mem.put(k,p);mem.ingest(g,t,p);mem.mark();return p;
  }
  return {query,stats:()=>({counts,work,memory:mem.stats()})};
 }
 function run(root){
  const trajectories=[];
  for(const tr of root.trajectories){
   const cs=Object.fromEntries(modes.map(m=>[m,controller(m,(root.spec.seed^config.seed^(tr.name==='parent'?1:2))>>>0||1)])),answers=[];
   for(const s of tr.steps)answers.push(Object.fromEntries(modes.map(m=>[m,cs[m].query(s.game,tr.target)])));
   const stats=Object.fromEntries(modes.map(m=>[m,cs[m].stats()])),audit={queries:0,outputs:0,parity:0,coldWork:{}};
   for(let i=0;i<tr.steps.length;i++){
    const g=tr.steps[i].game,t=tr.target,r=measure(()=>cold(g,t)),ref=r.value;add(audit.coldWork,r.work);audit.queries++;
    for(const m of modes){const p=answers[i][m];verify(g,t,p);
     ok(cmp(p.lower,ref.lower)>=0&&cmp(p.upper,ref.upper)<=0&&(ref.kind==='unresolved_no_witness'||p.kind!=='unresolved_no_witness'),'weaker '+m);
     audit.outputs++;if(p.lower===ref.lower&&p.upper===ref.upper)audit.parity++;
    }
   }
   for(const m of modes){const s=stats[m],q=s.counts;ok(q.identity+q.pure+q.transport+q.cold===q.queries&&q.attempts<=q.queries&&s.memory.peak<=config.totalBytes,'invariant');ok(q.packetWitnesses<=q.attempts*(m==='component_lru_6'?6:2)&&q.packetDuals<=q.attempts*12,'packet limit')}
   trajectories.push({name:tr.name,stats,audit});
  }
  return {spec:root.spec,trajectories};
 }
 function summarize(roots){
  const ts=roots.flatMap(r=>r.trajectories),aggregate=Object.fromEntries(modes.map(m=>{
   const counts={},work={},management={};let peak=0;
   for(const t of ts){const s=t.stats[m];add(counts,s.counts);add(work,s.work);add(management,s.memory.work);peak=Math.max(peak,s.memory.peak)}
   return [m,{counts,work,management,peak}];
  }));
  const paired=Object.fromEntries(modes.filter(m=>m!=='whole_pooled').map(m=>{
   const d=roots.map(r=>r.trajectories.reduce((n,t)=>n+t.stats.whole_pooled.work.rational_normalizations-t.stats[m].work.rational_normalizations,0));
   return [m,{wins:d.filter(x=>x>0).length,losses:d.filter(x=>x<0).length,ties:d.filter(x=>x===0).length,deltaByRoot:d}];
  }));
  return {status:'spent_development_only',config,roots:roots.length,trajectories:ts.length,queries:ts.reduce((n,t)=>n+t.audit.queries,0),outputs:ts.reduce((n,t)=>n+t.audit.outputs,0),parity:ts.reduce((n,t)=>n+t.audit.parity,0),aggregate,paired};
 }
 return {config,modes,run,summarize};
}
export const {config,modes,run,summarize}=study(B,S,H,C,A);
