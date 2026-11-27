import * as B from './balance.mjs';
import * as S from './strategic.mjs';
import * as G from './coordinate_gym.mjs';
function prospective(B,S,G){
 const ok=(v,m)=>{if(!v)throw Error(m)};
 const targets=[{coalition:'3/8',defection:'3/8',hold:'1/4'},{coalition:'1/4',defection:'1/4',hold:'1/2'},{coalition:'7/16',defection:'7/16',hold:'1/8'}];
 const utilities=[{coalition:['3/4','3/4'],defection:['1','0'],hold:['1/4','1/2']},{coalition:['1/2','1'],defection:['1','1/4'],hold:['3/4','3/4']}];
 const families=['ternary_diamond','bypass_relay'];
 const roster=families.flatMap((family,j)=>Array.from({length:4},(_,i)=>({id:family+'_'+(i+1),family,seed:6721049+j*104729+i*7919,target:(i+j)%3,utility:(i+j)%2})));
 const smokeRoster=families.map((family,i)=>({id:'smoke_'+family,family,seed:87019+i*7919,target:0,utility:0}));
 const c=value=>({pointer_type:'Bounded Number Constant',value}),ptr=(character,keyring,coefficient=1)=>({pointer_type:'Bounded Number Pointer',character,keyring,coefficient}),op=(operator_type,...operands)=>({operator_type,operands});
 const eff=(actor,k,delta)=>({effect_type:'Bounded Number Effect',Set:ptr(actor,k),to:op('Nudge',ptr(actor,k),c(delta))});
 const react=(id,consequence_id,desirability_script,after_effects=[])=>({id,consequence_id,desirability_script,after_effects});
 function instance(spec){
  const rng=G.rng(spec.seed),amp=()=> (2+rng(7))/20,shift=()=> (rng(5)-2)/20;
  const P=['Trust','B'],Q=['Trust','C'],M=['Trust','B','C'],N=['Trust','A','C'],BA=['Trust','A'];
  const a=amp(),b=amp(),d=amp(),e=amp(),f=amp(),h=amp(),k=amp(),l=amp(),hold=amp(),s=shift();
  const mk=(id,dests,fx)=>({id,options:dests.map((to,i)=>({id:id+'_'+i,visibility_script:true,reactions:[react(id+'_r'+i,to,c(0),fx(i))]}))});
  const final=id=>({id,options:[-1,1].map((sign,i)=>({id:id+'_'+i,visibility_script:true,reactions:[
   react(id+'_c'+i,'coalition',op('Addition',ptr('A',P),ptr('A',Q,.5),ptr('A',M),ptr('B',N,.5),c(sign*s))),
   react(id+'_d'+i,'defection',op('Addition',ptr('A',P,-1),ptr('A',Q,-.5),ptr('A',M,-1),ptr('B',N,-.5),c(-sign*s))),
   react(id+'_h'+i,'hold',c(hold))
  ]}))});
  let encounters,owners;
  if(spec.family==='ternary_diamond'){
   encounters=[
    mk('entry',['left','right','hold'],i=>[eff('A',P,(i-1)*a),eff('B',N,(1-i)*b)]),
    mk('left',['close','close'],i=>[eff('A',M,(2*i-1)*d),eff('A',Q,(2*i-1)*e),eff('B',BA,(1-2*i)*f)]),
    mk('right',['close','close'],i=>[eff('A',M,(1-2*i)*h),eff('A',Q,(2*i-1)*k),eff('B',N,(2*i-1)*l)]),
    final('close')
   ];owners={entry:'A',left:'B',right:'B',close:'A'};
  }else{
   ok(spec.family==='bypass_relay','family');
   encounters=[
    mk('entry',['screen','amend'],i=>[eff('A',P,(2*i-1)*a),eff('B',N,(2*i-1)*b)]),
    mk('screen',['amend','close'],i=>[eff('A',M,(2*i-1)*d),eff('B',BA,(1-2*i)*e)]),
    mk('amend',['ratify','ratify'],i=>[eff('A',Q,(2*i-1)*f),eff('A',M,(1-2*i)*h)]),
    mk('ratify',['close','defection'],i=>[eff('A',P,(2*i-1)*k),eff('B',N,(1-2*i)*l)]),
    final('close')
   ];owners={entry:'A',screen:'B',amend:'A',ratify:'B',close:'A'};
  }
  const ends=['coalition','defection','hold'];
  const world={storyworld_title:'PP2 prospective '+spec.id,characters:['A','B','C'].map(id=>({id,name:id,bnumber_properties:{Trust:.1}})),authored_properties:[{id:'Trust',property_name:'Trust',default_value:0}],spools:[{id:'main',spool_name:'Main',starts_active:true,encounters:encounters.map(e=>e.id)},{id:'ending',spool_name:'Endings',starts_active:false,encounters:ends}],encounters:[...encounters,...ends.map(id=>({id,options:[]}))]};
  const policies={};
  for(const actor of ['A','B']){
   let rows=[{}];
   for(const enc of encounters.filter(x=>owners[x.id]===actor)){
    const ids=enc.options.map(o=>o.id),ranks=ids.map((_,i)=>[...ids.slice(i),...ids.slice(0,i)]);
    rows=rows.flatMap(row=>ranks.map(rank=>({...row,[enc.id]:rank})));
   }
   // Policy IDs encode topology and the actual ordered rankings, avoiding aliases
   // between two same-sized but semantically distinct policy rosters.
   policies[actor]=rows.map(rankings=>({id:JSON.stringify([spec.family,actor,rankings]),rankings}));
  }
  return {world,manifest:{actors:['A','B'],owners,policies,utilities:utilities[spec.utility]},target:targets[spec.target]};
 }
 function extract(Engine,spec,grid,base){
  const {world,manifest,target,blocks}=base,p=G.apply(world,blocks,grid);
  const x=S.extract(Engine,p.world,manifest,{maxCells:64,maxDepth:16,maxTransitions:50000});
  const metric=B.measure(Engine,p.world,target,{maxDepth:16,maxTransitions:50000,influenceFloor:'1/8'});
  const game={R:x.R,C:x.C,endings:x.endings,row_policies:x.row_policies,column_policies:x.column_policies};
  return {game,readerTransitions:x.transitions+metric.transitions,metric,grid};
 }
 function setup(spec){const x=instance(spec);ok(B.auditWorld(x.world).admitted,'reader dialect');const blocks=G.blocks(x.world);ok(blocks.length>=4&&4**blocks.length>=64,'edit grid');return {...x,blocks}}
 function smoke(Engine){
  return smokeRoster.map(spec=>{
   const base=setup(spec),grid=Array(base.blocks.length).fill(1),v=extract(Engine,spec,grid,base);
   const shape=[v.game.R.length,v.game.R[0].length];
   ok(JSON.stringify(shape)===JSON.stringify(spec.family==='ternary_diamond'?[6,4]:[8,4]),'shape');
   ok(v.metric.dead_or_horizon==='0/1','smoke dead/horizon');
   return {spec,shape,blocks:base.blocks.length,transitions:v.readerTransitions};
  });
 }
 function stream(Engine,spec){
  ok(roster.some(x=>JSON.stringify(x)===JSON.stringify(spec)),'frozen roster only');
  const base=setup(spec),n=base.blocks.length,trajectories=[];
  for(const name of ['local_walk','random_global']){
   const rng=G.rng(spec.seed^(name==='local_walk'?481741:982531)),seen=new Set(),steps=[];
   let grid=Array(n).fill(1),readerTransitions=0;
   while(steps.length<64){
    const key=G.key(grid);ok(!seen.has(key),'duplicate');
    seen.add(key);const v=extract(Engine,spec,grid,base);readerTransitions+=v.readerTransitions;
    ok(v.metric.dead_or_horizon==='0/1','dead/horizon; stop frozen experiment');
    steps.push({key,game:v.game});
    if(steps.length===64)break;
    const ns=name==='local_walk'?G.neighbors(grid).filter(e=>!seen.has(e.key)):[];
    if(ns.length)grid=ns[rng(ns.length)].grid;
    else do{grid=Array.from({length:n},()=>rng(4))}while(seen.has(G.key(grid)));
   }
   trajectories.push({name,target:base.target,steps,readerTransitions});
  }
  return {spec,trajectories};
 }
 return {roster,smokeRoster,instance,smoke,stream};
}
export const {roster,smokeRoster,instance,smoke,stream}=prospective(B,S,G);
