# HG-08 results and reproduction

Prerecorded [registration](hg08_registration_v1.json) and [protocol](HG08_PROTOCOL.md), pinned in GPTStoryworld commit `a54c806b0c9b16219d9e823aabd399361078fc7e` before this data was produced.

- Registered public intervention census: 3,840 rows, 24 seeds, five dimension cohorts, k=1/2, four policies, four budgets. H1–H4 all pass. All fully certified supports predict 256/256 test outputs, with zero false releases; incomplete cases abstain.
- Matched CPU PyTorch study: 48 neural fits, six seeds × two cohort dimensions × four recurrent input-mask arms. The six-seed H5 direction gate fails at 1/6. The exact support mask matches the privileged true-mask condition on every seed; all trained models abstain and remain near chance.
- Mean adaptive native1024/k1 query cost 64.375 versus a 51-query sparse-support information lower bound. Group interventions flip arbitrary subsets and thus have different power from singleton-only probes.

### Run in GPTStoryworld subtree

```powershell
$env:PYTHONPATH = 'src'
& C:\Python311\python.exe -m unittest discover -s tests -p '*causal.py' -q
& C:\Python311\python.exe scripts/verify_hg08_causal.py
& C:\Python311\python.exe scripts/run_hg08_cpu.py --skip-neural --check --out output/evaluation_hypergames/hg08
```

The last command regenerates all 24 public seeds and compares the exact seed CSV and source-hashed summary to committed evidence. To rerun actual PyTorch weights use `python scripts/run_hg08_cpu.py --neural-only --out a-new-output-folder` with CPU PyTorch 2.10 and NumPy 2.3.5 installed. This model fitting takes CPU time and is separate from the exact intervention-replay CI gate.

Full discussion: `paper/hypergames_hg08_active_causal_results.md`. No Qwen runs or private HG-03 seeds were used.
