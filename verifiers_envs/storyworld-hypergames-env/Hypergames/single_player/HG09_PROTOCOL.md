# HG-09: Frontier-model goal reasoning and causal discovery

**Prospective, source-locked harness; no live API data yet.** Extends the GPTStoryworld HG-02 five-action information-gathering problem and HG-08 six-cause intervention gym. Cross-provider scores will come only from model API responses. HG-03's private seeds stay outside the experiment.

## Registrations and execution

Source base: GPTStoryworld HG-08 PR #14 at `855f2f3d5fc4e26518112925de4a53e6dc9bc42e`. The initial publicly known roster is stored in `models_hg09.json`. Model IDs, effort, price bounds, prompts and input dimensions must be recorded per replay.

The *pilot*, not a confirmatory held-out evaluation, uses existing public development seeds. HG-02 uses seed 202611170801 at 140 dimensions, seed 202611170802 at 140 dimensions with a four-action horizon, and seed 202611170801 at 512 dimensions. Each is paired across both sealed hidden modes. HG-08 uses seed 202611170801 in core-140 and seed 202611170802 in native-512, k=1, with a 64-query budget. This avoids promising robust estimates from six or two episodes. After an audited pilot, a future preregistration can provide fresh held-out seeds.

Each turn sends only the environment's public observation, and requires a strict JSON choice. HG-02 actions: `{ "action": "audit" }` or another listed action. HG-08 actions: `{ "query_indices": [1,4] }`, `{ "release_support": [[1,2,3,4,5,6]] }`, or `{ "abstain": true }`. The HG-08 support list is graded only after release; the oracle never reveals the true cause set in its replies. Invalid output abstains. Provider failures are recorded and excluded from valid-score denominators; a budget stop marks the receipt incomplete. Live runs fail preflight when a selected model's provider credential is absent, preventing fake abstention scores from unavailable APIs.

The entire transcript stores the visible observation, model final JSON, provider-exposed reasoning *summary or field*, token usage, latency, and response identifier. This is **not raw hidden chain-of-thought access**. OpenAI Responses API summaries, Anthropic summarized thinking, Gemini summarized thoughts, and OpenRouter's optional provider-exposed reasoning field have different semantics and cannot be compared as verbatim thought trajectories. Score actual actions and visible evidence first. Providers may return no reasoning artifact.

## Budget

Use explicit `--live`, `--max-usd`, and `--max-calls`. The cost reserver charges the user-specified *upper-bound model rates* against a conservative input-byte bound and the requested maximum output tokens **before each request**. This controls nominal standard text-token spend for the configured provider; request-dependent features, regional surcharges, tool calls or router fees should be reflected in the configured upper-bound rates. The pilot enables no billable tools or search. The stored reserve is an upper bound, not a statement of charged cost. The user must independently provide API credentials. Eligible ChatGPT Pro subscriptions can claim API credits for an owned, linked OpenAI API organization (see https://developers.openai.com/api/docs/guides/chatgpt-api-credits); those credits can cover OpenAI API calls after activation. Claude and Gemini require their respective provider accounts. The ChatGPT app's interactive model picker cannot be programmatically called through this harness.

OpenAI rates are from `https://developers.openai.com/api/docs/pricing`; Anthropic from `https://platform.claude.com/docs/en/about-claude/pricing`; Gemini from `https://ai.google.dev/gemini-api/docs/pricing`. Gemini model rates are set to the higher >200k-context tier to keep the local cap conservative. Check account-specific availability and tariffs before enabling live calls.

## Local Windows runner

From `verifiers_envs/storyworld-hypergames-env`, use PowerShell:

```powershell
$env:PYTHONPATH = 'src'
& 'C:\Python311\python.exe' -m unittest discover -s tests -p 'test_hg09_frontier.py' -v
& 'C:\Python311\python.exe' -m spiral_ln.hg09_frontier --config Hypergames/single_player/models_hg09.json --out output/hg09_dry.json --task hg02
# Configure OPENAI_API_KEY / ANTHROPIC_API_KEY / GEMINI_API_KEY as applicable.
& 'C:\Python311\python.exe' -m spiral_ln.hg09_frontier --config Hypergames/single_player/models_hg09.json --out output/hg09_hg02_paid.json --task hg02 --live --max-usd 25 --max-calls 100 --max-output-tokens 4096
& 'C:\Python311\python.exe' -m spiral_ln.hg09_scores output/hg09_hg02_paid.json --out output/hg09_hg02_summary.csv
```

For HG-08 use `--task hg08` and a larger call cap, since 64 intervention turns per episode are possible. Start with a one-model subset, especially at 512 dimensions. Every output path is create-only and should be gitignored. Store credentials as environment variables, never in source or receipts.

## Interpretation

Core comparisons: safe release rate, false accepts, causal support recovered per query, token cost, latency, and error rate. Provider summaries can be inspected to classify observable mistake patterns (incorrect parity calculations, premature releases, missing audits), with any interpretations labelled post hoc. Report matched seed-level outcomes and model-effort settings. The pilot's small roster is designed to debug provider formatting and costs, not to claim frontier rankings.
