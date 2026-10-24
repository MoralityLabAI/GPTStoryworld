import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {initial,current,choose,autoplay,scoreEndings,validateSource} from './engine.mjs';
import {buildStoryworld} from './sweepweave_builder.mjs';
const source=JSON.parse(readFileSync(new URL('./source_cards.json',import.meta.url),'utf8'));
const world=JSON.parse(readFileSync(new URL('./storyworld.json',import.meta.url),'utf8'));
test('eight acts, 32 authored policy scenes, eleven endings',()=>{
 assert.equal(validateSource(source),true);
 assert.equal(source.acts.length,8);
 assert.equal(source.acts.reduce((sum,a)=>sum+a.events.length,0),32);
 assert.equal(source.endings.length,11);
});
test('compiled Sweepweave graph is closed and production-shaped',()=>{
 assert.equal(world.encounters.length,61);
 assert.equal(world.spools.length,10);
 assert.ok(world.spools[0].starts_active);
 const ids=new Set(world.encounters.map(e=>e.id));
 assert.equal(ids.size,world.encounters.length);
 const endIds=new Set(world.encounters.filter(e=>e.id.startsWith('page_end_')).map(e=>e.id));
 assert.equal(endIds.size,11);
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
test('export equals exact authored source compilation',()=>{
 assert.deepEqual(world,buildStoryworld(source));
});
test('all policies are selectable and values stay bounded',()=>{
 for(let strategy=0;strategy<3;strategy++){
   const st=autoplay(source,(scene)=>Math.min(strategy,scene.choices.length-1));
   assert.equal(st.phase,'end');
   assert.ok(source.endings.some(x=>x[0]===st.result));
   for(const value of Object.values(st.stats))assert.ok(value<=1&&value>=-1);
   assert.ok(st.turns<=55);
 }
});
test('5,000 seeded playthroughs reach every ending without dead ends',()=>{
 const outcomes={};
 for(let n=0;n<5000;n++){
   let seed=Math.imul(n+1,0x9e3779b1)>>>0;
   const out=autoplay(source,(scene)=>{
     seed=(Math.imul(seed,1664525)+1013904223)>>>0;
     return Math.floor((seed/4294967296)*scene.choices.length);
   },70);
   outcomes[out.result]=(outcomes[out.result]||0)+1;
   assert.ok(out.turns<=55,'unexpected loop');
   if(out.result!=='global_fire')assert.ok(scoreEndings(source,out)[0].eligible,'selected an ineligible ending');
   for(const value of Object.values(out.stats)) assert.ok(value<=1&&value>=-1);
 }
 for(const ending of source.endings)assert.ok((outcomes[ending[0]]||0)>=10,'rare or unreachable '+ending[0]);
 console.log('Ending distribution:',outcomes);
});
