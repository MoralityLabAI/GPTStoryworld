// Deterministic, version-pinned save/replay for Balance of Reason.
// Checks structure and gameplay consistency. The checksum is a compatibility
// fingerprint, not a cryptographic signature or evidence of authenticity.
import {initial,current,choose} from './engine.mjs';

export const TRACE_PROTOCOL='balance-of-reason/decision-trace/v1';
const MAX_ACTIONS=120;
const EPSILON=1e-8;

export function sourceFingerprint(source){
  const content=JSON.stringify(source);
  let hash=2166136261;
  for(let i=0;i<content.length;i++){
    hash^=content.charCodeAt(i);
    hash=Math.imul(hash,16777619)>>>0;
  }
  return hash.toString(16).padStart(8,'0');
}

function fail(message){throw Error('Trace validation: '+message);}
function closeNumbers(expected,actual,label){
  if(!actual||typeof actual!=='object'||Array.isArray(actual))
    fail('missing '+label);
  const left=Object.keys(expected).sort(),right=Object.keys(actual).sort();
  if(left.join('|')!==right.join('|'))fail('unexpected '+label+' keys');
  for(const key of left){
    const a=actual[key],e=expected[key];
    if(typeof a!=='number'||!Number.isFinite(a)||Math.abs(e-a)>EPSILON)
      fail(label+'.'+key+' differs');
  }
}
function same(expected,actual,label){
  if(expected!==actual)fail(label+' differs');
}
function compactAction(step){
  return {
    turn:step.turn,year:step.year,phase:step.phase,title:step.title,
    optionIndex:step.optionIndex,choice:step.choice
  };
}
export function makeTrace(source,game){
  if(!source||!game||!Array.isArray(game.history))fail('missing source or gameplay history');
  if(game.history.length>MAX_ACTIONS)fail('too many gameplay actions');
  if(game.history.some(step=>!Number.isInteger(step.optionIndex)||step.optionIndex<0))
    fail('current game has unindexed legacy history; start a new game');
  return {
    protocol:TRACE_PROTOCOL,
    source_version:source.version,
    source_fingerprint:sourceFingerprint(source),
    title:source.title,
    phase:game.phase,
    result:game.result,
    war_episodes:game.warEpisodes,
    peace_episodes:game.peaceEpisodes,
    turn_count:game.turns,
    final_stats:{...game.stats},
    final_factions:{...game.factions},
    actions:game.history.map(compactAction),
    history:game.history.map(step=>({
      ...compactAction(step),outcome:step.outcome,
      stats:{...step.stats},factions:{...step.factions}
    }))
  };
}
export function replayTrace(source,trace){
  if(!trace||typeof trace!=='object'||Array.isArray(trace))fail('root must be an object');
  same(TRACE_PROTOCOL,trace.protocol,'protocol');
  same(source.version,trace.source_version,'source version');
  same(source.title,trace.title,'storyworld title');
  same(sourceFingerprint(source),trace.source_fingerprint,'source fingerprint');
  if(!Array.isArray(trace.actions)||trace.actions.length>MAX_ACTIONS)fail('action count exceeds limit');
  if(!Array.isArray(trace.history)||trace.history.length!==trace.actions.length)
    fail('incomplete recorded decision history');
  if(!Number.isInteger(trace.turn_count)||trace.turn_count!==trace.actions.length)
    fail('invalid turn count');
  const game=initial(source);
  for(let i=0;i<trace.actions.length;i++){
    const record=trace.actions[i],saved=trace.history[i],scene=current(source,game);
    if(!record||typeof record!=='object'||!Number.isInteger(record.optionIndex)||
      record.optionIndex<0||record.optionIndex>=scene.choices.length)fail('invalid choice at turn '+(i+1));
    same(i+1,record.turn,'turn number at '+(i+1));
    same(scene.year,record.year,'year at turn '+(i+1));
    same(game.phase,record.phase,'phase at turn '+(i+1));
    same(scene.title,record.title,'encounter title at turn '+(i+1));
    same(scene.choices[record.optionIndex][0],record.choice,'choice text at turn '+(i+1));
    choose(source,game,record.optionIndex);
    const actual=game.history[i];
    for(const field of ['turn','year','phase','title','optionIndex','choice','outcome'])
      same(actual[field],saved[field],field+' at turn '+(i+1));
    closeNumbers(actual.stats,saved.stats,'history stats at turn '+(i+1));
    closeNumbers(actual.factions,saved.factions,'history factions at turn '+(i+1));
  }
  same(game.turns,trace.turn_count,'final turn');
  same(game.phase,trace.phase,'final phase');
  same(game.result,trace.result,'final result');
  same(game.warEpisodes,trace.war_episodes,'war episodes');
  same(game.peaceEpisodes,trace.peace_episodes,'peace episodes');
  closeNumbers(game.stats,trace.final_stats,'final stats');
  closeNumbers(game.factions,trace.final_factions,'final factions');
  return game;
}
