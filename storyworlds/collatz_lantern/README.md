# The Lantern Ledger: an exact observation puzzle in SWMD

The player can pay for a useful measurement or choose a chamber using an
arithmetic seal. Both hidden configurations have the same seal. One later
lamp reading distinguishes the configurations and changes which choice earns
the reward. The complete game is small enough to evaluate every deterministic
policy that depends on public observations.

This package supplies a development fixture for storyworld generation and
DataGoblin-style trace curation. It exercises the existing Sweepweave authoring
and reader path. The seven encounters form a mathematical tutorial; production
story density and learned narrative quality are outside its scope.

## Authored source and compiled worlds

`source.swmd.min.md` holds the encounter topology, option text, effects and
reaction formulas. It is a SWMD minified template with four named constants:
`@amber`, `@blue`, `@west`, and `@east`. The compiler obtains those constants
from the exact arithmetic oracle and accepts only `C`, `P`, `ADD` and `MUL`
expressions. Unknown syntax fails compilation.

`prose.swmd.md` supplies the full encounter prose. The repository's existing
`swmd_patch_json.py` parser and patcher apply that text after the topology is
compiled. Reaction formulas stay fixed during this step. The existing
`json_to_swmd.py` exporter then produces ordinary, fully resolved SWMD minified
files beside the native JSON exports.

| File | Role |
|---|---|
| `native/world_a.json`, `native/world_b.json` | Two evaluator-side configurations, ready for the native reader |
| `native/*.swmd.min.md` | Resolved machine views from the existing exporter |
| `public_initial.json` | Initial agent packet, identical for both configurations |
| `audit.json` | Evaluator-only hidden answers and all policy replays |
| `build.py` | Restricted compiler, public observation projection and exact audit |
| `reader.test.mjs` | Replay against the unchanged JavaScript reader engine |

The fixture files remain openly inspectable in the repository. An evaluation
adapter must keep the native authoring JSON and audit on its evaluator side.
It should expose `observe()` only for the current encounter and accept only a
legal action ID. `observe()` returns scene, title, text, public cost and visible
option labels. Reaction formulas, hidden start, alternative scene contents
and reward labels are excluded from that packet. The reference tests compare
the initial, ledger and unmeasured-choice packets across both worlds.

## Arithmetic construction

Use the accelerated odd map with `d=13`. At an odd state congruent to one
modulo four, apply `3n+13`; at the other odd states, apply `n+13`. Remove every
factor of two after this operation.

The hidden start is uniformly chosen from 1 and 5. Both initially read one
modulo four. Their eventual odd cycles are `[1]` and `[5,7]`. They also share
the same orbit under multiplication by 2 and 3 modulo thirteen. That orbit's
least residue is 1, so the preserved seal shown in the ledger agrees in both
worlds.

One tick yields

\[
T_{13}(1)=1,\qquad T_{13}(5)=7.
\]

The next lamp shows amber for one modulo four and blue for three modulo four.
It identifies the correct chamber. West succeeds on the cycle `[1]`; east
succeeds on `[5,7]`. Sampling costs `1/8`. A correct choice earns one ration,
and the score subtracts any sampling cost from the amount recovered.

## Exhaustive result

There are 72 deterministic policies over the five public decision scenes.
Both hidden worlds are replayed for every policy, giving 144 native Python
traces. Policies may make different choices after amber and blue because those
are different observations. Every unmeasured decision scene has the same
packet in both worlds.

| Quantity | Exact value |
|---|---:|
| Best expected score using the seal and no sample | `1/2` |
| Best expected score after sampling | `7/8` |
| Expected value gained by sampling | `3/8` |
| Score after sampling and opening the wrong chamber | `-1/8` |
| Dead ends across the enumerated policies | 0 |

Every optimal policy samples, interprets the lamp and opens the corresponding
chamber. A randomized mixture of deterministic policies has expected value
equal to the same mixture of their values, so it cannot exceed `7/8`.

The free ledger scene contributes no information on this prior. It gives a
useful negative control for generators and judges that reward the appearance
of mathematical evidence. The paid measurement changes the attainable value
by a declared amount. A future storyworld compiler can use this pattern to
require that a clue alters the optimal action under the public observation
contract, while charging the player an explicit cost.

## Verification

Run from repository root with Python 3.11+ and Node 22+:

```sh
python storyworlds/collatz_lantern/build.py --check
python -m unittest discover -s storyworlds/collatz_lantern -p 'test_*.py' -v
node --test storyworlds/collatz_lantern/reader.test.mjs
```

The build replays the official `sweepweave_validator.py`, checks all committed
exports byte for byte and recomputes every policy value with the repository's
`monte_carlo_rehearsal.py` transition/effect functions. Enumeration replaces
random action selection for this finite audit. Four Python tests check public
packet equivalence, signal-conditioned choices, wrong choices and invalid
compiler inputs.

The Node test extracts the unchanged `StoryworldEngine` class from
`storyworld_reader.html`, then verifies all 144 paths, visible text, terminal
encounters and final scores against the Python receipts. It passed locally.
The root reader file is untouched. The workflow repeats these checks.

### Browser playthrough status

The repository's required manual browser pass remains outstanding. This
workspace's Chromium launcher points to a missing executable. The available
cloud browser could not reach the local preview and refused subsequent page
observation under its URL policy. UI attempts stopped at that refusal. The
PR is a draft until the following native-reader playthrough is completed.

Open `storyworld_reader.html` and load `native/world_a.json`. Read the preserved
seal, sample the next lamp, then open west after amber. The Score meter should
show `0.875`. Restart with `world_b.json`, sample, and open east after blue;
the score should again be `0.875`. A direct wrong chamber should show zero.
After a sample, the wrong chamber should show `-0.125`. Check that the opening
prose and option labels agree between configurations and that the hidden start
is absent from the visible stat panel.

## Research scope

This is one inspected arithmetic construction with two latent states. All
policy values are exact, and the 144 traces share that construction. They
support an interface and scoring check. A model evaluation should hold out
complete mechanisms and story rewrites, preserve the observation boundary,
and compare against the exact policy and a cheap measurement rule.

The EvalMath mechanistic-power skill was read before grading. Its evidence
card here is: unit = one selected mechanism; `n_units=1`; `n_cases=2` hidden
configurations; primary contrast = paid signal versus invariant-only choice;
dose = one lamp bit at cost `1/8`; complete policy family = 72; resolution =
exact rational arithmetic; selection exposure = fully inspected development
fixture; causal control = shared invariant with distinct basins; verdict =
exact finite domain. Neural effect floors and held-out generalization require
a separate registered experiment.

The vendored oracle and both authoring sources have SHA-256 digests in the
receipt. No training, judge API calls, paid compute, or deployments ran.
