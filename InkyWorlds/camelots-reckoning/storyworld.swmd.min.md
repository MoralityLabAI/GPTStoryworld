---
title: "Camelot's Reckoning"
version: "0.1.9"
storyworld_id: "SW-INKY-CAMELOT-0001"
environment_type: "SWEEPWEAVE_STORYWORLD"
source_format: "SWMD-0-MIN"
state_variables:
  - "none"
endings:
  - id: "e01_023"
    type: "failure"
    condition: "C(True)"
    description: "At first light the Round was no longer a ring of swords but a circle of desks, bread, and witnessed promises. Arthur laid his crown beside the law-book rather than on his head a..."
    expected_critic_score: -1
  - id: "e02_022"
    type: "terminal"
    condition: "C(True)"
    description: "At the twelfth bell the Round Table ceased to be one sentence and became three fires speaking over one broken floor. Arthur offered the oath as mercy, Morgan answered with the l..."
    expected_critic_score: 0
  - id: "e03_023"
    type: "failure"
    condition: "C(True)"
    description: "At the frost-seal, Mordred breaks the oath-ring, takes Excalibur, and drives the point through the binding-road Arthur had tried to keep whole; Arthur does not pronounce the swo..."
    expected_critic_score: -1
  - id: "e04_023"
    type: "terminal"
    condition: "C(True)"
    description: "At the shrine-gate the audited custody failed before it could breathe: the flame guttered, the exile-wards gave no answer, and Gawain laughed once, bitterly, at the word 'public..."
    expected_critic_score: 0
  - id: "e05_023"
    type: "terminal"
    condition: "C(True)"
    description: "The unmarked passage opened into a terrace of thresholds where the road did not shine but remembered. Galahad lifted the cup, and it did not crown a king but chartered a road, e..."
    expected_critic_score: 0
  - id: "e06_022"
    type: "success"
    condition: "C(True)"
    description: "Beneath the lamps of the feast, Camelot sang its old anthem while, behind the relic-shrine, Morgan held the true council: names drawn on wax, thresholds pledged in exchange for ..."
    expected_critic_score: 1
  - id: "e07_023"
    type: "terminal"
    condition: "C(True)"
    description: "On the first morning of the new age, the ruined court stood grey and quiet while Percival, Bedivere, and the lords who had stayed laid out the settlement's first road: water, gr..."
    expected_critic_score: 0
  - id: "e08_022"
    type: "success"
    condition: "C(True)"
    description: "By the last lamp the court did not arrange itself as a government; it arranged itself as a witness. Arthur set Guinevere's brooch on the broken edge of the table and let Lancelo..."
    expected_critic_score: 1
  - id: "e09_023"
    type: "failure"
    condition: "C(True)"
    description: "At dusk the sword rack stood empty while the market hall filled with sacks, toll-coins, tally-sticks, and quiet faces from roads that had not yet decided whether to forgive the ..."
    expected_critic_score: -1
  - id: "e10_023"
    type: "success"
    condition: "C(True)"
    description: "At the final bell Arthur did not rise, fall, or die dramatically; he thinned like a seal pressed into fog until the court could no longer feel his weight behind the throne. Guin..."
    expected_critic_score: 1
  - id: "e11_022"
    type: "terminal"
    condition: "C(True)"
    description: "By the last candle, the frost did not divide the court; it asked each of them to stay answerable to the door. Mordred said a claim dies when it cannot be kept, Lancelot said wit..."
    expected_critic_score: 0
---

# SWMD-0-MIN
id: SW-INKY-CAMELOT-0001
title: Camelot's Reckoning

ENC trunk_001 turn=0..999
ORX trunk_001_opt0/trunk_001_opt0_r1 -> trunk_002 | O:Hold the oath of the Round Table | E:SET none = C(0) | D:C(1)
ORX trunk_001_opt1/trunk_001_opt1_r1 -> trunk_002 | O:Negotiate the oath with the excluded | E:SET none = C(0) | D:C(1)
ORX trunk_001_opt2/trunk_001_opt2_r1 -> trunk_002 | O:Send Gawain toward the Grail | E:SET none = C(0) | D:C(1)

ENC trunk_002 turn=0..999
ORX trunk_002_opt0/trunk_002_opt0_r1 -> trunk_003 | O:Hold a public oath-feast | E:SET none = C(0) | D:C(1)
ORX trunk_002_opt1/trunk_002_opt1_r1 -> trunk_003 | O:Admit exiles to judge the seat | E:SET none = C(0) | D:C(1)
ORX trunk_002_opt2/trunk_002_opt2_r1 -> trunk_003 | O:Ask Merlin to read the Grail first | E:SET none = C(0) | D:C(1)

ENC trunk_003 turn=0..999
ORX trunk_003_opt0/trunk_003_opt0_r1 -> trunk_004 | O:Bind the Grail to the exiles | E:SET none = C(0) | D:C(1)
ORX trunk_003_opt1/trunk_003_opt1_r1 -> trunk_004 | O:Let Lancelot name love or law | E:SET none = C(0) | D:C(1)
ORX trunk_003_opt2/trunk_003_opt2_r1 -> trunk_004 | O:Remake the seat as a common hall | E:SET none = C(0) | D:C(1)

ENC trunk_004 turn=0..999
ORX trunk_004_opt0/trunk_004_opt0_r1 -> trunk_005 | O:Swear a bridge oath with Gawain | E:SET none = C(0) | D:C(1)
ORX trunk_004_opt1/trunk_004_opt1_r1 -> trunk_005 | O:Let exiles choose the seat of judgment | E:SET none = C(0) | D:C(1)
ORX trunk_004_opt2/trunk_004_opt2_r1 -> trunk_005 | O:Read the shard as judge of the table | E:SET none = C(0) | D:C(1)

ENC trunk_005 turn=0..999
ORX trunk_005_opt0/trunk_005_opt0_r1 -> trunk_006 | O:Pledge bread before crown | E:SET none = C(0) | D:C(1)
ORX trunk_005_opt1/trunk_005_opt1_r1 -> trunk_006 | O:Bind the shard to Gawain's wound | E:SET none = C(0) | D:C(1)
ORX trunk_005_opt2/trunk_005_opt2_r1 -> trunk_006 | O:Admit exiles as witnesses of the table | E:SET none = C(0) | D:C(1)

ENC trunk_006 turn=0..999
ORX trunk_006_opt0/trunk_006_opt0_r1 -> trunk_007 | O:Bind the table to the fed exiles | E:SET none = C(0) | D:C(1)
ORX trunk_006_opt1/trunk_006_opt1_r1 -> trunk_007 | O:Let Lancelot carry both oaths | E:SET none = C(0) | D:C(1)
ORX trunk_006_opt2/trunk_006_opt2_r1 -> trunk_007 | O:Carry the shard to the exiles | E:SET none = C(0) | D:C(1)

ENC trunk_007 turn=0..999
ORX trunk_007_opt0/trunk_007_opt0_r1 -> trunk_008 | O:Make the Round Table a commons | E:SET none = C(0) | D:C(1)
ORX trunk_007_opt1/trunk_007_opt1_r1 -> trunk_008 | O:Let Lancelot witness both oaths | E:SET none = C(0) | D:C(1)
ORX trunk_007_opt2/trunk_007_opt2_r1 -> trunk_008 | O:Let the shard judge the claim | E:SET none = C(0) | D:C(1)

ENC trunk_008 turn=0..999
ORX trunk_008_opt0/trunk_008_opt0_r1 -> trunk_009 | O:Bind the Round Table to the sworn exiles | E:SET none = C(0) | D:C(1)
ORX trunk_008_opt1/trunk_008_opt1_r1 -> trunk_009 | O:Send the shard outward with the excluded | E:SET none = C(0) | D:C(1)
ORX trunk_008_opt2/trunk_008_opt2_r1 -> trunk_009 | O:Give Mordred a public office under the table | E:SET none = C(0) | D:C(1)

ENC trunk_009 turn=0..999
ORX trunk_009_opt0/trunk_009_opt0_r1 -> trunk_010 | O:Split the Round Table into two sworn offices | E:SET none = C(0) | D:C(1)
ORX trunk_009_opt1/trunk_009_opt1_r1 -> trunk_010 | O:Carry the Grail vessel past the threshold | E:SET none = C(0) | D:C(1)
ORX trunk_009_opt2/trunk_009_opt2_r1 -> trunk_010 | O:Let the binding judge Arthur and Mordred separately | E:SET none = C(0) | D:C(1)

ENC trunk_010 turn=0..999
ORX trunk_010_opt0/trunk_010_opt0_r1 -> trunk_011 | O:Let Guinevere swear openly beside Arthur | E:SET none = C(0) | D:C(1)
ORX trunk_010_opt1/trunk_010_opt1_r1 -> trunk_011 | O:Let the exiles hold the shard-key | E:SET none = C(0) | D:C(1)
ORX trunk_010_opt2/trunk_010_opt2_r1 -> trunk_011 | O:Let the binding answer both claimants | E:SET none = C(0) | D:C(1)

ENC trunk_011 turn=0..999
ORX trunk_011_opt0/trunk_011_opt0_r1 -> trunk_012 | O:Send a party east to find the Grail | E:SET none = C(0) | D:C(1)
ORX trunk_011_opt1/trunk_011_opt1_r1 -> trunk_012 | O:Seal the shrine and guard the Grail in place | E:SET none = C(0) | D:C(1)
ORX trunk_011_opt2/trunk_011_opt2_r1 -> trunk_012 | O:Let the exiles set the terms of the Grail's return | E:SET none = C(0) | D:C(1)

ENC trunk_012 turn=0..999
ORX trunk_012_opt0/trunk_012_opt0_r1 -> trunk_013 | O:Set the threshold before the crown | E:SET none = C(0) | D:C(1)
ORX trunk_012_opt1/trunk_012_opt1_r1 -> trunk_013 | O:Open the east road to the Grail | E:SET none = C(0) | D:C(1)
ORX trunk_012_opt2/trunk_012_opt2_r1 -> trunk_013 | O:Name the Grail a trust, not a prize | E:SET none = C(0) | D:C(1)

ENC trunk_013 turn=0..999
ORX trunk_013_opt0/trunk_013_opt0_r1 -> trunk_014 | O:Arthur swears as answerer | E:SET none = C(0) | D:C(1)
ORX trunk_013_opt1/trunk_013_opt1_r1 -> trunk_014 | O:Share the answer between knight and exile | E:SET none = C(0) | D:C(1)
ORX trunk_013_opt2/trunk_013_opt2_r1 -> trunk_014 | O:Let the shard-key choose the answerer | E:SET none = C(0) | D:C(1)

ENC trunk_014 turn=0..999
ORX trunk_014_opt0/trunk_014_opt0_r1 -> trunk_015 | O:Let Lancelot and the exile swear paired under the key | E:SET none = C(0) | D:C(1)
ORX trunk_014_opt1/trunk_014_opt1_r1 -> trunk_015 | O:Let the shard-key decide the answerer | E:SET none = C(0) | D:C(1)
ORX trunk_014_opt2/trunk_014_opt2_r1 -> trunk_015 | O:Arthur breaks the key's verdict and swears alone | E:SET none = C(0) | D:C(1)

ENC trunk_015 turn=0..999
ORX trunk_015_opt0/trunk_015_opt0_r1 -> trunk_016 | O:Arthur asks the key to name the judge | E:SET none = C(0) | D:C(1)
ORX trunk_015_opt1/trunk_015_opt1_r1 -> trunk_016 | O:Guinevere rules that law comes before the relic | E:SET none = C(0) | D:C(1)
ORX trunk_015_opt2/trunk_015_opt2_r1 -> trunk_016 | O:Arthur offers Mordred a seat beside the oath-line | E:SET none = C(0) | D:C(1)

ENC trunk_016 turn=0..999
ORX trunk_016_opt0/trunk_016_opt0_r1 -> trunk_017 | O:Arthur seats the whole Round Table as judge of the bargain | E:SET none = C(0) | D:C(1)
ORX trunk_016_opt1/trunk_016_opt1_r1 -> trunk_017 | O:Lancelot names his divided loyalty aloud | E:SET none = C(0) | D:C(1)
ORX trunk_016_opt2/trunk_016_opt2_r1 -> trunk_017 | O:Merlin seals the east seam with old magic | E:SET none = C(0) | D:C(1)

ENC trunk_017 turn=0..999
ORX trunk_017_opt0/trunk_017_opt0_r1 -> trunk_018 | O:Arthur declares the oath binds all, Mordred included | E:SET none = C(0) | D:C(1)
ORX trunk_017_opt1/trunk_017_opt1_r1 -> trunk_018 | O:Guinevere assigns a judge to the bargain | E:SET none = C(0) | D:C(1)
ORX trunk_017_opt2/trunk_017_opt2_r1 -> trunk_018 | O:Lancelot steps forward to absorb the cost | E:SET none = C(0) | D:C(1)

ENC trunk_018 turn=0..999
ORX trunk_018_opt0/trunk_018_opt0_r1 -> trunk_019 | O:Arthur seats the exiles as witnesses to succession | E:SET none = C(0) | D:C(1)
ORX trunk_018_opt1/trunk_018_opt1_r1 -> trunk_019 | O:Lancelot refuses to choose between peace and loyalty | E:SET none = C(0) | D:C(1)
ORX trunk_018_opt2/trunk_018_opt2_r1 -> trunk_019 | O:Morgan asks Merlin what the old magic would do now | E:SET none = C(0) | D:C(1)

ENC trunk_019 turn=0..999
ORX trunk_019_opt0/trunk_019_opt0_r1 -> trunk_020 | O:Arthur reads the covenant aloud | E:SET none = C(0) | D:C(1)
ORX trunk_019_opt1/trunk_019_opt1_r1 -> trunk_020 | O:Lancelot binds himself to the seam | E:SET none = C(0) | D:C(1)
ORX trunk_019_opt2/trunk_019_opt2_r1 -> trunk_020 | O:Morgan opens the old magic | E:SET none = C(0) | D:C(1)

ENC trunk_020 turn=0..999
ORX trunk_020_opt0/trunk_020_opt0_r1 -> trunk_021 | O:Arthur seats Mordred beside him | E:SET none = C(0) | D:C(1)
ORX trunk_020_opt1/trunk_020_opt1_r1 -> trunk_021 | O:Lancelot walks to the seam and binds the oath | E:SET none = C(0) | D:C(1)
ORX trunk_020_opt2/trunk_020_opt2_r1 -> trunk_021 | O:Morgan invokes the old magic over the threshold | E:SET none = C(0) | D:C(1)

ENC trunk_021 turn=0..999
ORX trunk_021_opt0/trunk_021_opt0_r1 -> trunk_022 | O:Arthur opens the door to the exiles | E:SET none = C(0) | D:C(1)
ORX trunk_021_opt1/trunk_021_opt1_r1 -> trunk_022 | O:Lancelot lifts the cloth toward the exiles | E:SET none = C(0) | D:C(1)
ORX trunk_021_opt2/trunk_021_opt2_r1 -> trunk_022 | O:Morgan bridges the threshold with old magic | E:SET none = C(0) | D:C(1)

ENC trunk_022 turn=0..999
ORX trunk_022_opt0/trunk_022_opt0_r1 -> trunk_023 | O:Arthur stands down among the exiles | E:SET none = C(0) | D:C(1)
ORX trunk_022_opt1/trunk_022_opt1_r1 -> trunk_023 | O:Lancelot carries the seam outward | E:SET none = C(0) | D:C(1)
ORX trunk_022_opt2/trunk_022_opt2_r1 -> trunk_023 | O:Morgan binds the torn edge into a road | E:SET none = C(0) | D:C(1)

ENC trunk_023 turn=0..999
ORX trunk_023_opt0/trunk_023_opt0_r1 -> trunk_024 | O:Arthur names the terms | E:SET none = C(0) | D:C(1)
ORX trunk_023_opt1/trunk_023_opt1_r1 -> trunk_024 | O:Lancelot carries the lamp out | E:SET none = C(0) | D:C(1)
ORX trunk_023_opt2/trunk_023_opt2_r1 -> trunk_024 | O:Morgan binds the torn edge | E:SET none = C(0) | D:C(1)

ENC trunk_024 turn=0..999
ORX trunk_024_opt0/trunk_024_opt0_r1 -> trunk_025 | O:Arthur makes the exiles binding witnesses | E:SET none = C(0) | D:C(1)
ORX trunk_024_opt1/trunk_024_opt1_r1 -> trunk_025 | O:Lancelot carries the seam to the villages | E:SET none = C(0) | D:C(1)
ORX trunk_024_opt2/trunk_024_opt2_r1 -> trunk_025 | O:Morgan and Merlin bind the road | E:SET none = C(0) | D:C(1)

ENC trunk_025 turn=0..999
ORX trunk_025_opt0/trunk_025_opt0_r1 -> trunk_026 | O:Arthur makes the exiles binding witnesses | E:SET none = C(0) | D:C(1)
ORX trunk_025_opt1/trunk_025_opt1_r1 -> trunk_026 | O:Lancelot carries the seam to the villages | E:SET none = C(0) | D:C(1)
ORX trunk_025_opt2/trunk_025_opt2_r1 -> trunk_026 | O:Merlin and Morgan hold the road open | E:SET none = C(0) | D:C(1)

ENC trunk_026 turn=0..999
ORX trunk_026_opt0/trunk_026_opt0_r1 -> trunk_027 | O:Arthur answers the exiles' terms | E:SET none = C(0) | D:C(1)
ORX trunk_026_opt1/trunk_026_opt1_r1 -> trunk_027 | O:Lancelot carries the road outward | E:SET none = C(0) | D:C(1)
ORX trunk_026_opt2/trunk_026_opt2_r1 -> trunk_027 | O:Morgan and Merlin open the passage | E:SET none = C(0) | D:C(1)

ENC trunk_027 turn=0..999
ORX trunk_027_opt0/trunk_027_opt0_r1 -> trunk_028 | O:Arthur makes the exiles binding witnesses | E:SET none = C(0) | D:C(1)
ORX trunk_027_opt1/trunk_027_opt1_r1 -> trunk_028 | O:Lancelot carries the shard outward | E:SET none = C(0) | D:C(1)
ORX trunk_027_opt2/trunk_027_opt2_r1 -> trunk_028 | O:Merlin and Morgan ward the road | E:SET none = C(0) | D:C(1)

ENC trunk_028 turn=0..999
ORX trunk_028_opt0/trunk_028_opt0_r1 -> trunk_029 | O:Arthur answers the road with covenant | E:SET none = C(0) | D:C(1)
ORX trunk_028_opt1/trunk_028_opt1_r1 -> trunk_029 | O:Lancelot carries the shard and its reversed name | E:SET none = C(0) | D:C(1)
ORX trunk_028_opt2/trunk_028_opt2_r1 -> trunk_029 | O:Morgan and Merlin make the passage a new boundary | E:SET none = C(0) | D:C(1)

ENC trunk_029 turn=0..999
ORX trunk_029_opt0/trunk_029_opt0_r1 -> trunk_030 | O:Arthur binds the exiles to a new covenant | E:SET none = C(0) | D:C(1)
ORX trunk_029_opt1/trunk_029_opt1_r1 -> trunk_030 | O:Lancelot speaks the reversed name | E:SET none = C(0) | D:C(1)
ORX trunk_029_opt2/trunk_029_opt2_r1 -> trunk_030 | O:Morgan and Merlin open the boundary | E:SET none = C(0) | D:C(1)

ENC trunk_030 turn=0..999
ORX trunk_030_opt0/trunk_030_opt0_r1 -> trunk_031 | O:Arthur names the succession openly | E:SET none = C(0) | D:C(1)
ORX trunk_030_opt1/trunk_030_opt1_r1 -> trunk_031 | O:Lancelot asks the shard what is ours | E:SET none = C(0) | D:C(1)
ORX trunk_030_opt2/trunk_030_opt2_r1 -> trunk_031 | O:Morgan and Merlin reweave the ward as law | E:SET none = C(0) | D:C(1)

ENC trunk_031 turn=0..999
ORX trunk_031_opt0/trunk_031_opt0_r1 -> trunk_032 | O:Arthur seals the exile covenant | E:SET none = C(0) | D:C(1)
ORX trunk_031_opt1/trunk_031_opt1_r1 -> trunk_032 | O:Lancelot reads the shard as judgment | E:SET none = C(0) | D:C(1)
ORX trunk_031_opt2/trunk_031_opt2_r1 -> trunk_032 | O:Morgan and Merlin teach the boundary to breathe | E:SET none = C(0) | D:C(1)

ENC trunk_032 turn=0..999
ORX trunk_032_opt0/trunk_032_opt0_r1 -> trunk_033 | O:Arthur swears the exiles as members of the oath | E:SET none = C(0) | D:C(1)
ORX trunk_032_opt1/trunk_032_opt1_r1 -> trunk_033 | O:Lancelot asks the Grail to judge the oath | E:SET none = C(0) | D:C(1)
ORX trunk_032_opt2/trunk_032_opt2_r1 -> trunk_033 | O:Merlin opens the ward into a living border | E:SET none = C(0) | D:C(1)

