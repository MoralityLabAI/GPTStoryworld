# TSUN-01B × GGUF Neuron Explorer

An optional **live inference** harness for the existing [TSUN-01B SweepWeave fixture](../../storyworlds/tsun01b_last_train_home/README.md). The deterministic `Episode` in `storyworlds/tsun01b_last_train_home/tsun01b_env.py` alone decides transitions and outcomes. Qwen supplies Reina's JSON action and dialogue; its claimed beliefs cannot edit world state.

The 24-unit recipe is loaded from `steering_protocol.json` in the fixture. This implementation targets `gne serve --openai` and `llama.cpp` GGUF inference. It is **not an NPU injector**. The author's reported Qwen3.8-27B recipe should be used only with a verified compatible checkpoint and quantization. The API's model ID is checked, while the local operator remains responsible for verifying the actual model hash and injection semantics. Run `gne info` and `gne verify` on the exact model first.

## Offline oracle

From the repository root:

```bash
python -m integrations.gguf_neuron_explorer.runner --backend scripted --output /tmp/tsun01b_scripted.json
python -m unittest discover -s integrations/gguf_neuron_explorer -p 'test_*.py' -v
```

The eight scripted policies replay the finite counterfactual oracle. Their results have `model_inference_executed: false`, and persona/coherence scores stay null. The runner uses the original fixture directly; no model package or GPU is required.

## Live 27B GGUF experiment

On a machine with a supported GGUF and [GGUF Neuron Explorer](https://github.com/balaena01/gguf-neuron-explorer):

```bash
gne info -m /models/your-compatible-qwen27b.gguf
gne verify -m /models/your-compatible-qwen27b.gguf
gne serve --openai -m /models/your-compatible-qwen27b.gguf
# In another terminal, read the real ID from http://127.0.0.1:8791/v1/models
python -m integrations.gguf_neuron_explorer.runner \
  --backend gne \
  --expected-model-id 'ID_FROM_V1_MODELS' \
  --confirm-recipe-compatibility \
  --conditions baseline,half,tsundere,reverse,adaptive \
  --seeds 1 --temperature 0 \
  --output /tmp/tsun01b_gne.json
```

The adapter accepts only a loopback HTTP `/v1` endpoint. The baseline sends no `gne` field. Other conditions send the exact author-reported units and `when: assistant`, with recipe-wide scale of `0.5`, `1`, or `-1`. The adaptive arm uses a **hypothetical prespecified heuristic**: `clip(0.25 + 0.35*Pride + 0.15*(1-Care) + urgency, 0, 0.75)`, with urgency `0.10` during S2/S3. Its parameters are for controlled exploration, not an established personality model.

To run a separately prepared random direction, add `random_recipe` to `--conditions` and pass `--random-recipe YOUR_GNE_RECIPE`. The harness marks `random_norm_matched_verified: false`; random-vector norm equivalence and selection must be independently demonstrated before treating it as a valid null control.

GNE's API acknowledges a requested recipe in `response.gne.recipe`. The adapter records that acknowledgment separately from independent mechanistic verification. It deliberately keeps `result.steering_applied` false because an API acknowledgment alone cannot establish that the model's internal activations were changed as intended.

## Experimental interpretation

The runner supplies only scene, phase, departure time and available actions to Reina. Internal world flags and numeric traits stay in the controller. Invalid JSON, invalid actions, missing recipe acknowledgments and remote endpoints fail closed; incomplete trials have null results and retain error details and raw response. The emitted JSON contains condition/seed labels, full model-event traces, the source protocol hash, scenario hash, aggregate outcome rates and matched-seed differences against baseline.

`temperature=0` uses greedy decoding. Repeating seeds at that setting is a reproducibility check rather than independent statistical sampling. Use a positive temperature with paired seeds to measure stochastic variability. The outcome score is computed by the deterministic fixture, while persona, coherence and the weighted composite require independent blinded ratings and remain null here.

This is a fictional train-station decision experiment. Its medical events are authored game rules, never treatment guidance.
