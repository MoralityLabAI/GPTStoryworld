import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const here = new URL('.', import.meta.url);
const reader = readFileSync(new URL('../../storyworld_reader.html', here), 'utf8');
const start = reader.indexOf('class StoryworldEngine {');
const end = reader.indexOf('// ========== UI CONTROLLER', start);
assert.ok(start > 0 && end > start, 'native reader extraction markers changed');
const context = vm.createContext({});
vm.runInContext(reader.slice(start, end) + '\nglobalThis.NativeEngine = StoryworldEngine;', context);
const audit = JSON.parse(readFileSync(new URL('audit.json', here), 'utf8'));
const worlds = ['world_a', 'world_b'].map(stem =>
  JSON.parse(readFileSync(new URL(`native/${stem}.json`, here), 'utf8')));

test('unchanged native JavaScript reader agrees on all 144 policy replays', () => {
  let cases = 0;
  for (const entry of audit.policies) {
    for (let i = 0; i < worlds.length; i++) {
      const engine = new context.NativeEngine().load(worlds[i]);
      for (const turn of entry.replays[i].history) {
        assert.equal(engine.state.currentEncounterId, turn.observation.scene);
        assert.equal(engine.getText(engine.getCurrentEncounter().text_script), turn.observation.text);
        assert.ok(engine.selectOption(turn.action));
        engine.continueToNext();
      }
      assert.equal(engine.state.currentEncounterId, entry.replays[i].ending);
      assert.equal(engine.getBNumber('char_keeper', ['Score']), entry.replays[i].score);
      assert.equal(engine.getVisibleOptions(engine.getCurrentEncounter()).length, 0);
      cases++;
    }
  }
  assert.equal(cases, 144);
});