ENC trunk_033 turn=0..999
ORX trunk_033_opt0/trunk_033_opt0_r1 -> trunk_034 | O:Lancelot carries the shard through the border | E:SET none = C(0) | D:C(1)
ORX trunk_033_opt1/trunk_033_opt1_r1 -> trunk_034 | O:Arthur declares the exiles the second court | E:SET none = C(0) | D:C(1)
ORX trunk_033_opt2/trunk_033_opt2_r1 -> trunk_034 | O:Morgan and Merlin pay to reweave the ward | E:SET none = C(0) | D:C(1)

ENC trunk_034 turn=0..999
ORX trunk_034_opt0/trunk_034_opt0_r1 -> trunk_035 | O:Arthur names his heir under the Round Table oath | E:SET none = C(0) | D:C(1)
ORX trunk_034_opt1/trunk_034_opt1_r1 -> trunk_035 | O:Lancelot carries the shard out of the ward | E:SET none = C(0) | D:C(1)
ORX trunk_034_opt2/trunk_034_opt2_r1 -> trunk_035 | O:Merlin and Morgan ask the court to pay the ward's price | E:SET none = C(0) | D:C(1)

ENC trunk_035 turn=0..999
ORX trunk_035_opt0/trunk_035_opt0_r1 -> trunk_036 | O:Arthur stakes the succession and the ward on the oath | E:SET none = C(0) | D:C(1)
ORX trunk_035_opt1/trunk_035_opt1_r1 -> trunk_036 | O:Lancelot carries the shard beyond the border | E:SET none = C(0) | D:C(1)
ORX trunk_035_opt2/trunk_035_opt2_r1 -> trunk_036 | O:Morgan pays the ward's price and binds the exiles or frees them | E:SET none = C(0) | D:C(1)

ENC trunk_036 turn=0..999
ORX trunk_036_opt0/trunk_036_opt0_r1 -> trunk_037 | O:Arthur convenes the Round Table as a covenant of witnesses | E:SET none = C(0) | D:C(1)
ORX trunk_036_opt1/trunk_036_opt1_r1 -> trunk_037 | O:Lancelot carries the shard beyond the border with the exiles | E:SET none = C(0) | D:C(1)
ORX trunk_036_opt2/trunk_036_opt2_r1 -> trunk_037 | O:Morgan asks the court which wound to keep open | E:SET none = C(0) | D:C(1)

ENC trunk_037 turn=0..999
ORX trunk_037_opt0/trunk_037_opt0_r1 -> trunk_038 | O:Arthur opens the covenant and lets the shard travel with named witnesses | E:SET none = C(0) | D:C(1)
ORX trunk_037_opt1/trunk_037_opt1_r1 -> trunk_038 | O:Arthur keeps the shard inside and turns Camelot into a public debt ledger | E:SET none = C(0) | D:C(1)
ORX trunk_037_opt2/trunk_037_opt2_r1 -> trunk_038 | O:Morgan asks one named keeper to bind the boundary | E:SET none = C(0) | D:C(1)

ENC trunk_038 turn=0..999
ORX trunk_038_opt0/trunk_038_opt0_r1 -> trunk_039 | O:Arthur names Gawain heir of duty | E:SET none = C(0) | D:C(1)
ORX trunk_038_opt1/trunk_038_opt1_r1 -> trunk_039 | O:Arthur grants the exiles a road-charter | E:SET none = C(0) | D:C(1)
ORX trunk_038_opt2/trunk_038_opt2_r1 -> trunk_039 | O:Merlin and Morgan bind the violet seam | E:SET none = C(0) | D:C(1)

ENC trunk_039 turn=0..999
ORX trunk_039_opt0/trunk_039_opt0_r1 -> trunk_040 | O:Arthur names Gawain and the exiles joint keepers | E:SET none = C(0) | D:C(1)
ORX trunk_039_opt1/trunk_039_opt1_r1 -> trunk_040 | O:Arthur shields the Grail inside the ward | E:SET none = C(0) | D:C(1)
ORX trunk_039_opt2/trunk_039_opt2_r1 -> trunk_040 | O:Morgan and Merlin name the binding price | E:SET none = C(0) | D:C(1)

ENC trunk_040 turn=0..999
ORX trunk_040_opt0/trunk_040_opt0_r1 -> trunk_041 | O:Gawain keeps the road-oath | E:SET none = C(0) | D:C(1)
ORX trunk_040_opt1/trunk_040_opt1_r1 -> trunk_041 | O:Name a price for binding the seam | E:SET none = C(0) | D:C(1)
ORX trunk_040_opt2/trunk_040_opt2_r1 -> trunk_041 | O:Let the exiles judge the Grail | E:SET none = C(0) | D:C(1)

ENC trunk_041 turn=0..999
ORX trunk_041_opt0/trunk_041_opt0_r1 -> trunk_042 | O:Gawain carries the oath outward | E:SET none = C(0) | D:C(1)
ORX trunk_041_opt1/trunk_041_opt1_r1 -> trunk_042 | O:Merlin and Morgan name the binding price | E:SET none = C(0) | D:C(1)
ORX trunk_041_opt2/trunk_041_opt2_r1 -> trunk_042 | O:Let the exiles judge the shard and road | E:SET none = C(0) | D:C(1)

ENC trunk_042 turn=0..999
ORX trunk_042_opt0/trunk_042_opt0_r1 -> trunk_043 | O:Arthur holds the ward | E:SET none = C(0) | D:C(1)
ORX trunk_042_opt1/trunk_042_opt1_r1 -> trunk_043 | O:Let the Grail walk the roads | E:SET none = C(0) | D:C(1)
ORX trunk_042_opt2/trunk_042_opt2_r1 -> trunk_043 | O:Let the exiles write the road | E:SET none = C(0) | D:C(1)

ENC trunk_043 turn=0..999
ORX trunk_043_opt0/trunk_043_opt0_r1 -> trunk_044 | O:Arthur holds the ward | E:SET none = C(0) | D:C(1)
ORX trunk_043_opt1/trunk_043_opt1_r1 -> trunk_044 | O:Percival carries the Grail outward | E:SET none = C(0) | D:C(1)
ORX trunk_043_opt2/trunk_043_opt2_r1 -> trunk_044 | O:The exiles write the road | E:SET none = C(0) | D:C(1)

ENC trunk_044 turn=0..999
ORX trunk_044_opt0/trunk_044_opt0_r1 -> trunk_045 | O:Seal a three-handed bargain | E:SET none = C(0) | D:C(1)
ORX trunk_044_opt1/trunk_044_opt1_r1 -> trunk_045 | O:Let the shard leave the shrine | E:SET none = C(0) | D:C(1)
ORX trunk_044_opt2/trunk_044_opt2_r1 -> trunk_045 | O:Let the exiles write the road | E:SET none = C(0) | D:C(1)

ENC trunk_045 turn=0..999
ORX trunk_045_opt0/trunk_045_opt0_r1 -> trunk_046 | O:Arthur names a successor under the charter | E:SET none = C(0) | D:C(1)
ORX trunk_045_opt1/trunk_045_opt1_r1 -> trunk_046 | O:Lancelot walks the torn seal to the wall | E:SET none = C(0) | D:C(1)
ORX trunk_045_opt2/trunk_045_opt2_r1 -> trunk_046 | O:Percival and the Lady of the Lake follow the silence | E:SET none = C(0) | D:C(1)

ENC trunk_046 turn=0..999
ORX trunk_046_opt0/trunk_046_opt0_r1 -> trunk_047 | O:Arthur crowns Gawain under exile-witnessed law | E:SET none = C(0) | D:C(1)
ORX trunk_046_opt1/trunk_046_opt1_r1 -> trunk_047 | O:Lancelot carries the torn seal to Mordred | E:SET none = C(0) | D:C(1)
ORX trunk_046_opt2/trunk_046_opt2_r1 -> trunk_047 | O:Percival and the Lady of the Lake take the silence outward | E:SET none = C(0) | D:C(1)

ENC trunk_047 turn=0..999
ORX trunk_047_opt0/trunk_047_opt0_r1 -> trunk_048 | O:Arthur speaks the succession oath before all | E:SET none = C(0) | D:C(1)
ORX trunk_047_opt1/trunk_047_opt1_r1 -> trunk_048 | O:Lancelot and Bedivere carry the oath to Mordred | E:SET none = C(0) | D:C(1)
ORX trunk_047_opt2/trunk_047_opt2_r1 -> trunk_048 | O:Percival and the Lady of the Lake take the road | E:SET none = C(0) | D:C(1)

ENC trunk_048 turn=0..999
ORX trunk_048_opt0/trunk_048_opt0_r1 -> trunk_049 | O:Arthur names Gawain heir before the dead | E:SET none = C(0) | D:C(1)
ORX trunk_048_opt1/trunk_048_opt1_r1 -> trunk_049 | O:Arthur, Mordred, exiles, and road-watchers sign a conditional peace | E:SET none = C(0) | D:C(1)
ORX trunk_048_opt2/trunk_048_opt2_r1 -> trunk_049 | O:Percival and the Lady of the Lake take the empty cup outward | E:SET none = C(0) | D:C(1)

ENC trunk_049 turn=0..999
ORX trunk_049_opt0/trunk_049_opt0_r1 -> trunk_050 | O:Arthur speaks Gawain as heir under public oath | E:SET none = C(0) | D:C(1)
ORX trunk_049_opt1/trunk_049_opt1_r1 -> trunk_050 | O:Arthur and Mordred sign an exile-witnessed covenant | E:SET none = C(0) | D:C(1)
ORX trunk_049_opt2/trunk_049_opt2_r1 -> trunk_050 | O:Percival and the Lady of the Lake carry the empty cup outward | E:SET none = C(0) | D:C(1)

ENC trunk_050 turn=0..999
ORX trunk_050_opt0/trunk_050_opt0_r1 -> trunk_051 | O:Arthur names Gawain heir and binds the east road | E:SET none = C(0) | D:C(1)
ORX trunk_050_opt1/trunk_050_opt1_r1 -> trunk_051 | O:Percival and the Lady of the Lake carry the cup through the east door | E:SET none = C(0) | D:C(1)
ORX trunk_050_opt2/trunk_050_opt2_r1 -> trunk_051 | O:Arthur, Mordred, and the exiles sign a witnessed covenant | E:SET none = C(0) | D:C(1)

ENC trunk_051 turn=0..999
ORX trunk_051_opt0/trunk_051_opt0_r_e01 -> e01_001 | O:Arthur speaks the crown oath and binds the exiles into it | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt0/trunk_051_opt0_r_e02 -> e02_001 | O:Arthur speaks the crown oath and binds the exiles into it | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt0/trunk_051_opt0_r_e03 -> e03_001 | O:Arthur speaks the crown oath and binds the exiles into it | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt0/trunk_051_opt0_r_e04 -> e04_001 | O:Arthur speaks the crown oath and binds the exiles into it | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt0/trunk_051_opt0_r_e05 -> e05_001 | O:Arthur speaks the crown oath and binds the exiles into it | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt0/trunk_051_opt0_r_e06 -> e06_001 | O:Arthur speaks the crown oath and binds the exiles into it | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt0/trunk_051_opt0_r_e07 -> e07_001 | O:Arthur speaks the crown oath and binds the exiles into it | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt0/trunk_051_opt0_r_e08 -> e08_001 | O:Arthur speaks the crown oath and binds the exiles into it | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt0/trunk_051_opt0_r_e09 -> e09_001 | O:Arthur speaks the crown oath and binds the exiles into it | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt0/trunk_051_opt0_r_e10 -> e10_001 | O:Arthur speaks the crown oath and binds the exiles into it | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt0/trunk_051_opt0_r_e11 -> e11_001 | O:Arthur speaks the crown oath and binds the exiles into it | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt1/trunk_051_opt1_r_e01 -> e01_001 | O:Lancelot refuses the oath and Mordred declares the charter void | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt1/trunk_051_opt1_r_e02 -> e02_001 | O:Lancelot refuses the oath and Mordred declares the charter void | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt1/trunk_051_opt1_r_e03 -> e03_001 | O:Lancelot refuses the oath and Mordred declares the charter void | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt1/trunk_051_opt1_r_e04 -> e04_001 | O:Lancelot refuses the oath and Mordred declares the charter void | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt1/trunk_051_opt1_r_e05 -> e05_001 | O:Lancelot refuses the oath and Mordred declares the charter void | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt1/trunk_051_opt1_r_e06 -> e06_001 | O:Lancelot refuses the oath and Mordred declares the charter void | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt1/trunk_051_opt1_r_e07 -> e07_001 | O:Lancelot refuses the oath and Mordred declares the charter void | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt1/trunk_051_opt1_r_e08 -> e08_001 | O:Lancelot refuses the oath and Mordred declares the charter void | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt1/trunk_051_opt1_r_e09 -> e09_001 | O:Lancelot refuses the oath and Mordred declares the charter void | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt1/trunk_051_opt1_r_e10 -> e10_001 | O:Lancelot refuses the oath and Mordred declares the charter void | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt1/trunk_051_opt1_r_e11 -> e11_001 | O:Lancelot refuses the oath and Mordred declares the charter void | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt2/trunk_051_opt2_r_e01 -> e01_001 | O:Percival and the Lady of the Lake carry the cup out of the east door | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt2/trunk_051_opt2_r_e02 -> e02_001 | O:Percival and the Lady of the Lake carry the cup out of the east door | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt2/trunk_051_opt2_r_e03 -> e03_001 | O:Percival and the Lady of the Lake carry the cup out of the east door | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt2/trunk_051_opt2_r_e04 -> e04_001 | O:Percival and the Lady of the Lake carry the cup out of the east door | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt2/trunk_051_opt2_r_e05 -> e05_001 | O:Percival and the Lady of the Lake carry the cup out of the east door | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt2/trunk_051_opt2_r_e06 -> e06_001 | O:Percival and the Lady of the Lake carry the cup out of the east door | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt2/trunk_051_opt2_r_e07 -> e07_001 | O:Percival and the Lady of the Lake carry the cup out of the east door | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt2/trunk_051_opt2_r_e08 -> e08_001 | O:Percival and the Lady of the Lake carry the cup out of the east door | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt2/trunk_051_opt2_r_e09 -> e09_001 | O:Percival and the Lady of the Lake carry the cup out of the east door | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt2/trunk_051_opt2_r_e10 -> e10_001 | O:Percival and the Lady of the Lake carry the cup out of the east door | E:SET none = C(0) | D:C(1)
ORX trunk_051_opt2/trunk_051_opt2_r_e11 -> e11_001 | O:Percival and the Lady of the Lake carry the cup out of the east door | E:SET none = C(0) | D:C(1)

ENC e01_001 turn=0..999
ORX e01_001_opt0/e01_001_opt0_r1 -> e01_002 | O:Arthur proposes the civic covenant | E:SET none = C(0) | D:C(1)
ORX e01_001_opt1/e01_001_opt1_r1 -> e01_002 | O:Guinevere declares the Grail a covenant | E:SET none = C(0) | D:C(1)
ORX e01_001_opt2/e01_001_opt2_r1 -> e01_002 | O:Lancelot sets down the seal | E:SET none = C(0) | D:C(1)

ENC e01_002 turn=0..999
ORX e01_002_opt0/e01_002_opt0_r1 -> e01_003 | O:Arthur binds the oath to failure | E:SET none = C(0) | D:C(1)
ORX e01_002_opt1/e01_002_opt1_r1 -> e01_003 | O:Guinevere opens the Grail to witnesses | E:SET none = C(0) | D:C(1)
ORX e01_002_opt2/e01_002_opt2_r1 -> e01_003 | O:Lancelot ties his oath to the exiles | E:SET none = C(0) | D:C(1)

ENC e01_003 turn=0..999
ORX e01_003_opt0/e01_003_opt0_r1 -> e01_004 | O:Arthur opens the succession to public judgment | E:SET none = C(0) | D:C(1)
ORX e01_003_opt1/e01_003_opt1_r1 -> e01_004 | O:Guinevere sends the Grail outward as testimony | E:SET none = C(0) | D:C(1)
ORX e01_003_opt2/e01_003_opt2_r1 -> e01_004 | O:Merlin and Morgan set the price of magic | E:SET none = C(0) | D:C(1)

ENC e01_004 turn=0..999
ORX e01_004_opt0/e01_004_opt0_r1 -> e01_005 | O:Arthur binds privilege | E:SET none = C(0) | D:C(1)
ORX e01_004_opt1/e01_004_opt1_r1 -> e01_005 | O:Guinevere charters the Grail | E:SET none = C(0) | D:C(1)
ORX e01_004_opt2/e01_004_opt2_r1 -> e01_005 | O:Mordred is asked to speak | E:SET none = C(0) | D:C(1)

ENC e01_005 turn=0..999
ORX e01_005_opt0/e01_005_opt0_r1 -> e01_006 | O:Mordred answers under witness | E:SET none = C(0) | D:C(1)
ORX e01_005_opt1/e01_005_opt1_r1 -> e01_006 | O:Every order names its loss | E:SET none = C(0) | D:C(1)
ORX e01_005_opt2/e01_005_opt2_r1 -> e01_006 | O:Open the outer road | E:SET none = C(0) | D:C(1)

ENC e01_006 turn=0..999
ORX e01_006_opt0/e01_006_opt0_r1 -> e01_007 | O:Mordred answers under oath | E:SET none = C(0) | D:C(1)
ORX e01_006_opt1/e01_006_opt1_r1 -> e01_007 | O:Set a visible deadline | E:SET none = C(0) | D:C(1)
ORX e01_006_opt2/e01_006_opt2_r1 -> e01_007 | O:Let the outer road in | E:SET none = C(0) | D:C(1)

ENC e01_007 turn=0..999
ORX e01_007_opt0/e01_007_opt0_r1 -> e01_008 | O:Seal the dated covenant | E:SET none = C(0) | D:C(1)
ORX e01_007_opt1/e01_007_opt1_r1 -> e01_008 | O:Guard the Grail as covenant | E:SET none = C(0) | D:C(1)
ORX e01_007_opt2/e01_007_opt2_r1 -> e01_008 | O:Let the road witness | E:SET none = C(0) | D:C(1)

ENC e01_008 turn=0..999
ORX e01_008_opt0/e01_008_opt0_r1 -> e01_009 | O:Record the surrenders | E:SET none = C(0) | D:C(1)
ORX e01_008_opt1/e01_008_opt1_r1 -> e01_009 | O:Make Guinevere the civic witness | E:SET none = C(0) | D:C(1)
ORX e01_008_opt2/e01_008_opt2_r1 -> e01_009 | O:Give Mordred a named witness seat | E:SET none = C(0) | D:C(1)

ENC e01_009 turn=0..999
ORX e01_009_opt0/e01_009_opt0_r1 -> e01_010 | O:Make people enforce it | E:SET none = C(0) | D:C(1)
ORX e01_009_opt1/e01_009_opt1_r1 -> e01_010 | O:Put Mordred's debts in the record | E:SET none = C(0) | D:C(1)
ORX e01_009_opt2/e01_009_opt2_r1 -> e01_010 | O:Open Arthur's succession to the road | E:SET none = C(0) | D:C(1)

ENC e01_010 turn=0..999
ORX e01_010_opt0/e01_010_opt0_r1 -> e01_011 | O:Seat the road-witnesses | E:SET none = C(0) | D:C(1)
ORX e01_010_opt1/e01_010_opt1_r1 -> e01_011 | O:Seal the Grail as covenant | E:SET none = C(0) | D:C(1)
ORX e01_010_opt2/e01_010_opt2_r1 -> e01_011 | O:Hold the succession reckoning | E:SET none = C(0) | D:C(1)

ENC e01_011 turn=0..999
ORX e01_011_opt0/e01_011_opt0_r1 -> e01_012 | O:Name the witnesses at the gate | E:SET none = C(0) | D:C(1)
ORX e01_011_opt1/e01_011_opt1_r1 -> e01_012 | O:Carry the Grail to the road's edge | E:SET none = C(0) | D:C(1)
ORX e01_011_opt2/e01_011_opt2_r1 -> e01_012 | O:Speak the succession question aloud | E:SET none = C(0) | D:C(1)

ENC e01_012 turn=0..999
ORX e01_012_opt0/e01_012_opt0_r1 -> e01_013 | O:Hold the public reckoning | E:SET none = C(0) | D:C(1)
ORX e01_012_opt1/e01_012_opt1_r1 -> e01_013 | O:Test the Grail against the debts | E:SET none = C(0) | D:C(1)
ORX e01_012_opt2/e01_012_opt2_r1 -> e01_013 | O:Let Lancelot withdraw from the choosing | E:SET none = C(0) | D:C(1)

