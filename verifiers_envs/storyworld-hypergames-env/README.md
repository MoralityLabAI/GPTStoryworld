# GPTStoryworld Hypergames: single-player reasoning and alignment

This is the self-contained, Python-standard-library GPTStoryworld-facing copy of HG-01, HG-02, and HG-03, located in `verifiers_envs/storyworld-hypergames-env/`. No neural results have been measured. It is isolated from the main Sweepweave runtime.

## Source pins

- GPTStoryworld audited: `c8d46591f983473023daf0232e9b413baaa02194`
- EvalMath HG-01 PR #37: `c42de60c8a864f7a8e157dd9c5a20a7d998bd240`
- EvalMath HG-02 PR #39: `7f887d4441d119bde2f2c123f3e2384b68390dbf`
- EvalMath HG-03 PR #40: `51cee18188170320e740c9aa18c23c48d026d0d8`

All 23 mathematical source, fixture, test, protocol and receipt files are copied from the HG-03 EvalMath branch, retaining their contents and relative paths. Future divergence must be documented.

## Offline preflight

Change to this subfolder. Python 3.11+ suffices.

```powershell
$env:PYTHONPATH='src'
& 'C:\Python311\python.exe' -m unittest discover -s tests -p 'test_*.py' -q
& 'C:\Python311\python.exe' scripts/check_local_receipts.py
```

Local reproduction: 77 unit tests; HG-01 14 checks, HG-02 26 checks, HG-03 27 checks, each source-hashed receipt matching after normalizing Python tuples to JSON lists and ignoring generated timestamps.

## Frozen local Qwen

Read [QWEN_PROTOCOL.md](Hypergames/single_player/QWEN_PROTOCOL.md) and [qwen_registration_v1.json](Hypergames/single_player/qwen_registration_v1.json). Run `python -m spiral_ln.hypergames_qwen_eval` from this subfolder, with `PYTHONPATH=src`. The 140-core, 512-padded and 512-native cases share the registered HG-03 contract.

**The held-out seed manifest is private and is deliberately excluded from public GitHub.** Obtain `HG03_private_seeds_20261116.json` separately and store it outside Git, e.g. `C:\Users\patri\Documents\Codex\private-evals\HG03_private_seeds_20261116.json`. The exact registered SHA-256 is `4cd049c41b0ab0ab45688c0b44f098bdfe9437ebfc5a277e6867540558205c55`. Pass the absolute path using `--private-manifest`; replacement seeds would invalidate the frozen protocol. Keep model files and private results outside Git.

The Gym is an exact synthetic reference, not a live GPTStoryworld game, neural alignment result or quantum process.
