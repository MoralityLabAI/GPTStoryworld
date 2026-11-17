# AGENTS.md

## Purpose
This repo is a mixed storyworld research monorepo. It contains active Python environments, a React frontend, a small Vercel backend, large generated storyworld corpora, and archival/vendorized copies of older app trees.

The root README is only partially current. Start from the code and the nearest package README, not from repo-level assumptions.

## Hypergames and evaluation power

Before training or grading new Hypergames, Storyworld, or mechanistic-intervention runs, read the [EvalMath mechanistic-power skill](https://github.com/MoralityLabAI/EvalMath/tree/main/skills/evalmath-mechinterp-power). Identify independent generator worlds, calibrate matched-sham variation, declare a minimum meaningful causal change, count all comparisons, and screen prospective statistical resolution before using 64/256 repeated outcomes as evidence. Preserve raw per-world receipts and untouched held-out worlds. Treat symbolic GF(2) ceilings separately from neural mechanistic discovery; HG-07/08/09 illustrate this distinction.

## Canonical Areas
- `storyworld/`
  - Active diplomacy/storyworld environment code.
  - Contains schemas, generators, validators, tools, examples, and `unittest` coverage.
- `verifiers_envs/`
  - Separate Python packages for verifier-style environments.
  - Important subprojects include `storyworld-env`, `storyworld-symbolic-env`, and `negotiation-storyworld-env`.
- `storyworld-frontend/storyworld-frontend/`
  - Canonical frontend app.
  - React 18 + Vite app with its own `package.json` and lockfile.
- `storyworld-vercel-backend/storyworld-vercel/`
  - Lightweight Vercel/Next API route tree plus `schema.sql`.
- `storyworlds/`
  - Large corpus of authored and generated storyworld JSON artifacts.
  - Treat this as data unless the task is specifically about authoring, auditing, or balancing worlds.
- `hermes-skills/`, `codex-skills/`, `claude-skills/`
  - Agent workflow assets, prompts, and helper scripts.
  - If you work inside a subtree that has its own `AGENTS.md` or `SKILL.md`, follow that file.

## Areas To Avoid By Default
- `Storytron.com/`
  - Contains mirrored app trees and nested `node_modules`.
  - Do not touch this unless the user explicitly asks for that deployment/archive copy.
- `logs/`, `verifiers_envs/*/.venv/`, `__pycache__/`, `node_modules/`
  - Generated or dependency directories.
- `*.zip`, large benchmark outputs, and batch-generated JSON under `storyworlds/` and `benchmarks/`
  - Keep diffs narrow and intentional.

## Repo-Specific Working Rules
- Determine the authoritative surface before editing. Similar concepts appear in multiple places.
- Do not assume the root Node scaffold is live.
  - `README.md` and `package.json` reference `controller.js` and `meta-calc.js`, but those files are not present at repo root.
  - Do not assume `npm start` from the repo root works.
- Preserve existing JSON ordering in Sweepweave/storyworld files unless a task explicitly requires structural rewrites.
  - Some docs note that key ordering matters for downstream Godot/Sweepweave parsing.
- Avoid wholesale reformatting of large generated storyworld JSON.
- Prefer existing helper scripts over manual edits for large topology/balancing tasks.
  - Good starting points: `storyworlds/tools/`, `codex-skills/storyworld-building/scripts/`, `tools/`.
- The worktree may already be dirty. Never revert unrelated user changes.

## Search And Read Strategy
- Use targeted search. Full-repo scans can be noisy because this repo contains nested mirrors, `node_modules`, and large corpora.
- Prefer exclusions like:
  - `rg -n --glob '!**/node_modules/**' --glob '!**/.venv/**' --glob '!**/__pycache__/**' <pattern> C:\projects\GPTStoryworld`
- When inspecting files, read the closest local README or manifest for the subtree you are modifying.

## Validation Commands
- For `storyworld/` changes:
  - `python storyworld/validators/validate_storyworld.py storyworld/examples/diplomacy_min.json`
  - `python -m unittest storyworld.tests.test_turn_trace_export`
- For authored or revised storyworld JSON:
  - Do not stop at schema validation.
  - Open `storyworld_reader.html` in a browser and play the storyworld manually.
  - Use that pass to catch broken pacing, dead ends, incoherent choices, and bad reader-facing text.
- For `verifiers_envs/storyworld-symbolic-env/` changes:
  - `cd verifiers_envs/storyworld-symbolic-env`
  - `python symbolic_storyworld_env/hermes_storyworld.py --config examples/hermes_storyworld_config.json`
  - `python -m unittest tests.test_symbolic_smoke`
  - `python -m unittest tests.test_route_ablation`
- For `verifiers_envs/storyworld-env/` changes:
  - `cd verifiers_envs/storyworld-env`
  - `pytest test_sweepweave_env.py -v`
  - `black .`
  - `ruff check --fix .`
- For `verifiers_envs/negotiation-storyworld-env/` changes:
  - Run the relevant script directly, for example:
  - `python audit_storyworld.py --storyworld <path-to-world.json> --strict`
- For frontend changes:
  - `cd storyworld-frontend/storyworld-frontend`
  - `npm run build`

## Editing Guidance By Surface
- `storyworld/`
  - Keep schema, environment behavior, tools, and tests aligned.
  - Prefer adding or updating tests when changing turn-trace or environment semantics.
- `storyworlds/`
  - Edit the smallest possible set of files.
  - If a generated world needs systematic changes, use or extend an existing script rather than hand-editing huge JSON blobs.
  - When the task is authoring or revising a playable world, guide the author to test it in `storyworld_reader.html`.
- `storyworld-vercel-backend/storyworld-vercel/`
  - Route handlers are plain files under `api/`.
  - There is no obvious local test harness in this subtree; validate changes by reading the route logic and the SQL schema together.
- `hermes-skills/storyworld-conveyor/`
  - There is a nested `AGENTS.md` in that subtree with stricter operational guidance. Follow it instead of this root file when working there.

## Good Defaults
- Make minimal, local changes.
- Cite exact file paths in notes and handoff.
- If a doc conflicts with the checked-in code, trust the code and mention the mismatch.
