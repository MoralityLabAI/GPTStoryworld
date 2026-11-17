# HG-09 signed-in model campaign

This folder contains actual public-development model measurements, the frozen additional registration, availability probes, source audit, offline checks and create-only hash-chained JSONL journals. The published smoke checkpoint contains 12 completed episodes; later commits may expand the cohort. Read `measured_export.json` for exact current attempted/completed counts. Statistical analysis is in [EvalMath PR #48](https://github.com/MoralityLabAI/EvalMath/pull/48).

The requested aliases `gpt-6.1-sol` and `gpt-6-astra` were accepted by signed-in Codex CLI 0.167.0-alpha.3.2. Backend snapshots are not exposed. No paid API calls or model-side tools were used. The direct and deliberative wordings use the same requested low reasoning effort and action budgets. Output-token caps, temperature and the complete CLI scaffold are unavailable; the exact public task prompt and supplied model instructions are saved. Token counts do not disclose private reasoning text.

All dimensions, ranks, hidden modes and turns sharing a generator seed are clustered together. This public unsealed pilot is power-limited and cannot rank models or establish neural alignment mechanisms. The registered larger sequence includes 24 public roots; unrun cases are not scores. The private HG-03 manifest was not opened, and numeric disjointness from an unavailable list is not asserted.

From `verifiers_envs/storyworld-hypergames-env`, replay without inference:

```text
PYTHONPATH=src python -m unittest discover -s tests -p 'test_hg09*.py' -q
PYTHONPATH=src python -m unittest discover -s tests -p 'test_hypergames_observation_certificate.py' -q
PYTHONPATH=src python -m spiral_ln.hg09_replay --traces Hypergames/hg09/session_20261117/traces --registration Hypergames/hg09/session_20261117/registration.json --out output/hg09_replayed.json
```

On PowerShell set `$env:PYTHONPATH='src'` before the Python commands. Use a writable task-local TEMP/TMP directory if the managed Windows default denies temporary-file writes. The package's Git attributes preserve exact bytes, including archived CRLF CSVs and LF source/journal files. Source hashes are checked against the frozen registration; do not normalize a downloaded journal or edit a registration to make a check pass.

`hg09_session` is the inference runner. Its `--manifest`, `--out` and `--sandbox` arguments are required. It consumes signed-in model allowance, so do not invoke it to reproduce grades: use offline replay. A new episode path is create-only; an interrupted or failed episode must remain recorded and cannot be silently rerun or replaced. The CLI ignores user configuration, disables shell/image/web/agent tools where supported, and treats any tool event as invalid transport. A fresh process receives only public history; target masks, hidden-mode metadata and grades stay in the parent evaluator.

`measured_export.json` separates model episodes from structural adaptive-hash, singleton and full-rank dense GF(2) controls. The dense control does not implement an optimal sparse decoder. The supplementary public GF(2) certificate can prove that observed deltas and exact sparsity force a released support; it is sufficient, not necessary, and makes no claim about an internal neural representation.

The audit notes two instrument limits: HG-02 does not explicitly describe every action-transition semantic in its observation, and its 512-dimensional task also increases arithmetic widths. Preserve these caveats when interpreting horizon or dimension effects. Behavioral diagnostics remain distinct from inferred intentions.
