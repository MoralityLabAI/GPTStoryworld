# HG-07 CPU reproduction

This public synthetic CPU campaign continues HG-06's six-sparse parity construction. It has been frozen on the GPTStoryworld branch at registration commit `2b948b467fc9847d86cab00f65127cff6e77aa78` before neural training.

## Setup

Requires Python 3.11+, `numpy`, and CPU `torch` (run environment: Python 3.13.5, NumPy 2.3.5, PyTorch 2.10.0+cpu). Torch uses two threads. No GPU, hosted model or private HG-03 seed file is involved.

From `verifiers_envs/storyworld-hypergames-env` with the `src/spiral_ln` and `Hypergames/single_player/` paths present:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p '*raw*.py' -v
python scripts/verify_evaluation_hypergames_raw.py
python src/spiral_ln/hypergames_raw_recurrent.py --out output/evaluation_hypergames/hg07_new
python scripts/verify_hg07_cpu_replay.py --out output/evaluation_hypergames/hg07_new
```

The full registered run trains 360 neural fits. Use `--smoke` for one public development seed and one 140-D cohort. `scripts/verify_hg07_cpu_replay.py` audits the shipped six-seed result without retraining and checks all 15 integrity invariants. Reruns on different CPU libraries can yield small floating-point differences; the stored output is an empirical record, and its exact source hashes are verified.

`HG07_RAW_OBSERVABILITY_THEOREMS.md` gives independent GF(2) mathematical results. The compact results report states failures as well as passed directions. `hg07_public_seed_rows.csv` contains full per-model seed metrics; no cherry-picking of model checkpoints occurs.
