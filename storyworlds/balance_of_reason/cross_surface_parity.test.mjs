import {buildStoryworld} from './sweepweave_builder.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {initial,current,choose} from './engine.mjs';

const source=JSON.parse(readFileSync(new URL('./source_cards.json',import.meta.url),'utf8'));
const native=buildStoryworld(source);
const byId=new Map(native.encounters.map(e=>[e.id,e]));

function evalScript(expr,state){
  if(typeof expr==='number'||typeof expr==='boolean')return expr;
  if(!expr)return 0;
  if(expr.pointer_type==='Bounded Number Constant')return expr.value;
  if(expr.pointer_type==='Bounded Number Pointer')
    return (state[expr.character+'.'+expr.keyring[0]]??0)*(expr.coefficient??1);
  const ops=(expr.operands||[]).map(x=>evalScript(x,state));
  switch(expr.operator_type){
    case 'Nudge':return Math.max(-1,Math.min(1,ops[0]+ops[1]));
    case 'Addition':return ops.reduce((a,b)=>a+b,0);
    case 'Multiplication':return ops.reduce((a,b)=>a*b,1);
    case 'And':return ops.every(Boolean);
    case 'Or':return ops.some(Boolean);
    case 'Arithmetic Comparator':switch(expr.operator_subtype){
      case 'Greater Than or Equal To':return ops[0]>=ops[1];
      case 'Less Than or Equal To':return ops[0]<=ops[1];
      case 'Greater Than':return ops[0]>ops[1];
      case 'Less Than':return ops[0]<ops[1];
      default:throw Error('Unknown comparator: '+expr.operator_subtype);
    }
    default:throw Error('Unknown operator: '+expr.operator_type);
  }
}
function nativeStep(id,state,index){
  const page=byId.get(id);
  assert.ok(page,'unknown native encounter '+id);
  assert.ok(page.options[index],'missing native choice '+id+' option '+index);
  const option=page.options[index];
  let best=-Infinity,reaction=null;
  for(const rxn of option.reactions){
    const weight=evalScript(rxn.desirability_script,state);
    if(weight>best){best=weight;reaction=rxn;}
  }
  assert.ok(reaction,'missing native reaction '+id);
  for(const effect of reaction.after_effects){
    const key=effect.Set.character+'.'+effect.Set.keyring[0];
    state[key]=evalScript(effect.to,state);
  }
  return reaction.consequence_id;
}
function nextExpected(game){
  const year=source.acts[game.yearIndex].year;
  const phases={
    event:()=> 'page_'+year+'_0'+(game.sceneIndex+1),
    countermove:()=> 'page_'+year+'_countermove',
    crisis:()=> 'page_'+year+'_crisis',
    standoff:()=> 'page_'+year+'_standoff',
    war:()=> 'page_'+year+'_world_war',
    peace:()=> 'page_'+year+'_fragile_peace',
    final:()=> 'page_final_council',
    end:()=> 'page_end_'+game.result
  };
  assert.ok(phases[game.phase],'unknown browser phase '+game.phase);
  return phases[game.phase]();
}
const isAuto=id=>id==='page_ending_gate'||id.endsWith('_war_check')||id.endsWith('_war_outcome');

test('browser and Sweepweave share the same deterministic state transitions under 300 policy traces',()=>{
  let completed=0,gatewayEvents=0,yearlyCountermoves=0,terminalPaths=0;
  for(let trial=0;trial<300;trial++){
    const game=initial(source),state={};
    for(const actor of native.characters)
      for(const [key,value] of Object.entries(actor.bnumber_properties))
        state[actor.id+'.'+key]=value;
    let id='page_2034_01',seed=Math.imul(trial+1,0x9e3779b1)>>>0;
    for(let turn=0;turn<125;turn++){
      while(isAuto(id)){
        id=nativeStep(id,state,0);
        gatewayEvents++;
      }
      assert.equal(id,nextExpected(game),'different scene at trace '+trial+' turn '+turn);
      if(game.phase==='end'){
        const terminal=byId.get(id);
        assert.equal(terminal.options.length,0);
        assert.equal(evalScript(terminal.acceptability_script,state),true);
        completed++;terminalPaths++;
        break;
      }
      seed=(Math.imul(seed,1664525)+1013904223)>>>0;
      const options=current(source,game).choices;
      const index=Math.floor((seed/4294967296)*options.length);
      const oldPhase=game.phase;
      id=nativeStep(id,state,index);
      choose(source,game,index);
      if(oldPhase==='countermove')yearlyCountermoves++;
      for(const [shortName,longName] of Object.entries(source.metrics)){
        const actual=state['char_secretary.'+longName],expected=game.stats[shortName];
        assert.ok(Math.abs(actual-expected)<=.0003,
          'divergent metric '+shortName+' trace '+trial+' turn '+turn+': '+actual+' vs '+expected);
      }
      for(const faction of source.factions){
        const actual=state[faction.id+'.Coalition_Standing'],expected=game.factions[faction.id];
        assert.ok(Math.abs(actual-expected)<=.0003,
          'divergent faction '+faction.id+' trace '+trial+' turn '+turn+': '+actual+' vs '+expected);
      }
    }
  }
  assert.equal(completed,300,'incomplete parity traces');
  assert.ok(gatewayEvents>100,'expected native internal war/peace routing');
  assert.ok(yearlyCountermoves>1500,'council counterplay absent');
  assert.ok(terminalPaths===300);
});
