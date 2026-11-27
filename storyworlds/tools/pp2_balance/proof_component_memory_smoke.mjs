import {createProofBank} from './proof_component_memory.mjs';
function unit(createProofBank){
 const ok=(v,m)=>{if(!v)throw Error(m)},r=JSON.stringify([['a','b'],['c']]),other=JSON.stringify([['b','a'],['c']]);
 const bank=createProofBank({byteLimit:900,policy:'frequency'});
 const w={x:['1/2','1/2'],y:['1']},d={subset:['bad'],lambda:['1/2','0','0']};
 bank.ingest({roster:r,witnesses:[w,{x:['2/4','3/6'],y:['1/1']}],duals:[d,{subset:['bad'],lambda:['2/4','0/1','0/1']},{subset:['good'],lambda:['0','0','0']}]});
 ok(bank.stats().entries===2,'canonical dedup or zero dual');
 ok(bank.packet(r).witnesses.length===1&&bank.packet(r).duals.length===1,'packet');
 ok(bank.packet(other).witnesses.length===0,'roster isolation');
 const snapshot=JSON.stringify(bank.snapshot()),packet=bank.packet(r);packet.witnesses[0].x[0]='0';ok(JSON.stringify(bank.snapshot())===snapshot,'packet alias');
 let bad=0;
 for(const p of [{roster:r,witnesses:[w,{x:['1','1'],y:['1']}],duals:[]},{roster:r,witnesses:[w],duals:[{subset:['bad'],lambda:['-1','0','0']}]}]){
  try{bank.ingest(p)}catch{bad++}
 }
 ok(bad===2&&JSON.stringify(bank.snapshot())===snapshot,'invalid partial admission');
 bank.recordUse({kind:'transport_exact',roster:r,witness:w,duals:[d]});
 ok(bank.snapshot().entries.every(e=>e.uses===1),'verified component credit');
 for(let i=1;i<30;i++){
  bank.ingest({roster:r,witnesses:[{x:[i+'/31',(31-i)+'/31'],y:['1']}],duals:[{subset:['e'+i],lambda:[i+'/31','0','0']}]});
  ok(bank.stats().bytes<=900,'overflow');
 }
 ok(bank.stats().evicted>0&&bank.stats().peakBytes<=900,'eviction');
 ok(bank.packet(r,{maxWitnesses:1,maxDuals:1}).witnesses.length<=1&&bank.packet(r,{maxWitnesses:1,maxDuals:1}).duals.length<=1,'packet caps');
 const small=createProofBank({byteLimit:128});
 small.ingest({roster:r,witnesses:[w],duals:[d]});ok(small.stats().bytes<=128,'small cap');
 return {checks:'canonical dedup, implicit zero dual, isolation, copy, atomic invalid input, attribution, eviction, packet bounds, small cap',stats:bank.stats()};
}
console.log(JSON.stringify(unit(createProofBank),null,2));
