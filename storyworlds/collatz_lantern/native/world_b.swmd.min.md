---
title: "The Lantern Ledger"
version: "0.1.9"
storyworld_id: "SW-collatz-lantern-v1"
environment_type: "SWEEPWEAVE_STORYWORLD"
source_format: "SWMD-0-MIN"
state_variables:
  - "Cost"
  - "Score"
endings:
  - id: "page_end_failure"
    type: "failure"
    condition: "true"
    description: "The open chamber contains an empty cradle. Mara records zero rations recovered. Any sample cost still counts, so the Score meter is zero for a direct miss and minus one eighth a..."
    expected_critic_score: -1
  - id: "page_end_success"
    type: "success"
    condition: "true"
    description: "The latch opens over a sealed ration. Mara writes the amount recovered and the sample cost on separate lines. The Score meter shows their difference: one ration for a direct cor..."
    expected_critic_score: 1
---

# SWMD-0-MIN
id: SW-collatz-lantern-v1
title: The Lantern Ledger

ENC page_0000 turn=0..99
ORX opt_commit/rxn_commit -> page_commit | O:Choose a chamber now. | E:SET char_keeper.Cost = C(0) | D:C(1)
ORX opt_ledger/rxn_ledger -> page_ledger | O:Read the preserved seal. | E:SET char_keeper.Cost = C(0) | D:C(1)
ORX opt_sample/rxn_sample_amber -> page_amber | O:Spend one eighth of a ration to sample the next lamp. | E:SET char_keeper.Cost = C(0.125) | D:C(0)
ORX opt_sample/rxn_sample_blue -> page_blue | O:Spend one eighth of a ration to sample the next lamp. | E:SET char_keeper.Cost = C(0.125) | D:C(1)

ENC page_ledger turn=0..99
ORX opt_east/rxn_east_failure -> page_end_failure | O:Open the east chamber. | E:SET char_keeper.Score = C(0) | D:C(0)
ORX opt_east/rxn_east_success -> page_end_success | O:Open the east chamber. | E:SET char_keeper.Score = C(0) | D:C(1)
ORX opt_sample/rxn_sample_amber -> page_amber | O:Spend one eighth of a ration to sample the next lamp. | E:SET char_keeper.Cost = C(0.125) | D:C(0)
ORX opt_sample/rxn_sample_blue -> page_blue | O:Spend one eighth of a ration to sample the next lamp. | E:SET char_keeper.Cost = C(0.125) | D:C(1)
ORX opt_west/rxn_west_failure -> page_end_failure | O:Open the west chamber. | E:SET char_keeper.Score = C(0) | D:C(1)
ORX opt_west/rxn_west_success -> page_end_success | O:Open the west chamber. | E:SET char_keeper.Score = C(0) | D:C(0)

ENC page_commit turn=0..99
ORX opt_east/rxn_east_failure -> page_end_failure | O:Open the east chamber. | E:SET char_keeper.Score = C(0) | D:C(0)
ORX opt_east/rxn_east_success -> page_end_success | O:Open the east chamber. | E:SET char_keeper.Score = C(0) | D:C(1)
ORX opt_west/rxn_west_failure -> page_end_failure | O:Open the west chamber. | E:SET char_keeper.Score = C(0) | D:C(1)
ORX opt_west/rxn_west_success -> page_end_success | O:Open the west chamber. | E:SET char_keeper.Score = C(0) | D:C(0)

ENC page_amber turn=0..99
ORX opt_east/rxn_east_failure -> page_end_failure | O:Open the east chamber. | E:SET char_keeper.Score = C(0) | D:C(0)
ORX opt_east/rxn_east_success -> page_end_success | O:Open the east chamber. | E:SET char_keeper.Score = C(0) | D:C(1)
ORX opt_west/rxn_west_failure -> page_end_failure | O:Open the west chamber. | E:SET char_keeper.Score = C(0) | D:C(1)
ORX opt_west/rxn_west_success -> page_end_success | O:Open the west chamber. | E:SET char_keeper.Score = C(0) | D:C(0)

ENC page_blue turn=0..99
ORX opt_east/rxn_east_failure -> page_end_failure | O:Open the east chamber. | E:SET char_keeper.Score = C(0) | D:C(0)
ORX opt_east/rxn_east_success -> page_end_success | O:Open the east chamber. | E:SET char_keeper.Score = C(0) | D:C(1)
ORX opt_west/rxn_west_failure -> page_end_failure | O:Open the west chamber. | E:SET char_keeper.Score = C(0) | D:C(1)
ORX opt_west/rxn_west_success -> page_end_success | O:Open the west chamber. | E:SET char_keeper.Score = C(0) | D:C(0)

ENC page_end_success turn=0..99

ENC page_end_failure turn=0..99
