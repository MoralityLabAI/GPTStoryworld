// PP2-BAL-11 component store prototype. Payload bytes, not JS heap bytes.
export function createProofBank({byteLimit,policy='lru'}={}){
 const ok=(v,m)=>{if(!v)throw Error(m)},lex=(a,b)=>a<b?-1:a>b?1:0;
 const bytes=s=>{let n=0;for(const ch of s){const c=ch.codePointAt(0);n+=c<128?1:c<2048?2:c<65536?3:4}return n};
 const clone=x=>JSON.parse(JSON.stringify(x)),size=x=>bytes(JSON.stringify(x));
 const rat=s=>{
  ok(typeof s==='string'&&/^-?\d+(\/[1-9]\d*)?$/.test(s),'rational');
  let [a,b=1n]=s.split('/').map(BigInt);let g=a<0n?-a:a,h=b;
  while(h)[g,h]=[h,g%h];return (a/g)+'/'+(b/g);
 };
 const parts=s=>s.split('/').map(BigInt),nonneg=s=>parts(s)[0]>=0n;
 function simplex(v,n){
  ok(Array.isArray(v)&&v.length===n,'profile length');const p=v.map(rat);
  let a=0n,b=1n;for(const s of p){const [c,d]=parts(s);ok(c>=0n,'negative probability');a=a*d+c*b;b*=d}
  ok(a===b,'profile simplex');return p;
 }
 ok(Number.isSafeInteger(byteLimit)&&byteLimit>=128,'byte limit');
 ok(['lru','frequency'].includes(policy),'policy');
 let state={clock:0,entries:[]};
 const audit={admitted:0,duplicates:0,oversize:0,evicted:0,peakBytes:size(state)};
 const key=e=>JSON.stringify([e.roster,e.kind,e.payload]);
 function rank(a,b){return (policy==='frequency'?b.uses-a.uses:0)||b.last-a.last||lex(key(a),key(b))}
 function trim(){
  while(size(state)>byteLimit){
   ok(state.entries.length,'empty state overflow');
   state.entries.sort(rank);state.entries.pop();audit.evicted++;
  }
  audit.peakBytes=Math.max(audit.peakBytes,size(state));
 }
 function tick(){ok(state.clock<Number.MAX_SAFE_INTEGER,'clock overflow');state.clock++}
 function add(roster,kind,payload){
  const candidate={roster,kind,payload,last:state.clock,uses:0};
  const k=key(candidate),old=state.entries.find(e=>key(e)===k);
  if(old){old.last=state.clock;audit.duplicates++;trim();return}
  if(size({clock:state.clock,entries:[candidate]})>byteLimit){audit.oversize++;return}
  state.entries.push(candidate);audit.admitted++;trim();
 }
 // The caller must provide pools extracted from verified screens.
 function ingest(pool){
  ok(pool&&typeof pool.roster==='string'&&Array.isArray(pool.witnesses)&&Array.isArray(pool.duals),'pool');
  const roster=JSON.parse(pool.roster);
  ok(Array.isArray(roster)&&roster.length===2&&roster.every(r=>Array.isArray(r)&&r.length>0),'roster');
  const [n,m]=roster.map(r=>r.length),entries=[];
  // Validate the whole input before admission.
  for(const p of pool.witnesses)entries.push(['witness',{x:simplex(p.x,n),y:simplex(p.y,m)}]);
  for(const d of pool.duals){
   ok(Array.isArray(d.subset)&&d.subset.length>0&&d.subset.every(e=>typeof e==='string')&&new Set(d.subset).size===d.subset.length,'subset');
   ok(Array.isArray(d.lambda)&&d.lambda.length===n+m,'dual length');
   const lambda=d.lambda.map(rat);ok(lambda.every(nonneg),'negative dual');
   if(lambda.some(s=>s!=='0/1'))entries.push(['dual',{subset:[...d.subset].sort(),lambda}]);
  }
  tick();trim();for(const [kind,payload] of entries)add(pool.roster,kind,payload);trim();
 }
 // Read-only bounded joint packet. Prefer distinct ending subsets.
 function packet(roster,{maxWitnesses=6,maxDuals=12,perSubset=2}={}){
  for(const n of [maxWitnesses,maxDuals,perSubset])ok(Number.isSafeInteger(n)&&n>=0,'packet budget');
  const entries=state.entries.filter(e=>e.roster===roster).sort(rank);
  const w=entries.filter(e=>e.kind==='witness').slice(0,maxWitnesses);
  const d=entries.filter(e=>e.kind==='dual'),selected=[],counts=new Map();
  for(let pass=0;pass<Math.min(perSubset,d.length)&&selected.length<maxDuals;pass++){
   for(const e of d){if(selected.length>=maxDuals)break;const k=JSON.stringify(e.payload.subset);
    if((counts.get(k)||0)!==pass||selected.includes(e))continue;
    selected.push(e);counts.set(k,pass+1);
   }
  }
  return clone({roster,witnesses:w.map(e=>e.payload),duals:selected.map(e=>e.payload)});
 }
 // Caller must independently verify transport before recording use.
 function recordUse(proof){
  ok(proof&&proof.kind==='transport_exact'&&typeof proof.roster==='string'&&proof.witness&&Array.isArray(proof.duals),'verified transport required by caller');
  const p=proof.witness,keys=new Set([key({roster:proof.roster,kind:'witness',payload:{x:p.x.map(rat),y:p.y.map(rat)}})]);
  for(const d of proof.duals)keys.add(key({roster:proof.roster,kind:'dual',payload:{subset:[...d.subset].sort(),lambda:d.lambda.map(rat)}}));
  tick();for(const e of state.entries)if(keys.has(key(e))){e.last=state.clock;e.uses=Math.min(65535,e.uses+1)}trim();
 }
 return {ingest,packet,recordUse,snapshot:()=>clone(state),stats:()=>({...audit,bytes:size(state),entries:state.entries.length,byteLimit,policy})};
}
