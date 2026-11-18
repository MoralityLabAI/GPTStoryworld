# HGW-03: character-scoped reaction mathematics and Dirac distances

**Status:** source-reviewed implementation, development tests. The baseline HGW-02 replay remains frozen. These are authored mechanics for a fictional council rather than empirical estimates of individuals.

## Audit of HGW-02

The seven ordinary encounters offered 42 options and 84 ordinary reactions. Across all 92 reactions, 80 inclination scripts were constant. Two generic response texts appeared 42 times each. The original ordinary effect rule rotated through unrelated principals, sometimes leaving the scene speaker unaffected. The ending chooser also gave eight possible verdict reactions fixed ordered scores even though the canonical Python engine owns the vote.

## Scoped mathematics

First declare the scene's speaker, relevant counterparty and focal p2 edge. For each ordinary reaction, MathScope(vars_per_character=b,pvalue_terms=q1,p2value_terms=q2) selects at most 2b+q1+q2 public coordinates for the two participating characters, with 1<=b<=4, 0<=q1<=2 and 0<=q2<=1. The default (2,2,1) yields six terms on the first two turns and seven thereafter. Its named participants agree with the actual dialogue.

Each bounded x_j lies in [-1,1]. Choose authored signed coefficients c_j with sum_j abs(c_j)<=0.34, and define F=Σ c_j x_j, I0=1/2+F and I1=1/2-F. This places both scores in [0.16,0.84] and allows a different reaction to win as the game state changes. These numbers are fictional desirability scores; human consent remains an independent quantity. Each relevant action selects different trait axes, such as evidence caution for audits and human agency for recall disputes.

Each ordinary reaction nudges at least five coordinates: one salient trait for each participant, two first-order beliefs owned by Nūr and Nūr's Human_Agency. Late turns add a focal second-order keyring. Changes are bounded and action-specific.

## HG-01 Dirac geometry

Compute the squared numeric Clifford distance d_D(x,y)^2=Σ_j (w_j(x_j-y_j))^2 without allocating spinor matrices. Default positive weights are 1 for actual bounded traits, 3/4 for first-order pValues and 1/2 for second-order p2Values. Aggregate repeated keyrings before squaring. The nominal distance is determined by authored coefficients; in opt-in runtime mode, use the realized post-clamp deltas.

All 42 ordinary options have nonzero paired transition separation in the source audit. For the published default scope the squared reaction-pair distances lie between 0.00215552 and 0.00824538. The measurements are properties of the authored state transitions. A smaller formula scope may discard coordinates; preserve the winner only when the absolute projected preference gap exceeds the L1 bound for omitted signed terms.

## Runtime and acceptance

The exact posterior, source-root deduplication and legal votes remain owned by hyperworld_engine.py. The optional CairoHyperworld(seed,reaction_math=True,math_scope=MathScope(...)) reads public bounded values, chooses the higher scored reaction, applies narrative and trait effects and records a realized squared metric. Default reaction_math=False preserves the HGW-02 receipt.

The static SweepWeave export marks its verdict option hyperworld_native_verdict_required; it cannot certify a verdict from an authored score. Treat any new ending-frequency claim as a fresh opt-in experiment with its own frozen seed roster.

Validation requires every ordinary option to have distinct named-character responses with nonconstant arithmetic inclinations and five or more targeted effects; stable existing ID and keyring semantics; the SweepWeave validator; reproducible generated fixture; the original baseline replay; and public-only evidence traces. Before assigning learned model significance, quantify branch choice margins, projection stability, saturation, effect reachability and ending changes under seeds held outside development.

## Transfer to Three Voices in the Fog

For each involved AI select b_i of its 20 actual axes, two or more public axes for each relevant constituency, a small declared world-variable budget, and only legal observer-owned p and p2 projections. Pair or triple terms must correspond to real named edges in the fictional scene. Normalize total coefficient magnitude independently of the number of people and variables. A visible effect can differ substantially from what a rival inferred through fog; therefore publish both per-actor subjective and full-world grader-only distances. Never leak sealed RSI tests or another actor's private resources into the decision surface.
