import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {initial,current,choose} from './engine.mjs';
import {encodeCampaign,decodeCampaign,makeCampaignUrl,campaignTokenFromHash} from './share_route.mjs';

const source=JSON.parse(readFileSync(new URL('./source_cards.json',import.meta.url),'utf8'));
const clone=data=>JSON.parse(JSON.stringify(data));

test('empty campaigns have a canonical, portable playtest link',()=>{
  const state=initial(source);
  const token=encodeCampaign(source,state);
  assert.ok(token.length<100);
  const url=makeCampaignUrl('https://moralitylabai.github.io/GPTStoryworld/?visitor=test#old',source,state);
  assert.ok(url.startsWith('https://moralitylabai.github.io/GPTStoryworld/?visitor=test#campaign='));
  assert.equal(campaignTokenFromHash(new URL(url).hash),token);
  assert.equal(decodeCampaign(source,token).turns,0);
  assert.equal(campaignTokenFromHash('#gallery'),null);
});

test('300 seeded policies replay identically from short URLs, including every end state',()=>{
  const endings=new Set();
  for(let n=0;n<300;n++){
    let seed=Math.imul(n+1,0x9e3779b1)>>>0;
    const game=initial(source);
    for(let step=0;step<112&&game.phase!=='end';step++){
      seed=(Math.imul(seed,1664525)+1013904223)>>>0;
      const options=current(source,game).choices;
      choose(source,game,Math.floor(seed/4294967296*options.length));
      if(step%15===0 || game.phase==='end'){
        const token=encodeCampaign(source,game);
        assert.ok(token.length<=75);
        const fromUrl=campaignTokenFromHash(new URL(makeCampaignUrl('https://host.test/GPTStoryworld/',source,game)).hash);
        const restored=decodeCampaign(source,fromUrl);
        assert.deepEqual(restored.stats,game.stats);
        assert.deepEqual(restored.factions,game.factions);
        assert.deepEqual(restored.history,game.history);
        assert.equal(restored.result,game.result);
      }
    }
    endings.add(game.result);
  }
  assert.equal(endings.size,15);
});

test('malformed, edited, expired, and excessive routes are rejected',()=>{
  const game=initial(source);
  for(let n=0;n<15;n++)choose(source,game,n%3);
  const token=encodeCampaign(source,game);
  const badSignature=token.slice(0,-1)+(token.endsWith('f')?'e':'f');
  assert.throws(()=>decodeCampaign(source,badSignature),/checksum mismatch/);
  const edited=clone(source);
  edited.acts[0].events[0][1]+=' new edition';
  assert.throws(()=>decodeCampaign(edited,token),/different storyworld version/);
  assert.throws(()=>decodeCampaign(source,'bor1.'+'a'.repeat(600)),/too long/);
  assert.throws(()=>decodeCampaign(source,token.replace(/\.f/,'.!')),/invalid link format/);
  assert.throws(()=>campaignTokenFromHash('#campaign='+'a'.repeat(151)),/too long/);
});

test('a shared route contains only action indices and a source fingerprint',()=>{
  const game=initial(source);
  for(let n=0;n<6;n++)choose(source,game,1);
  const token=encodeCampaign(source,game);
  assert.match(token,/^bor1\.[a-f0-9]{8}\.[0-9a-z]{1,2}\.[A-Za-z0-9_-]+\.[a-f0-9]{8}$/);
  assert.ok(!token.includes('Lin Wenqi'));
  assert.ok(!token.includes('source_cards'));
  assert.ok(!token.includes('char_nurjan'));
});
