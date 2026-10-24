import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import {ART,LOCATIONS,portraitSvg} from './visuals.mjs';
import {initial,current,choose} from './engine.mjs';
import {makeTrace,replayTrace} from './trace_protocol.mjs';

const dir=dirname(fileURLToPath(import.meta.url));
const source=JSON.parse(readFileSync(join(dir,'source_cards.json'),'utf8'));
const html=readFileSync(join(dir,'index.html'),'utf8');
const css=readFileSync(join(dir,'visuals.css'),'utf8');

test('art direction provides fallback assets for every scene type',()=>{
  for(const [name,paths] of Object.entries(ART)){
    assert.equal(paths.length,2);
    assert.ok(paths[0].endsWith('.webp'),'raster override expected for '+name);
    assert.ok(paths[1].endsWith('.svg'),'SVG fallback expected for '+name);
    assert.ok(existsSync(join(dir,paths[1])),'missing visual fallback for '+name);
  }
  assert.ok(css.includes('.intro-stage'));
  assert.ok(css.includes('@media(max-width:670px)'));
});

test('portraits cover the independent institutions and remain valid static SVG',()=>{
  for(const faction of source.factions){
    const svg=portraitSvg(faction.id);
    assert.ok(svg.startsWith('<svg ')&&svg.endsWith('</svg>'));
    assert.ok(svg.includes('shape-rendering="crispEdges"'));
    assert.ok(svg.includes('viewBox="0 0 40 48"'));
    assert.ok(!svg.includes('undefined'),'unknown portrait palette for '+faction.id);
  }
  assert.ok(portraitSvg('char_secretary').includes('stroke="#bfc4bc"'));
});

test('atlas nodes remain geographic and each exposes a campaign story',()=>{
  assert.ok(LOCATIONS.length>=10);
  const uniq=new Set();
  for(const node of LOCATIONS){
    assert.ok(node.x>0&&node.x<100&&node.y>0&&node.y<100,node.name);
    assert.ok(node.mission.length>25);
    assert.ok(source.metrics[node.metric]);
    assert.ok(!uniq.has(node.id));
    uniq.add(node.id);
  }
  for(const name of ['dakar','gaza','gulf','manila','xinjiang','samarkand'])
    assert.ok(uniq.has(name));
});

test('game player imports the production layer without altering campaign logic',()=>{
  for(const text of ['./visuals.css','mountVisualPlayer','visuals.sync()','visuals.hideIntro()','autosave-v1'])
    assert.ok(html.includes(text),'missing integration '+text);
  assert.ok(html.includes('dataset.uiModalOpen')&&html.includes('dataset.uiMenuOpen'));
  const baseline=initial(source);
  choose(source,baseline,0);
  const save=makeTrace(source,baseline);
  assert.deepEqual(replayTrace(source,save).stats,baseline.stats);
  assert.equal(current(source,baseline).year,2034);
});

test('scene backdrops are independent of strategic choice data',()=>{
  const b=readFileSync(join(dir,'visuals.mjs'),'utf8');
  assert.ok(!/import\s+.*engine\.mjs/.test(b));
  assert.ok(b.includes('The original engine.mjs is the sole owner'));
  assert.ok(b.includes('return "summit"')&&b.includes('return "crisis"'));
});
