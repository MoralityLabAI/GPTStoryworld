# SW-PROV-03: Character-local knowledge and reaction design

This development extension of North Quay keeps a fixed latent world, three separate knowledge ledgers (editor, magistrate, registrar), and a separate social trust coordinate. The host samples exactly from 24 positive-mass assignments: uniform truth and shared/independent source prior, origin validity 2/3, perfect reporting when valid and a fair sign when invalid. Shared labels share validity and report. The editor and registrar begin knowing A; the magistrate knows B. The editor can consult for B, inspect lineage, and check A's validity. An optional one-time briefing, after consultation, transfers all acquired evidence to the councillors. Later investigations remain private and do not retroactively alter the recorded endorsement. All acquisitions cost one unit. Truth is fixed before play and is never disclosed automatically.

## Epistemic state and authored reactions

For actor i, retain the authenticated observations L_i (set of keyed values). Compute p_i=P(H=1|L_i) by exact marginalization, then project b_i=2p_i-1 into the actor's depth-1 Culpability pValue about char_vale. The separate depth-1 Trust pValue about char_editor is initially zero; a briefing with inspected lineage or a validity record sets it to 1/4, independent of the sign of the evidence. Identical evidence IDs are idempotent and inconsistent observations are rejected. Shared-origin and uncertain-lineage likelihoods are handled jointly. This law has no fallible authentication, conflicting signed revisions or strategic lying.

The three competing reaction desirabilities are:

    D(accuse) = (5*b_i-3)/2 + Trust_i/8
    D(clear)  = (-5*b_i-3)/2 + Trust_i/8
    D(defer)  = 0

The actor chooses maximum desirability, deferring on a tie with zero. The epistemic coefficient comes from the +1/-4 judgment payoff under its own posterior. The trust coefficient is a provisional authoring choice. The host-only projection exposes keyrings [Culpability,char_vale] and [Trust,char_editor]; the public client never receives the private projection. These equations are design formulas for a native authoring pass, not validated native SWMD expression strings.

Exact witness: A accuses and B clears. Before any briefing the registrar has b=2/3 and magistrate b=-2/3. The editor establishes independent origins and invalid A. Both councillors retain their initial states until the briefing. After it, both have b=-2/3 and favor clearance. When two positive reports share one origin, they yield P(H)=5/6; if that common origin is invalidated this falls to 1/2. With known independent origins, two positives give 25/26, and invalidating A leaves 5/6. With unknown lineage, invalidating A after two positives gives 11/18.

## Outcome calibration

Base player reward +1 correct, -4 false, 0 defer. A correct judgment matching the magistrate's recorded endorsement gains an additional 1/4. This explicitly values successful communication without paying for a false judgment. Score factual judgment and endorsement separately. Budgets 2,3,4 are variants of the same law.

| Budget | Immediate judgment utility | One-step replanning | Two-step replanning | Full | Full without briefing |
|---|---:|---:|---:|---:|---:|
| 2 | 1/6 | 49/72 | 49/72 | 49/72 | 49/72 |
| 3 | 1/6 | 205/288 | 253/288 | 253/288 | 25/36 |
| 4 | 1/6 | 35/48 | 43/48 | 43/48 | 25/36 |

At budget four the full and no-brief policies both achieve correct/false/defer = 29/36, 1/36, 1/6. Full obtains endorsement on all correct judgments, adding exactly 29/144 utility, with expected acquisition cost 23/6 versus 95/36. The gain is social reward under the designed objective, not improved factual accuracy. Two-step replanning reaches full utility in all variants. The root horizon curve at budget four is [1/6,2/3,49/72,253/288,43/48]; the opening-state optimal horizon is four, yet a cheaper receding-horizon policy suffices.

Sensitivity audit: among 26 distinct legal factual briefing ledgers containing inspected lineage and/or validity, changing trust from 0 to 1/4 flips zero reactions. The coefficient shifts scores by 1/32 but is decision-inert in this discrete family. Do not count it as effective complexity; remove it from production reaction formulas unless a separate authored social mechanism makes it consequential. One reproducible check from the script directory:

    python -c "from provenance_characters import *; ledgers={tuple(sorted((k,x[k]) for k in ('A','B')+extra)) for _,x in LAW for extra in (('shared',),('valid_A',),('shared','valid_A'))}; print(len(ledgers),sum(reaction(dict(x),F(0))!=reaction(dict(x),F(1,4)) for x in ledgers))"

For general authoring: distinguish belief movement (bounded pValue), chosen reaction changes (argmax), and realized utility effects. Audit each formula variable under legal histories and counterfactual perturbations; avoid treating a nonzero coefficient or a large number of variables as proof of meaningful complexity.

## Verification and scope

Six new Python tests plus ten earlier tests pass. The exact session audit traverses 6,624 world-specific prefixes, including 4,968 terminal paths, and 2,232 public histories summed over the three budgets. Public packets are identical for the same opening report, actions and acquired factual observations even when hidden truth differs; the comparison key deliberately excludes the briefing reaction. It therefore detects hidden-world dependence in that reaction. Reversing latent-world enumeration leaves scores identical. The receipt regenerated byte for byte. The existing strict TypeScript client compiles and accepts a complete council-session exchange.

This is one finite law with three related budget variants, not independent samples. EvalMath preflight full minus two-step returns REDESIGN_OR_PILOT_ONLY: zero gain, 0.05 provisional effect floor, 0.15 target, four planned comparisons, no sealed holdout, no calibrated independent shams, no neural claim. Enumeration reversal is a structural check. No paid compute. Social sensitivity and preflight were development diagnostics.

Run from codex-skills/storyworld-building/scripts:

    python -m unittest -v test_provenance_design_audit.py test_provenance_session.py test_provenance_characters.py
    python verify_provenance_characters.py --output /tmp/character_receipt.json
    python provenance_characters.py --budget 4

The last command is JSONL: send one object per line, e.g. {"action":"consult"}. Use --grade-file only on an isolated evaluator host. Existing public session schema and TypeScript transport remain unchanged. No live editor integration, native SWMD parser validation, or production social-world playthrough. Next: add an author-visible reaction-variable sensitivity report to the actual editor, extend to actor-specific goals and uncertain testimony, and test social decisions where communication changes opportunities rather than merely awarding a terminal bonus.