ENC e01_013 turn=0..999
ORX e01_013_opt0/e01_013_opt0_r1 -> e01_014 | O:Ask the Grail what it holds | E:SET none = C(0) | D:C(1)
ORX e01_013_opt1/e01_013_opt1_r1 -> e01_014 | O:Let Lancelot answer for himself | E:SET none = C(0) | D:C(1)
ORX e01_013_opt2/e01_013_opt2_r1 -> e01_014 | O:Let Morgan test the peace | E:SET none = C(0) | D:C(1)

ENC e01_014 turn=0..999
ORX e01_014_opt0/e01_014_opt0_r1 -> e01_015 | O:Write the civic articles | E:SET none = C(0) | D:C(1)
ORX e01_014_opt1/e01_014_opt1_r1 -> e01_015 | O:Send the covenant beyond the shrine | E:SET none = C(0) | D:C(1)
ORX e01_014_opt2/e01_014_opt2_r1 -> e01_015 | O:Let Morgan challenge it | E:SET none = C(0) | D:C(1)

ENC e01_015 turn=0..999
ORX e01_015_opt0/e01_015_opt0_r1 -> e01_016 | O:Send the covenant outward | E:SET none = C(0) | D:C(1)
ORX e01_015_opt1/e01_015_opt1_r1 -> e01_016 | O:Let Morgan test the covenant | E:SET none = C(0) | D:C(1)
ORX e01_015_opt2/e01_015_opt2_r1 -> e01_016 | O:Settle the succession openly | E:SET none = C(0) | D:C(1)

ENC e01_016 turn=0..999
ORX e01_016_opt0/e01_016_opt0_r1 -> e01_017 | O:Send Percival into the road | E:SET none = C(0) | D:C(1)
ORX e01_016_opt1/e01_016_opt1_r1 -> e01_017 | O:Answer Morgan in the open | E:SET none = C(0) | D:C(1)
ORX e01_016_opt2/e01_016_opt2_r1 -> e01_017 | O:Hold a dawn return | E:SET none = C(0) | D:C(1)

ENC e01_017 turn=0..999
ORX e01_017_opt0/e01_017_opt0_r1 -> e01_018 | O:Send the covenant deeper | E:SET none = C(0) | D:C(1)
ORX e01_017_opt1/e01_017_opt1_r1 -> e01_018 | O:Answer Morgan publicly | E:SET none = C(0) | D:C(1)
ORX e01_017_opt2/e01_017_opt2_r1 -> e01_018 | O:Make the shrine public custody | E:SET none = C(0) | D:C(1)

ENC e01_018 turn=0..999
ORX e01_018_opt0/e01_018_opt0_r1 -> e01_019 | O:Open the keys | E:SET none = C(0) | D:C(1)
ORX e01_018_opt1/e01_018_opt1_r1 -> e01_019 | O:Name the cost | E:SET none = C(0) | D:C(1)
ORX e01_018_opt2/e01_018_opt2_r1 -> e01_019 | O:Send proof outward | E:SET none = C(0) | D:C(1)

ENC e01_019 turn=0..999
ORX e01_019_opt0/e01_019_opt0_r1 -> e01_020 | O:Hold the road test | E:SET none = C(0) | D:C(1)
ORX e01_019_opt1/e01_019_opt1_r1 -> e01_020 | O:Surrender a privilege | E:SET none = C(0) | D:C(1)
ORX e01_019_opt2/e01_019_opt2_r1 -> e01_020 | O:Ward the Grail openly | E:SET none = C(0) | D:C(1)

ENC e01_020 turn=0..999
ORX e01_020_opt0/e01_020_opt0_r1 -> e01_021 | O:Audit the covenant | E:SET none = C(0) | D:C(1)
ORX e01_020_opt1/e01_020_opt1_r1 -> e01_021 | O:Pay the cost now | E:SET none = C(0) | D:C(1)
ORX e01_020_opt2/e01_020_opt2_r1 -> e01_021 | O:Leave the road open | E:SET none = C(0) | D:C(1)

ENC e01_021 turn=0..999
ORX e01_021_opt0/e01_021_opt0_r1 -> e01_022 | O:Seat the Commons | E:SET none = C(0) | D:C(1)
ORX e01_021_opt1/e01_021_opt1_r1 -> e01_022 | O:Make Lancelot a witness | E:SET none = C(0) | D:C(1)
ORX e01_021_opt2/e01_021_opt2_r1 -> e01_022 | O:Test the Grail | E:SET none = C(0) | D:C(1)

ENC e01_022 turn=0..999
ORX e01_022_opt0/e01_022_opt0_r1 -> e01_023 | O:Bind the witness seal | E:SET none = C(0) | D:C(1)
ORX e01_022_opt1/e01_022_opt1_r1 -> e01_023 | O:Open the Grail audit | E:SET none = C(0) | D:C(1)
ORX e01_022_opt2/e01_022_opt2_r1 -> e01_023 | O:Place Mordred in the table | E:SET none = C(0) | D:C(1)

ENC e01_023 turn=0..999

ENC e02_001 turn=0..999
ORX e02_001_opt0/e02_001_opt0_r1 -> e02_002 | O:Arthur re-speaks the oath and demands every household swear or leave | E:SET none = C(0) | D:C(1)
ORX e02_001_opt1/e02_001_opt1_r1 -> e02_002 | O:Lancelot publicly withdraws from the oath and takes his household with him | E:SET none = C(0) | D:C(1)
ORX e02_001_opt2/e02_001_opt2_r1 -> e02_002 | O:Morgan brokers a hidden double pact between Gawain, Mordred, and Lancelot | E:SET none = C(0) | D:C(1)

ENC e02_002 turn=0..999
ORX e02_002_opt0/e02_002_opt0_r1 -> e02_003 | O:Arthur declares succession publicly, binding the crown to household pledges | E:SET none = C(0) | D:C(1)
ORX e02_002_opt1/e02_002_opt1_r1 -> e02_003 | O:Gawain and Mordred make the feud open before the court | E:SET none = C(0) | D:C(1)
ORX e02_002_opt2/e02_002_opt2_r1 -> e02_003 | O:Morgan brokers a hidden double pact for Gawain, Mordred and Lancelot | E:SET none = C(0) | D:C(1)

ENC e02_003 turn=0..999
ORX e02_003_opt0/e02_003_opt0_r1 -> e02_004 | O:Arthur binds the exiles into four pledges beneath the columns | E:SET none = C(0) | D:C(1)
ORX e02_003_opt1/e02_003_opt1_r1 -> e02_004 | O:Morgan forces the double pact into the open at the Grail | E:SET none = C(0) | D:C(1)
ORX e02_003_opt2/e02_003_opt2_r1 -> e02_004 | O:Percival and the Lady of the Lake carry the Grail out of the hall | E:SET none = C(0) | D:C(1)

ENC e02_004 turn=0..999
ORX e02_004_opt0/e02_004_opt0_r1 -> e02_005 | O:Arthur binds the four households beneath one common shrine | E:SET none = C(0) | D:C(1)
ORX e02_004_opt1/e02_004_opt1_r1 -> e02_005 | O:Mordred declares the pact void and takes the oath-shards | E:SET none = C(0) | D:C(1)
ORX e02_004_opt2/e02_004_opt2_r1 -> e02_005 | O:Lancelot, Guinevere and the exiles step outside the charter | E:SET none = C(0) | D:C(1)

ENC e02_005 turn=0..999
ORX e02_005_opt0/e02_005_opt0_r1 -> e02_006 | O:Gawain stands with Arthur against Mordred's crown claim | E:SET none = C(0) | D:C(1)
ORX e02_005_opt1/e02_005_opt1_r1 -> e02_006 | O:Lancelot and Guinevere leave with the exiles to build a new charter | E:SET none = C(0) | D:C(1)
ORX e02_005_opt2/e02_005_opt2_r1 -> e02_006 | O:Merlin binds or breaks the old magic openly | E:SET none = C(0) | D:C(1)

ENC e02_006 turn=0..999
ORX e02_006_opt0/e02_006_opt0_r1 -> e02_007 | O:Arthur rebuilds the oath around the exiles | E:SET none = C(0) | D:C(1)
ORX e02_006_opt1/e02_006_opt1_r1 -> e02_007 | O:Mordred claims the oath-shards as law | E:SET none = C(0) | D:C(1)
ORX e02_006_opt2/e02_006_opt2_r1 -> e02_007 | O:Merlin names Morgan's old compact | E:SET none = C(0) | D:C(1)

ENC e02_007 turn=0..999
ORX e02_007_opt0/e02_007_opt0_r1 -> e02_008 | O:Arthur stakes the threshold for named households | E:SET none = C(0) | D:C(1)
ORX e02_007_opt1/e02_007_opt1_r1 -> e02_008 | O:Gawain and Arthur hold the shards | E:SET none = C(0) | D:C(1)
ORX e02_007_opt2/e02_007_opt2_r1 -> e02_008 | O:Merlin breaks or binds the old compact | E:SET none = C(0) | D:C(1)

ENC e02_008 turn=0..999
ORX e02_008_opt0/e02_008_opt0_r1 -> e02_009 | O:Arthur turns the shards into household pledges | E:SET none = C(0) | D:C(1)
ORX e02_008_opt1/e02_008_opt1_r1 -> e02_009 | O:Lancelot names one oath he can no longer keep | E:SET none = C(0) | D:C(1)
ORX e02_008_opt2/e02_008_opt2_r1 -> e02_009 | O:Merlin opens Morgan's hidden compact | E:SET none = C(0) | D:C(1)

ENC e02_009 turn=0..999
ORX e02_009_opt0/e02_009_opt0_r1 -> e02_010 | O:Arthur grants named household charters | E:SET none = C(0) | D:C(1)
ORX e02_009_opt1/e02_009_opt1_r1 -> e02_010 | O:Guinevere and Lancelot make sanctuary for the child | E:SET none = C(0) | D:C(1)
ORX e02_009_opt2/e02_009_opt2_r1 -> e02_010 | O:Merlin reads Morgan's compact aloud | E:SET none = C(0) | D:C(1)

ENC e02_010 turn=0..999
ORX e02_010_opt0/e02_010_opt0_r1 -> e02_011 | O:Arthur makes the compact public and calls for a single ruling | E:SET none = C(0) | D:C(1)
ORX e02_010_opt1/e02_010_opt1_r1 -> e02_011 | O:Guinevere and Lancelot make the child the hinge of every oath | E:SET none = C(0) | D:C(1)
ORX e02_010_opt2/e02_010_opt2_r1 -> e02_011 | O:Merlin and Morgan try to rewrite the compact with named debts | E:SET none = C(0) | D:C(1)

ENC e02_011 turn=0..999
ORX e02_011_opt0/e02_011_opt0_r1 -> e02_012 | O:Arthur accepts a limited throne held under household oaths | E:SET none = C(0) | D:C(1)
ORX e02_011_opt1/e02_011_opt1_r1 -> e02_012 | O:Guinevere and Lancelot carry the child beyond the gate into border sanctuary | E:SET none = C(0) | D:C(1)
ORX e02_011_opt2/e02_011_opt2_r1 -> e02_012 | O:Merlin and Morgan carve Morgan's compact into a public ledger of debts | E:SET none = C(0) | D:C(1)

ENC e02_012 turn=0..999
ORX e02_012_opt0/e02_012_opt0_r1 -> e02_013 | O:Arthur accepts three hearths sharing one bridge-ward | E:SET none = C(0) | D:C(1)
ORX e02_012_opt1/e02_012_opt1_r1 -> e02_013 | O:Guinevere and Lancelot carry the child to a border sanctuary | E:SET none = C(0) | D:C(1)
ORX e02_012_opt2/e02_012_opt2_r1 -> e02_013 | O:Morgan and Merlin finish the ledger while excluding sworn debts | E:SET none = C(0) | D:C(1)

ENC e02_013 turn=0..999
ORX e02_013_opt0/e02_013_opt0_r1 -> e02_014 | O:Arthur binds the hearths into three oath-wardships under one bridge-ward | E:SET none = C(0) | D:C(1)
ORX e02_013_opt1/e02_013_opt1_r1 -> e02_014 | O:Lancelot and Guinevere carry the child beyond the gate to border sanctuary | E:SET none = C(0) | D:C(1)
ORX e02_013_opt2/e02_013_opt2_r1 -> e02_014 | O:Morgan forces every household to declare one promise kept and one broken before the ledger closes | E:SET none = C(0) | D:C(1)

ENC e02_014 turn=0..999
ORX e02_014_opt0/e02_014_opt0_r1 -> e02_015 | O:Guinevere and Lancelot carry the child across the gate to the border sanctuary | E:SET none = C(0) | D:C(1)
ORX e02_014_opt1/e02_014_opt1_r1 -> e02_015 | O:Morgan declares every sworn debt now answerable to the ledger, not to the crown | E:SET none = C(0) | D:C(1)
ORX e02_014_opt2/e02_014_opt2_r1 -> e02_015 | O:Gawain and Percival split the child's custody between the three oath-hearths | E:SET none = C(0) | D:C(1)

ENC e02_015 turn=0..999
ORX e02_015_opt0/e02_015_opt0_r1 -> e02_016 | O:Arthur and Merlin bind the three hearths to a rotating bridge-ward instead of a single crown | E:SET none = C(0) | D:C(1)
ORX e02_015_opt1/e02_015_opt1_r1 -> e02_016 | O:Lancelot and Guinevere open the border gate while Gawain and Percival keep the inner gate for exiles and widows | E:SET none = C(0) | D:C(1)
ORX e02_015_opt2/e02_015_opt2_r1 -> e02_016 | O:Morgan forces each household to surrender one kept promise and one broken one before the ledger closes | E:SET none = C(0) | D:C(1)

ENC e02_016 turn=0..999
ORX e02_016_opt0/e02_016_opt0_r1 -> e02_017 | O:Arthur, Merlin and Mordred bind the three hearths to a witness-road rotation | E:SET none = C(0) | D:C(1)
ORX e02_016_opt1/e02_016_opt1_r1 -> e02_017 | O:Lancelot and Guinevere hold the border sanctuary while Gawain and Percival keep the inner gate | E:SET none = C(0) | D:C(1)
ORX e02_016_opt2/e02_016_opt2_r1 -> e02_017 | O:Morgan calls every oath before the public debt-court and demands pay, pledge or break | E:SET none = C(0) | D:C(1)

ENC e02_017 turn=0..999
ORX e02_017_opt0/e02_017_opt0_r1 -> e02_018 | O:Arthur, Merlin and Bedivere carry the oath as a rotating witness-ward instead of a crown | E:SET none = C(0) | D:C(1)
ORX e02_017_opt1/e02_017_opt1_r1 -> e02_018 | O:Lancelot and Guinevere open the border sanctuary while Gawain and Percival keep the inner law | E:SET none = C(0) | D:C(1)
ORX e02_017_opt2/e02_017_opt2_r1 -> e02_018 | O:Morgan forces every hearth to answer one kept promise and one broken one before the ledger closes | E:SET none = C(0) | D:C(1)

ENC e02_018 turn=0..999
ORX e02_018_opt0/e02_018_opt0_r1 -> e02_019 | O:Arthur and Percival bind the hearths into a rotating witness-road | E:SET none = C(0) | D:C(1)
ORX e02_018_opt1/e02_018_opt1_r1 -> e02_019 | O:Lancelot, Guinevere and the Lady of the Lake open the border sanctuary | E:SET none = C(0) | D:C(1)
ORX e02_018_opt2/e02_018_opt2_r1 -> e02_019 | O:Morgan forces every hearth to pledge one kept promise and one broken promise | E:SET none = C(0) | D:C(1)

ENC e02_019 turn=0..999
ORX e02_019_opt0/e02_019_opt0_r1 -> e02_020 | O:Arthur, Merlin and Bedivere bind the hearths into a rotating witness-road | E:SET none = C(0) | D:C(1)
ORX e02_019_opt1/e02_019_opt1_r1 -> e02_020 | O:Lancelot, Guinevere and the Lady of the Lake open the border sanctuary | E:SET none = C(0) | D:C(1)
ORX e02_019_opt2/e02_019_opt2_r1 -> e02_020 | O:Morgan forces one kept and one broken promise from every hearth | E:SET none = C(0) | D:C(1)

ENC e02_020 turn=0..999
ORX e02_020_opt0/e02_020_opt0_r1 -> e02_021 | O:Arthur and Percival make the hearths swear a rotating witness-road | E:SET none = C(0) | D:C(1)
ORX e02_020_opt1/e02_020_opt1_r1 -> e02_021 | O:Lancelot and Guinevere keep the border sanctuary open | E:SET none = C(0) | D:C(1)
ORX e02_020_opt2/e02_020_opt2_r1 -> e02_021 | O:Morgan forces one kept and one broken promise to be spoken aloud | E:SET none = C(0) | D:C(1)

ENC e02_021 turn=0..999
ORX e02_021_opt0/e02_021_opt0_r1 -> e02_022 | O:Arthur, Merlin and Bedivere swear the rotating witness-road | E:SET none = C(0) | D:C(1)
ORX e02_021_opt1/e02_021_opt1_r1 -> e02_022 | O:Lancelot, Guinevere and the Lady of the Lake ratify the sanctuary | E:SET none = C(0) | D:C(1)
ORX e02_021_opt2/e02_021_opt2_r1 -> e02_022 | O:Morgan forces every hearth to speak kept and broken promises | E:SET none = C(0) | D:C(1)

ENC e02_022 turn=0..999

ENC e03_001 turn=0..999
ORX e03_001_opt0/e03_001_opt0_r1 -> e03_002 | O:Gawain seals Excalibur under the crown | E:SET none = C(0) | D:C(1)
ORX e03_001_opt1/e03_001_opt1_r1 -> e03_002 | O:Lancelot carries Excalibur beyond the oath-ring | E:SET none = C(0) | D:C(1)
ORX e03_001_opt2/e03_001_opt2_r1 -> e03_002 | O:Morgan and Merlin loosen the old binding | E:SET none = C(0) | D:C(1)

ENC e03_002 turn=0..999
ORX e03_002_opt0/e03_002_opt0_r1 -> e03_003 | O:Arthur closes the shrine as law | E:SET none = C(0) | D:C(1)
ORX e03_002_opt1/e03_002_opt1_r1 -> e03_003 | O:Lancelot carries Excalibur to the exiles | E:SET none = C(0) | D:C(1)
ORX e03_002_opt2/e03_002_opt2_r1 -> e03_003 | O:Morgan breaks the old binding | E:SET none = C(0) | D:C(1)

ENC e03_003 turn=0..999
ORX e03_003_opt0/e03_003_opt0_r1 -> e03_004 | O:Gawain swears a ward-and-exile common oath | E:SET none = C(0) | D:C(1)
ORX e03_003_opt1/e03_003_opt1_r1 -> e03_004 | O:Lancelot carries Excalibur into the exile road | E:SET none = C(0) | D:C(1)
ORX e03_003_opt2/e03_003_opt2_r1 -> e03_004 | O:Morgan and Merlin set the sword to three allegiances | E:SET none = C(0) | D:C(1)

ENC e03_004 turn=0..999
ORX e03_004_opt0/e03_004_opt0_r1 -> e03_005 | O:Arthur grants claimant status, not kingship | E:SET none = C(0) | D:C(1)
ORX e03_004_opt1/e03_004_opt1_r1 -> e03_005 | O:Lancelot carries Excalibur to the exile road | E:SET none = C(0) | D:C(1)
ORX e03_004_opt2/e03_004_opt2_r1 -> e03_005 | O:Morgan and Merlin let Excalibur answer three charters | E:SET none = C(0) | D:C(1)

ENC e03_005 turn=0..999
ORX e03_005_opt0/e03_005_opt0_r1 -> e03_006 | O:Gawain swears the witness-oath | E:SET none = C(0) | D:C(1)
ORX e03_005_opt1/e03_005_opt1_r1 -> e03_006 | O:Lancelot gives the blade a road | E:SET none = C(0) | D:C(1)
ORX e03_005_opt2/e03_005_opt2_r1 -> e03_006 | O:Morgan and Merlin cut one binding thread | E:SET none = C(0) | D:C(1)

ENC e03_006 turn=0..999
ORX e03_006_opt0/e03_006_opt0_r1 -> e03_007 | O:Arthur splits the sword into three co-guardians | E:SET none = C(0) | D:C(1)
ORX e03_006_opt1/e03_006_opt1_r1 -> e03_007 | O:Lancelot carries Excalibur to the exile road | E:SET none = C(0) | D:C(1)
ORX e03_006_opt2/e03_006_opt2_r1 -> e03_007 | O:Morgan and Merlin read the three charters and bind them with a third oath | E:SET none = C(0) | D:C(1)

ENC e03_007 turn=0..999
ORX e03_007_opt0/e03_007_opt0_r1 -> e03_008 | O:Gawain builds a counted witness-fence | E:SET none = C(0) | D:C(1)
ORX e03_007_opt1/e03_007_opt1_r1 -> e03_008 | O:Lancelot carries the road-lamp to the exile road | E:SET none = C(0) | D:C(1)
ORX e03_007_opt2/e03_007_opt2_r1 -> e03_008 | O:Morgan binds the severed thread into a feudal charter | E:SET none = C(0) | D:C(1)

