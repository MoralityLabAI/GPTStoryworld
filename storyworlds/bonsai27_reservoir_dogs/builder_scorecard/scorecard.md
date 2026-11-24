# Small-Model Storyworld Builder Scorecard

- Manifest: `storyworlds\bonsai27_reservoir_dogs\builder_manifest.jsonl`
- Rows: `1`

| Rank | Run | Model | Condition | Score | Weakest Fix |
|---:|---|---|---|---:|---|
| 1 | `bonsai27_reservoir_dogs_small_storyworld_001` | `Ternary-Bonsai-2-27B-PTQ1_0.gguf` | `packet_author_native_repair` | 0.8734 | Run native planner receipts and append teacher rows before learned routing. |

## Interpretation

Use this as a fast optimization target for small-model runs. A low component score should become the next bounded packet or native-schema repair target, not a larger one-shot prompt.
