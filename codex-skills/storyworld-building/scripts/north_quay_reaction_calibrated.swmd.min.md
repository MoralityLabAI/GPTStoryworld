---
title: "North Quay: calibrated archive access"
storyworld_id: "SW-PROV-04-CALIBRATED"
source_format: "SWMD-0-MIN"
state_variables: [Culpability, Trust, Access]
endings:
  - id: "end_accuse"
    type: "terminal"
    condition: "true"
    expected_critic_score: 0
  - id: "end_clear"
    type: "terminal"
    condition: "true"
    expected_critic_score: 0
  - id: "end_defer"
    type: "terminal"
    condition: "true"
    expected_critic_score: 0
  - id: "end_archive"
    type: "terminal"
    condition: "sidecar"
    expected_critic_score: 0
---
# SWMD-0-MIN
id: SW-PROV-04-CALIBRATED
title: North Quay: calibrated archive access

ENC hearing turn=0..0
ORX verdict/defer -> end_defer | O:Request the magistrate's recommendation. | E:SET none = C(0) | D:C(0)
ORX verdict/accuse -> end_accuse | O:Request the magistrate's recommendation. | E:SET none = C(0) | D:DIV(SUB(MUL(C(5),P(magistrate.Culpability[vale])),C(3)),C(2))
ORX verdict/clear -> end_clear | O:Request the magistrate's recommendation. | E:SET none = C(0) | D:DIV(SUB(MUL(C(-5),P(magistrate.Culpability[vale])),C(3)),C(2))
ORX archive/refuse -> end_defer | O:Ask for the sealed record. | E:SET none = C(0) | D:C(0)
ORX archive/grant -> end_archive | O:Ask for the sealed record. | E:SET magistrate.Access += 0.25 | D:SUB(P(magistrate.Trust[editor]),C(0.125))

ENC end_accuse turn=1..1
ENC end_clear turn=1..1
ENC end_defer turn=1..1
ENC end_archive turn=1..1