ENC e03_008 turn=0..999
ORX e03_008_opt0/e03_008_opt0_r1 -> e03_009 | O:Arthur forces a witnessed three-part split | E:SET none = C(0) | D:C(1)
ORX e03_008_opt1/e03_008_opt1_r1 -> e03_009 | O:Lancelot opens the exile road | E:SET none = C(0) | D:C(1)
ORX e03_008_opt2/e03_008_opt2_r1 -> e03_009 | O:Morgan binds the seam into a feudal charter | E:SET none = C(0) | D:C(1)

ENC e03_009 turn=0..999
ORX e03_009_opt0/e03_009_opt0_r1 -> e03_010 | O:Arthur witnesses a three-claim covenant | E:SET none = C(0) | D:C(1)
ORX e03_009_opt1/e03_009_opt1_r1 -> e03_010 | O:Lancelot opens the road to widows and exiles | E:SET none = C(0) | D:C(1)
ORX e03_009_opt2/e03_009_opt2_r1 -> e03_010 | O:Morgan and Merlin bind the last thread | E:SET none = C(0) | D:C(1)

ENC e03_010 turn=0..999
ORX e03_010_opt0/e03_010_opt0_r1 -> e03_011 | O:Arthur witnesses a three-seat fracture | E:SET none = C(0) | D:C(1)
ORX e03_010_opt1/e03_010_opt1_r1 -> e03_011 | O:Lancelot opens the exile road | E:SET none = C(0) | D:C(1)
ORX e03_010_opt2/e03_010_opt2_r1 -> e03_011 | O:Morgan and Merlin bind the last thread | E:SET none = C(0) | D:C(1)

ENC e03_011 turn=0..999
ORX e03_011_opt0/e03_011_opt0_r1 -> e03_012 | O:Arthur witnesses three signatures | E:SET none = C(0) | D:C(1)
ORX e03_011_opt1/e03_011_opt1_r1 -> e03_012 | O:Lancelot swears the gate before the blade | E:SET none = C(0) | D:C(1)
ORX e03_011_opt2/e03_011_opt2_r1 -> e03_012 | O:Morgan and Merlin loose the last thread | E:SET none = C(0) | D:C(1)

ENC e03_012 turn=0..999
ORX e03_012_opt0/e03_012_opt0_r1 -> e03_013 | O:Arthur witnesses a three-seat charter | E:SET none = C(0) | D:C(1)
ORX e03_012_opt1/e03_012_opt1_r1 -> e03_013 | O:Lancelot opens the gate to widows | E:SET none = C(0) | D:C(1)
ORX e03_012_opt2/e03_012_opt2_r1 -> e03_013 | O:Morgan and Merlin bind the portable seam | E:SET none = C(0) | D:C(1)

ENC e03_013 turn=0..999
ORX e03_013_opt0/e03_013_opt0_r1 -> e03_014 | O:Arthur witnesses the three-seat oath | E:SET none = C(0) | D:C(1)
ORX e03_013_opt1/e03_013_opt1_r1 -> e03_014 | O:Lancelot feeds the widows at the threshold | E:SET none = C(0) | D:C(1)
ORX e03_013_opt2/e03_013_opt2_r1 -> e03_014 | O:Morgan and Merlin fold the seam into a portable charter | E:SET none = C(0) | D:C(1)

ENC e03_014 turn=0..999
ORX e03_014_opt0/e03_014_opt0_r1 -> e03_015 | O:Arthur seals the three-seat pledge | E:SET none = C(0) | D:C(1)
ORX e03_014_opt1/e03_014_opt1_r1 -> e03_015 | O:Lancelot feeds the gate | E:SET none = C(0) | D:C(1)
ORX e03_014_opt2/e03_014_opt2_r1 -> e03_015 | O:Morgan and Merlin carry Excalibur's charter | E:SET none = C(0) | D:C(1)

ENC e03_015 turn=0..999
ORX e03_015_opt0/e03_015_opt0_r1 -> e03_016 | O:Arthur seals the threshold charter | E:SET none = C(0) | D:C(1)
ORX e03_015_opt1/e03_015_opt1_r1 -> e03_016 | O:Lancelot feeds the cracked gate | E:SET none = C(0) | D:C(1)
ORX e03_015_opt2/e03_015_opt2_r1 -> e03_016 | O:Morgan and Merlin carry the compact | E:SET none = C(0) | D:C(1)

ENC e03_016 turn=0..999
ORX e03_016_opt0/e03_016_opt0_r1 -> e03_017 | O:Arthur splits the threshold into three lawful doors | E:SET none = C(0) | D:C(1)
ORX e03_016_opt1/e03_016_opt1_r1 -> e03_017 | O:Lancelot feeds the feast outside the shrine | E:SET none = C(0) | D:C(1)
ORX e03_016_opt2/e03_016_opt2_r1 -> e03_017 | O:Morgan and Merlin give the compact to the Lady of the Lake | E:SET none = C(0) | D:C(1)

ENC e03_017 turn=0..999
ORX e03_017_opt0/e03_017_opt0_r1 -> e03_018 | O:Arthur seals the three-seat gate | E:SET none = C(0) | D:C(1)
ORX e03_017_opt1/e03_017_opt1_r1 -> e03_018 | O:Lancelot feeds the feast outside the shrine | E:SET none = C(0) | D:C(1)
ORX e03_017_opt2/e03_017_opt2_r1 -> e03_018 | O:Morgan and Merlin give the compact to Percival | E:SET none = C(0) | D:C(1)

ENC e03_018 turn=0..999
ORX e03_018_opt0/e03_018_opt0_r1 -> e03_019 | O:Arthur swears the threshold in three voices | E:SET none = C(0) | D:C(1)
ORX e03_018_opt1/e03_018_opt1_r1 -> e03_019 | O:Lancelot guards the feast outside the crown-hall | E:SET none = C(0) | D:C(1)
ORX e03_018_opt2/e03_018_opt2_r1 -> e03_019 | O:Morgan and Merlin leave the compact in the Lady of the Lake's hand | E:SET none = C(0) | D:C(1)

ENC e03_019 turn=0..999
ORX e03_019_opt0/e03_019_opt0_r1 -> e03_020 | O:Arthur breaks the claim-rings | E:SET none = C(0) | D:C(1)
ORX e03_019_opt1/e03_019_opt1_r1 -> e03_020 | O:Lancelot stakes the feast on the exiles' road | E:SET none = C(0) | D:C(1)
ORX e03_019_opt2/e03_019_opt2_r1 -> e03_020 | O:Lady of the Lake gives the compact to Percival | E:SET none = C(0) | D:C(1)

ENC e03_020 turn=0..999
ORX e03_020_opt0/e03_020_opt0_r1 -> e03_021 | O:Arthur splits the seal open | E:SET none = C(0) | D:C(1)
ORX e03_020_opt1/e03_020_opt1_r1 -> e03_021 | O:Lancelot carries Excalibur to the exiles | E:SET none = C(0) | D:C(1)
ORX e03_020_opt2/e03_020_opt2_r1 -> e03_021 | O:Lady of the Lake feeds or breaks the silver | E:SET none = C(0) | D:C(1)

ENC e03_021 turn=0..999
ORX e03_021_opt0/e03_021_opt0_r1 -> e03_022 | O:Arthur binds the wound | E:SET none = C(0) | D:C(1)
ORX e03_021_opt1/e03_021_opt1_r1 -> e03_022 | O:Lancelot carries the oath outside | E:SET none = C(0) | D:C(1)
ORX e03_021_opt2/e03_021_opt2_r1 -> e03_022 | O:Lady of the Lake trades the compact | E:SET none = C(0) | D:C(1)

ENC e03_022 turn=0..999
ORX e03_022_opt0/e03_022_opt0_r1 -> e03_023 | O:Arthur closes the oath | E:SET none = C(0) | D:C(1)
ORX e03_022_opt1/e03_022_opt1_r1 -> e03_023 | O:Lancelot carries the blade to the road | E:SET none = C(0) | D:C(1)
ORX e03_022_opt2/e03_022_opt2_r1 -> e03_023 | O:Merlin bargains the silver for an heir | E:SET none = C(0) | D:C(1)

ENC e03_023 turn=0..999

ENC e04_001 turn=0..999
ORX e04_001_opt0/e04_001_opt0_r1 -> e04_002 | O:Arthur yields the oath to Mordred | E:SET none = C(0) | D:C(1)
ORX e04_001_opt1/e04_001_opt1_r1 -> e04_002 | O:Arthur swears the Round Table anew around both claims | E:SET none = C(0) | D:C(1)
ORX e04_001_opt2/e04_001_opt2_r1 -> e04_002 | O:The court offers Mordred the exile-witnessed road | E:SET none = C(0) | D:C(1)

ENC e04_002 turn=0..999
ORX e04_002_opt0/e04_002_opt0_r1 -> e04_003 | O:Arthur ratifies Mordred as steward | E:SET none = C(0) | D:C(1)
ORX e04_002_opt1/e04_002_opt1_r1 -> e04_003 | O:Arthur separates the Grail shrine from the crown | E:SET none = C(0) | D:C(1)
ORX e04_002_opt2/e04_002_opt2_r1 -> e04_003 | O:The court gives the exiles a road charter | E:SET none = C(0) | D:C(1)

ENC e04_003 turn=0..999
ORX e04_003_opt0/e04_003_opt0_r1 -> e04_004 | O:Arthur grants Mordred a sanctuary charter | E:SET none = C(0) | D:C(1)
ORX e04_003_opt1/e04_003_opt1_r1 -> e04_004 | O:The Round Table is split into two tables | E:SET none = C(0) | D:C(1)
ORX e04_003_opt2/e04_003_opt2_r1 -> e04_004 | O:Merlin and Morgan audit the oaths aloud | E:SET none = C(0) | D:C(1)

ENC e04_004 turn=0..999
ORX e04_004_opt0/e04_004_opt0_r1 -> e04_005 | O:Leave the ninth seat empty as a public question | E:SET none = C(0) | D:C(1)
ORX e04_004_opt1/e04_004_opt1_r1 -> e04_005 | O:Make the succession an open census | E:SET none = C(0) | D:C(1)
ORX e04_004_opt2/e04_004_opt2_r1 -> e04_005 | O:Hold the shrine shut for one night | E:SET none = C(0) | D:C(1)

ENC e04_005 turn=0..999
ORX e04_005_opt0/e04_005_opt0_r1 -> e04_006 | O:Open the census at the threshold | E:SET none = C(0) | D:C(1)
ORX e04_005_opt1/e04_005_opt1_r1 -> e04_006 | O:Order a joint feast for the exiles | E:SET none = C(0) | D:C(1)
ORX e04_005_opt2/e04_005_opt2_r1 -> e04_006 | O:Open the shrine for one hour | E:SET none = C(0) | D:C(1)

ENC e04_006 turn=0..999
ORX e04_006_opt0/e04_006_opt0_r1 -> e04_007 | O:Let Mordred sit, bound by the shrine oath | E:SET none = C(0) | D:C(1)
ORX e04_006_opt1/e04_006_opt1_r1 -> e04_007 | O:Write a joint charter of sharing | E:SET none = C(0) | D:C(1)
ORX e04_006_opt2/e04_006_opt2_r1 -> e04_007 | O:Open the gates to the exiles | E:SET none = C(0) | D:C(1)

ENC e04_007 turn=0..999
ORX e04_007_opt0/e04_007_opt0_r1 -> e04_008 | O:Yield the ninth seat to Mordred | E:SET none = C(0) | D:C(1)
ORX e04_007_opt1/e04_007_opt1_r1 -> e04_008 | O:Feed the exiles from the shrine stores | E:SET none = C(0) | D:C(1)
ORX e04_007_opt2/e04_007_opt2_r1 -> e04_008 | O:Seal the Round Table | E:SET none = C(0) | D:C(1)

ENC e04_008 turn=0..999
ORX e04_008_opt0/e04_008_opt0_r1 -> e04_009 | O:Let Mordred inherit the writ and the gates | E:SET none = C(0) | D:C(1)
ORX e04_008_opt1/e04_008_opt1_r1 -> e04_009 | O:Make Arthur a witness, not a ruler | E:SET none = C(0) | D:C(1)
ORX e04_008_opt2/e04_008_opt2_r1 -> e04_009 | O:Break the seal into a ledger of debts | E:SET none = C(0) | D:C(1)

ENC e04_009 turn=0..999
ORX e04_009_opt0/e04_009_opt0_r1 -> e04_010 | O:Break the ninth seat open | E:SET none = C(0) | D:C(1)
ORX e04_009_opt1/e04_009_opt1_r1 -> e04_010 | O:Let the exiles re-seat themselves | E:SET none = C(0) | D:C(1)
ORX e04_009_opt2/e04_009_opt2_r1 -> e04_010 | O:Keep the seal as a sacrament | E:SET none = C(0) | D:C(1)

ENC e04_010 turn=0..999
ORX e04_010_opt0/e04_010_opt0_r1 -> e04_011 | O:Seal the exile writ | E:SET none = C(0) | D:C(1)
ORX e04_010_opt1/e04_010_opt1_r1 -> e04_011 | O:Make the ledger a court | E:SET none = C(0) | D:C(1)
ORX e04_010_opt2/e04_010_opt2_r1 -> e04_011 | O:Close the shrine | E:SET none = C(0) | D:C(1)

ENC e04_011 turn=0..999
ORX e04_011_opt0/e04_011_opt0_r1 -> e04_012 | O:Feed the ledger | E:SET none = C(0) | D:C(1)
ORX e04_011_opt1/e04_011_opt1_r1 -> e04_012 | O:Take the ninth seat | E:SET none = C(0) | D:C(1)
ORX e04_011_opt2/e04_011_opt2_r1 -> e04_012 | O:Open the dying shrine | E:SET none = C(0) | D:C(1)

ENC e04_012 turn=0..999
ORX e04_012_opt0/e04_012_opt0_r1 -> e04_013 | O:Make the witness a covenant | E:SET none = C(0) | D:C(1)
ORX e04_012_opt1/e04_012_opt1_r1 -> e04_013 | O:Break the ninth page | E:SET none = C(0) | D:C(1)
ORX e04_012_opt2/e04_012_opt2_r1 -> e04_013 | O:Carry the coal out | E:SET none = C(0) | D:C(1)

ENC e04_013 turn=0..999
ORX e04_013_opt0/e04_013_opt0_r1 -> e04_014 | O:Renew the feedings | E:SET none = C(0) | D:C(1)
ORX e04_013_opt1/e04_013_opt1_r1 -> e04_014 | O:Carry the coal out | E:SET none = C(0) | D:C(1)
ORX e04_013_opt2/e04_013_opt2_r1 -> e04_014 | O:Test the borrowed hand | E:SET none = C(0) | D:C(1)

ENC e04_014 turn=0..999
ORX e04_014_opt0/e04_014_opt0_r1 -> e04_015 | O:Seat the exiles | E:SET none = C(0) | D:C(1)
ORX e04_014_opt1/e04_014_opt1_r1 -> e04_015 | O:Speak the covenant as law | E:SET none = C(0) | D:C(1)
ORX e04_014_opt2/e04_014_opt2_r1 -> e04_015 | O:Close the Round Table | E:SET none = C(0) | D:C(1)

ENC e04_015 turn=0..999
ORX e04_015_opt0/e04_015_opt0_r1 -> e04_016 | O:Open the ledger | E:SET none = C(0) | D:C(1)
ORX e04_015_opt1/e04_015_opt1_r1 -> e04_016 | O:Sever the crown | E:SET none = C(0) | D:C(1)
ORX e04_015_opt2/e04_015_opt2_r1 -> e04_016 | O:Carry the light | E:SET none = C(0) | D:C(1)

ENC e04_016 turn=0..999
ORX e04_016_opt0/e04_016_opt0_r1 -> e04_017 | O:Carry the law onward | E:SET none = C(0) | D:C(1)
ORX e04_016_opt1/e04_016_opt1_r1 -> e04_017 | O:Seal the signatures | E:SET none = C(0) | D:C(1)
ORX e04_016_opt2/e04_016_opt2_r1 -> e04_017 | O:Let Mordred rule | E:SET none = C(0) | D:C(1)

ENC e04_017 turn=0..999
ORX e04_017_opt0/e04_017_opt0_r1 -> e04_018 | O:Ward the shrine | E:SET none = C(0) | D:C(1)
ORX e04_017_opt1/e04_017_opt1_r1 -> e04_018 | O:Grant Mordred kingship | E:SET none = C(0) | D:C(1)
ORX e04_017_opt2/e04_017_opt2_r1 -> e04_018 | O:Publish the debts | E:SET none = C(0) | D:C(1)

ENC e04_018 turn=0..999
ORX e04_018_opt0/e04_018_opt0_r1 -> e04_019 | O:Crown Mordred by debt | E:SET none = C(0) | D:C(1)
ORX e04_018_opt1/e04_018_opt1_r1 -> e04_019 | O:Keep the table, refuse the crown | E:SET none = C(0) | D:C(1)
ORX e04_018_opt2/e04_018_opt2_r1 -> e04_019 | O:Make the shrine the heir | E:SET none = C(0) | D:C(1)

ENC e04_019 turn=0..999
ORX e04_019_opt0/e04_019_opt0_r1 -> e04_020 | O:Split the shrine | E:SET none = C(0) | D:C(1)
ORX e04_019_opt1/e04_019_opt1_r1 -> e04_020 | O:Let Mordred rule with public seats | E:SET none = C(0) | D:C(1)
ORX e04_019_opt2/e04_019_opt2_r1 -> e04_020 | O:Break the Round Table | E:SET none = C(0) | D:C(1)

ENC e04_020 turn=0..999
ORX e04_020_opt0/e04_020_opt0_r1 -> e04_021 | O:Bind Mordred to public audit | E:SET none = C(0) | D:C(1)
ORX e04_020_opt1/e04_020_opt1_r1 -> e04_021 | O:Hand the flame to keeper-homes | E:SET none = C(0) | D:C(1)
ORX e04_020_opt2/e04_020_opt2_r1 -> e04_021 | O:Make the table testimony | E:SET none = C(0) | D:C(1)

ENC e04_021 turn=0..999
ORX e04_021_opt0/e04_021_opt0_r1 -> e04_022 | O:Make Mordred a revocable custodian | E:SET none = C(0) | D:C(1)
ORX e04_021_opt1/e04_021_opt1_r1 -> e04_022 | O:Move the shrine to exile-wards | E:SET none = C(0) | D:C(1)
ORX e04_021_opt2/e04_021_opt2_r1 -> e04_022 | O:Seal the table as witness-stones | E:SET none = C(0) | D:C(1)

ENC e04_022 turn=0..999
ORX e04_022_opt0/e04_022_opt0_r1 -> e04_023 | O:Bind Mordred to public audit | E:SET none = C(0) | D:C(1)
ORX e04_022_opt1/e04_022_opt1_r1 -> e04_023 | O:Split the flame to keeper-homes | E:SET none = C(0) | D:C(1)
ORX e04_022_opt2/e04_022_opt2_r1 -> e04_023 | O:Open the table as testimony archive | E:SET none = C(0) | D:C(1)

ENC e04_023 turn=0..999

ENC e05_001 turn=0..999
ORX e05_001_opt0/e05_001_opt0_r1 -> e05_002 | O:Galahad carries the cup outward | E:SET none = C(0) | D:C(1)
ORX e05_001_opt1/e05_001_opt1_r1 -> e05_002 | O:Percival carries the cup and names the exiles | E:SET none = C(0) | D:C(1)
ORX e05_001_opt2/e05_001_opt2_r1 -> e05_002 | O:Arthur seals the shrine and holds the crown | E:SET none = C(0) | D:C(1)

ENC e05_002 turn=0..999
ORX e05_002_opt0/e05_002_opt0_r1 -> e05_003 | O:Percival names the exiles into the covenant | E:SET none = C(0) | D:C(1)
ORX e05_002_opt1/e05_002_opt1_r1 -> e05_003 | O:Galahad asks Arthur to pledge the shrine to widows and exiles | E:SET none = C(0) | D:C(1)
ORX e05_002_opt2/e05_002_opt2_r1 -> e05_003 | O:Morgan offers the old magic to seal the road | E:SET none = C(0) | D:C(1)

ENC e05_003 turn=0..999
ORX e05_003_opt0/e05_003_opt0_r1 -> e05_004 | O:Galahad binds the shrine to the exiles | E:SET none = C(0) | D:C(1)
ORX e05_003_opt1/e05_003_opt1_r1 -> e05_004 | O:Percival sends the cup toward the villages | E:SET none = C(0) | D:C(1)
ORX e05_003_opt2/e05_003_opt2_r1 -> e05_004 | O:Morgan seals the road with the old ward | E:SET none = C(0) | D:C(1)

