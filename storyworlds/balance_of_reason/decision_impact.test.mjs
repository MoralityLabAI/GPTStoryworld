import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {initial,current,choose} from './engine.mjs';
import {latestDecisionImpact,METRIC_LABELS} from './decision_impact.mjs';
import {makeTrace,replayTrace} from './trace_protocol.mjs';

const source=JSON.parse(readFileSync(new URL('./source_cards.json',import.meta.url),'utf8'));

test('the first policy reports actual metric and faction changes',()=>{
 const game=initial(source);
 assert.equal(latestDecisionImpact(source,game),null);
 choose(source,game,0);
 const impact=latestDecisionImpact(source,game);
 assert.equal(impact.turn,1);
 assert.equal(impact.year,2034);
 assert.equal(impact.choice,game.history[0].choice);
 assert.ok(impact.national.length>=3);
 assert.ok(impact.coalitions.length>=2);
 for(const row of impact.national){
   const actual=game.stats[row.id];
   assert.ok(Math.abs(row.delta-actual)<=1e-10,'incorrect national delta '+row.id);
   assert.equal(row.name,METRIC_LABELS[row.id]);
 }
 for(const row of impact.coalitions){
   const previous=source.factions.find(f=>f.id===row.id).initial;
   assert.ok(Math.abs(row.delta-(game.factions[row.id]-previous))<=1e-10,'incorrect faction delta '+row.id);
 }
});

test('all paths report changes relative to the previous decision, not campaign start',()=>{
 const game=initial(source);
 for(let i=0;i<35;i++){
   if(game.phase==='end')break;
   choose(source,game,i%3);
   const impact=latestDecisionImpact(source,game);
   const prior=game.history.at(-2);
   for(const row of impact.national){
     assert.ok(Math.abs(row.delta-(game.stats[row.id]-(prior?.stats[row.id]??0)))<=1e-10);
   }
   for(const row of impact.coalitions){
     const baseline=prior?.factions[row.id]??source.factions.find(f=>f.id===row.id).initial;
     assert.ok(Math.abs(row.delta-(game.factions[row.id]-baseline))<=1e-10);
   }
 }
});

test('save and replay preserve the same player-facing consequences',()=>{
 const original=initial(source);
 for(let i=0;i<31;i++)choose(source,original,(i+2)%3);
 const copy=JSON.parse(JSON.stringify(makeTrace(source,original)));
 const replayed=replayTrace(source,copy);
 assert.deepEqual(latestDecisionImpact(source,replayed),latestDecisionImpact(source,original));
 const impact=latestDecisionImpact(source,replayed,{national:3,coalitions:2});
 assert.ok(impact.national.length<=3);
 assert.ok(impact.coalitions.length<=2);
});

test('risks improving or worsening receive the correct orientation',()=>{
 const game=initial(source);
 choose(source,game,1);
 const impact=latestDecisionImpact(source,game);
 for(const item of impact.national){
   const risk=['B','M','F','G','H'].includes(item.id);
   assert.equal(item.improvement,risk?item.delta<0:item.delta>0);
 }
});
