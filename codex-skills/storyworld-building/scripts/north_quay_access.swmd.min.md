---
title: "North Quay: sealed registry access mechanism"
storyworld_id: "SW-PROV-05-ACCESS"
source_format: "SWMD-0-MIN"
state_variables: [Documented, Trust, Access, RecordRead]
endings:
  - id: "end_record"
    type: "terminal"
    condition: "sidecar"
    expected_critic_score: 0
  - id: "end_defer"
    type: "terminal"
    condition: "true"
    expected_critic_score: 0
  - id: "end_refused"
    type: "terminal"
    condition: "true"
    expected_critic_score: 0
---
# SWMD-0-MIN
id: SW-PROV-05-ACCESS
title: North Quay: sealed registry access mechanism

ENC hearing turn=0..0
ORX inspect/document -> briefing | O:Trace the seals before filing the application. | E:SET editor.Documented += 0.25 | D:C(0)
ORX premature/queue -> application | O:Approach the application desk without the documented lineage. | E:SET none = C(0) | D:C(0)
ORX defer/stop -> end_defer | O:Defer the application. | E:SET none = C(0) | D:C(0)

ENC briefing turn=1..1
ORX present/accept -> application | O:Show the registrar the documented comparison. | E:SET registrar.Trust[editor] += 0.25 | D:C(0)
ORX abandon/stop -> end_defer | O:Keep the evidence private and defer. | E:SET none = C(0) | D:C(0)

ENC application turn=1..2
ORX apply/refuse -> end_refused | O:File the sole application. | E:SET none = C(0) | D:C(0)
ORX apply/grant -> opened | O:File the sole application. | E:SET registrar.Access += 0.25 | D:SUB(P(registrar.Trust[editor]),C(0.125))
ORX defer/stop -> end_defer | O:Defer without filing. | E:SET none = C(0) | D:C(0)

ENC opened turn=2..3
ORX read/inspect -> end_record | O:Read the opened validity register. | E:SET editor.RecordRead += 0.25 | D:C(0)
ORX abandon/stop -> end_defer | O:Leave the record unread. | E:SET none = C(0) | D:C(0)

ENC end_record turn=3..4
ENC end_defer turn=1..4
ENC end_refused turn=1..3
