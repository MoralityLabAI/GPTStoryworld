// Reader-ready deterministic export. The verbose Godot-style tree remains
// available as buildSweepweave(source) from build_sweepweave.mjs.
import {buildSweepweave} from './build_sweepweave.mjs';
import {compactSweepweave} from './compact_sweepweave.mjs';

export function buildStoryworld(source){
  return compactSweepweave(buildSweepweave(source));
}
