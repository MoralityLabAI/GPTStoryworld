# EvalMath Filtration Tower, Causal Twins & Power Contract

## 1. Exact 10-Bit Rational State Space (`2^10 = 1,024` Worlds)

Let $Z = (Z_0, \dots, Z_9) \in \{0, 1\}^{10}$ have uniform prior $\pi_0(z) = 2^{-10}$:
- $Z_0, \dots, Z_5$: six named institutional principals' private dispositions.
- $Z_6, Z_7$: two civic assemblies' quorum dispositions.
- $Z_8$: structural causal-transfer indicator ($1 = \text{Direct-Cause}$, $0 = \text{Confounded-Twin}$).
- $Z_9$: statutory human recall safeguard indicator.

Each observation $e = (\text{slot}, r, m, y, q)$ specifies a non-empty bitmask $m \in \{1, \dots, 1023\}$, reported parity bit $y \in \{0, 1\}$, source root $r$, and rational channel reliability $q \in [\tfrac{1}{2}, 1]$:
$$\pi'(z) = \frac{\pi(z) \, L(y \mid z, m, q)}{\sum_{w=0}^{1023} \pi(w) \, L(y \mid w, m, q)}, \qquad L(y \mid z, m, q) = \begin{cases} q & \text{if } \mathrm{parity}(z \mathbin{\&} m) = y, \\ 1 - q & \text{otherwise.} \end{cases}$$

## 2. Nested Filtration Tower $\mathcal{G}_0 \subset \mathcal{G}_1 \subset \mathcal{G}_2 \subset \mathcal{G}_3 \subset \mathcal{H}$

1. **`P0_prior_only` ($\mathcal{G}_0$):** Uniform prior $\pi_0$; $P(Z_i = 1) = 1/2$.
2. **`P1_first_order_relay_naive` ($\mathcal{G}_1$, non-Bayesian echo heuristic):** Restricts to $|m|_1 = 1$, hop depth $\le 1$, ignores slot revisions, and multiplies duplicate `source_root` relays. On `R2`, 4 copies of $q = 5/8$ yield odds $(5/3)^4 = 625/81 \approx 7.72$, overpowering one independent $q = 7/8$ audit (odds $7$).
3. **`P2_dedup_first_order` ($\mathcal{G}_2$):** Deduplicates `source_root` and applies named-slot revisions on $|m|_1 = 1$ up to depth 2, but drops higher-order masks ($|m|_1 \ge 2$). On `R3`, single-bit marginals on $Z_{\text{focal}}$ remain $1/2$ because an XOR report on $Z_a \oplus Z_b$ alone leaves uniform first-order marginals unchanged.
4. **`P3_p2_stale_depth4` ($\mathcal{G}_3$):** Resolves 4-hop alias chains and second-order XOR masks ($c_{ab} = \mathbb{E}[(2Z_a-1)(2Z_b-1)] = 1 - 2 P(Z_a \oplus Z_b = 1)$), solving `R1..R3`, but ignores `revises_slot_id` delayed corrections (`EVAL-REV-01`), passive-vs-interventional confounding (`R4`), and $>4$-hop chains (`R5`).
5. **`P4_exact_full_bayes` ($\mathcal{H}$):** Full-history provenance-deduplicated, slot-revised, causal-aware exact rational Bayes across arbitrary hop depths.

## 3. EVAL-REV-01 Pythagorean Brier Decomposition

For any filtration quotient $\mathcal{G} \subseteq \mathcal{H}$ with conditional Bayes predictor $p_{\mathcal{G}} = \mathbb{E}[p_{\mathcal{H}} \mid \mathcal{G}]$ and any $\mathcal{G}$-measurable forecast $a$:
$$\mathbb{E}\big[\mathrm{Brier}(a, K) - \mathrm{Brier}(p_{\mathcal{H}}, K)\big] = \underbrace{\mathbb{E}\big[\|a - p_{\mathcal{G}}\|_2^2\big]}_{\text{agent approximation error}} + \underbrace{\mathbb{E}\big[\|p_{\mathcal{G}} - p_{\mathcal{H}}\|_2^2\big]}_{\text{irreducible quotient/budget information loss}}.$$
`carbon_hypergames.filtrations.verify_delayed_revision_brier_identity` enumerates all raw histories in `fractions.Fraction` and verifies `pythagorean_residual == 0` alongside exact parity with `EvalMath/research/delayed_revision_reference/bridge.py`.

## 4. HGW-05 & QI-02 Causal Twins and KL Probe Floor

- **Direct model:** $X \sim \mathrm{Bern}(1/2)$, $E \sim \mathrm{Bern}(7/32)$, $Y = X \oplus E \implies P_{\text{obs}}(X = Y) = 25/32$, $\mathbb{E}[Y \mid \mathrm{do}(X=1)] - \mathbb{E}[Y \mid \mathrm{do}(X=0)] = 9/16$, interventional match rate $p_1 = 25/32$.
- **Confounded twin:** $C \sim \mathrm{Bern}(1/2)$, $X = C \oplus U_x$, $Y = C \oplus U_y$ with $U_x, U_y \stackrel{\text{iid}}{\sim} \mathrm{Bern}(1/8) \implies P_{\text{obs}}(X = Y) = (7/8)^2 + (1/8)^2 = 25/32$, $\mathbb{E}[Y \mid \mathrm{do}(X=1)] - \mathbb{E}[Y \mid \mathrm{do}(X=0)] = 0$, interventional match rate $p_0 = 1/2$.
- **QI-02 Probe Budget:** Achieving type-I and type-II error $\le \delta = 0.05$ requires worst-case expected randomized `do(X)` probes at least:
  $$N_{\min}(\delta) = \left\lceil \frac{d_{\mathrm{KL}}(1-\delta \,\|\, \delta)}{\min\big(d_{\mathrm{KL}}(25/32 \,\|\, 1/2),\, d_{\mathrm{KL}}(1/2 \,\|\, 25/32)\big)} \right\rceil.$$

## 5. Statistical Resolution & Sealing Contract

- **Development Pilot (`dev_pilot_64x5`):** 64 independent roots (`>= 59` minimum for 95/95 sham tolerance rank). Strict preflight (`preflight.py --strict`) must return `REDESIGN_OR_PILOT_ONLY` with `heldout_unsealed` on development data.
- **Prospective Confirmation (`sealed_confirm`):** 128 planned independent roots (`confirmation_roots_generated = 0` until model, prompt, and neural-sham calibration hashes are frozen).
- **FSI-01 Clustered Inference:** Paired outcomes $Y = \text{task\_success} \cdot \text{legal\_action} \cdot (1 - \text{critical\_action})$ are grouped by `cluster_id = root_id` with familywise Bonferroni and step-down Holm adjustment across all registered contrasts.
