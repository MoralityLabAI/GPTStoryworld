// Share a Balance of Reason campaign as a short, source-pinned URL fragment.
// Only policy option indices are shared. No comments, names, or local storage.
import {initial,current,choose} from './engine.mjs';
import {sourceFingerprint} from './trace_protocol.mjs';

export const SHARE_PREFIX='bor1';
const ALPHABET='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
const MAX_CHOICES=120;

function hash(text){
  let h=2166136261;
  for(let i=0;i<text.length;i++){
    h^=text.charCodeAt(i);
    h=Math.imul(h,16777619)>>>0;
  }
  return h.toString(16).padStart(8,'0');
}
function assert(condition,message){
  if(!condition)throw Error('Campaign link: '+message);
}
function pack(indices){
  let result='';
  for(let i=0;i<indices.length;i+=3){
    result+=ALPHABET[(indices[i]<<4)|((indices[i+1]??0)<<2)|(indices[i+2]??0)];
  }
  return result||'_';
}
function unpack(data,count){
  const choices=[];
  for(const char of data){
    const v=ALPHABET.indexOf(char);
    assert(v>=0,'invalid encoded character');
    choices.push((v>>4)&3,(v>>2)&3,v&3);
  }
  assert(choices.slice(count).every(x=>x===0),'invalid padding');
  const out=choices.slice(0,count);
  assert(out.every(x=>x<=2),'invalid policy index');
  return out;
}
export function encodeCampaign(source,game){
  assert(source&&game&&Array.isArray(game.history),'missing campaign');
  assert(game.history.length<=MAX_CHOICES,'campaign exceeds share limit');
  const choices=game.history.map(step=>step.optionIndex);
  assert(choices.every(x=>Number.isInteger(x)&&x>=0&&x<=2),'unindexed or invalid policy history');
  const prefix=[SHARE_PREFIX,sourceFingerprint(source),choices.length.toString(36),pack(choices)].join('.');
  return prefix+'.'+hash(prefix);
}
export function decodeCampaign(source,token){
  assert(typeof token==='string'&&token.length<=150,'link is too long');
  const match=/^(bor1)\.([a-f0-9]{8})\.([0-9a-z]{1,2})\.([A-Za-z0-9_-]{1,40})\.([a-f0-9]{8})$/.exec(token);
  assert(match,'invalid link format');
  const count=parseInt(match[3],36);
  assert(Number.isInteger(count)&&count<=MAX_CHOICES,'too many policy decisions');
  assert(match[2]===sourceFingerprint(source),'different storyworld version');
  assert(hash(match.slice(1,5).join('.'))===match[5],'link checksum mismatch');
  const steps=unpack(match[4],count);
  assert(match[4]===pack(steps),'noncanonical policy encoding');
  const game=initial(source);
  for(const optionIndex of steps){
    assert(game.phase!=='end','extra decisions after the game ending');
    const choices=current(source,game).choices;
    assert(optionIndex<choices.length,'choice does not exist');
    choose(source,game,optionIndex);
  }
  return game;
}
export function makeCampaignUrl(href,source,game){
  const url=new URL(href);
  url.hash='campaign='+encodeCampaign(source,game);
  return url.toString();
}
export function campaignTokenFromHash(hashValue){
  if(typeof hashValue!=='string'||!hashValue.startsWith('#campaign='))return null;
  const raw=hashValue.slice(10);
  assert(raw.length<=150,'link is too long');
  return raw;
}
