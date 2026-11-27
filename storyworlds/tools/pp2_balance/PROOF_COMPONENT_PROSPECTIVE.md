# PP2-BAL-12: frozen structural transfer of proof memory

Frozen before running any prospective controller or extracting any fresh roster game. PP2-BAL-11B is a spent development study; its strongest observed arm is whole_single. All eight arms, code and 8192-byte configuration are pinned by proof_component_study.mjs at commit a7177832880b87c908567df65e7150d81a56aa08. No changes after inspecting fresh outcomes. Primary endpoint: root-paired verifier normalization reduction against whole_single; component_lru and component_utility are prespecified challenger arms, all others controls. No claim of aggregate time savings without including bank management and wall time. Report every root, trajectory and all secondary counters; root (not query) is the unit. Require all exact certificates independently verified, intervals contained in cold reference, witness availability preserved and retained serialized state <=8192. No learned policy promotion without clear paired savings over whole_single and accounting of management cost. For each challenger report mean paired root cost difference, median, and wins/losses/ties, with exact sign test as descriptive (small sample; no multiple-comparison-adjusted inference). Treat any failed admission, dead horizon, replay error or verifier assertion as failed campaign, not an exclusion.

Two distinct synthetic structures: ternary_diamond (A ternary decision with early hold exit, two B branches rejoin final A; six row and four column declared policy rankings), bypass_relay (five decisions with bypasses and early defection, eight row and four column declared policies). Policies use cyclic option rankings; for binary options these exhaust permutations, for ternary options this is a restricted declared policy roster. Semantic policy IDs include family and ordered rankings. Four roots per structure. All seeds and utility/target assignments in the generator are frozen. Two 64-query trajectories per root: a local random walk among unvisited one-coordinate edits, with random-global restart only on exhaustion, and a global uniform draw without replacement. Streams are generated independent of all controller choices. Existing scalar block patch preserves authored signs. Native reader extraction and uniform-choice measurement precede the controller; report transitions separately. Reset controller memory per trajectory as in 11B. These are new synthetic families, not production playthrough or cross-roster transport. Do not mix or reuse banks across rosters.

Smoke uses only separate seeds 87019 and 94938; no controller run. Both base fixtures passed reader audit, native extraction, and zero dead/horizon checks in JS isolate. Frozen campaign is explicit: node storyworlds/tools/pp2_balance/proof_component_prospective_replay.mjs --evaluate-frozen --write . File is write-once; future verification should compare rerun output to receipt. CI runs smoke and spent replays only, not this fresh campaign. No prospective outcomes recorded at freeze.

Generator smoke receipt:
[
  {
    "spec": {
      "id": "smoke_ternary_diamond",
      "family": "ternary_diamond",
      "seed": 87019,
      "target": 0,
      "utility": 0
    },
    "shape": [
      6,
      4
    ],
    "blocks": 9,
    "transitions": 101
  },
  {
    "spec": {
      "id": "smoke_bypass_relay",
      "family": "bypass_relay",
      "seed": 94938,
      "target": 0,
      "utility": 0
    },
    "shape": [
      8,
      4
    ],
    "blocks": 9,
    "transitions": 194
  }
]
