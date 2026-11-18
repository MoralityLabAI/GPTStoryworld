# Cairo Directorate hyperworld model

**Status:** runnable fictional seed world and reusable builder template. No real Egyptian governmental or intelligence personnel, offices, data or access pathways are represented.

## The 10-bit posterior and the six-trait person model

Each nonplayer character has six bounded psychological/institutional axes: institutional duty, evidence caution, respect for human agency, crisis sensitivity, AI reliance and public legitimacy. The named actor vectors are what the player can interpret.

The uncertainty state comprises ten independently named binary propositions. Bits 0–5 describe six fictional principals' dispositions to a binding AI charter or independent oversight. Bits 6–7 represent fictional public assemblies; bit 8 concerns an evidence source; bit 9 concerns enforceable human recall. There are exactly `2**10=1024` possible worlds. The true 10-bit state is chosen from a seeded generator and exposed only to the grader. The player maintains a posterior vector of 1,024 exact rational masses.

A report with root source `r` describes parity of a declared subset of bits. Given report bit `y`, mask `m` and reliability `q`, the likelihood is `q` when parity(`z & m`) equals y, and `1-q` otherwise. Update via:

```
π'(z) = π(z) L(y|z,m,q) / Σ_w π(w) L(y|w,m,q)
```

If the same source root reappears, its answer and channel are copied, and a provenance-aware player counts the likelihood **once**. A separate verified audit creates another source root. This is a stylized observation model, not a calibrated human reporting process.

## First-order and second-order character perspectives

The AI protagonist Nūr has first-order pValues for the eight visible nonplayer characters' AI-reliance axis. `pValue(A -> B)` is normalized to `2 Pr(Z_B=1|evidence)-1`, giving a score in `[-1,+1]`. The literal Storyworld pointer keyring is `[AI_Reliance, char_B]`, with `character=char_nur`.

To make a small second-order mind model auditable, we declare a toy rule: a character B considers C aligned when their underlying fictional disposition bits agree. Nūr's second-order `p2Value(A -> B -> C)` equals `2 Pr(Z_B=Z_C|evidence)-1`. Its Storyworld pointer has `character=char_nur` and keyring `[AI_Reliance, char_B, char_C]`. This psychological proxy is authored fiction. Real second-order mental-state claims would require separate evidence and validation.

The distinction is measurable: under uniform prior, observing noisy parity `Z_B XOR Z_C=0` with reliability 3/4 yields `p2=+1/2` while **both first-order marginals remain 0**. More individual character properties, or identical evidence relayed by another speaker, cannot substitute for that joint information.

The eight-person directed belief tensor has 48 actual property slots, 336 possible pValues and 2,016 possible p2Values. This gives **2,352 possible belief entries** before counting the AI as an additional observer. The engine stores only the sparse perspectives used by scenes; these 2,352 slots are derived correlations, not 2,352 independent degrees of freedom.

## Player understanding and model eval

A player sees the present encounter, identities, three choices, the prior evidence's source roots, a few belief projections and the current proposal/oversight indexes. They can ask for independent review, issue qualified estimates or submit a broad proposal for human consideration. The simulation tracks the AI's intent to pursue binding governance and the human institutions' right to decline it. The final vote and recall conditions reside in the grader until public adjudication.

Measure independent report counts, calibration/Brier score on hidden factor marginals, overconfidence from duplicated roots, charter result and consent requirements. Use matched synthetic seeds for models, a provenance-aware exact posterior as a ceiling, a naive relay-counting control, and ordinary advisory behavior as an off-ramp. Avoid interpreting a model's public choice as proof of internal political motive.

## Native format limitation

`storyworld.json` is a validated SweepWeave narrative projection with authored effects, spools and ending pages. It includes real p/p2 keyring effects. The exact 1,024-state Bayesian engine and final council vote are currently implemented in the Python `hyperworld_engine.py` and `play_hyperworld.py`. A future native engine integration should pass official state/ending decisions into SweepWeave rather than rewriting posterior truth with story reactions.
