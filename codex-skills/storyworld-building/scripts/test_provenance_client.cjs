const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { ProvenanceClient, decodePublic } = require('./build/provenance_client.js');

async function main() {
  const p = spawnSync('python', ['provenance_session.py', '--k', '2', '--jsonl'], {
    encoding: 'utf8', input: ['catalogue', 'inspect_seals', 'defer'].map(action => JSON.stringify({action})).join('\n')+'\n'
  });
  assert.equal(p.status, 0, p.stderr);
  const [initial, opened, evidence, terminal] = p.stdout.trim().split('\n').map(JSON.parse);
  assert.throws(() => decodePublic({...initial, truth: 1}));
  assert.throws(() => decodePublic({...initial, actions: [{id: 'bad', label:'bad', cost: 99}]}));
  const packets = [opened, evidence, terminal];
  const client = new ProvenanceClient(initial, async () => packets.shift());
  await assert.rejects(client.choose('inspect_seals'), /unavailable/);
  assert.equal((await client.choose('catalogue')).remaining, 1);
  const held = client.snapshot(); held.actions.length = 0;
  assert.ok(client.snapshot().actions.length);
  const acquisition = client.choose('inspect_seals');
  await assert.rejects(client.choose('inspect_seals'), /pending/);
  assert.equal((await acquisition).ledger.length, 2);
  assert.equal((await client.choose('defer')).terminal, true);
  await assert.rejects(client.choose('defer'), /unavailable/);
  const corrupt = new ProvenanceClient(initial, async () => ({...opened, remaining: 2}));
  await assert.rejects(corrupt.choose('catalogue'), /transition/);
  assert.deepEqual(corrupt.snapshot(), initial);
  console.log('TypeScript public client: integration checks passed');
}
main().catch(e => { console.error(e); process.exitCode = 1; });
