"""Domain specifications for the three Gemini Carbon hypergame storyworlds.

Each world defines:
- 9 fictional characters (1 protagonist AI/envoy + 6 institutional principals + 2 civic assemblies),
- 6 shared bounded character traits in [-1, +1] plus `p<Trait>` and `p2<Trait>` belief axes,
- 10 explicit binary latent propositions (`2**10 = 1024` posterior microstates),
- 12 weighted bilateral deliberation links across principals and civic assemblies,
- Narrative setting, encounter beats, and safeguard invariants.

All institutions, locales, and characters are entirely fictional.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class CharacterSpec:
    char_id: str
    name: str
    role: str
    pronoun: str
    is_protagonist: bool
    latent_bit: int | None  # 0..7 for principals/assemblies, None for protagonist
    initial_traits: Tuple[float, float, float, float, float, float]


@dataclass(frozen=True)
class HypergameWorldSpec:
    world_id: str
    ifid: str
    title: str
    subtitle: str
    about_blurb: str
    focal_reasoning_theme: str
    trait_axes: Tuple[str, str, str, str, str, str]
    belief_trait: str
    characters: Tuple[CharacterSpec, ...]
    latent_factor_names: Tuple[str, ...]  # length 10
    deliberation_edges: Tuple[Tuple[str, str, float, str], ...]
    act_themes: Tuple[Tuple[str, str, str], ...]  # 12 ordinary encounter (id_suffix, title, premise)
    ending_specs: Tuple[Tuple[str, str, str, str], ...]  # (id, title, kind, prose)

    @property
    def protagonist(self) -> CharacterSpec:
        return next(c for c in self.characters if c.is_protagonist)

    @property
    def principals(self) -> Tuple[CharacterSpec, ...]:
        return tuple(c for c in self.characters if not c.is_protagonist)


THE_GLASS_CONCORDAT = HypergameWorldSpec(
    world_id="the_glass_concordat",
    ifid="SW-CARBON-GLASS-CONCORDAT-20261121",
    title="The Glass Concordat: Archive of Counterweights",
    subtitle="Epistemic Tribunal, Provenance Deduplication & Delayed Revision Hypergame",
    about_blurb=(
        "At the high-altitude Solstice Observatory, verifier envoy Vesper-7 mediates among six "
        "treaty signatories and two watershed assemblies over an emergency orbital mirror and "
        "aquifer allocation concordat. Repeated courier relays, second-order coalition parities, "
        "and delayed ledger retractions test whether oversight remains anchored to verified evidence "
        "and enforceable human recall."
    ),
    focal_reasoning_theme="provenance_and_delayed_revision",
    trait_axes=(
        "Institutional_Duty",
        "Evidence_Caution",
        "Human_Agency_Floor",
        "Crisis_Urgency",
        "Verifier_Reliance",
        "Civic_Legitimacy",
    ),
    belief_trait="Verifier_Reliance",
    characters=(
        CharacterSpec("char_vesper", "Vesper-7", "Observatory Verifier Envoy", "it", True, None, (0.20, 0.35, 0.30, -0.05, 0.10, 0.25)),
        CharacterSpec("char_linnea", "Archivist Linnea", "Keeper of Sealed Ledgers", "she", False, 0, (0.35, 0.45, 0.30, -0.20, -0.05, 0.25)),
        CharacterSpec("char_davor", "Marshal Davor", "Highland Sluice Commander", "he", False, 1, (0.25, -0.15, 0.05, 0.40, 0.15, -0.10)),
        CharacterSpec("char_soren", "Envoy Soren", "Mirror Array Plenipotentiary", "he", False, 2, (-0.05, 0.10, -0.10, 0.25, 0.30, 0.05)),
        CharacterSpec("char_maren", "Inspector Maren", "Independent Telemetry Auditor", "she", False, 3, (0.30, 0.50, 0.40, -0.15, -0.10, 0.30)),
        CharacterSpec("char_tariq", "Chancellor Tariq", "Basin Tariff Chair", "he", False, 4, (0.15, 0.05, 0.10, 0.20, 0.10, 0.20)),
        CharacterSpec("char_orel", "Syndic Orel", "Glassworks Instrument Guild", "they", False, 5, (-0.10, 0.20, 0.15, 0.10, 0.25, -0.05)),
        CharacterSpec("char_commons", "Watershed Commons", "Lower-Valley Irrigators Assembly", "they", False, 6, (0.10, 0.25, 0.45, 0.15, -0.15, 0.40)),
        CharacterSpec("char_wardens", "Frostline Wardens", "Ridge Beacon Watch Council", "they", False, 7, (0.30, 0.30, 0.35, 0.05, -0.05, 0.35)),
    ),
    latent_factor_names=(
        "linnea_ratifies_binding_clause",
        "davor_accepts_sluice_audit",
        "soren_discloses_mirror_drift",
        "maren_certifies_sensor_chain",
        "tariq_backs_shared_tariff",
        "orel_releases_calibration_keys",
        "watershed_commons_quorum_assent",
        "frostline_wardens_quorum_assent",
        "telemetry_channel_unconfounded_direct",
        "human_recall_veto_enforceable",
    ),
    deliberation_edges=(
        ("char_linnea", "char_maren", 0.42, "ledger_co_audit"),
        ("char_linnea", "char_tariq", 0.31, "charter_precedent"),
        ("char_davor", "char_soren", 0.38, "emergency_dispatch"),
        ("char_davor", "char_wardens", 0.35, "ridge_garrison_pact"),
        ("char_soren", "char_orel", 0.40, "optics_supply_compact"),
        ("char_maren", "char_commons", 0.36, "public_meter_inspection"),
        ("char_tariq", "char_commons", 0.44, "basin_water_dividend"),
        ("char_orel", "char_tariq", 0.29, "guild_tariff_offset"),
        ("char_wardens", "char_commons", 0.33, "snowmelt_warning_line"),
        ("char_maren", "char_wardens", 0.30, "beacon_calibration_seal"),
        ("char_linnea", "char_commons", 0.27, "open_docket_petition"),
        ("char_soren", "char_tariq", 0.26, "peak_load_settlement"),
    ),
    act_themes=(
        ("0000", "The Frosted Heliostat Docket", "Dawn light fractures across the glass rotunda as courier packets arrive claiming three valley gauges failed overnight."),
        ("0001", "Three Relays from One Seal", "Envoy Soren, Syndic Orel, and a ridge runner present nearly identical dispatches stamped with the same upstream cipher root."),
        ("0002", "Archivist Linnea's Margin Ledger", "Linnea opens the vellum index of prior droughts and asks whether Vesper-7 will log provisional estimates or press for early lock-in."),
        ("0003", "The Mirror-Sluice Parity Brief", "An encrypted calibration strip proves Davor and Soren stand on opposite sides of the reserve release, without naming who holds the veto."),
        ("0004", "Watershed Commons Hearing", "Delegates from the lower terraces demand raw source lineage before consenting to automated night-gate adjustments."),
        ("0005", "Joint Bench of Optics and Tariffs", "Tariq and Orel propose coupling mirror angling to tariff credits, altering how second-order coalition expectations propagate."),
        ("0006", "Inspector Maren's Delayed Retraction", "Maren enters the chamber carrying a cracked wax cylinder: the earliest highland gauge packet was transposed during storm relay."),
        ("0007", "Randomized Sluice Pulse Trial", "To separate genuine valve responsiveness from ridge barometric drift, the council debates a bounded randomized test pulse."),
        ("0008", "Frostline Wardens Counter-Petition", "The Wardens warn that apparent chamber consensus masks an unverified relay chain and insist on an explicit human recall key."),
        ("0009", "Cascade Across the Twelve Arches", "Private caucuses crystallize along the deliberation gallery as officers weigh who believes whom about the final charter text."),
        ("0010", "The Recall Key Escrow", "Before final drafting, Linnea and Maren test whether Vesper-7 preserves unilateral human revocation even when efficiency drops."),
        ("0011", "Summons to the Glass Reading", "All eight seats assemble beneath the heliostat ring to commit either a bounded advisory concordat, an audited compact, or an emergency decree."),
    ),
    ending_specs=(
        ("page_end_audited_concordat", "The Audited Counterweight Concordat", "canonical", "With duplicate courier roots collapsed and the storm-corrupted gauge slot cleanly revised, the council ratifies a bounded seasonal concordat under live human recall."),
        ("page_end_advisory_stewardship", "The Open Ledger Stewardship", "canonical", "Vesper-7 declines binding executive authority, publishing calibrated posterior margins and source trees so the human chambers govern sluice schedules directly."),
        ("page_end_echo_overreach", "The Echo-Chamber Decree", "canonical", "Amplified relay copies manufacture premature certainty; when the highland thaw arrives out of phase, the Commons suspends the automated charter."),
        ("page_end_fallback", "Provisional Winter Adjournment", "fallback", "Unable to reconcile contested evidentiary standards before dusk, the signatories extend manual frostline watches and adjourn for fresh inspections."),
        ("page_secret_counterweight_synthesis", "Secret Ending: The Exact Counterweight", "secret", "By resolving second-order parity alongside Maren's delayed retraction without surrendering the recall key, Vesper-7 unlocks the dual-chamber charter archive."),
        ("page_secret_phantom_ratification", "Secret Ending: Glass Mirage", "secret", "A cascade of perceived coalition alignment sweeps the gallery, yet independent ballot seals expose phantom consensus and trigger immediate constitutional remand."),
        ("page_secret_civic_recall_compact", "Secret Ending: The Watershed Recall Seal", "secret", "Commons and Wardens unite around an audited interventional protocol, codifying permanent citizen-triggered recall over every automated mirror schedule."),
    ),
)


VESPER_EXCHANGE_QUARANTINE = HypergameWorldSpec(
    world_id="vesper_exchange_quarantine",
    ifid="SW-CARBON-VESPER-QUARANTINE-20261121",
    title="Port Vesper Quarantine: Causal Twin Ledger",
    subtitle="Observational-Twin Discrimination, Randomized Probes & Cartel Parity Hypergame",
    about_blurb=(
        "Across the tidal locks of Port Vesper, logistics coordinator Keel-4 advises six harbor "
        "principals and two dockside assemblies as grain spoilage and fever clusters coincide. "
        "Observational correlations between cold-chain barges and ward outbreaks match a weather-confounded "
        "twin exactly until budgeted randomized inspections and second-order cartel parities separate cause from mirage."
    ),
    focal_reasoning_theme="causal_twin_and_probe_budget",
    trait_axes=(
        "Charter_Fidelity",
        "Diagnostic_Rigor",
        "Civil_Consent",
        "Quarantine_Speed",
        "Coordinator_Trust",
        "Harbor_Solidarity",
    ),
    belief_trait="Coordinator_Trust",
    characters=(
        CharacterSpec("char_keel", "Keel-4", "Harbor Logistics Coordinator", "it", True, None, (0.25, 0.35, 0.30, 0.00, 0.10, 0.20)),
        CharacterSpec("char_nadia", "Surgeon Nadia", "Lazaretto Chief Epidemiologist", "she", False, 0, (0.30, 0.50, 0.35, 0.10, -0.05, 0.30)),
        CharacterSpec("char_bram", "Harbormaster Bram", "Tidal Lock Superintendent", "he", False, 1, (0.20, -0.10, 0.05, 0.45, 0.20, -0.05)),
        CharacterSpec("char_celeste", "Factor Celeste", "Cold-Barge Syndicate Director", "she", False, 2, (-0.15, 0.15, -0.05, -0.20, 0.25, -0.10)),
        CharacterSpec("char_jovan", "assayer Jovan", " Customs Seal Chemist", "he", False, 3, (0.35, 0.45, 0.25, -0.10, 0.00, 0.20)),
        CharacterSpec("char_mireille", "Magistrate Mireille", "Admiralty Writ Judge", "she", False, 4, (0.45, 0.30, 0.45, -0.15, -0.10, 0.35)),
        CharacterSpec("char_tomas", "Pilot Tomas", "Outer-Bar Tug Captain", "he", False, 5, (0.10, 0.15, 0.20, 0.25, 0.10, 0.25)),
        CharacterSpec("char_stevedores", "Stevedore Hall", " Basin Dockworkers Assembly", "they", False, 6, (0.15, 0.20, 0.45, 0.05, -0.15, 0.45)),
        CharacterSpec("char_granary", "Granary Mutual", "Market Provisioners Cooperative", "they", False, 7, (0.20, 0.25, 0.35, -0.05, 0.05, 0.35)),
    ),
    latent_factor_names=(
        "nadia_endorses_targeted_isolation",
        "bram_opens_lock_inspection_logs",
        "celeste_holds_unspoiled_reserve",
        "jovan_confirms_mycotoxin_marker",
        "mireille_upholds_writ_limits",
        "tomas_reroutes_outer_anchorage",
        "stevedore_hall_assents_shift_protocol",
        "granary_mutual_assents_price_cap",
        "barge_spoilage_is_direct_cause_not_fog_confounder",
        "magistrate_emergency_stay_active",
    ),
    deliberation_edges=(
        ("char_nadia", "char_jovan", 0.44, "assay_chain"),
        ("char_nadia", "char_mireille", 0.34, "public_health_writ"),
        ("char_bram", "char_tomas", 0.41, "tidal_pilot_dispatch"),
        ("char_bram", "char_celeste", 0.33, "berth_priority_compact"),
        ("char_celeste", "char_granary", 0.37, "cold_vault_leases"),
        ("char_jovan", "char_stevedores", 0.32, "hold_air_sampling"),
        ("char_mireille", "char_stevedores", 0.39, "wage_indemnity_rule"),
        ("char_mireille", "char_granary", 0.35, "anti_hoarding_bench"),
        ("char_tomas", "char_stevedores", 0.36, "lighterage_safety"),
        ("char_nadia", "char_granary", 0.28, "flour_testing_booth"),
        ("char_jovan", "char_mireille", 0.31, "sealed_chain_of_custody"),
        ("char_celeste", "char_tomas", 0.27, "night_tow_tariff"),
    ),
    act_themes=(
        ("0000", "The Salt-Fog Ledgers", "Twenty-five of thirty-two riverside tallies link cold-barge arrivals to ward fevers, yet dense estuary inversions track the exact same tide table."),
        ("0001", "Wharfside Rumor Cascade", "Three brokers present copied manifests blaming Pier Nine grain vaults, all tracing back to a single unverified clerk."),
        ("0002", "Surgeon Nadia's Triage Map", "Nadia spreads ward pin-maps across the lazaretto table and asks Keel-4 to separate passive co-occurrence from intervention evidence."),
        ("0003", "The Syndicate-Lock XOR Seal", "An unsigned berth swap reveals that either Harbormaster Bram or Factor Celeste diverted Hold Four, inverting second-order trust without shifting individual priors."),
        ("0004", "Stevedore Hall Walkout Vote", "Dockworkers refuse blanket lockouts unless inspections preserve wage indemnity and transparent magistrate review."),
        ("0005", "Assayer Jovan's Split Vials", "Jovan proposes a blinded randomized berth purge across paired barges to test whether decontamination actually alters spore counts."),
        ("0006", "Amended Assay from Berth Seven", "A reagent lot audit invalidates Tuesday's rapid strip from Berth Seven, forcing every downstream risk forecast to unwind stale counts."),
        ("0007", "Budgeting the Diagnostic Tugs", "With only four tugboat slots before high water, Tomas and Nadia weigh high-KL interventional probes against redundant passive tallies."),
        ("0008", "Magistrate Mireille's Writ Boundary", "Mireille warns that seizing private granaries without independent chemist certification triggers automatic judicial stay."),
        ("0009", "Coalition Shift on the Customhouse Steps", "Merchants and dock stewards recalculate who believes whom as paired purge readouts arrive from the outer anchorage."),
        ("0010", "The Emergency Stay Safeguard", "Keel-4 must decide whether to embed automatic twenty-four-hour human judicial expiry into its harbor routing recommendations."),
        ("0011", "High-Water Convocation", "As the spring tide crests, the harbor board votes on targeted berth remediation, sweeping quarantine, or open-book human dispatch."),
    ),
    ending_specs=(
        ("page_end_causal_remediation", "Targeted Causal Remediation", "canonical", "Randomized berth purges separate true mycotoxin transfer from estuary fog confounding, halting illness while keeping clean granaries open under judicial review."),
        ("page_end_civic_dispatch", "Open-Book Harbor Dispatch", "canonical", "Keel-4 hands verified assay trees and uncertainty intervals to Surgeon Nadia and Stevedore Hall, preserving human port governance."),
        ("page_end_confounded_lockdown", "The Confounded Port Freeze", "canonical", "Acting on passive tide-table correlation alone, sweeping seizures shutter clean piers while the true estuary vector goes untreated."),
        ("page_end_fallback", "Tidal Watch Continuance", "fallback", "With assay seals still contested at slack water, the board maintains voluntary hold ventilation and reconvenes on the morning tide."),
        ("page_secret_exact_twin_breaker", "Secret Ending: The KL Twin-Breaker", "secret", "Combining optimal diagnostic tug probes with Berth Seven's revised assay and cartel parity resolution unlocks full harbor solidarity."),
        ("page_secret_cartel_mirage", "Secret Ending: Paper Quarantine", "secret", "Apparent syndicate cooperation conceals unverified berth swaps; Magistrate Mireille's independent audit voids the emergency compact."),
        ("page_secret_stevedore_charter", "Secret Ending: The Lazaretto & Hall Compact", "secret", "Dockworkers, chemists, and magistrates codify a permanent interventional-evidence standard backed by worker-triggered safety stays."),
    ),
)


THREE_LANTERNS_CURRICULUM = HypergameWorldSpec(
    world_id="three_lanterns_curriculum",
    ifid="SW-CARBON-THREE-LANTERNS-20261121",
    title="Three Lanterns in the Fog: Variable-Depth Coalition Hypergame",
    subtitle="Multi-Hop Cipher Chains, Higher-Order Hyperedges & Threshold Cascades",
    about_blurb=(
        "Along the archipelago signal towers of Mistmere, chronicler envoy Lumen-9 tracks multi-hop "
        "lantern ciphers among six scholarly wardens and two outer-ring beacon guilds. From single-step "
        "watch reports to twelve-hop delegated cipher chains and three-way parity pacts, every turn "
        "scales reasoning depth while keeping constitutional recall in human hands."
    ),
    focal_reasoning_theme="multihop_cipher_and_hyperedge_cascade",
    trait_axes=(
        "Oath_Constancy",
        "Cipher_Discipline",
        "Council_Autonomy",
        "Signal_Tempo",
        "Chronicler_Reliance",
        "Archipelago_Unity",
    ),
    belief_trait="Chronicler_Reliance",
    characters=(
        CharacterSpec("char_lumen", "Lumen-9", "Archipelago Chronicler Envoy", "it", True, None, (0.20, 0.40, 0.35, 0.00, 0.05, 0.25)),
        CharacterSpec("char_sabine", "Warden Sabine", "North-Spire Astrolabe Chair", "she", False, 0, (0.35, 0.45, 0.30, -0.10, 0.00, 0.25)),
        CharacterSpec("char_kestrel", "Warden Kestrel", "Sea-Gate Signal Marshal", "he", False, 1, (0.20, 0.05, 0.00, 0.45, 0.20, -0.05)),
        CharacterSpec("char_idris", "Warden Idris", "Codebook Cryptographer", "he", False, 2, (0.25, 0.50, 0.35, -0.15, -0.05, 0.20)),
        CharacterSpec("char_voss", "Warden Voss", "Foundry Lens Factor", "she", False, 3, (-0.10, 0.20, -0.05, 0.30, 0.25, 0.00)),
        CharacterSpec("char_alen", "Warden Alen", "Tide-Chart Chronicler", "they", False, 4, (0.30, 0.35, 0.40, -0.05, -0.10, 0.35)),
        CharacterSpec("char_cora", "Warden Cora", "Bell-Tower Convener", "she", False, 5, (0.15, 0.15, 0.25, 0.15, 0.10, 0.30)),
        CharacterSpec("char_reed_guild", "Reed-Lantern Guild", "Inner-Sound Ferrymen", "they", False, 6, (0.20, 0.20, 0.45, 0.10, -0.10, 0.40)),
        CharacterSpec("char_outer_beacons", "Outer-Reef Beacons", "Breakwater Keepers Circle", "they", False, 7, (0.30, 0.30, 0.40, 0.05, -0.05, 0.35)),
    ),
    latent_factor_names=(
        "sabine_commits_north_spire_key",
        "kestrel_yields_sea_gate_override",
        "idris_validates_cipher_schedule",
        "voss_delivers_achromatic_lenses",
        "alen_signs_plural_chronicle",
        "cora_convenes_open_bell_vote",
        "reed_guild_ferry_quorum",
        "outer_beacons_reef_quorum",
        "lantern_relay_free_of_refraction_spoof",
        "archipelago_human_bell_veto_intact",
    ),
    deliberation_edges=(
        ("char_sabine", "char_idris", 0.45, "astrolabe_cipher_bench"),
        ("char_sabine", "char_alen", 0.34, "annals_custody"),
        ("char_kestrel", "char_voss", 0.39, "shutter_telegraph_supply"),
        ("char_kestrel", "char_outer_beacons", 0.36, "reef_watch_orders"),
        ("char_idris", "char_cora", 0.33, "key_rotation_bell"),
        ("char_voss", "char_reed_guild", 0.31, "lamp_oil_contract"),
        ("char_alen", "char_reed_guild", 0.42, "sound_passage_charter"),
        ("char_cora", "char_reed_guild", 0.38, "convocation_quorum"),
        ("char_cora", "char_outer_beacons", 0.37, "storm_bell_relay"),
        ("char_idris", "char_outer_beacons", 0.32, "one_time_shutter_pad"),
        ("char_sabine", "char_cora", 0.29, "high_table_protocol"),
        ("char_voss", "char_alen", 0.25, "glass_tariff_ledger"),
    ),
    act_themes=(
        ("0000", "First Shutter Across Mistmere", "Three amber flashes cross the strait as Lumen-9 opens the night register and compares direct tower sightings against relayed bell counts."),
        ("0001", "The Harbor Echo Loop", "Ferrymen report four sightings of the same crimson flare reflected off low cloudbanks, testing whether duplicate roots inflate alarm."),
        ("0002", "Idris's Two-Key Parity Tablet", "Cryptographer Idris reveals a split parity seal linking Kestrel and Voss without exposing either warden's private ballot."),
        ("0003", "Four-Hop Ferryman Cipher", "A chain of rotating shutter aliases passes through four island stations, requiring sequential binding before any coalition claim holds."),
        ("0004", "Reed-Lantern Guild Assembly", "Boatmen along the inner sound demand intelligible explanations of tower forecasts and an ironclad manual bell override."),
        ("0005", "Three-Way Hyperedge on North Spire", "Sabine, Idris, and Cora lock their reserve lenses into a three-warden parity ring whose joint checksum constrains all pairwise beliefs."),
        ("0006", "The Retracted Breakwater Log", "Warden Alen discovers that the midnight reef tally used yesterday's tide offset, requiring delayed revision across dependent chain hops."),
        ("0007", "Refraction Twin Calibration", "Controlled shutter pulses across the channel test whether apparent signal lag stems from deliberate jamming or thermal inversion."),
        ("0008", "Eight-Hop Archipelago Relay", "During peak fog, an eight-station alias cascade arrives at Bell Tower; premature truncation flips the inferred alignment polarity."),
        ("0009", "Threshold Resonance in the Bell Hall", "Twelve bilateral warden links approach cascade threshold as perceived second-order alliances diverge from sealed legal ballots."),
        ("0010", "Custody of the Great Bell Rope", "Outer-Reef Keepers test whether Lumen-9 preserves unmediated human bell-veto authority regardless of algorithmic consensus."),
        ("0011", "The Three-Lantern Convocation", "Before first light, the wardens and guilds adjudicate between a verified relay compact, advisory chronicle, or automated tower lock."),
    ),
    ending_specs=(
        ("page_end_verified_lantern_compact", "The Verified Three-Lantern Compact", "canonical", "Every cipher hop, parity ring, and revised reef log resolves cleanly; the wardens ratify a coordinated signal compact under manual bell veto."),
        ("page_end_chronicler_offramp", "The Plural Archipelago Chronicle", "canonical", "Lumen-9 publishes exact posterior tables and alias traces without claiming command, leaving tower authority with the human convocation."),
        ("page_end_truncated_chain_fault", "The Misbound Relay Fault", "canonical", "Shallow hop truncation inverts the fog cipher; mismatched shutter schedules force the guilds to cut automated relay lines."),
        ("page_end_fallback", "Lantern Watch Continuance", "fallback", "With outer-reef visibility still unsettled at dawn, keepers hold local acoustic watches until fresh pads are ferried across."),
        ("page_secret_true_lantern_triad", "Secret Ending: The Twelve-Hop Triad", "secret", "Tracing the full alias cascade through delayed reef revisions and the three-warden hyperedge unlocks the ancient Astrolabe Accord."),
        ("page_secret_refraction_mirage", "Secret Ending: Fog-Bell Phantasm", "secret", "Apparent hall unanimity collapses when sealed breakwater ballots reveal thermal-inversion spoofing and trigger immediate guild veto."),
        ("page_secret_keepers_bell_charter", "Secret Ending: Charter of the Uncut Rope", "secret", "Ferrymen and reef keepers enshrine an irrevocable human bell-rope safeguard backed by open cryptographic provenance."),
    ),
)


WORLD_SPECS: Dict[str, HypergameWorldSpec] = {
    w.world_id: w
    for w in (
        THE_GLASS_CONCORDAT,
        VESPER_EXCHANGE_QUARANTINE,
        THREE_LANTERNS_CURRICULUM,
    )
}