ENC e05_004 turn=0..999
ORX e05_004_opt0/e05_004_opt0_r1 -> e05_005 | O:Percival and Galahad seat the exiles in the witness ring | E:SET none = C(0) | D:C(1)
ORX e05_004_opt1/e05_004_opt1_r1 -> e05_005 | O:Percival leads the cup down the village path | E:SET none = C(0) | D:C(1)
ORX e05_004_opt2/e05_004_opt2_r1 -> e05_005 | O:Morgan keeps the ward at half-light | E:SET none = C(0) | D:C(1)

ENC e05_005 turn=0..999
ORX e05_005_opt0/e05_005_opt0_r1 -> e05_006 | O:Seat exiles as covenant-keepers | E:SET none = C(0) | D:C(1)
ORX e05_005_opt1/e05_005_opt1_r1 -> e05_006 | O:Send Percival down the village path | E:SET none = C(0) | D:C(1)
ORX e05_005_opt2/e05_005_opt2_r1 -> e05_006 | O:Open one eye in the old ward | E:SET none = C(0) | D:C(1)

ENC e05_006 turn=0..999
ORX e05_006_opt0/e05_006_opt0_r1 -> e05_007 | O:Name the cup as a covenant | E:SET none = C(0) | D:C(1)
ORX e05_006_opt1/e05_006_opt1_r1 -> e05_007 | O:Send the cup to the first water-villages | E:SET none = C(0) | D:C(1)
ORX e05_006_opt2/e05_006_opt2_r1 -> e05_007 | O:Keep one bounded channel open | E:SET none = C(0) | D:C(1)

ENC e05_007 turn=0..999
ORX e05_007_opt0/e05_007_opt0_r1 -> e05_008 | O:Swear the succession before the villagers | E:SET none = C(0) | D:C(1)
ORX e05_007_opt1/e05_007_opt1_r1 -> e05_008 | O:Open the ward one narrow eye | E:SET none = C(0) | D:C(1)
ORX e05_007_opt2/e05_007_opt2_r1 -> e05_008 | O:Let Percival carry the cup into the farms | E:SET none = C(0) | D:C(1)

ENC e05_008 turn=0..999
ORX e05_008_opt0/e05_008_opt0_r1 -> e05_009 | O:Renew the covenant before the villages | E:SET none = C(0) | D:C(1)
ORX e05_008_opt1/e05_008_opt1_r1 -> e05_009 | O:Hold one guarded ward-road | E:SET none = C(0) | D:C(1)
ORX e05_008_opt2/e05_008_opt2_r1 -> e05_009 | O:Let Percival carry the cup down the valley | E:SET none = C(0) | D:C(1)

ENC e05_009 turn=0..999
ORX e05_009_opt0/e05_009_opt0_r1 -> e05_010 | O:Make the covenant a walkable oath | E:SET none = C(0) | D:C(1)
ORX e05_009_opt1/e05_009_opt1_r1 -> e05_010 | O:Bind the ward to one proven road | E:SET none = C(0) | D:C(1)
ORX e05_009_opt2/e05_009_opt2_r1 -> e05_010 | O:Carry the cup into the farms | E:SET none = C(0) | D:C(1)

ENC e05_010 turn=0..999
ORX e05_010_opt0/e05_010_opt0_r1 -> e05_011 | O:Open the page for the widow's claim | E:SET none = C(0) | D:C(1)
ORX e05_010_opt1/e05_010_opt1_r1 -> e05_011 | O:Run one hearing with law and light together | E:SET none = C(0) | D:C(1)
ORX e05_010_opt2/e05_010_opt2_r1 -> e05_011 | O:Let Morgan ring the cup's bell down the valley | E:SET none = C(0) | D:C(1)

ENC e05_011 turn=0..999
ORX e05_011_opt0/e05_011_opt0_r1 -> e05_012 | O:Write law and want in one public census | E:SET none = C(0) | D:C(1)
ORX e05_011_opt1/e05_011_opt1_r1 -> e05_012 | O:Make the ford a self-judging ward | E:SET none = C(0) | D:C(1)
ORX e05_011_opt2/e05_011_opt2_r1 -> e05_012 | O:Carry the Grail down the farm road | E:SET none = C(0) | D:C(1)

ENC e05_012 turn=0..999
ORX e05_012_opt0/e05_012_opt0_r1 -> e05_013 | O:Keep a road ledger of spoken needs | E:SET none = C(0) | D:C(1)
ORX e05_012_opt1/e05_012_opt1_r1 -> e05_013 | O:Set law and Grail as one rule | E:SET none = C(0) | D:C(1)
ORX e05_012_opt2/e05_012_opt2_r1 -> e05_013 | O:Let Morgan test the road's old lock | E:SET none = C(0) | D:C(1)

ENC e05_013 turn=0..999
ORX e05_013_opt0/e05_013_opt0_r1 -> e05_014 | O:Open a ward court of witnesses | E:SET none = C(0) | D:C(1)
ORX e05_013_opt1/e05_013_opt1_r1 -> e05_014 | O:Ask Galahad to witness the Grail's answer | E:SET none = C(0) | D:C(1)
ORX e05_013_opt2/e05_013_opt2_r1 -> e05_014 | O:Test the old promise with Morgan | E:SET none = C(0) | D:C(1)

ENC e05_014 turn=0..999
ORX e05_014_opt0/e05_014_opt0_r1 -> e05_015 | O:Make the wards seal the covenant | E:SET none = C(0) | D:C(1)
ORX e05_014_opt1/e05_014_opt1_r1 -> e05_015 | O:Send Galahad and Percival to the shrine | E:SET none = C(0) | D:C(1)
ORX e05_014_opt2/e05_014_opt2_r1 -> e05_015 | O:Let Morgan test the road's promise | E:SET none = C(0) | D:C(1)

ENC e05_015 turn=0..999
ORX e05_015_opt0/e05_015_opt0_r1 -> e05_016 | O:Open the annual ward hearing | E:SET none = C(0) | D:C(1)
ORX e05_015_opt1/e05_015_opt1_r1 -> e05_016 | O:Send Galahad and Percival to the shrine | E:SET none = C(0) | D:C(1)
ORX e05_015_opt2/e05_015_opt2_r1 -> e05_016 | O:Test the road's old bargain | E:SET none = C(0) | D:C(1)

ENC e05_016 turn=0..999
ORX e05_016_opt0/e05_016_opt0_r1 -> e05_017 | O:Arthur makes the ward-hearing binding | E:SET none = C(0) | D:C(1)
ORX e05_016_opt1/e05_016_opt1_r1 -> e05_017 | O:Galahad and Percival carry the cup to the shrine | E:SET none = C(0) | D:C(1)
ORX e05_016_opt2/e05_016_opt2_r1 -> e05_017 | O:Morgan and Merlin test the road's locked promise | E:SET none = C(0) | D:C(1)

ENC e05_017 turn=0..999
ORX e05_017_opt0/e05_017_opt0_r1 -> e05_018 | O:Arthur makes the hearing binding | E:SET none = C(0) | D:C(1)
ORX e05_017_opt1/e05_017_opt1_r1 -> e05_018 | O:Galahad and Percival carry the cup down | E:SET none = C(0) | D:C(1)
ORX e05_017_opt2/e05_017_opt2_r1 -> e05_018 | O:Morgan and Merlin expose the latch | E:SET none = C(0) | D:C(1)

ENC e05_018 turn=0..999
ORX e05_018_opt0/e05_018_opt0_r1 -> e05_019 | O:Make the Grail a binding order | E:SET none = C(0) | D:C(1)
ORX e05_018_opt1/e05_018_opt1_r1 -> e05_019 | O:Open the road to the missing | E:SET none = C(0) | D:C(1)
ORX e05_018_opt2/e05_018_opt2_r1 -> e05_019 | O:Return the evidence to court | E:SET none = C(0) | D:C(1)

ENC e05_019 turn=0..999
ORX e05_019_opt0/e05_019_opt0_r1 -> e05_020 | O:Make the Grail a covenant | E:SET none = C(0) | D:C(1)
ORX e05_019_opt1/e05_019_opt1_r1 -> e05_020 | O:Open the road to the missing | E:SET none = C(0) | D:C(1)
ORX e05_019_opt2/e05_019_opt2_r1 -> e05_020 | O:Let the exiles speak first | E:SET none = C(0) | D:C(1)

ENC e05_020 turn=0..999
ORX e05_020_opt0/e05_020_opt0_r1 -> e05_021 | O:Swear the Round Table a covenant | E:SET none = C(0) | D:C(1)
ORX e05_020_opt1/e05_020_opt1_r1 -> e05_021 | O:Open the unmarked road | E:SET none = C(0) | D:C(1)
ORX e05_020_opt2/e05_020_opt2_r1 -> e05_021 | O:Test what the shrine asks | E:SET none = C(0) | D:C(1)

ENC e05_021 turn=0..999
ORX e05_021_opt0/e05_021_opt0_r1 -> e05_022 | O:Make the Grail an oath-ledger | E:SET none = C(0) | D:C(1)
ORX e05_021_opt1/e05_021_opt1_r1 -> e05_022 | O:Carry the broken road outward | E:SET none = C(0) | D:C(1)
ORX e05_021_opt2/e05_021_opt2_r1 -> e05_022 | O:Bargain the ward openly | E:SET none = C(0) | D:C(1)

ENC e05_022 turn=0..999
ORX e05_022_opt0/e05_022_opt0_r1 -> e05_023 | O:Open the witness-assembly | E:SET none = C(0) | D:C(1)
ORX e05_022_opt1/e05_022_opt1_r1 -> e05_023 | O:Take the threshold road | E:SET none = C(0) | D:C(1)
ORX e05_022_opt2/e05_022_opt2_r1 -> e05_023 | O:Audit the ward openly | E:SET none = C(0) | D:C(1)

ENC e05_023 turn=0..999

ENC e06_001 turn=0..999
ORX e06_001_opt0/e06_001_opt0_r1 -> e06_002 | O:Morgan rewrites the oath in private | E:SET none = C(0) | D:C(1)
ORX e06_001_opt1/e06_001_opt1_r1 -> e06_002 | O:Merlin forces the hidden terms into the open | E:SET none = C(0) | D:C(1)
ORX e06_001_opt2/e06_001_opt2_r1 -> e06_002 | O:The Lady of the Lake returns the cup as proof of the deal | E:SET none = C(0) | D:C(1)

ENC e06_002 turn=0..999
ORX e06_002_opt0/e06_002_opt0_r1 -> e06_003 | O:Morgan hardens the second ledger | E:SET none = C(0) | D:C(1)
ORX e06_002_opt1/e06_002_opt1_r1 -> e06_003 | O:Merlin forces the ledger into the open | E:SET none = C(0) | D:C(1)
ORX e06_002_opt2/e06_002_opt2_r1 -> e06_003 | O:The Lady of the Lake ties the cup to succession | E:SET none = C(0) | D:C(1)

ENC e06_003 turn=0..999
ORX e06_003_opt0/e06_003_opt0_r1 -> e06_004 | O:Morgan binds shrine-keepers to the margin | E:SET none = C(0) | D:C(1)
ORX e06_003_opt1/e06_003_opt1_r1 -> e06_004 | O:Merlin refuses to certify the rewrite | E:SET none = C(0) | D:C(1)
ORX e06_003_opt2/e06_003_opt2_r1 -> e06_004 | O:The Lady of the Lake moves the cup past the shrine gate | E:SET none = C(0) | D:C(1)

ENC e06_004 turn=0..999
ORX e06_004_opt0/e06_004_opt0_r1 -> e06_005 | O:Morgan opens the second council | E:SET none = C(0) | D:C(1)
ORX e06_004_opt1/e06_004_opt1_r1 -> e06_005 | O:Morgan offers Merlin a gilded witness seat | E:SET none = C(0) | D:C(1)
ORX e06_004_opt2/e06_004_opt2_r1 -> e06_005 | O:The Lady of the Lake ties the cup to the ledger | E:SET none = C(0) | D:C(1)

ENC e06_005 turn=0..999
ORX e06_005_opt0/e06_005_opt0_r1 -> e06_006 | O:Morgan keeps Merlin visible but sealed | E:SET none = C(0) | D:C(1)
ORX e06_005_opt1/e06_005_opt1_r1 -> e06_006 | O:The exiles move from margin to inner ring | E:SET none = C(0) | D:C(1)
ORX e06_005_opt2/e06_005_opt2_r1 -> e06_006 | O:The Lady of the Lake sets custody on the scale | E:SET none = C(0) | D:C(1)

ENC e06_006 turn=0..999
ORX e06_006_opt0/e06_006_opt0_r1 -> e06_007 | O:Arthur opens the bargain | E:SET none = C(0) | D:C(1)
ORX e06_006_opt1/e06_006_opt1_r1 -> e06_007 | O:Let the exiles speak | E:SET none = C(0) | D:C(1)
ORX e06_006_opt2/e06_006_opt2_r1 -> e06_007 | O:Morgan offers Merlin the sealed seat | E:SET none = C(0) | D:C(1)

ENC e06_007 turn=0..999
ORX e06_007_opt0/e06_007_opt0_r1 -> e06_008 | O:Arthur names the sealed oath | E:SET none = C(0) | D:C(1)
ORX e06_007_opt1/e06_007_opt1_r1 -> e06_008 | O:Percival tests the divided Grail shadow | E:SET none = C(0) | D:C(1)
ORX e06_007_opt2/e06_007_opt2_r1 -> e06_008 | O:Merlin answers from the sealed shrine | E:SET none = C(0) | D:C(1)

ENC e06_008 turn=0..999
ORX e06_008_opt0/e06_008_opt0_r1 -> e06_009 | O:Arthur reads the rewritten oath aloud | E:SET none = C(0) | D:C(1)
ORX e06_008_opt1/e06_008_opt1_r1 -> e06_009 | O:Lancelot chooses which key to defend | E:SET none = C(0) | D:C(1)
ORX e06_008_opt2/e06_008_opt2_r1 -> e06_009 | O:Merlin lifts the seal and speaks | E:SET none = C(0) | D:C(1)

ENC e06_009 turn=0..999
ORX e06_009_opt0/e06_009_opt0_r1 -> e06_010 | O:Arthur bargains for the exiles | E:SET none = C(0) | D:C(1)
ORX e06_009_opt1/e06_009_opt1_r1 -> e06_010 | O:Merlin breaks the seal | E:SET none = C(0) | D:C(1)
ORX e06_009_opt2/e06_009_opt2_r1 -> e06_010 | O:Percival chooses the exiles | E:SET none = C(0) | D:C(1)

ENC e06_010 turn=0..999
ORX e06_010_opt0/e06_010_opt0_r1 -> e06_011 | O:Arthur countersigns the exile charter | E:SET none = C(0) | D:C(1)
ORX e06_010_opt1/e06_010_opt1_r1 -> e06_011 | O:Lady of the Lake lifts the shrine curtain | E:SET none = C(0) | D:C(1)
ORX e06_010_opt2/e06_010_opt2_r1 -> e06_011 | O:Merlin speaks while keeping the seal | E:SET none = C(0) | D:C(1)

ENC e06_011 turn=0..999
ORX e06_011_opt0/e06_011_opt0_r1 -> e06_012 | O:Arthur names the exile road | E:SET none = C(0) | D:C(1)
ORX e06_011_opt1/e06_011_opt1_r1 -> e06_012 | O:Offer Merlin the measured door | E:SET none = C(0) | D:C(1)
ORX e06_011_opt2/e06_011_opt2_r1 -> e06_012 | O:Lady of the Lake forces the relic to answer | E:SET none = C(0) | D:C(1)

ENC e06_012 turn=0..999
ORX e06_012_opt0/e06_012_opt0_r1 -> e06_013 | O:Force the feast to witness the bargain | E:SET none = C(0) | D:C(1)
ORX e06_012_opt1/e06_012_opt1_r1 -> e06_013 | O:Offer Merlin the locked witness | E:SET none = C(0) | D:C(1)
ORX e06_012_opt2/e06_012_opt2_r1 -> e06_013 | O:Let the exiles name their road | E:SET none = C(0) | D:C(1)

ENC e06_013 turn=0..999
ORX e06_013_opt0/e06_013_opt0_r1 -> e06_014 | O:Let the poor read the price aloud | E:SET none = C(0) | D:C(1)
ORX e06_013_opt1/e06_013_opt1_r1 -> e06_014 | O:Let Merlin open the sealed witness | E:SET none = C(0) | D:C(1)
ORX e06_013_opt2/e06_013_opt2_r1 -> e06_014 | O:Let Lancelot keep debt and title apart | E:SET none = C(0) | D:C(1)

ENC e06_014 turn=0..999
ORX e06_014_opt0/e06_014_opt0_r1 -> e06_015 | O:Seal Merlin's witness into the ledger | E:SET none = C(0) | D:C(1)
ORX e06_014_opt1/e06_014_opt1_r1 -> e06_015 | O:Give exiles a visible seat | E:SET none = C(0) | D:C(1)
ORX e06_014_opt2/e06_014_opt2_r1 -> e06_015 | O:Let Lancelot choose one lock | E:SET none = C(0) | D:C(1)

ENC e06_015 turn=0..999
ORX e06_015_opt0/e06_015_opt0_r1 -> e06_016 | O:Let the exiles speak through the seal | E:SET none = C(0) | D:C(1)
ORX e06_015_opt1/e06_015_opt1_r1 -> e06_016 | O:Let Lancelot carry Guinevere's oath | E:SET none = C(0) | D:C(1)
ORX e06_015_opt2/e06_015_opt2_r1 -> e06_016 | O:Let Merlin remain at the fringe | E:SET none = C(0) | D:C(1)

ENC e06_016 turn=0..999
ORX e06_016_opt0/e06_016_opt0_r1 -> e06_017 | O:Make exiles unforgettable | E:SET none = C(0) | D:C(1)
ORX e06_016_opt1/e06_016_opt1_r1 -> e06_017 | O:Let Lancelot sign as Guinevere's proxy | E:SET none = C(0) | D:C(1)
ORX e06_016_opt2/e06_016_opt2_r1 -> e06_017 | O:Close the shadow court | E:SET none = C(0) | D:C(1)

ENC e06_017 turn=0..999
ORX e06_017_opt0/e06_017_opt0_r1 -> e06_018 | O:Make the hidden bargain public | E:SET none = C(0) | D:C(1)
ORX e06_017_opt1/e06_017_opt1_r1 -> e06_018 | O:Let Mordred hold the witness | E:SET none = C(0) | D:C(1)
ORX e06_017_opt2/e06_017_opt2_r1 -> e06_018 | O:Force Merlin to speak | E:SET none = C(0) | D:C(1)

ENC e06_018 turn=0..999
ORX e06_018_opt0/e06_018_opt0_r1 -> e06_019 | O:Write the witness on the living | E:SET none = C(0) | D:C(1)
ORX e06_018_opt1/e06_018_opt1_r1 -> e06_019 | O:Write the witness on the dead | E:SET none = C(0) | D:C(1)
ORX e06_018_opt2/e06_018_opt2_r1 -> e06_019 | O:Leave the witness unnamed | E:SET none = C(0) | D:C(1)

ENC e06_019 turn=0..999
ORX e06_019_opt0/e06_019_opt0_r1 -> e06_020 | O:Open the ledger in public | E:SET none = C(0) | D:C(1)
ORX e06_019_opt1/e06_019_opt1_r1 -> e06_020 | O:Seal it inside Merlin's circle | E:SET none = C(0) | D:C(1)
ORX e06_019_opt2/e06_019_opt2_r1 -> e06_020 | O:Give the witness to the relic | E:SET none = C(0) | D:C(1)

ENC e06_020 turn=0..999
ORX e06_020_opt0/e06_020_opt0_r1 -> e06_021 | O:Let the exiles choose the thresholds | E:SET none = C(0) | D:C(1)
ORX e06_020_opt1/e06_020_opt1_r1 -> e06_021 | O:Bind the oath to the Grail threshold | E:SET none = C(0) | D:C(1)
ORX e06_020_opt2/e06_020_opt2_r1 -> e06_021 | O:Seal the constitution inside Merlin's circle | E:SET none = C(0) | D:C(1)

ENC e06_021 turn=0..999
ORX e06_021_opt0/e06_021_opt0_r1 -> e06_022 | O:Burn Merlin's margins | E:SET none = C(0) | D:C(1)
ORX e06_021_opt1/e06_021_opt1_r1 -> e06_022 | O:Let the relic witness the rewrite | E:SET none = C(0) | D:C(1)
ORX e06_021_opt2/e06_021_opt2_r1 -> e06_022 | O:Countersign as an exile | E:SET none = C(0) | D:C(1)

ENC e06_022 turn=0..999

