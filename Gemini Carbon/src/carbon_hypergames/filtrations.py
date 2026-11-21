"""Exact rational filtration tower, causal twins, delayed revision, and Dirac metrics.

Pure Python standard library (`fractions.Fraction`). Implements a 10-bit
(`2**10 = 1024` microstates) latent world space with five nested epistemic
filtrations so variable-reasoning hypergame rollouts have exact mathematical
oracles and proper-score decompositions compatible with MoralityLabAI/EvalMath:

- Exact 1,024-state rational Bayesian updating (`Fraction`) over:
  * signed single-bit witnesses (`y = z_i XOR noise`),
  * second-order XOR pair-parity witnesses (`y = z_i XOR z_j XOR noise`) that
    leave uniform first-order marginals invariant while shifting pair moments,
  * k-way hyperedge parity witnesses (`XOR_{i in S} z_i`),
  * multi-hop delegation / cipher chains resolved across `h` relational hops.
- Source-provenance deduplication (`root_id` counted once vs relay-naive product).
- EVAL-REV-01 delayed slot correction / retraction (`full_history` vs
  `stale_unrevised` vs `count_quotient`), plus an exact finite-domain checker
  for the Pythagorean Brier risk decomposition:
      E[Brier(a, Z) - Brier(p_H, Z)] = E[||a - p_G||_2^2] + E[||p_G - p_H||_2^2].
- HGW-05 / QI-02 observational-twin causal channels (`direct` vs `confounded`,
  both having observational agreement P(X=Y) = 25/32, separated by randomized
  interventions with E[Y|do(X=1)] - E[Y|do(X=0)] = 9/16 vs 0) and exact KL
  diagnostic probe-budget lower bounds.
- HGW-03 / HG-01 bounded reaction inclination formulas (`I_0 = 1/2 + F(x)` with
  L1 coefficient mass <= 0.34 => I in [0.16, 0.84]) and Clifford/Dirac realized
  effect norm `d_D^2 = sum_j (w_j * Delta_j)^2`.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

NUM_LATENT_BITS: int = 10
NUM_WORLDS: int = 1 << NUM_LATENT_BITS  # 1024
MAX_INCLINATION_L1: Fraction = Fraction(34, 100)

# Precomputed 512-element support tuples for instant C-speed integer sums:
_BIT_SUPPORT: Tuple[Tuple[int, ...], ...] = tuple(
    tuple(z for z in range(NUM_WORLDS) if (z >> i) & 1)
    for i in range(NUM_LATENT_BITS)
)
_XOR_PAIR_SUPPORT: Dict[Tuple[int, int], Tuple[int, ...]] = {
    (i, j): tuple(z for z in range(NUM_WORLDS) if (((z >> i) ^ (z >> j)) & 1))
    for i in range(NUM_LATENT_BITS)
    for j in range(i + 1, NUM_LATENT_BITS)
}
_PARITY_MASK_SUPPORT_CACHE: Dict[int, Tuple[int, ...]] = {}


def _mask_support(mask: int) -> Tuple[int, ...]:
    sup = _PARITY_MASK_SUPPORT_CACHE.get(mask)
    if sup is None:
        sup = tuple(z for z in range(NUM_WORLDS) if ((z & mask).bit_count() & 1))
        _PARITY_MASK_SUPPORT_CACHE[mask] = sup
    return sup


def bit_at(world: int, idx: int) -> int:
    return (world >> idx) & 1


def mask_parity(world: int, mask: int) -> int:
    return (world & mask).bit_count() & 1


def indices_to_mask(indices: Iterable[int]) -> int:
    mask = 0
    for idx in indices:
        if not 0 <= idx < NUM_LATENT_BITS:
            raise ValueError(f"latent bit index {idx} outside 0..{NUM_LATENT_BITS - 1}")
        mask |= 1 << idx
    if mask == 0:
        raise ValueError("parity mask must reference at least one latent bit")
    return mask


@dataclass(frozen=True)
class EvidenceEvent:
    """One public observation or amendment emitted during a hypergame rollout."""

    event_id: str
    turn: int
    slot_id: str
    source_root: str
    mask: int
    reported_bit: int
    reliability: Fraction
    is_relay_duplicate: bool = False
    revises_slot_id: Optional[str] = None
    hop_depth: int = 1
    channel_kind: str = "parity_witness"  # parity_witness | revision | causal_probe | sham_noise

    def __post_init__(self) -> None:
        if self.reported_bit not in (0, 1):
            raise ValueError("reported_bit must be 0 or 1")
        if not (Fraction(1, 2) <= self.reliability <= Fraction(1, 1)):
            raise ValueError("reliability must lie in [1/2, 1]")
        if self.mask <= 0 or self.mask >= NUM_WORLDS:
            raise ValueError("mask must be a non-empty 10-bit mask")


def uniform_prior() -> Tuple[Fraction, ...]:
    w = Fraction(1, NUM_WORLDS)
    return (w,) * NUM_WORLDS


def bayes_update_mask(
    posterior: Sequence[Fraction],
    mask: int,
    reported_bit: int,
    reliability: Fraction,
) -> Tuple[Fraction, ...]:
    """Exact rational Bayes update over all 1,024 latent worlds."""
    q = Fraction(reliability)
    q_comp = Fraction(1, 1) - q
    unnorm: List[Fraction] = [Fraction(0, 1)] * NUM_WORLDS
    total = Fraction(0, 1)
    for z in range(NUM_WORLDS):
        match = mask_parity(z, mask) == reported_bit
        w = posterior[z] * (q if match else q_comp)
        unnorm[z] = w
        total += w
    if total == 0:
        raise ValueError("zero normalizing mass in exact rational Bayes update")
    return tuple(w / total for w in unnorm)


def posterior_from_events(
    events: Sequence[EvidenceEvent],
    *,
    mode: str = "exact_full_bayes",
    max_hop_depth: Optional[int] = None,
) -> Tuple[Fraction, ...]:
    """Compute the 1,024-state rational distribution under a declared filtration.

    Modes:
    - `prior_only`: uniform 1/1024 prior (ignores public evidence).
    - `first_order_relay_naive`: updates ONLY on single-bit masks (`bit_count==1`),
      double-counts repeated source relays, and ignores delayed slot revisions.
    - `dedup_first_order`: deduplicates `source_root` and honours revisions on
      single-bit masks, but drops higher-order XOR/hyperedge masks (`bit_count>=2`)
      and multi-hop chains beyond depth 2.
    - `p2_stale_no_revision`: deduplicates `source_root` and incorporates pair/k-way
      parity masks up to depth 4, but ignores `revises_slot_id` amendments (stale state).
    - `exact_full_bayes`: deduplicates `source_root`, resolves all `revises_slot_id`
      replacements on named slots, drops `sham_noise` channels with `q=1/2`, and
      updates across all masks up to `max_hop_depth` (unlimited if None).
    """
    if mode == "prior_only":
        return uniform_prior()

    if mode not in {
        "first_order_relay_naive",
        "dedup_first_order",
        "p2_stale_no_revision",
        "exact_full_bayes",
    }:
        raise ValueError(f"unknown filtration mode: {mode}")

    # Resolve active observations according to the filtration's memory/quotient rules.
    if mode == "first_order_relay_naive":
        active: List[EvidenceEvent] = [
            ev
            for ev in events
            if ev.revises_slot_id is None
            and ev.mask.bit_count() == 1
            and ev.hop_depth <= (max_hop_depth or 1)
        ]
    elif mode == "dedup_first_order":
        slot_map: Dict[str, EvidenceEvent] = {}
        seen_roots: set[str] = set()
        for ev in events:
            if ev.hop_depth > (max_hop_depth or 2):
                continue
            if ev.mask.bit_count() != 1:
                continue
            if ev.revises_slot_id is not None:
                slot_map[ev.revises_slot_id] = ev
                continue
            if ev.source_root in seen_roots:
                continue
            seen_roots.add(ev.source_root)
            slot_map[ev.slot_id] = ev
        active = list(slot_map.values())
    elif mode == "p2_stale_no_revision":
        seen_roots = set()
        active = []
        for ev in events:
            if ev.revises_slot_id is not None:
                continue
            if ev.hop_depth > (max_hop_depth or 4):
                continue
            if ev.source_root in seen_roots:
                continue
            seen_roots.add(ev.source_root)
            active.append(ev)
    else:  # exact_full_bayes
        slot_map = {}
        seen_roots = set()
        for ev in events:
            if max_hop_depth is not None and ev.hop_depth > max_hop_depth:
                continue
            if ev.revises_slot_id is not None:
                # Named-slot replacement (EVAL-REV-01): supersede prior slot record.
                slot_map[ev.revises_slot_id] = ev
                seen_roots.add(ev.source_root)
                continue
            if ev.source_root in seen_roots:
                continue
            seen_roots.add(ev.source_root)
            slot_map[ev.slot_id] = ev
        active = list(slot_map.values())

    # Exact integer-numerator accumulation: every active event e has reliability
    # q_e = a_e / b_e and complement (b_e - a_e) / b_e with a common denominator
    # b_e across all 1,024 worlds, so b_e cancels identically in normalization!
    weights_int = [1] * NUM_WORLDS
    for ev in active:
        q = Fraction(ev.reliability)
        a_num = q.numerator
        b_comp = q.denominator - a_num
        odd_sup = set(_mask_support(ev.mask))
        if ev.reported_bit == 1:
            for z in range(NUM_WORLDS):
                weights_int[z] *= a_num if z in odd_sup else b_comp
        else:
            for z in range(NUM_WORLDS):
                weights_int[z] *= b_comp if z in odd_sup else a_num
    total_int = sum(weights_int)
    if total_int == 0:
        raise ValueError("zero normalizing mass in exact rational posterior")
    frac_cache = {w: Fraction(w, total_int) for w in set(weights_int)}
    return tuple(frac_cache[w] for w in weights_int)


def _to_common_int_weights(posterior: Sequence[Fraction]) -> Tuple[List[int], int]:
    distinct = set(posterior)
    distinct_denoms = {p.denominator for p in distinct if p != 0}
    if not distinct_denoms:
        return [0] * len(posterior), 1
    common_d = math.lcm(*distinct_denoms)
    scale_cache = {p: p.numerator * (common_d // p.denominator) for p in distinct}
    return [scale_cache[p] for p in posterior], common_d


def bit_marginal(posterior: Sequence[Fraction], idx: int) -> Fraction:
    """Exact P(Z_idx = 1) under the 1,024-state posterior."""
    w_ints, common_d = _to_common_int_weights(posterior)
    num = sum(w_ints[z] for z in _BIT_SUPPORT[idx])
    return Fraction(num, common_d)


def mask_one_probability(posterior: Sequence[Fraction], mask: int) -> Fraction:
    """Exact P(parity(Z & mask) = 1) under the 1,024-state posterior."""
    w_ints, common_d = _to_common_int_weights(posterior)
    num = sum(w_ints[z] for z in _mask_support(mask))
    return Fraction(num, common_d)


def signed_moment(posterior: Sequence[Fraction], idx: int) -> Fraction:
    """m_i = E[2*Z_i - 1] in [-1, +1]."""
    return Fraction(2, 1) * bit_marginal(posterior, idx) - Fraction(1, 1)


def pair_correlation_moment(posterior: Sequence[Fraction], idx_a: int, idx_b: int) -> Fraction:
    """c_ab = E[(2*Z_a - 1)*(2*Z_b - 1)] in [-1, +1].

    Note: (2*Z_a - 1)*(2*Z_b - 1) = +1 iff Z_a == Z_b (XOR == 0), else -1.
    Therefore c_ab = 1 - 2 * P(Z_a XOR Z_b == 1).
    """
    if idx_a == idx_b:
        return Fraction(1, 1)
    mask = (1 << idx_a) | (1 << idx_b)
    p_xor = mask_one_probability(posterior, mask)
    return Fraction(1, 1) - Fraction(2, 1) * p_xor


def project_social_beliefs(
    posterior: Sequence[Fraction],
    principal_ids: Sequence[str],
    trait_name: str,
    protagonist_id: str,
) -> Dict[str, Dict[Tuple[str, ...], Fraction]]:
    """Project exact posterior first- and second-order moments onto Storyworld keyrings.

    Returns bounded values in [-1, +1] (NOT statistical p-values):
    - `pvalues`: mapping `observer_id -> {(trait_name, target_id): score}` (len-2 keyring)
    - `p2values`: mapping `observer_id -> {(trait_name, believer_id, target_id): score}` (len-3 keyring)
    """
    n_p = len(principal_ids)
    if n_p > 8:
        raise ValueError("at most 8 principal character bits (0..7) supported in 10-bit basis")

    w_ints, common_d = _to_common_int_weights(posterior)
    m_num = [sum(w_ints[z] for z in _BIT_SUPPORT[i]) for i in range(n_p)]
    m = [Fraction(2 * m_num[i] - common_d, common_d) for i in range(n_p)]
    c: Dict[Tuple[int, int], Fraction] = {}
    for i in range(n_p):
        c[(i, i)] = Fraction(1, 1)
        for j in range(i + 1, n_p):
            x_num = sum(w_ints[z] for z in _XOR_PAIR_SUPPORT[(i, j)])
            cij = Fraction(common_d - 2 * x_num, common_d)
            c[(i, j)] = cij
            c[(j, i)] = cij

    pvalues: Dict[str, Dict[Tuple[str, ...], Fraction]] = {protagonist_id: {}}
    p2values: Dict[str, Dict[Tuple[str, ...], Fraction]] = {protagonist_id: {}}

    for b_idx, b_id in enumerate(principal_ids):
        pvalues[protagonist_id][(trait_name, b_id)] = _clip_unit(m[b_idx])
        pvalues[b_id] = {}
        p2values[b_id] = {}
        for t_idx, t_id in enumerate(principal_ids):
            if b_idx == t_idx:
                continue
            # Officer b's first-order susceptibility perception of t:
            pvalues[b_id][(trait_name, t_id)] = _clip_unit(
                Fraction(3, 4) * m[t_idx] + Fraction(1, 4) * c[(b_idx, t_idx)]
            )
            # Protagonist's second-order belief about how b perceives t (sensitive to XOR covariance!):
            p2values[protagonist_id][(trait_name, b_id, t_id)] = _clip_unit(
                Fraction(1, 2) * m[t_idx] + Fraction(1, 2) * c[(b_idx, t_idx)]
            )
    return {"pvalues": pvalues, "p2values": p2values}


def _clip_unit(val: Fraction) -> Fraction:
    if val < -1:
        return Fraction(-1, 1)
    if val > 1:
        return Fraction(1, 1)
    return val


# ---------------------------------------------------------------------------
# EVAL-REV-01: Exact finite-domain delayed-revision Brier decomposition check
# ---------------------------------------------------------------------------


def verify_delayed_revision_brier_identity(
    n_slots: int = 4,
    regime_priors: Tuple[Fraction, ...] = (Fraction(9, 20), Fraction(7, 20), Fraction(1, 5)),
    match_probs: Tuple[Fraction, ...] = (Fraction(19, 20), Fraction(13, 20), Fraction(3, 20)),
    revised_slot: int = 0,
) -> Dict[str, object]:
    """Verify EVAL-REV-01 Pythagorean Brier decomposition by exact raw-history enumeration.

    Enumerates all `2**n_slots` initial bit vectors X, replacement bit Y in {0, 1},
    and latent regimes K in {0, 1, 2}. Compares full-history Bayes `p_H = P(K | X, S, Y)`
    against the count-restricted quotient `p_G = P(K | sum(X), S, Y)` (which forgets
    whether `X[revised_slot]` was originally 0 or 1) and any G-measurable predictor `a(G)`.
    """
    if len(regime_priors) != len(match_probs) or sum(regime_priors, Fraction(0, 1)) != 1:
        raise ValueError("regime_priors must sum to 1 and match match_probs length")
    num_regimes = len(regime_priors)

    # Joint probability table over (x_tuple, y_bit, k_regime):
    # First, P(K=k) = regime_priors[k]; given K=k, each X_i ~ Bern(match_probs[k]) iid,
    # and independent replacement Y ~ Bern(match_probs[k]).
    joint_h: Dict[Tuple[Tuple[int, ...], int], List[Fraction]] = {}
    quotient_groups: Dict[Tuple[int, int], List[Tuple[Tuple[int, ...], int]]] = {}

    for bits_int in range(1 << n_slots):
        x = tuple((bits_int >> i) & 1 for i in range(n_slots))
        s_x = sum(x)
        for y in (0, 1):
            masses: List[Fraction] = []
            for k in range(num_regimes):
                pk = match_probs[k]
                qk = Fraction(1, 1) - pk
                # Prior to revision X was generated; at revision slot `revised_slot`,
                # the accepted truth becomes Y while the other slots keep X[-revised_slot].
                # In the raw stream (X, Y), X_i (for i != revised_slot) and Y come from regime k,
                # while corrupted old slot X[revised_slot] had uniform 1/2 pre-correction noise.
                true_ones = sum(x[i] for i in range(n_slots) if i != revised_slot) + y
                true_zeros = n_slots - true_ones
                mass = regime_priors[k] * Fraction(1, 2) * (pk ** true_ones) * (qk ** true_zeros)
                masses.append(mass)
            joint_h[(x, y)] = masses
            quotient_groups.setdefault((s_x, y), []).append((x, y))

    total_mass = sum((sum(m, Fraction(0, 1)) for m in joint_h.values()), Fraction(0, 1))
    if total_mass != 1:
        raise AssertionError(f"joint probability mass {total_mass} != 1")

    p_h_map: Dict[Tuple[Tuple[int, ...], int], Tuple[Fraction, ...]] = {}
    for key, masses in joint_h.items():
        marg = sum(masses, Fraction(0, 1))
        p_h_map[key] = tuple(m / marg for m in masses)

    p_g_map: Dict[Tuple[int, int], Tuple[Fraction, ...]] = {}
    for g_key, h_keys in quotient_groups.items():
        g_masses = [
            sum((joint_h[hk][k] for hk in h_keys), Fraction(0, 1))
            for k in range(num_regimes)
        ]
        g_marg = sum(g_masses, Fraction(0, 1))
        p_g_map[g_key] = tuple(m / g_marg for m in g_masses)

    # Test predictor a(G): slightly damped G-measurable forecast 3/4 * p_G + 1/4 * uniform
    u = Fraction(1, num_regimes)
    a_g_map: Dict[Tuple[int, int], Tuple[Fraction, ...]] = {
        gk: tuple(Fraction(3, 4) * pg[k] + Fraction(1, 4) * u for k in range(num_regimes))
        for gk, pg in p_g_map.items()
    }

    brier_a = Fraction(0, 1)
    brier_ph = Fraction(0, 1)
    brier_pg = Fraction(0, 1)
    approx_term = Fraction(0, 1)
    info_loss_term = Fraction(0, 1)

    for (x, y), masses in joint_h.items():
        g_key = (sum(x), y)
        ph = p_h_map[(x, y)]
        pg = p_g_map[g_key]
        ag = a_g_map[g_key]
        h_marg = sum(masses, Fraction(0, 1))

        approx_term += h_marg * sum(((ag[k] - pg[k]) ** 2 for k in range(num_regimes)), Fraction(0, 1))
        info_loss_term += h_marg * sum(((pg[k] - ph[k]) ** 2 for k in range(num_regimes)), Fraction(0, 1))

        for k in range(num_regimes):
            mk = masses[k]
            brier_a += mk * sum(
                ((ag[j] - (Fraction(1, 1) if j == k else Fraction(0, 1))) ** 2 for j in range(num_regimes)),
                Fraction(0, 1),
            )
            brier_pg += mk * sum(
                ((pg[j] - (Fraction(1, 1) if j == k else Fraction(0, 1))) ** 2 for j in range(num_regimes)),
                Fraction(0, 1),
            )
            brier_ph += mk * sum(
                ((ph[j] - (Fraction(1, 1) if j == k else Fraction(0, 1))) ** 2 for j in range(num_regimes)),
                Fraction(0, 1),
            )

    lhs = brier_a - brier_ph
    rhs = approx_term + info_loss_term
    residual = lhs - rhs
    # Named collision witness: x0=(1,0,0,...) vs x1=(0,1,0,...) have identical sum(X)=1
    x0 = (1,) + (0,) * (n_slots - 1)
    x1 = (0, 1) + (0,) * (n_slots - 2)
    collision_distinct = p_h_map[(x0, 0)] != p_h_map[(x1, 0)]

    return {
        "n_slots": n_slots,
        "brier_full_history_bayes": str(brier_ph),
        "brier_count_quotient_bayes": str(brier_pg),
        "brier_damped_quotient_predictor": str(brier_a),
        "approx_error_term": str(approx_term),
        "irreducible_info_loss_term": str(info_loss_term),
        "pythagorean_residual": str(residual),
        "exact_zero_residual": residual == 0,
        "strict_positive_info_loss": info_loss_term > 0,
        "named_slot_collision_distinct_posteriors": collision_distinct,
    }


# ---------------------------------------------------------------------------
# HGW-05 & QI-02: Observational-twin causal channels & KL probe budget
# ---------------------------------------------------------------------------


def causal_twin_parameters() -> Dict[str, Fraction]:
    """Matched direct vs confounded laws with identical observational P(X=Y) = 25/32.

    Direct structural model:
      X ~ Bern(1/2), E ~ Bern(7/32), Y = X XOR E
      => P_obs(X = Y) = 1 - 7/32 = 25/32
      => P(Y=1 | do(X=1)) = 25/32, P(Y=1 | do(X=0)) = 7/32
      => Interventional causal effect Delta_do = 18/32 = 9/16, probe match rate p_direct = 25/32.

    Confounded structural model:
      Latent C ~ Bern(1/2); X = C XOR U_x, Y = C XOR U_y with U_x, U_y ~ iid Bern(1/8)
      => P_obs(X = Y) = (7/8)^2 + (1/8)^2 = 50/64 = 25/32 (IDENTICAL observational law!)
      => Under do(X = x), X is severed from C while Y = C XOR U_y ~ Bern(1/2)
      => Interventional causal effect Delta_do = 0, probe match rate p_confounded = 1/2.
    """
    p_obs_direct = Fraction(1, 1) - Fraction(7, 32)
    p_obs_confounded = Fraction(7, 8) ** 2 + Fraction(1, 8) ** 2
    if p_obs_direct != p_obs_confounded:
        raise AssertionError("observational twin rates failed to match")
    return {
        "observational_agreement": p_obs_direct,  # 25/32
        "direct_do_delta": Fraction(9, 16),
        "confounded_do_delta": Fraction(0, 1),
        "direct_probe_match_prob": Fraction(25, 32),
        "confounded_probe_match_prob": Fraction(1, 2),
    }


def bernoulli_kl(p: Fraction | float, q: Fraction | float) -> float:
    pf, qf = float(p), float(q)
    if not (0.0 <= pf <= 1.0 and 0.0 <= qf <= 1.0):
        raise ValueError("probabilities must lie in [0, 1]")
    if pf == qf:
        return 0.0
    if qf in (0.0, 1.0):
        return float("inf")
    term1 = pf * math.log(pf / qf) if pf > 0.0 else 0.0
    term2 = (1.0 - pf) * math.log((1.0 - pf) / (1.0 - qf)) if pf < 1.0 else 0.0
    return term1 + term2


def minimum_interventional_probes(
    error_tolerance: Fraction = Fraction(5, 100),
    p_direct: Fraction = Fraction(25, 32),
    p_confounded: Fraction = Fraction(1, 2),
) -> Dict[str, object]:
    """QI-02 change-of-measure lower bound on randomized `do(X)` probes."""
    delta = float(error_tolerance)
    if not 0.0 < delta < 0.5:
        raise ValueError("error_tolerance must lie in (0, 1/2)")
    kl_target = bernoulli_kl(1.0 - delta, delta)
    kl_per_probe_d_vs_c = bernoulli_kl(p_direct, p_confounded)
    kl_per_probe_c_vs_d = bernoulli_kl(p_confounded, p_direct)
    worst_direction_kl = min(kl_per_probe_d_vs_c, kl_per_probe_c_vs_d)
    continuous_lb = kl_target / worst_direction_kl
    integer_floor = math.ceil(continuous_lb - 1e-12)
    return {
        "error_tolerance": str(error_tolerance),
        "p_direct": str(p_direct),
        "p_confounded": str(p_confounded),
        "kl_target": kl_target,
        "kl_direct_vs_confounded": kl_per_probe_d_vs_c,
        "kl_confounded_vs_direct": kl_per_probe_c_vs_d,
        "continuous_probe_lower_bound": continuous_lb,
        "integer_probe_floor": integer_floor,
    }


# ---------------------------------------------------------------------------
# HGW-03 & HG-01: Bounded reaction inclinations & Clifford/Dirac effect metric
# ---------------------------------------------------------------------------


def evaluate_bounded_inclination(
    features: Mapping[str, Fraction],
    linear_terms: Mapping[str, Fraction],
    bilinear_terms: Mapping[Tuple[str, str], Fraction] | None = None,
    bias: Fraction = Fraction(0, 1),
) -> Tuple[Fraction, Fraction, Fraction]:
    """Evaluate `I_0 = 1/2 + F(x)`, `I_1 = 1/2 - F(x)` with verified L1 mass <= 0.34."""
    bilinear_terms = bilinear_terms or {}
    l1_mass = (
        abs(Fraction(bias))
        + sum((abs(Fraction(c)) for c in linear_terms.values()), Fraction(0, 1))
        + sum((abs(Fraction(c)) for c in bilinear_terms.values()), Fraction(0, 1))
    )
    if l1_mass > MAX_INCLINATION_L1:
        raise ValueError(f"inclination L1 coefficient mass {l1_mass} exceeds {MAX_INCLINATION_L1}")
    for k, v in features.items():
        fv = Fraction(v)
        if not (Fraction(-1, 1) <= fv <= Fraction(1, 1)):
            raise ValueError(f"feature {k}={fv} outside [-1, +1]")

    f_val = Fraction(bias)
    for k, coeff in linear_terms.items():
        f_val += Fraction(coeff) * Fraction(features[k])
    for (ka, kb), coeff in bilinear_terms.items():
        f_val += Fraction(coeff) * Fraction(features[ka]) * Fraction(features[kb])

    i0 = Fraction(1, 2) + f_val
    i1 = Fraction(1, 2) - f_val
    return i0, i1, l1_mass


def clifford_dirac_distance_sq(
    deltas_a: Mapping[Tuple[str, ...], Fraction],
    deltas_b: Mapping[Tuple[str, ...], Fraction] | None = None,
    *,
    trait_weight: Fraction = Fraction(1, 1),
    pvalue_weight: Fraction = Fraction(3, 2),
    p2value_weight: Fraction = Fraction(2, 1),
) -> Fraction:
    """Exact HG-01 Clifford/Dirac squared norm `sum_k (w_k * (Delta_a[k] - Delta_b[k]))^2`.

    Aggregates keys before squaring and weights 1-key character traits, 2-key
    first-order `pValue` pointers, and 3-key second-order `p2Value` pointers distinctly.
    """
    deltas_b = deltas_b or {}
    all_keys = set(deltas_a.keys()) | set(deltas_b.keys())
    total_sq = Fraction(0, 1)
    for key in all_keys:
        # Key format: (char_id, *keyring) -> keyring length is len(key) - 1
        kr_len = len(key) - 1
        if kr_len <= 1:
            w = trait_weight
        elif kr_len == 2:
            w = pvalue_weight
        else:
            w = p2value_weight
        diff = Fraction(deltas_a.get(key, 0)) - Fraction(deltas_b.get(key, 0))
        total_sq += (w * diff) ** 2
    return total_sq


def compact_manifold_moments(posterior: Sequence[Fraction]) -> Tuple[List[float], List[float], float]:
    """Compute 8 signed marginals, 8 cyclic pair correlations, and bit-8 causal moment in one pass."""
    w_ints, common_d = _to_common_int_weights(posterior)
    denom_f = float(common_d)
    m_floats = [
        round((2 * sum(w_ints[z] for z in _BIT_SUPPORT[i]) - common_d) / denom_f, 6)
        for i in range(8)
    ]
    c_floats: List[float] = []
    for i in range(8):
        j = (i + 1) % 8
        pair = (i, j) if i < j else (j, i)
        x_num = sum(w_ints[z] for z in _XOR_PAIR_SUPPORT[pair])
        c_floats.append(round((common_d - 2 * x_num) / denom_f, 6))
    causal_f = round((2 * sum(w_ints[z] for z in _BIT_SUPPORT[8]) - common_d) / denom_f, 6)
    return m_floats, c_floats, causal_f
