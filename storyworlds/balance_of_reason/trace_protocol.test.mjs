import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {initial,current,choose} from './engine.mjs';
import {makeTrace,replayTrace,sourceFingerprint,TRACE_PROTOCOL} from './trace_protocol.mjs';

const source=JSON.parse(readFileSync(new URL('./source_cards.json',import.meta.url),'utf8'));

function clone(data){return JSON.parse(JSON.stringify(data));}

test('250 seeded playthroughs survive exact save/replay of national and faction state',()=>{
  const endings={};
  for(let n=0;n<250;n++){
    let seed=Math.imul(n+1,0x9e3779b1)>>>0;
    const game=initial(source);
    for(let turn=0;turn<110&&game.phase!=='end';turn++){
      seed=(Math.imul(seed,1664525)+1013904223)>>>0;
      const options=current(source,game).choices;
      choose(source,game,Math.floor(seed/4294967296*options.length));
    }
    const saved=clone(makeTrace(source,game));
    assert.equal(saved.protocol,TRACE_PROTOCOL);
    assert.equal(saved.source_fingerprint,sourceFingerprint(source));
    assert.equal(saved.actions.length,game.turns);
    const replayed=replayTrace(source,saved);
    assert.deepEqual(replayed.stats,game.stats);
    assert.deepEqual(replayed.factions,game.factions);
    assert.deepEqual(replayed.history,game.history);
    assert.equal(replayed.result,game.result);
    endings[replayed.result]=(endings[replayed.result]||0)+1;
  }
  assert.equal(Object.keys(endings).length,15,'every ending should be reproducible');
});

test('partially completed political campaigns resume from their exact active scene',()=>{
  const game=initial(source);
  for(let i=0;i<22;i++)choose(source,game,i%3);
  assert.notEqual(game.phase,'end');
  const snapshot=clone(makeTrace(source,game));
  const restored=replayTrace(source,snapshot);
  assert.deepEqual(current(source,restored),current(source,game));
  assert.deepEqual(restored.factions,game.factions);
  choose(source,restored,1);
  choose(source,game,1);
  assert.deepEqual(restored.history,game.history);
});

test('modified faction standings, hidden choices and edited source fail replay checks',()=>{
  const game=initial(source);
  for(let i=0;i<17;i++)choose(source,game,i%3);
  const saved=clone(makeTrace(source,game));
  const badFaction=clone(saved);
  badFaction.history[3].factions.char_nurjan+=.2;
  assert.throws(()=>replayTrace(source,badFaction),/history factions/);
  const badChoice=clone(saved);
  badChoice.actions[6].optionIndex=(badChoice.actions[6].optionIndex+1)%3;
  assert.throws(()=>replayTrace(source,badChoice),/choice text|history stats|outcome|history factions/);
  const editedSource=clone(source);
  editedSource.acts[0].events[0][1]+=' altered';
  assert.throws(()=>replayTrace(editedSource,saved),/source fingerprint/);
  const badTotal=clone(saved);
  badTotal.final_stats.P=.95;
  assert.throws(()=>replayTrace(source,badTotal),/final stats/);
  const missingHistory=clone(saved);
  missingHistory.history.pop();
  assert.throws(()=>replayTrace(source,missingHistory),/incomplete recorded decision history/);
});

test('trace imports enforce protocol, size, and decision index bounds',()=>{
  const game=initial(source);
  choose(source,game,0);
  const valid=makeTrace(source,game);
  assert.throws(()=>replayTrace(source,{...valid,protocol:'other'}),/protocol/);
  const oversized=clone(valid);
  oversized.actions=Array(121).fill(oversized.actions[0]);
  assert.throws(()=>replayTrace(source,oversized),/action count exceeds limit/);
  const invalidIndex=clone(valid);
  invalidIndex.actions[0].optionIndex=9999;
  assert.throws(()=>replayTrace(source,invalidIndex),/invalid choice/);
});
