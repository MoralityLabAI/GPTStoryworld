import {buildStoryworld} from './sweepweave_builder.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const source=JSON.parse(readFileSync(new URL('./source_cards.json',import.meta.url),'utf8'));
const world=buildStoryworld(source);

function evaluate(expression,state){
  if(expression===true||expression===false||typeof expression==='number')return expression;
  if(!expression)return 0;
  if(expression.pointer_type==='Bounded Number Constant')return expression.value;
  if(expression.pointer_type==='Bounded Number Pointer')
    return (state[expression.character+'.'+expression.keyring[0]]??0)*(expression.coefficient??1);
  const operands=(expression.operands||[]).map(v=>evaluate(v,state));
  switch(expression.operator_type){
    case 'Nudge':return Math.max(-1,Math.min(1,operands[0]+operands[1]));
    case 'Addition':return operands.reduce((a,b)=>a+b,0);
    case 'Multiplication':return operands.reduce((a,b)=>a*b,1);
    case 'And':return operands.every(Boolean);
    case 'Or':return operands.some(Boolean);
    case 'Arithmetic Comparator':{
      const [a,b]=operands;
      switch(expression.operator_subtype){
        case 'Greater Than':return a>b;
        case 'Less Than':return a<b;
        case 'Greater Than or Equal To':return a>=b;
        case 'Less Than or Equal To':return a<=b;
        default:throw Error('Unknown comparator '+expression.operator_subtype);
      }
    }
    default:throw Error('Unknown operator '+expression.operator_type);
  }
}

test('5,000 native Sweepweave paths reach all 15 endings with valid gates',()=>{
  const byId=new Map(world.encounters.map(e=>[e.id,e]));
  const counts={};let war=0,peace=0,total=0;
  for(let n=0;n<5000;n++){
    let seed=Math.imul(n+1,0x9e3779b1)>>>0;
    const state={};
    for(const actor of world.characters)
      for(const [key,v] of Object.entries(actor.bnumber_properties))
        state[actor.id+'.'+key]=v;
    let current='page_2034_01',steps=0;
    while(steps<120){
      const encounter=byId.get(current);
      assert.ok(encounter,'unknown encounter '+current);
      if(encounter.options.length===0){
        assert.equal(evaluate(encounter.acceptability_script,state),true,
          'invalid ending threshold '+current);
        counts[current]=(counts[current]||0)+1;break;
      }
      if(current.endsWith('_world_war'))war++;
      if(current.endsWith('_fragile_peace'))peace++;
      seed=(Math.imul(seed,1664525)+1013904223)>>>0;
      const option=encounter.options[Math.floor(seed/4294967296*encounter.options.length)];
      let choice=null,best=-Infinity;
      for(const reaction of option.reactions){
        const weight=evaluate(reaction.desirability_script,state);
        if(weight>best){best=weight;choice=reaction;}
      }
      assert.ok(choice,'reaction missing '+current);
      for(const effect of choice.after_effects){
        const key=effect.Set.character+'.'+effect.Set.keyring[0];
        state[key]=evaluate(effect.to,state);
        assert.ok(state[key]>=-1&&state[key]<=1,'out of bounds '+key);
      }
      current=choice.consequence_id;steps++;
    }
    assert.ok(steps<120,'native run timed out');
    total+=steps;
  }
  assert.equal(Object.values(counts).reduce((a,b)=>a+b,0),5000);
  for(const ending of source.endings)
    assert.ok((counts['page_end_'+ending[0]]||0)>=10,
      'unreachable native ending '+ending[0]);
  assert.ok(Math.max(...Object.values(counts))<=1500,'dominant ending above 30%');
  assert.ok(war>1000&&peace>1000,'missing world-war or peace branch');
  console.log('native ending counts',counts,'war',war,'peace',peace,'mean length',total/5000);
});

test('Sweepweave institutional countermove can cooperate or resist under the same player choice',()=>{
  const council=world.encounters.find(e=>e.id==='page_2034_countermove');
  assert.ok(council);
  assert.equal(council.options.length,3);
  const result=council.options[0].reactions;
  assert.equal(result.length,2);
  const select=standing=>{
    const state={'char_veteran.Coalition_Standing':standing};
    return result.slice().sort((a,b)=>
      evaluate(b.desirability_script,state)-evaluate(a.desirability_script,state))[0];
  };
  const cooperating=select(.6),resisting=select(-.6);
  assert.notEqual(cooperating.id,resisting.id,'independent faction agency must change the outcome');
  assert.ok(cooperating.id.includes('cooperate'));
  assert.ok(resisting.id.includes('resist'));
  const standingEffects=cooperating.after_effects.filter(e=>e.Set.keyring[0]==='Coalition_Standing');
  assert.ok(standingEffects.length>0,'player policy must alter institutional standing');
});
