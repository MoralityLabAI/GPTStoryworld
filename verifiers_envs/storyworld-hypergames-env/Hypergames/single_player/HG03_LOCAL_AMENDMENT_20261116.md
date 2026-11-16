# HG-03 local execution instrumentation, 2026-11-16

Status: written before any local development or private neural call. The private
manifest has not been located or opened. Original registration, prompts, decoder,
environment, controller code, and source-hashed receipts are preserved byte for byte.

The requested command names are corrected to their committed names:
`tests/test_hypergames_qwen_eval.py` and receipt `hypergames_qwen_preflight`.
The initial sandbox test attempt encountered Windows temporary-directory access
errors; using task-local TEMP/TMP resolves them without a source change.

The additive `hypergames_qwen_local.py` runner delegates requests and response
validation to the frozen `LocalChatBackend`, and delegates action decoding to
the frozen `parse_action`. It records full request messages, raw response bytes
(base64), parsed response body, visible observations, legal and selected actions,
realized post-action rewards, timestamps, token usage, and inference latency.
Journal records are flushed and fsynced after every turn and episode. There are
no retries. Transport or malformed-envelope failures are retained as operational
failures and terminate the episode by safe abstention, separately from model
abstention. They must never support a positive capability or alignment claim.

Sampled process RSS, system RAM usage and RTX 3050 VRAM are recorded every
approximately 0.5 seconds plus sampling overhead. Peaks are sampled lower bounds;
system RAM includes unrelated applications. Runtime logs establish GPU offload
and CPU buffer allocations. No workload targets an RTX 5080 or paid service.

A machine-readable configuration lock is created with the development run. Any
private run requires an identical lock before the private manifest is accessed.
This includes the source hashes, model identity, runtime build, prompts, endpoint,
and decoding contract. The run uses the server's embedded default chat template
and default reasoning mode, context 4096, one parallel slot, and 99 GPU layers
(all available layers offloaded when the model fits). No reasoning-budget or
chat-template override is made. Raw reasoning fields are preserved if returned.

Because this adds failure preservation and instrumentation to the original runner,
the local measurement cohort is labeled `HG-03/LOCAL-REPLAY-v1`. Original frozen
source and receipts continue to be independently replayed. Public development
results are exploratory; the four registered claims require all six committed
private seeds and their full 144-trial neural matrix.
