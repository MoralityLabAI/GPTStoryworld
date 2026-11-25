/** Public session adapter for an editor/player. No private sidecar or grading API. */
export type Evidence = { query: string; outcome: string; text: string };
export type Choice = { id: string; label: string; cost: number };
export type PublicState = {
  schema: 'SW-PROV/session/v1'; title: string; remaining: number; turn: number;
  terminal: boolean; text: string; ledger: Evidence[]; actions: Choice[]; swmd_card: string;
};
export type Transport = (request: { action: string }) => Promise<unknown>;

function record(x: unknown): Record<string, unknown> {
  if (typeof x !== 'object' || x === null || Array.isArray(x)) throw new Error('Expected object');
  return x as Record<string, unknown>;
}
function string(x: unknown): string {
  if (typeof x !== 'string') throw new Error('Expected text');
  return x;
}
function units(x: unknown): number {
  if (typeof x !== 'number' || !Number.isSafeInteger(x) || x < 0) throw new Error('Invalid units');
  return x;
}
function exactKeys(o: Record<string, unknown>, keys: string[]): void {
  if (Object.keys(o).sort().join(',') !== [...keys].sort().join(',')) throw new Error('Unexpected packet fields');
}

export function decodePublic(packet: unknown): PublicState {
  const o = record(packet);
  exactKeys(o, ['schema','title','remaining','turn','terminal','text','ledger','actions','swmd_card']);
  if (o.schema !== 'SW-PROV/session/v1' || typeof o.terminal !== 'boolean' || !Array.isArray(o.ledger) || !Array.isArray(o.actions)) throw new Error('Invalid session packet');
  const ledger = o.ledger.map((x: unknown): Evidence => {
    const e = record(x); exactKeys(e, ['query','outcome','text']);
    return { query: string(e.query), outcome: string(e.outcome), text: string(e.text) };
  });
  const actions = o.actions.map((x: unknown): Choice => {
    const a = record(x); exactKeys(a, ['id','label','cost']);
    return { id: string(a.id), label: string(a.label), cost: units(a.cost) };
  });
  const remaining = units(o.remaining), turn = units(o.turn);
  if (turn !== ledger.length || new Set(ledger.map(x => x.query)).size !== ledger.length ||
      new Set(actions.map(x => x.id)).size !== actions.length ||
      actions.some(a => a.cost > remaining || ledger.some(e => e.query === a.id)) ||
      (o.terminal ? actions.length !== 0 : actions.length === 0)) throw new Error('Inconsistent public state');
  return { schema: o.schema, title: string(o.title), remaining, turn, terminal: o.terminal,
           text: string(o.text), ledger, actions, swmd_card: string(o.swmd_card) };
}

export class ProvenanceClient {
  private current: PublicState;
  private pending = false;
  constructor(initial: unknown, private readonly send: Transport) {
    this.current = decodePublic(initial);
  }
  snapshot(): PublicState { return structuredClone(this.current); }
  async choose(id: string): Promise<PublicState> {
    if (this.pending) throw new Error('A choice is already pending');
    const choice = this.current.actions.find(a => a.id === id);
    if (!choice) throw new Error('Choice unavailable');
    this.pending = true;
    try {
      const packet = record(await this.send({action: id}));
      if (packet.error !== undefined) throw new Error('Host rejected choice');
      const next = decodePublic(packet);
      const prior = this.current;
      const judgment = choice.cost === 0;
      if (next.title !== prior.title || next.remaining !== prior.remaining - choice.cost ||
          next.terminal !== judgment || next.turn !== prior.turn + Number(!judgment) ||
          prior.ledger.some((e, i) => JSON.stringify(e) !== JSON.stringify(next.ledger[i])) ||
          (!judgment && next.ledger.at(-1)?.query !== id)) throw new Error('Unexpected transition');
      this.current = next;
      return this.snapshot();
    } finally { this.pending = false; }
  }
}
