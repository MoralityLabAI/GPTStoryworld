---
name: hypergames
description: Build challenging, exact-graded eval families for frontier models from the Cairo hyperworld engine (1,024 hidden worlds, parity evidence through noisy channels, relayed reports, first- and second-order beliefs), check that baselines fail, and freeze a private held-out split. From GPTStoryworld codex-skills/hyperworld-builder and verifiers_envs/storyworld-hypergames-env.
metadata:
  version: 1
  mode: hypergames
  source: codex-skills/hyperworld-builder/SKILL.md
---

# Hypergames

A hypergame is a scenario where each character plays a different subjective game over a hidden world. The
Cairo hyperworld engine holds ten hidden binary factors (1,024 worlds). Every evidence item reports the parity
of some factors through a binary symmetric channel with a stated reliability, and some officials relay an
earlier report under the same source root, which carries no new information. The engine computes the exact
posterior with rational arithmetic, so questions about it have exact answers. Strong models still fail them
when they count relays twice, drop the XOR structure, or confuse a second-order belief with a marginal.

## Arguments

`/hypergames <family> [aim]`, for example `/hypergames relay-traps-v1 hardest late-game items`.

## Workflow

1. `hyperworld_status`: engine present, policies, item kinds, existing families.
2. `hyperworld_view` on a seed or two to see what players observe (`seed`, `actions`).
3. `hyperworld_family_build` with public dev seeds (for example 0-15). Item kinds:
   - `marginal`: P(factor = 1).
   - `parity`: P(a XOR b = 1).
   - `p2_alignment`: 2 P(a = b) - 1, the engine's belief-about-belief score between two actors.
   - `fresh_count`: how many evidence items carry independent information.
   Policies: the engine's scripted ones and `random` (seeded legal play, the most varied traces). Later
   turns (5-7) give longer, more entangled traces. `traps_only: true` keeps items the relay-counting
   baseline gets wrong.
4. Read `baselines` and `accepted`. A family is accepted only when the oracle scores 1.0 and the naive
   (relay-counting) and uniform baselines stay low. If it is rejected, change policy, turns, kinds or
   traps_only and rebuild under a new family name; do not loosen the acceptance rule.
5. Optionally probe with `hyperworld_family_score` on answers you write yourself, to see which kinds are hard.
6. `hyperworld_family_freeze` with an absolute `heldout_dir` outside the repository (the operator gives it).
   It draws private seeds and records only their hashes; the family cannot be rebuilt after a freeze.
7. Report: family, items by kind, baselines, accepted, frozen, and the held-out commitments.

## Rules (from hyperworld-builder)

- All characters and institutions are fictional; keep them abstract. No real organisations or people.
- Posterior entries are probabilities over possible worlds, not frequentist p-values.
- Never place grader-only state (the hidden world, future evidence) in a prompt; the tools render prompts
  from the public trace only.
- Freeze the seed roster and held-out policy before any frontier evaluation; held-out seeds never enter git.
- Report only numbers the tools returned.