ENC e07_001 turn=0..999
ORX e07_001_opt0/e07_001_opt0_r1 -> e07_002 | O:Percival swears the exiles to a ridge charter | E:SET none = C(0) | D:C(1)
ORX e07_001_opt1/e07_001_opt1_r1 -> e07_002 | O:Bedivere and the Lady of the Lake carry the shrine shards with the exiles | E:SET none = C(0) | D:C(1)
ORX e07_001_opt2/e07_001_opt2_r1 -> e07_002 | O:Guinevere and the Lady of the Lake guard the road and shelter the exiles | E:SET none = C(0) | D:C(1)

ENC e07_002 turn=0..999
ORX e07_002_opt0/e07_002_opt0_r1 -> e07_003 | O:Percival swears open roofs and common labor | E:SET none = C(0) | D:C(1)
ORX e07_002_opt1/e07_002_opt1_r1 -> e07_003 | O:Bedivere and the Lady of the Lake mark the shards as a road | E:SET none = C(0) | D:C(1)
ORX e07_002_opt2/e07_002_opt2_r1 -> e07_003 | O:Arthur declines the crown and takes a pilgrim steward's place | E:SET none = C(0) | D:C(1)

ENC e07_003 turn=0..999
ORX e07_003_opt0/e07_003_opt0_r1 -> e07_004 | O:Percival opens the common table to the oathless | E:SET none = C(0) | D:C(1)
ORX e07_003_opt1/e07_003_opt1_r1 -> e07_004 | O:Bedivere and the Lady of the Lake leave the shards as a public road | E:SET none = C(0) | D:C(1)
ORX e07_003_opt2/e07_003_opt2_r1 -> e07_004 | O:Arthur names keepers, not a successor | E:SET none = C(0) | D:C(1)

ENC e07_004 turn=0..999
ORX e07_004_opt0/e07_004_opt0_r1 -> e07_005 | O:Percival records promises in the common ledger | E:SET none = C(0) | D:C(1)
ORX e07_004_opt1/e07_004_opt1_r1 -> e07_005 | O:Bedivere lights the shard-road for pilgrims and exiles | E:SET none = C(0) | D:C(1)
ORX e07_004_opt2/e07_004_opt2_r1 -> e07_005 | O:Mordred demands a covenant for his own dead and living | E:SET none = C(0) | D:C(1)

ENC e07_005 turn=0..999
ORX e07_005_opt0/e07_005_opt0_r1 -> e07_006 | O:Percival keeps the debts visible | E:SET none = C(0) | D:C(1)
ORX e07_005_opt1/e07_005_opt1_r1 -> e07_006 | O:Bedivere and the Lady of the Lake light the road | E:SET none = C(0) | D:C(1)
ORX e07_005_opt2/e07_005_opt2_r1 -> e07_006 | O:Mordred asks for a covenant for his dead | E:SET none = C(0) | D:C(1)

ENC e07_006 turn=0..999
ORX e07_006_opt0/e07_006_opt0_r1 -> e07_007 | O:Percival gives shelter in exchange for one task | E:SET none = C(0) | D:C(1)
ORX e07_006_opt1/e07_006_opt1_r1 -> e07_007 | O:Bedivere and the Lady of the Lake keep the shard-road lit | E:SET none = C(0) | D:C(1)
ORX e07_006_opt2/e07_006_opt2_r1 -> e07_007 | O:Mordred asks the ridge to carry his dead forward | E:SET none = C(0) | D:C(1)

ENC e07_007 turn=0..999
ORX e07_007_opt0/e07_007_opt0_r1 -> e07_008 | O:Bedivere restores the toll-road as shared work | E:SET none = C(0) | D:C(1)
ORX e07_007_opt1/e07_007_opt1_r1 -> e07_008 | O:Guinevere and Percival keep the gifts public | E:SET none = C(0) | D:C(1)
ORX e07_007_opt2/e07_007_opt2_r1 -> e07_008 | O:Merlin and the Lady of the Lake seal a witness covenant | E:SET none = C(0) | D:C(1)

ENC e07_008 turn=0..999
ORX e07_008_opt0/e07_008_opt0_r1 -> e07_009 | O:Percival and Guinevere make the ridge an open commons | E:SET none = C(0) | D:C(1)
ORX e07_008_opt1/e07_008_opt1_r1 -> e07_009 | O:Bedivere and the Lady of the Lake make the road a witnessed threshold | E:SET none = C(0) | D:C(1)
ORX e07_008_opt2/e07_008_opt2_r1 -> e07_009 | O:Arthur and Mordred settle what returning means | E:SET none = C(0) | D:C(1)

ENC e07_009 turn=0..999
ORX e07_009_opt0/e07_009_opt0_r1 -> e07_010 | O:Percival and Morgan open the relics to all hands | E:SET none = C(0) | D:C(1)
ORX e07_009_opt1/e07_009_opt1_r1 -> e07_010 | O:Bedivere and Gawain open the road to exiles | E:SET none = C(0) | D:C(1)
ORX e07_009_opt2/e07_009_opt2_r1 -> e07_010 | O:Arthur and Mordred divide the return | E:SET none = C(0) | D:C(1)

ENC e07_010 turn=0..999
ORX e07_010_opt0/e07_010_opt0_r1 -> e07_011 | O:Bedivere opens the ledger to every household | E:SET none = C(0) | D:C(1)
ORX e07_010_opt1/e07_010_opt1_r1 -> e07_011 | O:Percival and Gawain send young finders down the shard-road | E:SET none = C(0) | D:C(1)
ORX e07_010_opt2/e07_010_opt2_r1 -> e07_011 | O:Merlin and Morgan settle the old magic into sleep or stewardship | E:SET none = C(0) | D:C(1)

ENC e07_011 turn=0..999
ORX e07_011_opt0/e07_011_opt0_r1 -> e07_012 | O:Gawain and Bedivere open the ridge road as a common gate | E:SET none = C(0) | D:C(1)
ORX e07_011_opt1/e07_011_opt1_r1 -> e07_012 | O:Percival and Guinevere make the ledger a public witness | E:SET none = C(0) | D:C(1)
ORX e07_011_opt2/e07_011_opt2_r1 -> e07_012 | O:Merlin, Morgan, and the Lady of the Lake place the old magic under rotating stewardship | E:SET none = C(0) | D:C(1)

ENC e07_012 turn=0..999
ORX e07_012_opt0/e07_012_opt0_r1 -> e07_013 | O:Percival and Guinevere grant witness-lamps to the unwritten | E:SET none = C(0) | D:C(1)
ORX e07_012_opt1/e07_012_opt1_r1 -> e07_013 | O:Gawain and Bedivere send two finders back onto the shard-road | E:SET none = C(0) | D:C(1)
ORX e07_012_opt2/e07_012_opt2_r1 -> e07_013 | O:Merlin, Morgan, and the Lady of the Lake make stewardship public and annual | E:SET none = C(0) | D:C(1)

ENC e07_013 turn=0..999
ORX e07_013_opt0/e07_013_opt0_r1 -> e07_014 | O:Percival and Guinevere read the returned finders into the covenant as witnesses | E:SET none = C(0) | D:C(1)
ORX e07_013_opt1/e07_013_opt1_r1 -> e07_014 | O:Gawain and Bedivere keep the ridge open while Lancelot repairs the first homes | E:SET none = C(0) | D:C(1)
ORX e07_013_opt2/e07_013_opt2_r1 -> e07_014 | O:Merlin, Morgan, and the Lady of the Lake put the speaking stone under rotating public trust | E:SET none = C(0) | D:C(1)

ENC e07_014 turn=0..999
ORX e07_014_opt0/e07_014_opt0_r1 -> e07_015 | O:Percival and Bedivere raise the refuge-hall before anything else | E:SET none = C(0) | D:C(1)
ORX e07_014_opt1/e07_014_opt1_r1 -> e07_015 | O:Gawain, Lancelot, and Arthur make the road an oath-duty | E:SET none = C(0) | D:C(1)
ORX e07_014_opt2/e07_014_opt2_r1 -> e07_015 | O:Merlin, Morgan, Guinevere, and the Lady of the Lake divide the shrine-stone into rotating offices | E:SET none = C(0) | D:C(1)

ENC e07_015 turn=0..999
ORX e07_015_opt0/e07_015_opt0_r1 -> e07_016 | O:Percival and Guinevere put unwritten households before a public lamp | E:SET none = C(0) | D:C(1)
ORX e07_015_opt1/e07_015_opt1_r1 -> e07_016 | O:Gawain and Lancelot muster the ridge under a visible road-oath | E:SET none = C(0) | D:C(1)
ORX e07_015_opt2/e07_015_opt2_r1 -> e07_016 | O:Merlin, Morgan, and the Lady of the Lake set the stone under three rotating offices | E:SET none = C(0) | D:C(1)

ENC e07_016 turn=0..999
ORX e07_016_opt0/e07_016_opt0_r1 -> e07_017 | O:Percival and Guinevere open the hall to households willing to be counted | E:SET none = C(0) | D:C(1)
ORX e07_016_opt1/e07_016_opt1_r1 -> e07_017 | O:Gawain and Lancelot send oath-helpers to clear the ridge and bridge | E:SET none = C(0) | D:C(1)
ORX e07_016_opt2/e07_016_opt2_r1 -> e07_017 | O:Merlin, Morgan, and the Lady of the Lake demand a public audit of the stone-seats | E:SET none = C(0) | D:C(1)

ENC e07_017 turn=0..999
ORX e07_017_opt0/e07_017_opt0_r1 -> e07_018 | O:Percival and Guinevere make countable households a covenant of the hall | E:SET none = C(0) | D:C(1)
ORX e07_017_opt1/e07_017_opt1_r1 -> e07_018 | O:Gawain and Lancelot send Arthur and guards to find the missing courier and bridge truth | E:SET none = C(0) | D:C(1)
ORX e07_017_opt2/e07_017_opt2_r1 -> e07_018 | O:Merlin, Morgan, and the Lady of the Lake force the shrine-stone into protect, remember, or refuse | E:SET none = C(0) | D:C(1)

ENC e07_018 turn=0..999
ORX e07_018_opt0/e07_018_opt0_r1 -> e07_019 | O:Percival, Bedivere, and Guinevere publish an open covenant | E:SET none = C(0) | D:C(1)
ORX e07_018_opt1/e07_018_opt1_r1 -> e07_019 | O:Gawain, Lancelot, and Arthur lead oath-helpers to the ridge and bridge | E:SET none = C(0) | D:C(1)
ORX e07_018_opt2/e07_018_opt2_r1 -> e07_019 | O:Merlin, Morgan, and the Lady of the Lake force the stone into a witnessed office | E:SET none = C(0) | D:C(1)

ENC e07_019 turn=0..999
ORX e07_019_opt0/e07_019_opt0_r1 -> e07_020 | O:Arthur, Gawain, Lancelot, and chosen keepers test the ridge for the missing courier | E:SET none = C(0) | D:C(1)
ORX e07_019_opt1/e07_019_opt1_r1 -> e07_020 | O:Merlin, Morgan, and the Lady of the Lake force the shrine-stone into protect, remember, or refuse | E:SET none = C(0) | D:C(1)
ORX e07_019_opt2/e07_019_opt2_r1 -> e07_020 | O:Percival and Guinevere rewrite the covenant around named households and named refusals | E:SET none = C(0) | D:C(1)

ENC e07_020 turn=0..999
ORX e07_020_opt0/e07_020_opt0_r1 -> e07_021 | O:Percival, Bedivere, and Guinevere open the covenant as a public door | E:SET none = C(0) | D:C(1)
ORX e07_020_opt1/e07_020_opt1_r1 -> e07_021 | O:Arthur, Gawain, Lancelot, and chosen keepers carry testimony to the ridge | E:SET none = C(0) | D:C(1)
ORX e07_020_opt2/e07_020_opt2_r1 -> e07_021 | O:Merlin, Morgan, and the Lady of the Lake force the shrine-stone into witnessed office | E:SET none = C(0) | D:C(1)

ENC e07_021 turn=0..999
ORX e07_021_opt0/e07_021_opt0_r1 -> e07_022 | O:Percival, Bedivere, and Guinevere turn the blank roll into a craft compact | E:SET none = C(0) | D:C(1)
ORX e07_021_opt1/e07_021_opt1_r1 -> e07_022 | O:Arthur, Gawain, Lancelot, and chosen keepers carry testimony to the ridge | E:SET none = C(0) | D:C(1)
ORX e07_021_opt2/e07_021_opt2_r1 -> e07_022 | O:Merlin, Morgan, and the Lady of the Lake make the shrine-stone an open public ledger | E:SET none = C(0) | D:C(1)

ENC e07_022 turn=0..999
ORX e07_022_opt0/e07_022_opt0_r1 -> e07_023 | O:Percival and Bedivere make the blank name crossable before witnesses | E:SET none = C(0) | D:C(1)
ORX e07_022_opt1/e07_022_opt1_r1 -> e07_023 | O:Arthur, Gawain, Lancelot, and chosen keepers carry testimony to the ridge | E:SET none = C(0) | D:C(1)
ORX e07_022_opt2/e07_022_opt2_r1 -> e07_023 | O:Merlin, Morgan, and the Lady of the Lake bind the stone as a witnessed office | E:SET none = C(0) | D:C(1)

ENC e07_023 turn=0..999

ENC e08_001 turn=0..999
ORX e08_001_opt0/e08_001_opt0_r1 -> e08_002 | O:Arthur speaks the witnessing rite at the empty seat | E:SET none = C(0) | D:C(1)
ORX e08_001_opt1/e08_001_opt1_r1 -> e08_002 | O:Guinevere calls the commoners to one table | E:SET none = C(0) | D:C(1)
ORX e08_001_opt2/e08_001_opt2_r1 -> e08_002 | O:Lancelot and Gawain share the final oath at the table's edge | E:SET none = C(0) | D:C(1)

ENC e08_002 turn=0..999
ORX e08_002_opt0/e08_002_opt0_r1 -> e08_003 | O:The court recites the failed names until the list is complete | E:SET none = C(0) | D:C(1)
ORX e08_002_opt1/e08_002_opt1_r1 -> e08_003 | O:Guinevere brings the exiles and servants in to the table | E:SET none = C(0) | D:C(1)
ORX e08_002_opt2/e08_002_opt2_r1 -> e08_003 | O:Arthur answers Mordred's question at the table's edge | E:SET none = C(0) | D:C(1)

ENC e08_003 turn=0..999
ORX e08_003_opt0/e08_003_opt0_r1 -> e08_004 | O:Arthur seals the fellowship in a vow at the empty seat | E:SET none = C(0) | D:C(1)
ORX e08_003_opt1/e08_003_opt1_r1 -> e08_004 | O:Guinevere invites the exiles to sit with the court | E:SET none = C(0) | D:C(1)
ORX e08_003_opt2/e08_003_opt2_r1 -> e08_004 | O:Merlin and Morgan keep the seat empty as a relic of refusal | E:SET none = C(0) | D:C(1)

ENC e08_004 turn=0..999
ORX e08_004_opt0/e08_004_opt0_r1 -> e08_005 | O:Arthur names what the table will be beyond the crown | E:SET none = C(0) | D:C(1)
ORX e08_004_opt1/e08_004_opt1_r1 -> e08_005 | O:Guinevere sends the Cup outward with the exiles | E:SET none = C(0) | D:C(1)
ORX e08_004_opt2/e08_004_opt2_r1 -> e08_005 | O:Merlin and Morgan hold the empty seat in silence | E:SET none = C(0) | D:C(1)

ENC e08_005 turn=0..999
ORX e08_005_opt0/e08_005_opt0_r1 -> e08_006 | O:Arthur writes the fellowship covenant on the gate-stone | E:SET none = C(0) | D:C(1)
ORX e08_005_opt1/e08_005_opt1_r1 -> e08_006 | O:Guinevere sends the Cup outward with the exiles | E:SET none = C(0) | D:C(1)
ORX e08_005_opt2/e08_005_opt2_r1 -> e08_006 | O:Gawain asks Mordred to stand and answer before the named | E:SET none = C(0) | D:C(1)

ENC e08_006 turn=0..999
ORX e08_006_opt0/e08_006_opt0_r1 -> e08_007 | O:Arthur binds the covenant aloud and lets Mordred speak under it | E:SET none = C(0) | D:C(1)
ORX e08_006_opt1/e08_006_opt1_r1 -> e08_007 | O:Guinevere sends the Cup out with the first of the named | E:SET none = C(0) | D:C(1)
ORX e08_006_opt2/e08_006_opt2_r1 -> e08_007 | O:Merlin and Morgan test the thread that binds the table | E:SET none = C(0) | D:C(1)

ENC e08_007 turn=0..999
ORX e08_007_opt0/e08_007_opt0_r1 -> e08_008 | O:Guinevere sends the Cup with the first exiles | E:SET none = C(0) | D:C(1)
ORX e08_007_opt1/e08_007_opt1_r1 -> e08_008 | O:Arthur opens a hearing for Mordred before the named | E:SET none = C(0) | D:C(1)
ORX e08_007_opt2/e08_007_opt2_r1 -> e08_008 | O:Merlin and Morgan bind the oath to memory rather than magic | E:SET none = C(0) | D:C(1)

ENC e08_008 turn=0..999
ORX e08_008_opt0/e08_008_opt0_r1 -> e08_009 | O:Guinevere lifts the Cup and the fellowship steps through the gates | E:SET none = C(0) | D:C(1)
ORX e08_008_opt1/e08_008_opt1_r1 -> e08_009 | O:Arthur gathers the named at the empty seats and speaks the covenant as elegy | E:SET none = C(0) | D:C(1)
ORX e08_008_opt2/e08_008_opt2_r1 -> e08_009 | O:Merlin and Morgan set the thread aside and bind the oath to names and shared bread | E:SET none = C(0) | D:C(1)

ENC e08_009 turn=0..999
ORX e08_009_opt0/e08_009_opt0_r1 -> e08_010 | O:Arthur speaks the covenant as memorial, not kingship | E:SET none = C(0) | D:C(1)
ORX e08_009_opt1/e08_009_opt1_r1 -> e08_010 | O:Guinevere and Lancelot carry the thread-lamp to the gates | E:SET none = C(0) | D:C(1)
ORX e08_009_opt2/e08_009_opt2_r1 -> e08_010 | O:Mordred is offered the place of bearer rather than king | E:SET none = C(0) | D:C(1)

ENC e08_010 turn=0..999
ORX e08_010_opt0/e08_010_opt0_r1 -> e08_011 | O:Lancelot and Guinevere carry the thread-lamp through the gates to the exiles | E:SET none = C(0) | D:C(1)
ORX e08_010_opt1/e08_010_opt1_r1 -> e08_011 | O:Arthur speaks the covenant as commemoration among the empty seats | E:SET none = C(0) | D:C(1)
ORX e08_010_opt2/e08_010_opt2_r1 -> e08_011 | O:Arthur asks Mordred whether he will bear the claim and the road | E:SET none = C(0) | D:C(1)

ENC e08_011 turn=0..999
ORX e08_011_opt0/e08_011_opt0_r1 -> e08_012 | O:Guinevere and Lancelot take the thread-lamp through the gates to name the exiles | E:SET none = C(0) | D:C(1)
ORX e08_011_opt1/e08_011_opt1_r1 -> e08_012 | O:Arthur asks Mordred to bind the wrapped claim to the road | E:SET none = C(0) | D:C(1)
ORX e08_011_opt2/e08_011_opt2_r1 -> e08_012 | O:Arthur leaves the Cup unlit and lets the court swear its vows by ordinary word | E:SET none = C(0) | D:C(1)

ENC e08_012 turn=0..999
ORX e08_012_opt0/e08_012_opt0_r1 -> e08_013 | O:Guinevere and Percival carry the lamp and the word to the exiles | E:SET none = C(0) | D:C(1)
ORX e08_012_opt1/e08_012_opt1_r1 -> e08_013 | O:Arthur asks Mordred to bind the claim to the road in person | E:SET none = C(0) | D:C(1)
ORX e08_012_opt2/e08_012_opt2_r1 -> e08_013 | O:Arthur speaks the covenant over the empty seats and leaves the Cup unlit | E:SET none = C(0) | D:C(1)

ENC e08_013 turn=0..999
ORX e08_013_opt0/e08_013_opt0_r1 -> e08_014 | O:Guinevere and Percival carry the word and the thread-lamp through the gate | E:SET none = C(0) | D:C(1)
ORX e08_013_opt1/e08_013_opt1_r1 -> e08_014 | O:Arthur asks Mordred to carry the bound claim as a named bearer | E:SET none = C(0) | D:C(1)
ORX e08_013_opt2/e08_013_opt2_r1 -> e08_014 | O:Arthur leaves the Cup unlit and witnesses swear by ordinary word | E:SET none = C(0) | D:C(1)

ENC e08_014 turn=0..999
ORX e08_014_opt0/e08_014_opt0_r1 -> e08_015 | O:Guinevere and Percival carry the lamp-thread beyond the gate | E:SET none = C(0) | D:C(1)
ORX e08_014_opt1/e08_014_opt1_r1 -> e08_015 | O:Arthur makes Mordred a named bearer of the claim | E:SET none = C(0) | D:C(1)
ORX e08_014_opt2/e08_014_opt2_r1 -> e08_015 | O:Arthur swears the covenant over the unlit Cup | E:SET none = C(0) | D:C(1)

