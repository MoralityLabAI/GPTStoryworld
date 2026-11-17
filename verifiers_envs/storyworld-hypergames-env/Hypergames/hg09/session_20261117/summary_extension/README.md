# Separately registered summary-observability repeats

This is a post-pilot configuration-observability extension, separate from the primary campaign. Eight episodes were registered before their inference: the previously observed public seed 202611170801, HG-02 at 140 dimensions and horizon five, both hidden modes, both models and both prompting conditions. It adds no independent generator roots. Read `measured_export.json` for actual completed counts after the export is committed; planned episodes are not scores.

The extension requests `model_reasoning_summary="auto"`. It reuses the frozen primary `run_episode` observation boundary, prompts, parser, transitions and grader unchanged, at requested low effort and the same action horizon. Summary configuration may influence generation, so these repeats are not pooled with primary scores or treated as a model-level sham. The primary registered requests retain their original configuration.

The preceding unscored arithmetic probes are in `../capabilities/`. Initial attempts failed locally before inference because the managed sandbox could not access native Codex state. The immutable `native-access-retry01` attempts succeeded: Sol returned one brief provider-exposed reasoning item, and Astra returned none on that probe. Absence on one probe does not establish universal unavailability. Neither arithmetic probe is an HG-02 or HG-08 model score.

Provider-returned reasoning items, including brief headings, have separate provenance in response records. They are not reconstructed private chain-of-thought, complete internal traces, or evaluator-generated explanations. Correct actions and provider headings alone do not identify internal alignment mechanisms.

From the package directory, reproduce grades without inference:

```text
PYTHONPATH=src python -m spiral_ln.hg09_replay --traces Hypergames/hg09/session_20261117/summary_extension/traces --registration Hypergames/hg09/session_20261117/summary_extension/registration.json --out output/hg09_summary_replayed.json
```

Compare that output byte-for-byte with the committed `measured_export.json`. The separate registration pins the primary sources and new dispatcher source. The registered extension was frozen in commit `d39b775` before calls. Invoking `hg09_summary_observability --execute` consumes ordinary signed-in allowance and is not required for offline reproduction; existing journals are create-only and cannot be silently replaced.
