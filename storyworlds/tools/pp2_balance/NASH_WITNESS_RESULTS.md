# PP2-BAL-08 results: witness transport, sparse strategic signal

Development-only campaign; six fresh coefficient roots held out by structural family, eight matched proposal arms with 8/16/32/64 unique-candidate budgets. The existing 960 training edges were independently relabeled using exact rational witness and dual transport. The six test runs cover 2,933 distinct candidate worlds, 171 distinct games and 376,250 native reader transitions; 432 independent post-search probe edges.

## Counterfactual evidence

356/960 training edges change the game, 931 have exact worst-TV deltas, and only 59 change exact worst-TV. There are 63 author-loss-changing edits with identical games. 107 old worst-case witnesses become infeasible; 102 of those lack a certified improvement in W. Parent witness/dual transport closes the interval exactly on 785/960 edges. Test probes: 206/432 game changes, 37 exact worst-TV changes, 43 witness invalidations (33 without certified improvement), and 343 exact transported intervals. One test edge introduces a newly binding deviation; none of the training edges do.

## Search verdict

At 8 queries, factored J=0.6625 versus direction 0.7479167 and shuffled factored 0.76875; parent-priority and geometry-scalar tie the factored model. At 16 queries, scalar 0.6416667 beats factored 0.6520833. At 32/64 queries, scalar and factored tie at 0.6416667. Parent-priority reaches 0.6104167 at 64 queries, the best observed reference score in every root. Random-global reaches 0.6208333. At 64 queries the factored arm is only 0.0020833 ahead of its shuffled control. All snapshots admit a certified candidate. No global-optimum claim on the full coordinate spaces.

On post-search probes, factored admission accuracy is 0.599537 versus direction 0.537037 and shuffled 0.532407. Its delta-J MSE is 0.026923 versus scalar 0.025721 and direction 0.026432. Witness survival accuracy is 0.868056, below shuffled 0.898148; this is a highly imbalanced label. The factored learner does not earn promotion. Retain exact transport for audit and potentially for proof reuse. A predicted counterfactual bound remains a proposal heuristic, not an acceptance certificate.

The next experiment should prioritize reducing verifier work. Use identity and transported bound certificates to avoid recomputing robustness when the native reader produces an equivalent game or the transported interval closes; independently verify a target bound before using it. Compare cold computation, same-game caching, and transport with matched search trajectories and explicit counts of strategy evaluations and rational operations. Evaluate against the full independent screen on every development candidate before considering a live optimization. Keep no-certificate fallbacks and count all screening/transport costs.

Replay: node storyworlds/tools/pp2_balance/nash_witness_replay.mjs. Source and edited witnesses, rational gaps, labels, fitted models, trajectories and game screens are committed. The local execution was in a JavaScript isolate; hosted replay is pending at this commit. No native TRM/BPD training or new structural family is claimed. Production authoring assets remain unchanged.