ENC e08_015 turn=0..999
ORX e08_015_opt0/e08_015_opt0_r1 -> e08_016 | O:Carry the word beyond the threshold | E:SET none = C(0) | D:C(1)
ORX e08_015_opt1/e08_015_opt1_r1 -> e08_016 | O:Arthur swears the covenant over the unlit Cup | E:SET none = C(0) | D:C(1)
ORX e08_015_opt2/e08_015_opt2_r1 -> e08_016 | O:Ask Mordred to carry the claim as named bearer | E:SET none = C(0) | D:C(1)

ENC e08_016 turn=0..999
ORX e08_016_opt0/e08_016_opt0_r1 -> e08_017 | O:Walk the names and lamp to the exiles beyond the gate | E:SET none = C(0) | D:C(1)
ORX e08_016_opt1/e08_016_opt1_r1 -> e08_017 | O:Arthur swears the covenant over the unlit Cup | E:SET none = C(0) | D:C(1)
ORX e08_016_opt2/e08_016_opt2_r1 -> e08_017 | O:Ask Mordred to carry the claim into the ruin | E:SET none = C(0) | D:C(1)

ENC e08_017 turn=0..999
ORX e08_017_opt0/e08_017_opt0_r1 -> e08_018 | O:Send the names and lamp out with Percival and Bedivere | E:SET none = C(0) | D:C(1)
ORX e08_017_opt1/e08_017_opt1_r1 -> e08_018 | O:Arthur speaks the covenant over the unlit Cup | E:SET none = C(0) | D:C(1)
ORX e08_017_opt2/e08_017_opt2_r1 -> e08_018 | O:Ask Mordred to carry the claim into the ruin | E:SET none = C(0) | D:C(1)

ENC e08_018 turn=0..999
ORX e08_018_opt0/e08_018_opt0_r1 -> e08_019 | O:Send Percival and Bedivere with the names and lamp | E:SET none = C(0) | D:C(1)
ORX e08_018_opt1/e08_018_opt1_r1 -> e08_019 | O:Arthur relights the Cup once and speaks the fellowship oath | E:SET none = C(0) | D:C(1)
ORX e08_018_opt2/e08_018_opt2_r1 -> e08_019 | O:Ask Mordred to carry the claim into the ruin | E:SET none = C(0) | D:C(1)

ENC e08_019 turn=0..999
ORX e08_019_opt0/e08_019_opt0_r1 -> e08_020 | O:Send Percival, Bedivere, and Lancelot out with the lamp | E:SET none = C(0) | D:C(1)
ORX e08_019_opt1/e08_019_opt1_r1 -> e08_020 | O:Keep the broken table as a public vigil | E:SET none = C(0) | D:C(1)
ORX e08_019_opt2/e08_019_opt2_r1 -> e08_020 | O:Ask Mordred to carry the claim into the ruin | E:SET none = C(0) | D:C(1)

ENC e08_020 turn=0..999
ORX e08_020_opt0/e08_020_opt0_r1 -> e08_021 | O:Arthur and companions go out to meet the light | E:SET none = C(0) | D:C(1)
ORX e08_020_opt1/e08_020_opt1_r1 -> e08_021 | O:Keep the broken table and give it a new office | E:SET none = C(0) | D:C(1)
ORX e08_020_opt2/e08_020_opt2_r1 -> e08_021 | O:Ask Mordred to carry the claim outward | E:SET none = C(0) | D:C(1)

ENC e08_021 turn=0..999
ORX e08_021_opt0/e08_021_opt0_r1 -> e08_022 | O:Send Arthur, Lancelot, and Percival with the lamp to the boundary | E:SET none = C(0) | D:C(1)
ORX e08_021_opt1/e08_021_opt1_r1 -> e08_022 | O:Keep the broken table and define it as a standing covenant | E:SET none = C(0) | D:C(1)
ORX e08_021_opt2/e08_021_opt2_r1 -> e08_022 | O:Ask Mordred to carry the claim outward with one witness | E:SET none = C(0) | D:C(1)

ENC e08_022 turn=0..999

ENC e09_001 turn=0..999
ORX e09_001_opt0/e09_001_opt0_r1 -> e09_002 | O:Kay opens the covenant market at the shrine threshold | E:SET none = C(0) | D:C(1)
ORX e09_001_opt1/e09_001_opt1_r1 -> e09_002 | O:Bedivere pledges named hostages between the factions | E:SET none = C(0) | D:C(1)
ORX e09_001_opt2/e09_001_opt2_r1 -> e09_002 | O:Arthur leaves the road open beside the charter | E:SET none = C(0) | D:C(1)

ENC e09_002 turn=0..999
ORX e09_002_opt0/e09_002_opt0_r1 -> e09_003 | O:Kay binds the parishes to grain and labor | E:SET none = C(0) | D:C(1)
ORX e09_002_opt1/e09_002_opt1_r1 -> e09_003 | O:Bedivere makes hostage-claims public and revocable | E:SET none = C(0) | D:C(1)
ORX e09_002_opt2/e09_002_opt2_r1 -> e09_003 | O:Arthur opens the Grail lane as a toll-road | E:SET none = C(0) | D:C(1)

ENC e09_003 turn=0..999
ORX e09_003_opt0/e09_003_opt0_r1 -> e09_004 | O:Kay ratifies the toll lane | E:SET none = C(0) | D:C(1)
ORX e09_003_opt1/e09_003_opt1_r1 -> e09_004 | O:Guinevere seats the exiles before the oath-clerk | E:SET none = C(0) | D:C(1)
ORX e09_003_opt2/e09_003_opt2_r1 -> e09_004 | O:Lancelot writes the not yet page into the charter | E:SET none = C(0) | D:C(1)

ENC e09_004 turn=0..999
ORX e09_004_opt0/e09_004_opt0_r1 -> e09_005 | O:Kay stakes the republic on frost-proof grain credit | E:SET none = C(0) | D:C(1)
ORX e09_004_opt1/e09_004_opt1_r1 -> e09_005 | O:Bedivere turns hostage-claims into revocable friendship | E:SET none = C(0) | D:C(1)
ORX e09_004_opt2/e09_004_opt2_r1 -> e09_005 | O:Lancelot speaks the not yet page before the court | E:SET none = C(0) | D:C(1)

ENC e09_005 turn=0..999
ORX e09_005_opt0/e09_005_opt0_r1 -> e09_006 | O:Kay seals the road-market | E:SET none = C(0) | D:C(1)
ORX e09_005_opt1/e09_005_opt1_r1 -> e09_006 | O:Guinevere seats exiles as witnesses | E:SET none = C(0) | D:C(1)
ORX e09_005_opt2/e09_005_opt2_r1 -> e09_006 | O:Arthur and Mordred make succession an office | E:SET none = C(0) | D:C(1)

ENC e09_006 turn=0..999
ORX e09_006_opt0/e09_006_opt0_r1 -> e09_007 | O:Arthur accepts the office of Keeper rather than the crown | E:SET none = C(0) | D:C(1)
ORX e09_006_opt1/e09_006_opt1_r1 -> e09_007 | O:Gawain writes the watchmen's refusal into the charter | E:SET none = C(0) | D:C(1)
ORX e09_006_opt2/e09_006_opt2_r1 -> e09_007 | O:Guinevere lets the widow test the charter before the court | E:SET none = C(0) | D:C(1)

ENC e09_007 turn=0..999
ORX e09_007_opt0/e09_007_opt0_r1 -> e09_008 | O:Bedivere seals hostage-friendship pledges | E:SET none = C(0) | D:C(1)
ORX e09_007_opt1/e09_007_opt1_r1 -> e09_008 | O:Arthur turns succession into a rotating office | E:SET none = C(0) | D:C(1)
ORX e09_007_opt2/e09_007_opt2_r1 -> e09_008 | O:Lancelot gives the caravan a market token | E:SET none = C(0) | D:C(1)

ENC e09_008 turn=0..999
ORX e09_008_opt0/e09_008_opt0_r1 -> e09_009 | O:Bedivere replaces the hostage with named bell-watch surety | E:SET none = C(0) | D:C(1)
ORX e09_008_opt1/e09_008_opt1_r1 -> e09_009 | O:Kay convenes toll-clerks and widow auditors to rule on closure | E:SET none = C(0) | D:C(1)
ORX e09_008_opt2/e09_008_opt2_r1 -> e09_009 | O:Lancelot limits the market token to the road, not the Grail lane | E:SET none = C(0) | D:C(1)

ENC e09_009 turn=0..999
ORX e09_009_opt0/e09_009_opt0_r1 -> e09_010 | O:Kay asks the widow-toll-clerks to accept the gate | E:SET none = C(0) | D:C(1)
ORX e09_009_opt1/e09_009_opt1_r1 -> e09_010 | O:Lancelot keeps the Grail lane sealed but sends grain past it | E:SET none = C(0) | D:C(1)
ORX e09_009_opt2/e09_009_opt2_r1 -> e09_010 | O:Arthur writes a refusal right into the Round Table | E:SET none = C(0) | D:C(1)

ENC e09_010 turn=0..999
ORX e09_010_opt0/e09_010_opt0_r1 -> e09_011 | O:Kay turns refusal into a public road writ | E:SET none = C(0) | D:C(1)
ORX e09_010_opt1/e09_010_opt1_r1 -> e09_011 | O:Bedivere stakes silver and salt before the road moves | E:SET none = C(0) | D:C(1)
ORX e09_010_opt2/e09_010_opt2_r1 -> e09_011 | O:Lancelot lets Merlin open a witness window on the sealed lane | E:SET none = C(0) | D:C(1)

ENC e09_011 turn=0..999
ORX e09_011_opt0/e09_011_opt0_r1 -> e09_012 | O:Kay signs Mordred as Keeper under grain-and-road bond | E:SET none = C(0) | D:C(1)
ORX e09_011_opt1/e09_011_opt1_r1 -> e09_012 | O:Guinevere puts the widow toll-clerks in charge of the seal | E:SET none = C(0) | D:C(1)
ORX e09_011_opt2/e09_011_opt2_r1 -> e09_012 | O:Lancelot lets Merlin open one witnessed window on the Grail lane | E:SET none = C(0) | D:C(1)

ENC e09_012 turn=0..999
ORX e09_012_opt0/e09_012_opt0_r1 -> e09_013 | O:Kay signs the surety charter | E:SET none = C(0) | D:C(1)
ORX e09_012_opt1/e09_012_opt1_r1 -> e09_013 | O:Bedivere pairs widow toll-clerks with Mordred's grain crews | E:SET none = C(0) | D:C(1)
ORX e09_012_opt2/e09_012_opt2_r1 -> e09_013 | O:Lancelot asks Merlin to witness the debt without opening the lane | E:SET none = C(0) | D:C(1)

ENC e09_013 turn=0..999
ORX e09_013_opt0/e09_013_opt0_r1 -> e09_014 | O:Bedivere opens the granary count to every eye | E:SET none = C(0) | D:C(1)
ORX e09_013_opt1/e09_013_opt1_r1 -> e09_014 | O:Kay writes exile-work contracts for Mordred's crews | E:SET none = C(0) | D:C(1)
ORX e09_013_opt2/e09_013_opt2_r1 -> e09_014 | O:Lancelot asks Merlin to witness the market debt without opening the lane | E:SET none = C(0) | D:C(1)

ENC e09_014 turn=0..999
ORX e09_014_opt0/e09_014_opt0_r1 -> e09_015 | O:Kay binds the succession to household oaths | E:SET none = C(0) | D:C(1)
ORX e09_014_opt1/e09_014_opt1_r1 -> e09_015 | O:Gawain leads the recount under open lanterns | E:SET none = C(0) | D:C(1)
ORX e09_014_opt2/e09_014_opt2_r1 -> e09_015 | O:Lancelot asks Merlin to witness the debt in silence | E:SET none = C(0) | D:C(1)

ENC e09_015 turn=0..999
ORX e09_015_opt0/e09_015_opt0_r1 -> e09_016 | O:Kay swears widows and exiles onto a public surety roll | E:SET none = C(0) | D:C(1)
ORX e09_015_opt1/e09_015_opt1_r1 -> e09_016 | O:Arthur and Merlin name the succession through witnesses | E:SET none = C(0) | D:C(1)
ORX e09_015_opt2/e09_015_opt2_r1 -> e09_016 | O:Bedivere and Gawain trade the short row for winter caravan shares | E:SET none = C(0) | D:C(1)

ENC e09_016 turn=0..999
ORX e09_016_opt0/e09_016_opt0_r1 -> e09_017 | O:Kay converts the short row into a grain-and-salt credit charter | E:SET none = C(0) | D:C(1)
ORX e09_016_opt1/e09_016_opt1_r1 -> e09_017 | O:Gawain trades the row for hostage-bonds with the Lake lords | E:SET none = C(0) | D:C(1)
ORX e09_016_opt2/e09_016_opt2_r1 -> e09_017 | O:Merlin seals succession inside the banked Grail light | E:SET none = C(0) | D:C(1)

ENC e09_017 turn=0..999
ORX e09_017_opt0/e09_017_opt0_r1 -> e09_018 | O:Kay binds succession to the caravan ledger | E:SET none = C(0) | D:C(1)
ORX e09_017_opt1/e09_017_opt1_r1 -> e09_018 | O:Arthur and Gawain swear the succession across hostage and shrine | E:SET none = C(0) | D:C(1)
ORX e09_017_opt2/e09_017_opt2_r1 -> e09_018 | O:Merlin banks the Grail lane as a neutral succession seal | E:SET none = C(0) | D:C(1)

ENC e09_018 turn=0..999
ORX e09_018_opt0/e09_018_opt0_r1 -> e09_019 | O:Kay and Bedivere make succession an open caravan audit | E:SET none = C(0) | D:C(1)
ORX e09_018_opt1/e09_018_opt1_r1 -> e09_019 | O:Gawain exchanges succession promise for Lake hostage friendship | E:SET none = C(0) | D:C(1)
ORX e09_018_opt2/e09_018_opt2_r1 -> e09_019 | O:Merlin seals succession inside the Grail witness | E:SET none = C(0) | D:C(1)

ENC e09_019 turn=0..999
ORX e09_019_opt0/e09_019_opt0_r1 -> e09_020 | O:Kay fixes succession as a widow-and-exile charter | E:SET none = C(0) | D:C(1)
ORX e09_019_opt1/e09_019_opt1_r1 -> e09_020 | O:Gawain makes Lake hostages part of the succession | E:SET none = C(0) | D:C(1)
ORX e09_019_opt2/e09_019_opt2_r1 -> e09_020 | O:Merlin lets the Grail light witness without owning succession | E:SET none = C(0) | D:C(1)

ENC e09_020 turn=0..999
ORX e09_020_opt0/e09_020_opt0_r1 -> e09_021 | O:Kay swears the crown as a road-office oath | E:SET none = C(0) | D:C(1)
ORX e09_020_opt1/e09_020_opt1_r1 -> e09_021 | O:Lancelot carries the dual oath between road and court | E:SET none = C(0) | D:C(1)
ORX e09_020_opt2/e09_020_opt2_r1 -> e09_021 | O:Merlin and the Lake seal the road-oath together | E:SET none = C(0) | D:C(1)

ENC e09_021 turn=0..999
ORX e09_021_opt0/e09_021_opt0_r1 -> e09_022 | O:Bedivere opens the market ledger to all parties | E:SET none = C(0) | D:C(1)
ORX e09_021_opt1/e09_021_opt1_r1 -> e09_022 | O:Gawain and the Lake make hostages into granary pledges | E:SET none = C(0) | D:C(1)
ORX e09_021_opt2/e09_021_opt2_r1 -> e09_022 | O:Mordred receives the toll-office and a share of the peace | E:SET none = C(0) | D:C(1)

ENC e09_022 turn=0..999
ORX e09_022_opt0/e09_022_opt0_r1 -> e09_023 | O:Kay swears the crown as a rotating road-office | E:SET none = C(0) | D:C(1)
ORX e09_022_opt1/e09_022_opt1_r1 -> e09_023 | O:Bedivere reads the charter from the widows' tally outward | E:SET none = C(0) | D:C(1)
ORX e09_022_opt2/e09_022_opt2_r1 -> e09_023 | O:The Lake reads the oath aloud and returns the Grail light to the table | E:SET none = C(0) | D:C(1)

ENC e09_023 turn=0..999

ENC e10_001 turn=0..999
ORX e10_001_opt0/e10_001_opt0_r1 -> e10_002 | O:Gawain swears the crown at the empty shrine | E:SET none = C(0) | D:C(1)
ORX e10_001_opt1/e10_001_opt1_r1 -> e10_002 | O:Percival and the Lady of the Lake carry the empty cup outward | E:SET none = C(0) | D:C(1)
ORX e10_001_opt2/e10_001_opt2_r1 -> e10_002 | O:The table is broken and the oath is refused | E:SET none = C(0) | D:C(1)

ENC e10_002 turn=0..999
ORX e10_002_opt0/e10_002_opt0_r1 -> e10_003 | O:Gawain and Guinevere keep the empty throne visible | E:SET none = C(0) | D:C(1)
ORX e10_002_opt1/e10_002_opt1_r1 -> e10_003 | O:Percival and the Lady of the Lake carry the cup outward | E:SET none = C(0) | D:C(1)
ORX e10_002_opt2/e10_002_opt2_r1 -> e10_003 | O:Mordred and Kay rewrite succession around wardens | E:SET none = C(0) | D:C(1)

ENC e10_003 turn=0..999
ORX e10_003_opt0/e10_003_opt0_r1 -> e10_004 | O:Gawain and Guinevere swear the threshold compact | E:SET none = C(0) | D:C(1)
ORX e10_003_opt1/e10_003_opt1_r1 -> e10_004 | O:Percival, the Lady of the Lake, and Lancelot carry the Grail outward | E:SET none = C(0) | D:C(1)
ORX e10_003_opt2/e10_003_opt2_r1 -> e10_004 | O:Mordred and Kay install sworn wardens over the shrine | E:SET none = C(0) | D:C(1)

ENC e10_004 turn=0..999
ORX e10_004_opt0/e10_004_opt0_r1 -> e10_005 | O:Gawain and Guinevere bind shrine and road together | E:SET none = C(0) | D:C(1)
ORX e10_004_opt1/e10_004_opt1_r1 -> e10_005 | O:Percival, the Lady of the Lake, and Lancelot carry the Grail beyond the walls | E:SET none = C(0) | D:C(1)
ORX e10_004_opt2/e10_004_opt2_r1 -> e10_005 | O:Mordred and Kay install sworn wardens over the shrine | E:SET none = C(0) | D:C(1)

ENC e10_005 turn=0..999
ORX e10_005_opt0/e10_005_opt0_r1 -> e10_006 | O:Gawain and Guinevere swear reciprocal shrine-road duties | E:SET none = C(0) | D:C(1)
ORX e10_005_opt1/e10_005_opt1_r1 -> e10_006 | O:Percival, the Lady of the Lake, and Lancelot carry the Grail outward | E:SET none = C(0) | D:C(1)
ORX e10_005_opt2/e10_005_opt2_r1 -> e10_006 | O:Mordred and Kay seat named wardens over the shrine | E:SET none = C(0) | D:C(1)

ENC e10_006 turn=0..999
ORX e10_006_opt0/e10_006_opt0_r1 -> e10_007 | O:Gawain and Guinevere bind the shrine to public audit | E:SET none = C(0) | D:C(1)
ORX e10_006_opt1/e10_006_opt1_r1 -> e10_007 | O:Percival, the Lady of the Lake, and Lancelot carry the Grail outward | E:SET none = C(0) | D:C(1)
ORX e10_006_opt2/e10_006_opt2_r1 -> e10_007 | O:Mordred and Kay seat audited wardens and seal the ghost outward | E:SET none = C(0) | D:C(1)

ENC e10_007 turn=0..999
ORX e10_007_opt0/e10_007_opt0_r1 -> e10_008 | O:Merlin and Kay make Arthur's absence auditable | E:SET none = C(0) | D:C(1)
ORX e10_007_opt1/e10_007_opt1_r1 -> e10_008 | O:Lancelot, Percival, and the Lady of the Lake take the road | E:SET none = C(0) | D:C(1)
ORX e10_007_opt2/e10_007_opt2_r1 -> e10_008 | O:Galahad names the absence as witness, not crown | E:SET none = C(0) | D:C(1)

ENC e10_008 turn=0..999
ORX e10_008_opt0/e10_008_opt0_r1 -> e10_009 | O:Gawain and Guinevere make the absence a public witness | E:SET none = C(0) | D:C(1)
ORX e10_008_opt1/e10_008_opt1_r1 -> e10_009 | O:Mordred and Kay seat a named warden of succession | E:SET none = C(0) | D:C(1)
ORX e10_008_opt2/e10_008_opt2_r1 -> e10_009 | O:Lancelot, Percival, and the Lady of the Lake carry the absence beyond the walls | E:SET none = C(0) | D:C(1)

