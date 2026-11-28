# StoryworldBench

One scored, reproducible harness over the evals already in this repo, with three tracks that match the three skills of the companion Storyworld agent app. Standard library only, offline, CPU, about a minute for a full baseline sweep.

| Track | Skill | Tasks (dev/test) | What is graded |
| --- | --- | --- | --- |
| `builder` | `storyworld-builder` | 15 (11/4) | Whole-world SweepWeave JSON: repair 12 broken worlds, author 3 new worlds |
| `small` | `small-storyworld` | 26 (16/10) | One encounter per packet (prompt under 8k tokens): micro-spec compile/compression/repair/targeted_edit, SWMD block patches, Camelot page repair |
| `hypergames` | `hypergames` | 27 (16/11) | Exact-graded decision and inference: HG-02 sealed gym, HG-01 goal inference and probe cover, tier-1 eval turns |

## CLI

Run from the repo root. Two equivalent forms; `-m` is the documented one.

```
python -m benchmarks.storyworld_bench <cmd>
python benchmarks/storyworld_bench/cli.py <cmd>
```

- `tasks [--track builder|small|hypergames] [--split dev|test]` prints JSONL, one task per line: `{task_id, track, skill, prompt, inputs, grading_only, budget_tokens, scorer, answer_format}`. `inputs` maps a name to a repo-relative path the agent may read. `grading_only` lists repo paths that hold or compute the answer (oracle worlds, the repaired Camelot world, the HG solver modules and fixture, the tier-1 world whose option tags name the answer); a harness whose agent can read files must refuse them (the Storyworld GDK app's `bench` command does). Gold answers are never in this output.
- `score --task <task_id> --artifact <path>` prints one JSON object `{task_id, track, score, passed, checks, error?}`. The artifact is the file the agent wrote: a storyworld JSON, an SWMD block, or a JSON answer. Unknown task ids exit 2.
- `run --track <t> --agent <agent> --out <dir> [--limit N] [--seed S] [--split dev|test|all]` writes `<dir>/results.jsonl`, `<dir>/artifacts/` and `<dir>/summary.json` (`{track, agent, n, mean_score, pass_rate, per_check_means, source_hashes, sources_match_manifest, split}`). `--split` defaults to `dev`. `--limit` takes a seeded sample.
- `selftest` runs the null and oracle baselines on every track, checks source hashes and manifest determinism, asserts oracle at least 0.99 (mean and pass rate) and null at most 0.02, and exits non-zero otherwise.
- `freeze` regenerates `data/` and `manifest.json`. `verify` compares source hashes to the manifest. `upstream` runs the hypergames env's own `check_local_receipts.py`.

Agents: `baseline:null` (empty artifact), `baseline:oracle` (the known-good answer), `baseline:identity` (the input returned unchanged for builder and small, the first option for hypergames; shows how far "do nothing" gets), and `openai:<base_url>#<model>`. The OpenAI agent posts to `<base_url>/chat/completions` (or `/v1/chat/completions` when the base URL does not end in `/v1`) with `temperature` 0, `max_tokens` taken from the task, and `seed` from `--seed`. It reads `OPENAI_API_KEY` from the environment if set. Local llama-server and squid models work this way:

```
python -m benchmarks.storyworld_bench run --track small --agent "openai:http://127.0.0.1:18090/v1#inkling-2-mini" --out runs/inky-small
```

Reasoning wrappers (`<think>` blocks, code fences, leading prose) are stripped before parsing. `model_parse_ok` is the raw artifact parsing as bare JSON (or a bare SWMD block); `parse_ok` is the artifact recoverable after stripping. Both are reported on every task.

## Splits and the manifest

`manifest.json` is the frozen task set: every task, its gold answer, the generated inputs under `data/`, and the SHA-256 of every source file the tasks and scorers read (text hashes are CRLF-normalised). Task generation uses seed `20261128`; splits are `sha256(task_id)` modulo 100, below 70 is `dev`, so a split never depends on task order. `selftest` regenerates everything and fails if it differs from the manifest. `tasks` warns on stderr when a source file no longer matches.

**`dev` is for development. `test` is for one-shot reporting only**: run a model on it once, at the end, with the settings you will report. `run --split test` or `--split all` with an `openai:` agent requires `--confirm-one-shot`.

## Tracks

### builder (large context)

Source of truth: `codex-skills/storyworld-building/scripts/sweepweave_validator.py`, `storyworld_quality_gate.py` (28 checks), `monte_carlo_rehearsal.py` (200 runs, seed 42) and `benchmarks/storyworld_builder_small_model/score_small_model_storyworld_builder.py` (control_logic, branching and text_surface components, reported as `metric_diag_*`, not scored).

- 12 repair tasks (`builder.repair.*`). Ten take a valid repo world from `storyworlds/` (england_to_france_honest, russia_to_austria_grudger, france_to_germany_machiavellian and the `_p` variants) and apply two seeded corruptions (`no_start`+`dangling`, or `spool_ghost`+`missing_keys`). Two use repo worlds that are invalid as committed (`diplo1`, `glam_to_shadow_honest`; spools lack `encounters`), with a deterministic spool rebuild from `connected_spools` as the oracle. The prompt carries the validator rules and the validator output.
- 3 author tasks (`builder.author.small|medium|full`): write a new world to a brief with encounter, ending and character minimums. The oracle is `storyworlds/the_fifth_testimony_p2.json`, the one repo world that passes the gate 28/28 with every ending reached in rehearsal.

Schema-valid and gate-passing are separate bars (the Repair Addendum in `codex-skills/small-storyworld-builder/SKILL.md`). `checks` carries `schema_valid` and `quality_gate_pass` separately, plus `metric_gate_checks_passed/total`.

- Repair score: invalid world 0.3 x rest; valid world 0.4 + 0.6 x rest, where rest = 0.3 ids_preserved + 0.2 text_preserved + 0.3 gate_retained + 0.2 endings_retained. `gate_retained` and `endings_retained` are relative to the uncorrupted original, so a repair never has to beat the source world. `passed` needs schema valid, every id and every text cell preserved, and gate and reachability no worse than the original.
- Author score: invalid 0.3 x rest/0.65; valid 0.35 + 0.15 brief + 0.35 gate_checks_fraction + 0.15 endings_reachable. `passed` needs a valid world, all brief minimums, the full quality gate, and every required ending reached.

### small (8k packets)

Every prompt is one encounter or one micro-spec, at most 1.2k estimated tokens (chars/4) against the 8192-token packet budget with 1024 reserved for output; `metric_packet_tokens` and `metric_packet_within_budget` are in `checks`.

- 12 micro-spec tasks (`small.compile|compression|repair|targeted_edit.*`), 3 per type, from `swmd_build_qlora_examples.build_examples` over `InkyWorlds/hat-that-held-the-moon` and `InkyWorlds/city-that-lost-its-night-bell` SWMD-min worlds (the skill's 40/25/20/15 task mix). Checks: schema key, identical key set, encounter id and action (`rxn_*`-derived) ids preserved, valid transitions, type-specific constraints (at most 5 agents and 10 state vars; unique action ids; no new agents and two conflict incentives), and `exact_match` against the builder's output. `exact_match` is scored but does not gate `passed`.
- 6 SWMD block patch tasks (`small.patch.*`): from `json_to_swmd.emit_full` blocks of three repo worlds, redirect one reaction target or add an exact phrase to the encounter text. The artifact block is parsed with `swmd_patch_json.parse_swmd_full`, patched into the base JSON with `patch_world`, and the result is run through the validator (`validator_after_patch`). Other checks: ids preserved, `E:`/`D:` formula lines untouched, edit applied, no collateral change.
- 8 Camelot repair tasks (`small.repair.camelot.*`), the 8 cases of `InkyWorlds/camelots-reckoning/bench/bench_repair.py` (`build_task` and `score_page` are reused as is) plus the validator on the reconstructed world. `bench_repair.py` resolves its data from its own folder but the data is one level up, so the harness loads the module with `RUN` pointed at `InkyWorlds/camelots-reckoning`. The 11-way fan-out case needs about 9000 output tokens, so its `budget_tokens` is 9000.

`score` is the mean of the boolean checks; `passed` needs all of them except `model_parse_ok` (and `exact_match` for micro-specs).

### hypergames (frontier-hard)

`verifiers_envs/storyworld-hypergames-env` (`PYTHONPATH=src` is set by the harness; Fraction math throughout).

- 10 HG-02 decisions (`hg.hg02.s<seed>.step<k>`): the route and verification choices of the sealed single-player gym, 140-coordinate state, horizon 5, seeds 17, 23, 41, 59, 73. Graded by recomputing the exact Bellman action values with `hypergames_single_player.action_value` on the public information cell. Optimal action scores 1; a legal suboptimal action scores half its normalised value; an illegal action scores 0.
- 5 HG-01 goal-inference tasks and 3 robust probe-cover tasks, seeded instances graded with `evaluation_hypergames.infer_goals` (Jaccard partial credit, exact set passes) and `minimum_robust_probe_cover` (feasibility, claimed cost, cover validity, minimum cost).
- 1 task from the registered fixture `Hypergames/fixtures/hg01_registered.json`.
- 8 tier-1 eval turns (`hg.tier1.turn<N>`) from `storyworlds/evals/eval_tier1_signal_sorting.json`: pick an option; graded by the world's `scoring_contract.option_scores`. Options are lettered in a seeded shuffle, the hidden secret option is withheld, and the generator tag suffix (`[phase 2, oracle]`) is stripped because it names the answer. Best option scores 1, otherwise half the normalised option quality.

## Baselines measured

`dev` split (what `run` does by default); `all` is dev plus test.

| Track | null (dev) | identity (dev) | oracle (dev) | null (all) | oracle (all) |
| --- | --- | --- | --- | --- | --- |
| builder | 0.000 / 0% pass | 0.209 / 0% | 1.000 / 100% | 0.000 / 0% | 1.000 / 100% |
| small | 0.000 / 0% | 0.520 / 0% | 1.000 / 100% | 0.000 / 0% | 1.000 / 100% |
| hypergames | 0.000 / 0% | 0.360 / 12.5% | 1.000 / 100% | 0.000 / 0% | 1.000 / 100% |

Cells are mean score / pass rate. The identity row shows the schema bar and the content bars separating: unchanged broken worlds are invalid (builder 0.209), unchanged micro-specs keep most structure but fail the edit (small 0.520), and the first-option policy gets some hypergames items by chance.

## Sources reused, by path

- `codex-skills/storyworld-building/scripts/`: `sweepweave_validator.py`, `storyworld_quality_gate.py` (and `polish_metrics.py`), `monte_carlo_rehearsal.py`, `json_to_swmd.py`, `swmd_patch_json.py`
- `codex-skills/small-storyworld-builder/scripts/`: `swmd_encounter_index.py`, `swmd_build_qlora_examples.py`
- `InkyWorlds/camelots-reckoning/bench/bench_repair.py` and its data
- `benchmarks/storyworld_builder_small_model/score_small_model_storyworld_builder.py`
- `verifiers_envs/storyworld-hypergames-env/src/spiral_ln/{hypergames_single_player,evaluation_hypergames}.py`, `Hypergames/fixtures/hg01_registered.json`
- `storyworlds/evals/eval_tier1_signal_sorting.json`
- `benchmarks/storyworld_reasoning_v2_turn_traces/BENCHMARK_SPEC.md` (the per-turn, legal-action, hidden-state-is-grading-only contract the hypergames prompts follow)

## Left out of the default suite

- **Tiers 2 to 5 of `storyworlds/evals/`**: the README calls them a private pack and `manifest.json` carries their score tables, but the world files are not in this checkout. Only tier 1 is present. `mas_turn_runner.py` imports `monte_carlo_spool`, which is also missing, so tier 1 is graded from its scoring contract directly.
- **HG-03 held-out seeds and the frozen Qwen eval** (`hypergames_qwen_eval`): the private manifest `HG03_private_seeds_20261116.json` is not in the repo and is neither required nor created here.
- **HG-04 to HG-09 CPU replays**: these are mechanism checks with their own receipts, not agent-facing tasks.
- **`verifiers_envs/storyworld-text-quality-env/evaluate_text_quality.py`**: needs a judge model API.
- **`verifiers_envs/storyworld-env/quality_vector_score.py`**: imports `from __init__`, which pulls the verifiers runtime; the in-repo equivalents above cover the same metrics offline.
- **`benchmarks/storyworld_builder_small_model` campaign runners and `swmd_mcp_*` pipelines**: need a GPU model and the MCP server.
- **`benchmarks/storyworld_reasoning_v2_turn_traces/1984_benchmark`**: its scripts read `storyworlds/generated/1984_benchmark/`, which is not in the repo. **`storyworld_reasoning_v1`** is a results archive with no gradable items. The v2 spec rows (forecasts, hidden_state_reveal) have no tracked data, so only the spec's contract is used.
- **`verifiers_envs/storyworld-symbolic-env`**: an environment with its own rollout loop and no frozen item set with exact answers.
- **`check_local_receipts.py`** (`upstream` command): informational. On this checkout it prints `hg01: regenerated receipt differs`; it is not part of `selftest`.

## Tests

```
python -m unittest discover -s benchmarks/storyworld_bench/tests -v
pytest benchmarks/storyworld_bench/tests
```

22 tests: manifest hashes and determinism, hash-based splits, CLI contract in both invocation forms, every scorer family (oracle 1.0, null 0.0), builder corruption breaks the validator, valid-but-failing-gate scored separately, parse-metric split, patch collateral detection, exact Bellman scoring, no answer leaks in tier-1 prompts, the OpenAI agent against a local mock server, and the test-split guard.
