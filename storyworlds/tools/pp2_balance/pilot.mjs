import {auditWorld,sites,patch,enumerate,measure,balance,parse,cmp} from './balance.mjs';
const assert=(x,m)=>{if(!x)throw Error(m)};
const c=value=>({pointer_type:'Bounded Number Constant',value});
const ptr=(character,keyring,coefficient=1)=>({pointer_type:'Bounded Number Pointer',character,keyring,coefficient});
const op=(operator_type,...operands)=>({operator_type,operands});
const eff=(actor,keyring,delta)=>({effect_type:'Bounded Number Effect',Set:ptr(actor,keyring),to:op('Nudge',ptr(actor,keyring),c(delta))});
const reaction=(id,to,score,after_effects=[])=>({id,consequence_id:to,desirability_script:score,after_effects});
function fixture(seed){
 let s=seed>>>0;const r=n=>{s^=s<<13;s^=s>>>17;s^=s<<5;return (s>>>0)%n};
 const P=['Trust','B'],Q=['Trust','C'],M=['Trust','B','C'],amp=()=> (2+r(7))/20;
 const a=amp(),b=amp(),d=amp(),f=amp(),g=amp(),hold=(1+r(7))/20,shift=(r(5)-2)/20;
 const mk=(id,next,fx)=>({id,options:[-1,1].map((sign,i)=>({id:id+'_'+i,visibility_script:true,reactions:[reaction(id+'_r'+i,next,c(0),fx(sign))]}))});
 const first=mk('turn1','turn2',sign=>[eff('A',P,sign*a),eff('A',['Trust'],sign/20)]);
 const second=mk('turn2','turn3',sign=>[eff('A',Q,sign*b),eff('B',['Trust','C'],sign*d)]);
 const third=mk('turn3','turn4',sign=>[eff('A',M,sign*f),eff('C',['Trust','A'],sign*g)]);
 const decision={id:'turn4',options:[-1,1].map((sign,i)=>({id:'decision_'+i,visibility_script:true,reactions:[
  reaction('coal_'+i,'coalition',op('Addition',ptr('A',P,1),ptr('A',Q,0.5),ptr('A',M,1),c(sign*shift))),
  reaction('def_'+i,'defection',op('Addition',ptr('A',P,-1),ptr('A',Q,-0.5),ptr('A',M,-1),c(-sign*shift))),
  reaction('hold_'+i,'hold',c(hold))
 ]}))};
 return {storyworld_title:'PP2 controlled '+seed,characters:['A','B','C'].map(id=>({id,name:id,bnumber_properties:{Trust:0.1}})),authored_properties:[{id:'Trust',property_name:'Trust',default_value:0}],spools:[{id:'main',spool_name:'Main',starts_active:true,encounters:['turn1','turn2','turn3','turn4']},{id:'ending',spool_name:'Endings',starts_active:false,encounters:['coalition','defection','hold']}],encounters:[first,second,third,decision,...['coalition','defection','hold'].map(id=>({id,options:[]}))]};
}
function unit(Engine){
 const world=fixture(101),e=new Engine();e.load(world);
 e.setBNumber('A',['Trust'],0.7);e.setBNumber('A',['Trust','B'],0.2);e.setBNumber('A',['Trust','C'],-0.3);e.setBNumber('A',['Trust','B','C'],-0.8);
 assert(e.getBNumber('A',['Trust'])===0.7&&e.getBNumber('A',['Trust','B'])===0.2&&e.getBNumber('A',['Trust','C'])===-0.3&&e.getBNumber('A',['Trust','B','C'])===-0.8,'full keyring isolation');
 const a=auditWorld(world);assert(a.admitted&&a.legacy_alias_groups>0,'fixture admission');
 const x=enumerate(Engine,world);assert(x.leaves===16&&x.transitions===30,'exact tree coverage');
 const approved=sites(world),p=patch(world,approved,[2,0,2,0]);assert(p.edits.length>0,'patch');
 assert(JSON.stringify(p.world.spools)===JSON.stringify(world.spools)&&JSON.stringify(p.world.characters)===JSON.stringify(world.characters),'topology/init changed');
 const bad=JSON.parse(JSON.stringify(world));bad.encounters[0].options[0].reactions[0].after_effects[0].effect_type='Set';assert(!auditWorld(bad).admitted,'unsupported effect accepted');
 let rejected=false;try{patch(world,[{...approved[0],original:999}], [1,1,1,1])}catch(e){rejected=true}assert(rejected,'corrupted approval accepted');
 return {status:'PASS',keyring_isolation:4,tree_leaves:x.leaves,transitions:x.transitions,approved_sites:approved.length,legacy_alias_groups:a.legacy_alias_groups,unsupported_effect_rejected:true,wrong_approval_rejected:true};
}
function pilot(Engine){
 const rows=[],targets=[{coalition:'3/8',defection:'3/8',hold:'1/4'},{coalition:'1/4',defection:'1/4',hold:'1/2'},{coalition:'7/16',defection:'7/16',hold:'1/8'}];
 for(let k=0;k<24;k++){
  const seed=198171+7919*k,world=fixture(seed),target=targets[k%3],approved=sites(world);
  for(const mode of ['greedy','restart','frontier']){
   const r=balance(Engine,world,approved,target,{mode,budget:16,seed:seed^8391,influenceFloor:'1/8'});
   assert(cmp(parse(r.best.metric.loss),parse(r.initial.metric.loss))<=0,'incumbent degraded');
   rows.push({seed,approved_sites:approved.length,...r});
  }
 }
 const mean=a=>a.reduce((s,v)=>s+v,0)/a.length,num=x=>{const [a,b]=parse(x);return Number(a)/Number(b)};
 const summary=['greedy','restart','frontier'].map(mode=>{const a=rows.filter(r=>r.mode===mode);return {mode,roots:a.length,initial:mean(a.map(r=>num(r.initial.metric.loss))),final:mean(a.map(r=>num(r.best.metric.loss))),target_tv:mean(a.map(r=>num(r.best.metric.target_tv))),p_influence:mean(a.map(r=>num(r.best.metric.p_readout_tv))),p2_influence:mean(a.map(r=>num(r.best.metric.p2_readout_tv))),zero_loss:a.filter(r=>r.best.metric.loss==='0/1').length,mean_candidates:mean(a.map(r=>r.evaluations)),mean_transitions:mean(a.map(r=>r.transitions)),higher_loss_exploratory_parent:a.filter(r=>r.history.some(h=>h.parent&&cmp(parse(r.history.find(x=>x.key===h.parent).metric.loss),parse(r.best.metric.loss))>0)).length}});
 const paired=[];for(const b of ['greedy','restart']){const a=rows.filter(r=>r.mode==='frontier'),m=new Map(rows.filter(r=>r.mode===b).map(r=>[r.seed,r]));const d=a.map(r=>cmp(parse(m.get(r.seed).best.metric.loss),parse(r.best.metric.loss)));paired.push({baseline:b,wins:d.filter(x=>x>0).length,losses:d.filter(x=>x<0).length,ties:d.filter(x=>!x).length})}
 return {status:'development_only',unit:unit(Engine),roots:24,summary,paired,rows};
}
export {fixture,unit,pilot};
