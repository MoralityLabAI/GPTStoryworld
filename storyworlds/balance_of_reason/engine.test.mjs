import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {initial,current,choose,autoplay,scoreEndings,validateSource} from './engine.mjs';
import {buildStoryworld} from './sweepweave_builder.mjs';
const source=JSON.parse(readFileSync(new URL('./source_cards.json',import.meta.url),'utf8'));
const world=buildStoryworld(source);
test('eight acts, 56 authored policy scenes, fifteen endings',()=>{
 assert.equal(validateSource(source),true);
 assert.equal(source.acts.length,8);
 assert.equal(source.acts.reduce((sum,a)=>sum+a.events.length,0),56);
 assert.equal(source.endings.length,15);
 assert.equal(source.version,3);
 assert.equal(source.factions.length,11);
 assert.ok(source.acts.every(a=>a.countermove?.options.length===3));
 assert.ok(source.acts.every(a=>a.events.length===7));
 assert.equal(source.acts.filter(a=>a.conflict).length,4);
});
test('compiled Sweepweave graph is closed and production-shaped',()=>{
 assert.equal(world.encounters.length,113);
 assert.equal(world.encounters.reduce((n,e)=>n+e.options.length,0),285);
 assert.equal(world.encounters.reduce((n,e)=>n+e.options.reduce((r,o)=>r+o.reactions.length,0),0),596);
 assert.equal(world.spools.length,10);
 assert.equal(world.encounters.filter(e=>e.id.endsWith("_countermove")).length,8);
 assert.ok(world.spools[0].starts_active);
 const ids=new Set(world.encounters.map(e=>e.id));
 assert.equal(ids.size,world.encounters.length);
 const endIds=new Set(world.encounters.filter(e=>e.id.startsWith('page_end_')).map(e=>e.id));
 assert.equal(endIds.size,15);
 for(const spool of world.spools){
   assert.ok(spool.encounters.length>0);
   for(const id of spool.encounters)assert.ok(ids.has(id),'invalid spool target '+id);
 }
 for(const e of world.encounters){
   assert.ok(e.acceptability_script!==undefined);
   assert.ok(e.desirability_script!==undefined);
   if(!endIds.has(e.id))assert.ok(e.options.length>=2,'inert '+e.id);
   for(const option of e.options){
     assert.ok(option.visibility_script!==undefined);
     assert.ok(option.performability_script!==undefined);
     assert.ok(option.reactions.length>=2);
     for(const reaction of option.reactions){
       assert.ok(ids.has(reaction.consequence_id),'dangling '+reaction.consequence_id);
       assert.ok(reaction.after_effects.length>=3,'few effects '+reaction.id);
       assert.ok(reaction.desirability_script);
     }
   }
 }
});
test('pure native compilation is reproducible from authored source',()=>{
 assert.deepEqual(world,buildStoryworld(source));
 assert.equal(JSON.stringify(world),JSON.stringify(buildStoryworld(source)));
});
test('all policies are selectable and values stay bounded',()=>{
 for(let strategy=0;strategy<3;strategy++){
   const st=autoplay(source,(scene)=>Math.min(strategy,scene.choices.length-1));
   assert.equal(st.phase,'end');
   assert.ok(source.endings.some(x=>x[0]===st.result));
   for(const value of Object.values(st.stats))assert.ok(value<=1&&value>=-1);
   for(const value of Object.values(st.factions))assert.ok(value<=1&&value>=-1);
   assert.ok(st.turns<=95);
 }
});
test('5,000 seeded playthroughs cover fifteen endings without dead ends',()=>{
 const outcomes={};
 for(let n=0;n<5000;n++){
   let seed=Math.imul(n+1,0x9e3779b1)>>>0;
   const out=autoplay(source,(scene)=>{
     seed=(Math.imul(seed,1664525)+1013904223)>>>0;
     return Math.floor((seed/4294967296)*scene.choices.length);
   },105);
   outcomes[out.result]=(outcomes[out.result]||0)+1;
   assert.ok(out.turns<=95,'unexpected loop');
   if(out.result!=='global_fire')assert.ok(scoreEndings(source,out)[0].eligible,'selected an ineligible ending');
   for(const value of Object.values(out.stats)) assert.ok(value<=1&&value>=-1);
   for(const value of Object.values(out.factions))assert.ok(value<=1&&value>=-1);
 }
 for(const ending of source.endings)assert.ok((outcomes[ending[0]]||0)>=10,'rare or unreachable '+ending[0]);
 assert.ok(Math.max(...Object.values(outcomes))<=1500,'ending dominance >30%');
 console.log('Ending distribution:',outcomes);
});

test('AI-driven world war and negotiated peace are separate playable campaign paths',()=>{
 const war=initial(source);
 war.yearIndex=4;war.phase='crisis';war.stats.G=.4;
 choose(source,war,2);
 assert.equal(war.phase,'war');
 assert.equal(current(source,war).title,source.acts[4].conflict.war[0]);
 choose(source,war,0);
 assert.equal(war.yearIndex,5);
 assert.equal(war.warEpisodes,1);
 const peace=initial(source);
 peace.yearIndex=4;peace.phase='crisis';peace.stats.C=.4;
 choose(source,peace,2);
 assert.equal(peace.phase,'peace');
 choose(source,peace,0);
 assert.equal(peace.peaceEpisodes,1);
 const falseCeasefire=initial(source);
 falseCeasefire.yearIndex=4;falseCeasefire.sceneIndex=6;
 choose(source,falseCeasefire,1);
 assert.ok(falseCeasefire.stats.G>.30);
 assert.ok(falseCeasefire.stats.C<-.2);
});

test('independent constituencies accumulate contrasting policy preferences',()=>{
 const civic=initial(source),coercive=initial(source);
 civic.sceneIndex=1;coercive.sceneIndex=1;
 choose(source,civic,0);
 choose(source,coercive,1);
 assert.ok(civic.factions.char_veteran>coercive.factions.char_veteran,
   'constitutional liberty should retain unconverted Party support');
 assert.ok(civic.factions.char_nurjan>coercive.factions.char_nurjan,
   'religious councils should respond to civil liberties');

 const agree=initial(source),resist=initial(source);
 agree.phase='countermove';resist.phase='countermove';
 agree.factions.char_veteran=.55;resist.factions.char_veteran=-.55;
 choose(source,agree,0);choose(source,resist,0);
 assert.equal(agree.phase,'crisis');
 assert.equal(resist.phase,'crisis');
 assert.ok(agree.stats.F<resist.stats.F,
   'independent resistance must change constitutional stability');
 assert.notEqual(agree.history.at(-1).outcome,resist.history.at(-1).outcome);
});
