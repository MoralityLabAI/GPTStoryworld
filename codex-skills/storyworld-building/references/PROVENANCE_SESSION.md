# SW-PROV-02: playable provenance sessions

This extends SW-PROV-01 with an executable development fixture and a strict TypeScript public client. The North Quay Inquiry uses the same three finite variants and payoff contract (+1 correct, -4 false, 0 defer). Each session samples one latent world with exact rational weights before play begins. The evaluator fixes all outcomes, enforces prerequisites, consumes the acquisition budget, prevents repeated queries and grades the terminal judgment privately.

The JSONL service emits only the public text, acquired evidence ledger, legal choices, remaining budget and an SWMD-style live encounter card. The card uses ENC/T/OPT notation; it is an adapter surface, not a complete native SWMD file. The player does not receive unqueried observations or the selected world's truth, index or score. The optional grade file belongs on the host side. In any protected deployment the host must isolate the private sidecar, score output, process and random state from the player. This public development fixture is not a sealed benchmark.

The standalone TypeScript client validates packets, budgets, append-only evidence and action transitions, guards concurrent requests and exports a copied snapshot. Its transport is injectable. It currently has no connection to the live editor, persistent sessions, authentication or retry/resynchronization protocol. The canonical frontend inspected on main is React/JS and exposes a generation UI; no native TypeScript SWMD runtime was located in the inspected checkout.

## Exact audit

| Difficulty | Latent assignments | World-specific action prefixes | Terminal prefixes | Distinct public histories | Full utility |
| --- | ---: | ---: | ---: | ---: | ---: |
| K1 | 4 | 48 | 36 | 16 | 5/26 |
| K2 | 4 | 96 | 72 | 28 | 5/26 |
| K3 | 12 | 768 | 576 | 268 | 15/64 |
| Total | 20 | 912 | 684 | 312 | -- |

A public history here includes the ordered action path and acquired query outcomes. Counts include terminal decisions and are distinct from the earlier merged information-state counts. All equal public histories emit equal packets across compatible latent assignments. All four policy rollouts (one, two, macro and full) match the offline exact oracle in correct/false/defer rates and acquisition cost for all three variants. This is a finite functional check, not statistical evidence about reasoning ability. K1 one-step utility is 5/26, correcting the earlier chart. K3 two-step replanning attains 15/64 as well, at expected cost 11/4 rather than full's 5/2.

Ten Python unit tests pass, TypeScript strict compilation and the Node integration script pass, and the source-hashed session receipt regenerates identically. A terminal smoke playthrough completed. No model training or paid compute.

## Reproduction

Run in codex-skills/storyworld-building/scripts:

    python provenance_session.py --k 2
    python -m unittest -v test_provenance_design_audit.py test_provenance_session.py
    tsc --strict --target ES2022 --module commonjs --outDir build provenance_client.ts
    node test_provenance_client.cjs
    python verify_provenance_session.py --output /tmp/session_receipt.json

The committed session_receipt.json records the exact audit and source hashes. For automated play use python provenance_session.py --k 3 --jsonl and send one object per line, for example {"action":"read_ledger_a"}. The opening packet precedes all actions. Terminal grading is only returned internally or written to a deliberately configured private --grade-file.

## Limits and next integration

This is a narrow North Quay adapter, not a production storyworld. Its decision hub intentionally exposes all legal terminal and query actions; a native authoring pass must split the hub into small encounter cards, author reactions and social effects, and validate native exports and reader playthroughs. The SWMD card is generated rather than parsed by a native engine. No existing authored world, editor build or engine behavior changed. The next stage should connect a host transport and author-visible audit panel to the actual editor, with explicit public/private exports, then extend to character-specific knowledge and source revocation without changing the established hidden events. Preserve the earlier preflight verdict (development only). No independent confirmation roots exist.
