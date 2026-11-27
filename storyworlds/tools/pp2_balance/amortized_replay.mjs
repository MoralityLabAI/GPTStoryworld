import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import * as A from './amortized_verification.mjs';
const ids=['geo_chain_1','geo_chain_2','geo_fork_1','geo_fork_2','geo_veto_1','geo_veto_2'];
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8')),write=process.argv.includes('--write');
const base='./amortized_receipts/';
function record(id,value){
 const url=new URL(base+id+'.json',import.meta.url);
 if(write){mkdirSync(new URL(base,import.meta.url),{recursive:true});writeFileSync(url,JSON.stringify(value)+'\n')}
 else assert.deepEqual(value,read(base+id+'.json'));
}
const unit=A.unit(),roots=ids.map(id=>{const r=A.benchmark(read('./nash_witness_receipts/'+id+'.json'));record(id,r);return r});
const result={unit,...A.summarize(roots)};
record('summary',result);console.log(JSON.stringify(result,null,2));