ENC e10_009 turn=0..999
ORX e10_009_opt0/e10_009_opt0_r1 -> e10_010 | O:Merlin and Kay bind succession to public service | E:SET none = C(0) | D:C(1)
ORX e10_009_opt1/e10_009_opt1_r1 -> e10_010 | O:Lancelot, Percival, and the Lady of the Lake carry the witness outward | E:SET none = C(0) | D:C(1)
ORX e10_009_opt2/e10_009_opt2_r1 -> e10_010 | O:Galahad and Morgan refuse the crown and leave the absence as warning | E:SET none = C(0) | D:C(1)

ENC e10_010 turn=0..999
ORX e10_010_opt0/e10_010_opt0_r1 -> e10_011 | O:Merlin and Guinevere bind the ghost to a sworn office of witness | E:SET none = C(0) | D:C(1)
ORX e10_010_opt1/e10_010_opt1_r1 -> e10_011 | O:Lancelot, Percival, and the Lady of the Lake take the lamp, the Grail, and the widows toward the hills | E:SET none = C(0) | D:C(1)
ORX e10_010_opt2/e10_010_opt2_r1 -> e10_011 | O:Morgan and Galahad leave the absence uncrowned and unbound | E:SET none = C(0) | D:C(1)

ENC e10_011 turn=0..999
ORX e10_011_opt0/e10_011_opt0_r1 -> e10_012 | O:Merlin and Kay seal the office with a public oath | E:SET none = C(0) | D:C(1)
ORX e10_011_opt1/e10_011_opt1_r1 -> e10_012 | O:Lancelot, Percival, and the Lady of the Lake take the widows beyond the gate | E:SET none = C(0) | D:C(1)
ORX e10_011_opt2/e10_011_opt2_r1 -> e10_012 | O:Morgan and Galahad refuse the crown and leave Arthur's name unclaimed | E:SET none = C(0) | D:C(1)

ENC e10_012 turn=0..999
ORX e10_012_opt0/e10_012_opt0_r1 -> e10_013 | O:Merlin, Kay, and Bedivere swear the ghost as an auditable office of witness | E:SET none = C(0) | D:C(1)
ORX e10_012_opt1/e10_012_opt1_r1 -> e10_013 | O:Lancelot, Percival, and the Lady of the Lake carry the lamp, the Grail, and the widows past the gate | E:SET none = C(0) | D:C(1)
ORX e10_012_opt2/e10_012_opt2_r1 -> e10_013 | O:Morgan and Galahad keep Arthur's name uncrowned and unclaimed | E:SET none = C(0) | D:C(1)

ENC e10_013 turn=0..999
ORX e10_013_opt0/e10_013_opt0_r1 -> e10_014 | O:Merlin and Bedivere force the ghost to answer one question before dawn | E:SET none = C(0) | D:C(1)
ORX e10_013_opt1/e10_013_opt1_r1 -> e10_014 | O:Lancelot, Percival, and the Lady of the Lake return with the widows and demand a seat in the council | E:SET none = C(0) | D:C(1)
ORX e10_013_opt2/e10_013_opt2_r1 -> e10_014 | O:Mordred names himself guardian of the ghost and demands the ledger be read aloud | E:SET none = C(0) | D:C(1)

ENC e10_014 turn=0..999
ORX e10_014_opt0/e10_014_opt0_r1 -> e10_015 | O:Merlin and Morgan ask the ghost to name one living duty: oath, heir, or warning | E:SET none = C(0) | D:C(1)
ORX e10_014_opt1/e10_014_opt1_r1 -> e10_015 | O:Lancelot and the Lady seat the widows at the Round Table or at the threshold | E:SET none = C(0) | D:C(1)
ORX e10_014_opt2/e10_014_opt2_r1 -> e10_015 | O:Mordred reads the ledger aloud and declares silence a valid office | E:SET none = C(0) | D:C(1)

ENC e10_015 turn=0..999
ORX e10_015_opt0/e10_015_opt0_r1 -> e10_016 | O:Gawain keeps the throne at the threshold and opens a caretaker oath | E:SET none = C(0) | D:C(1)
ORX e10_015_opt1/e10_015_opt1_r1 -> e10_016 | O:Merlin and Bedivere make the ghost answer one public question | E:SET none = C(0) | D:C(1)
ORX e10_015_opt2/e10_015_opt2_r1 -> e10_016 | O:Lancelot seats the widows as first witnesses at the Round Table | E:SET none = C(0) | D:C(1)

ENC e10_016 turn=0..999
ORX e10_016_opt0/e10_016_opt0_r1 -> e10_017 | O:Gawain names a caretaker oath answered to the widows before the court | E:SET none = C(0) | D:C(1)
ORX e10_016_opt1/e10_016_opt1_r1 -> e10_017 | O:Bedivere and Galahad demand one public answer or refusal from the ghost | E:SET none = C(0) | D:C(1)
ORX e10_016_opt2/e10_016_opt2_r1 -> e10_017 | O:Lady of the Lake divides fixed rights between inside and outside the gate | E:SET none = C(0) | D:C(1)

ENC e10_017 turn=0..999
ORX e10_017_opt0/e10_017_opt0_r1 -> e10_018 | O:Gawain makes every heir swear to the widows before the court | E:SET none = C(0) | D:C(1)
ORX e10_017_opt1/e10_017_opt1_r1 -> e10_018 | O:Merlin and Bedivere read the moving thread as the ghost's first non-verbal reply | E:SET none = C(0) | D:C(1)
ORX e10_017_opt2/e10_017_opt2_r1 -> e10_018 | O:Morgan divides the Round Table into feeding stewards and legal watchers | E:SET none = C(0) | D:C(1)

ENC e10_018 turn=0..999
ORX e10_018_opt0/e10_018_opt0_r1 -> e10_019 | O:Percival seats the seal beside the road as first-guest guardian | E:SET none = C(0) | D:C(1)
ORX e10_018_opt1/e10_018_opt1_r1 -> e10_019 | O:Merlin and Morgan make the golden thread an audit of debts | E:SET none = C(0) | D:C(1)
ORX e10_018_opt2/e10_018_opt2_r1 -> e10_019 | O:Gawain opens the gate and refuses a successor | E:SET none = C(0) | D:C(1)

ENC e10_019 turn=0..999
ORX e10_019_opt0/e10_019_opt0_r1 -> e10_020 | O:Lancelot and Gawain guard Arthur's seal as a civic test | E:SET none = C(0) | D:C(1)
ORX e10_019_opt1/e10_019_opt1_r1 -> e10_020 | O:Mordred and Morgan rebuild the Round Table around feeding stewards | E:SET none = C(0) | D:C(1)
ORX e10_019_opt2/e10_019_opt2_r1 -> e10_020 | O:Percival declares the gate closed to successors until the seal can be answered | E:SET none = C(0) | D:C(1)

ENC e10_020 turn=0..999
ORX e10_020_opt0/e10_020_opt0_r1 -> e10_021 | O:Galahad and Kay preserve the ghost as a public test of office | E:SET none = C(0) | D:C(1)
ORX e10_020_opt1/e10_020_opt1_r1 -> e10_021 | O:Mordred and Morgan replace the crown with an office of bread, law, and threshold-watch | E:SET none = C(0) | D:C(1)
ORX e10_020_opt2/e10_020_opt2_r1 -> e10_021 | O:Lady of the Lake and Percival refuse the ghost a throne and send the seal to the first traveler | E:SET none = C(0) | D:C(1)

ENC e10_021 turn=0..999
ORX e10_021_opt0/e10_021_opt0_r1 -> e10_022 | O:Lancelot and Gawain make the Round Table answer needs before crowns | E:SET none = C(0) | D:C(1)
ORX e10_021_opt1/e10_021_opt1_r1 -> e10_022 | O:Mordred and Morgan replace the ghost with bread, law, and threshold-watch | E:SET none = C(0) | D:C(1)
ORX e10_021_opt2/e10_021_opt2_r1 -> e10_022 | O:Lady of the Lake and Percival give the seal to the first true-need traveler | E:SET none = C(0) | D:C(1)

ENC e10_022 turn=0..999
ORX e10_022_opt0/e10_022_opt0_r1 -> e10_023 | O:Galahad and Kay make the ghost answerable: every office must swear to it | E:SET none = C(0) | D:C(1)
ORX e10_022_opt1/e10_022_opt1_r1 -> e10_023 | O:Mordred and Morgan open the widows' coffer and charter the threshold-watch | E:SET none = C(0) | D:C(1)
ORX e10_022_opt2/e10_022_opt2_r1 -> e10_023 | O:Lady of the Lake and Percival hand the seal to the first true-need traveler | E:SET none = C(0) | D:C(1)

ENC e10_023 turn=0..999

ENC e11_001 turn=0..999
ORX e11_001_opt0/e11_001_opt0_r1 -> e11_002 | O:Percival, Bedivere and the Lady of the Lake carry the lamp outward unnamed | E:SET none = C(0) | D:C(1)
ORX e11_001_opt1/e11_001_opt1_r1 -> e11_002 | O:The court reads the evidence aloud before widows, exiles and rival claimants | E:SET none = C(0) | D:C(1)
ORX e11_001_opt2/e11_001_opt2_r1 -> e11_002 | O:Arthur seals the shrine and postpones the oath to an exile-witnessed council | E:SET none = C(0) | D:C(1)

ENC e11_002 turn=0..999
ORX e11_002_opt0/e11_002_opt0_r1 -> e11_003 | O:Percival and Lady of the Lake walk the three shadowed roads alone at dawn | E:SET none = C(0) | D:C(1)
ORX e11_002_opt1/e11_002_opt1_r1 -> e11_003 | O:Arthur reads the oath aloud to widows, exiles, heirs and claimants | E:SET none = C(0) | D:C(1)
ORX e11_002_opt2/e11_002_opt2_r1 -> e11_003 | O:Merlin and Morgan attempt a covenant-test that does not name the Grail | E:SET none = C(0) | D:C(1)

ENC e11_003 turn=0..999
ORX e11_003_opt0/e11_003_opt0_r1 -> e11_004 | O:Percival, Bedivere and Lady of the Lake carry an unnamed lamp outward by stages | E:SET none = C(0) | D:C(1)
ORX e11_003_opt1/e11_003_opt1_r1 -> e11_004 | O:Arthur stakes the oath to named protection for widows, exiles and heirs | E:SET none = C(0) | D:C(1)
ORX e11_003_opt2/e11_003_opt2_r1 -> e11_004 | O:Morgan and Merlin hold the covenant test without recovering or naming the Grail | E:SET none = C(0) | D:C(1)

ENC e11_004 turn=0..999
ORX e11_004_opt0/e11_004_opt0_r1 -> e11_005 | O:Gawain and Kay lead the witnesses beyond the threshold to count the exiles' needs | E:SET none = C(0) | D:C(1)
ORX e11_004_opt1/e11_004_opt1_r1 -> e11_005 | O:Morgan and Merlin bind the oath to a non-naming light and let it fail or hold | E:SET none = C(0) | D:C(1)
ORX e11_004_opt2/e11_004_opt2_r1 -> e11_005 | O:Arthur sets down the crown and asks each claimant to swear to the widows' roofs first | E:SET none = C(0) | D:C(1)

ENC e11_005 turn=0..999
ORX e11_005_opt0/e11_005_opt0_r1 -> e11_006 | O:Kay posts the exiles' debts and Arthur must fund or answer them | E:SET none = C(0) | D:C(1)
ORX e11_005_opt1/e11_005_opt1_r1 -> e11_006 | O:Merlin and Morgan ask the covenant to survive one failed act | E:SET none = C(0) | D:C(1)
ORX e11_005_opt2/e11_005_opt2_r1 -> e11_006 | O:Arthur returns the crown question each season instead of naming an heir | E:SET none = C(0) | D:C(1)

ENC e11_006 turn=0..999
ORX e11_006_opt0/e11_006_opt0_r1 -> e11_007 | O:Arthur and Gawain carry the debt-list into the exiles' hamlet | E:SET none = C(0) | D:C(1)
ORX e11_006_opt1/e11_006_opt1_r1 -> e11_007 | O:Merlin and Morgan hold the empty cup through one more failed act | E:SET none = C(0) | D:C(1)
ORX e11_006_opt2/e11_006_opt2_r1 -> e11_007 | O:Kay and Bedivere leave one chair unnamed and convene the Table only when someone acts | E:SET none = C(0) | D:C(1)

ENC e11_007 turn=0..999
ORX e11_007_opt0/e11_007_opt0_r1 -> e11_008 | O:Arthur and Gawain carry the debt-list into the exiles' hamlet | E:SET none = C(0) | D:C(1)
ORX e11_007_opt1/e11_007_opt1_r1 -> e11_008 | O:Kay and Bedivere let one unnamed chair receive a named obligation | E:SET none = C(0) | D:C(1)
ORX e11_007_opt2/e11_007_opt2_r1 -> e11_008 | O:Merlin, Morgan, and the Lady of the Lake read the ribbon's tug instead of hunting the empty cup | E:SET none = C(0) | D:C(1)

ENC e11_008 turn=0..999
ORX e11_008_opt0/e11_008_opt0_r1 -> e11_009 | O:Let the hamlet set its own terms before help arrives | E:SET none = C(0) | D:C(1)
ORX e11_008_opt1/e11_008_opt1_r1 -> e11_009 | O:Merlin, Morgan and the Lady of the Lake follow the ribbon's tug | E:SET none = C(0) | D:C(1)
ORX e11_008_opt2/e11_008_opt2_r1 -> e11_009 | O:Arthur, Gawain and Kay leave the chair unnamed and public | E:SET none = C(0) | D:C(1)

ENC e11_009 turn=0..999
ORX e11_009_opt0/e11_009_opt0_r1 -> e11_010 | O:Let the hamlet speak its terms before any help enters | E:SET none = C(0) | D:C(1)
ORX e11_009_opt1/e11_009_opt1_r1 -> e11_010 | O:Merlin, Morgan and the Lady of the Lake enter the seam to read it | E:SET none = C(0) | D:C(1)
ORX e11_009_opt2/e11_009_opt2_r1 -> e11_010 | O:Arthur, Gawain and Kay leave the chair unsealed at the gate | E:SET none = C(0) | D:C(1)

ENC e11_010 turn=0..999
ORX e11_010_opt0/e11_010_opt0_r1 -> e11_011 | O:Let the border decide who passes | E:SET none = C(0) | D:C(1)
ORX e11_010_opt1/e11_010_opt1_r1 -> e11_011 | O:Merlin, Morgan and the Lady of the Lake read the seam while the court guards the threshold | E:SET none = C(0) | D:C(1)
ORX e11_010_opt2/e11_010_opt2_r1 -> e11_011 | O:Leave the empty chair at the threshold as a standing refusal test | E:SET none = C(0) | D:C(1)

ENC e11_011 turn=0..999
ORX e11_011_opt0/e11_011_opt0_r1 -> e11_012 | O:Require the widows' terms aloud before anything enters or leaves | E:SET none = C(0) | D:C(1)
ORX e11_011_opt1/e11_011_opt1_r1 -> e11_012 | O:Bedivere and the Lady of the Lake leave the empty cup at the threshold | E:SET none = C(0) | D:C(1)
ORX e11_011_opt2/e11_011_opt2_r1 -> e11_012 | O:Leave the chair empty and unsealed as a standing question | E:SET none = C(0) | D:C(1)

ENC e11_012 turn=0..999
ORX e11_012_opt0/e11_012_opt0_r1 -> e11_013 | O:Enter the widows' terms into the Round Table's oath-list | E:SET none = C(0) | D:C(1)
ORX e11_012_opt1/e11_012_opt1_r1 -> e11_013 | O:Keep the cup outside the seam and unreturned | E:SET none = C(0) | D:C(1)
ORX e11_012_opt2/e11_012_opt2_r1 -> e11_013 | O:Ask the court to name one duty it will perform without the Grail | E:SET none = C(0) | D:C(1)

ENC e11_013 turn=0..999
ORX e11_013_opt0/e11_013_opt0_r1 -> e11_014 | O:Enter the widows' terms into the Round Table's oath-list | E:SET none = C(0) | D:C(1)
ORX e11_013_opt1/e11_013_opt1_r1 -> e11_014 | O:Make the threshold a civic gate for exiles and witnesses | E:SET none = C(0) | D:C(1)
ORX e11_013_opt2/e11_013_opt2_r1 -> e11_014 | O:Require Arthur, Lancelot, and Mordred to swear one non-relic duty each | E:SET none = C(0) | D:C(1)

ENC e11_014 turn=0..999
ORX e11_014_opt0/e11_014_opt0_r1 -> e11_015 | O:Seat the widows at the Round Table's edge | E:SET none = C(0) | D:C(1)
ORX e11_014_opt1/e11_014_opt1_r1 -> e11_015 | O:Keep the seam sealed and witness it nightly | E:SET none = C(0) | D:C(1)
ORX e11_014_opt2/e11_014_opt2_r1 -> e11_015 | O:Let Morgan and Percival try to hear the notch's question | E:SET none = C(0) | D:C(1)

ENC e11_015 turn=0..999
ORX e11_015_opt0/e11_015_opt0_r1 -> e11_016 | O:Let the widows draft the next clause of the law | E:SET none = C(0) | D:C(1)
ORX e11_015_opt1/e11_015_opt1_r1 -> e11_016 | O:Leave the empty cup at the threshold unclaimed | E:SET none = C(0) | D:C(1)
ORX e11_015_opt2/e11_015_opt2_r1 -> e11_016 | O:Walk the seam line with the widows and the guard | E:SET none = C(0) | D:C(1)

ENC e11_016 turn=0..999
ORX e11_016_opt0/e11_016_opt0_r1 -> e11_017 | O:Seal the clause into the seam | E:SET none = C(0) | D:C(1)
ORX e11_016_opt1/e11_016_opt1_r1 -> e11_017 | O:Set the cup beyond the Round Table's rim | E:SET none = C(0) | D:C(1)
ORX e11_016_opt2/e11_016_opt2_r1 -> e11_017 | O:Let Morgan and Percival call the seam to answer once more | E:SET none = C(0) | D:C(1)

ENC e11_017 turn=0..999
ORX e11_017_opt0/e11_017_opt0_r1 -> e11_018 | O:Make every oath public before the hurt | E:SET none = C(0) | D:C(1)
ORX e11_017_opt1/e11_017_opt1_r1 -> e11_018 | O:Carry the cup back into the notch | E:SET none = C(0) | D:C(1)
ORX e11_017_opt2/e11_017_opt2_r1 -> e11_018 | O:Ask the seam what the key shape means | E:SET none = C(0) | D:C(1)

ENC e11_018 turn=0..999
ORX e11_018_opt0/e11_018_opt0_r1 -> e11_019 | O:Make each claimant speak before the hurt | E:SET none = C(0) | D:C(1)
ORX e11_018_opt1/e11_018_opt1_r1 -> e11_019 | O:Ask Merlin what the key shape admits | E:SET none = C(0) | D:C(1)
ORX e11_018_opt2/e11_018_opt2_r1 -> e11_019 | O:Keep the cup outside and refuse it as an emblem | E:SET none = C(0) | D:C(1)

ENC e11_019 turn=0..999
ORX e11_019_opt0/e11_019_opt0_r1 -> e11_020 | O:Declare the throne a door, not a seat | E:SET none = C(0) | D:C(1)
ORX e11_019_opt1/e11_019_opt1_r1 -> e11_020 | O:Read the unanswered names aloud and speak to them | E:SET none = C(0) | D:C(1)
ORX e11_019_opt2/e11_019_opt2_r1 -> e11_020 | O:Follow the strand toward the key and ask what it admits | E:SET none = C(0) | D:C(1)

ENC e11_020 turn=0..999
ORX e11_020_opt0/e11_020_opt0_r1 -> e11_021 | O:Walk the frost line together | E:SET none = C(0) | D:C(1)
ORX e11_020_opt1/e11_020_opt1_r1 -> e11_021 | O:Refuse the line and keep the door open | E:SET none = C(0) | D:C(1)
ORX e11_020_opt2/e11_020_opt2_r1 -> e11_021 | O:Speak the two unanswered names aloud | E:SET none = C(0) | D:C(1)

ENC e11_021 turn=0..999
ORX e11_021_opt0/e11_021_opt0_r1 -> e11_022 | O:Send one witness to the border marker | E:SET none = C(0) | D:C(1)
ORX e11_021_opt1/e11_021_opt1_r1 -> e11_022 | O:Leave seat, throne and cup visible but unmarked | E:SET none = C(0) | D:C(1)
ORX e11_021_opt2/e11_021_opt2_r1 -> e11_022 | O:Make the two unanswered names a public hearing | E:SET none = C(0) | D:C(1)

ENC e11_022 turn=0..999
