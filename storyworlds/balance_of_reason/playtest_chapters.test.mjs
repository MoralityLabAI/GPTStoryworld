import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {current,choose} from './engine.mjs';
import {PLAYTEST_CHAPTERS,loadPlaytestChapter} from './playtest_chapters.mjs';
import {encodeCampaign,decodeCampaign} from './share_route.mjs';
import {makeTrace,replayTrace} from './trace_protocol.mjs';

const source=JSON.parse(readFileSync(new URL('./source_cards.json',import.meta.url),'utf8'));

test('three mid-campaign previews replay real history into the expected authored scenes',()=>{
 assert.equal(PLAYTEST_CHAPTERS.length,3);
 const ids=new Set();
 for(const chapter of PLAYTEST_CHAPTERS){
   assert.ok(!ids.has(chapter.id));ids.add(chapter.id);
   const state=loadPlaytestChapter(source,chapter.id);
   assert.equal(state.phase,'event');
   assert.equal(current(source,state).title,chapter.title);
   assert.equal(current(source,state).year,chapter.year);
   assert.ok(state.turns>=40);
   assert.equal(encodeCampaign(source,state),chapter.token);
   assert.deepEqual(decodeCampaign(source,chapter.token).history,state.history);
   assert.deepEqual(replayTrace(source,makeTrace(source,state)).factions,state.factions);
 }
});

test('chapter previews preserve the ability to continue play and share progress',()=>{
 for(const chapter of PLAYTEST_CHAPTERS){
   const game=loadPlaytestChapter(source,chapter.id);
   const turns=game.turns;
   choose(source,game,0);
   assert.equal(game.turns,turns+1);
   const encoded=encodeCampaign(source,game);
   const restored=decodeCampaign(source,encoded);
   assert.equal(restored.turns,turns+1);
   assert.deepEqual(restored.stats,game.stats);
   assert.deepEqual(restored.factions,game.factions);
 }
});

test('chapter presets reject foreign editions and unknown identifiers',()=>{
 assert.throws(()=>loadPlaytestChapter(source,'invalid'),/Unknown playtest chapter/);
 const edited=JSON.parse(JSON.stringify(source));
 edited.acts[0].events[0][1]+=' New edition.';
 assert.throws(()=>loadPlaytestChapter(edited,PLAYTEST_CHAPTERS[0].id),/different storyworld version/);
});
