---
title: "Reservoir Dogs: Blood on the Warehouse Floor"
version: "0.1.9"
storyworld_id: "SW-BONSAI27-RESERVOIR-DOGS-001"
environment_type: "SWEEPWEAVE_STORYWORLD"
source_format: "SWMD-0-MIN"
state_variables:
  - "Crew_Loyalty"
  - "Diamond_Leverage"
  - "Phase_Clock"
  - "Professional_Discipline"
  - "Rat_Suspicion"
  - "Sadistic_Escalation"
endings:
  - id: "page_end_blonde_gasoline_inferno"
    type: "terminal"
    condition: "AND(ARITHMETIC COMPARATOR(P(char_white.Phase_Clock),C(0.55)),ARITHMETIC COMPARATOR(P(char_blonde.Sadistic_Escalation),C(0.05)))"
    description: "Unchecked sadism turns the safehouse into an inferno as spilled gasoline catches a stray muzzle flash under the tinny groove of seventies AM radio. Black smoke pours from the mo..."
    expected_critic_score: 0
    proximity_spec:
      - var: "Phase_Clock"
        op: ">="
        threshold: 0.55
      - var: "Sadistic_Escalation"
        op: ">="
        threshold: 0.05
  - id: "page_end_cabot_executes_the_plant"
    type: "terminal"
    condition: "AND(ARITHMETIC COMPARATOR(P(char_white.Phase_Clock),C(0.55)),ARITHMETIC COMPARATOR(P(char_pink.Rat_Suspicion),C(-0.1)))"
    description: "Convinced by the timeline gaps and Pink's cold ambush arithmetic, Mr. White lowers his forty-five half an inch when Joe Cabot calls Freddy Newandyke a plant. Joe finishes the jo..."
    expected_critic_score: 0
    proximity_spec:
      - var: "Phase_Clock"
        op: ">="
        threshold: 0.55
      - var: "Rat_Suspicion"
        op: ">="
        threshold: -0.1
  - id: "page_end_mexican_standoff_collapse"
    type: "failure"
    condition: "ARITHMETIC COMPARATOR(P(char_white.Phase_Clock),C(0.55))"
    description: "Joe fires at Orange, White shoots Joe, Eddie shoots White, and White drops Eddie in a deafening three-second thunderclap. Crawling across the blood-slick floor to cradle Freddy'..."
    expected_critic_score: -1
    proximity_spec:
      - var: "Phase_Clock"
        op: ">="
        threshold: 0.55
  - id: "page_end_pink_ghosts_with_stones"
    type: "terminal"
    condition: "AND(ARITHMETIC COMPARATOR(P(char_white.Phase_Clock),C(0.55)),ARITHMETIC COMPARATOR(P(char_pink.Professional_Discipline),C(-0.15)))"
    description: "While ego and blood oaths detonate the center of the warehouse, Mr. Pink stays crouched beneath the wooden ramp with both hands locked around the Karina diamond satchel. Slippin..."
    expected_critic_score: 0
    proximity_spec:
      - var: "Phase_Clock"
        op: ">="
        threshold: 0.55
      - var: "Professional_Discipline"
        op: ">="
        threshold: -0.15
  - id: "page_end_white_mercy_hospital_trap"
    type: "terminal"
    condition: "AND(ARITHMETIC COMPARATOR(P(char_white.Phase_Clock),C(0.55)),ARITHMETIC COMPARATOR(P(char_white.Crew_Loyalty),C(-0.05)))"
    description: "Refusing to watch the kid bleed out on concrete for Joe Cabot's rules, Larry Dimmick abandons the diamond split and shoulders Freddy into a stolen sedan bound for emergency surg..."
    expected_critic_score: 0
    proximity_spec:
      - var: "Phase_Clock"
        op: ">="
        threshold: 0.55
      - var: "Crew_Loyalty"
        op: ">="
        threshold: -0.05
  - id: "page_secret_undercover_truce"
    type: "terminal"
    condition: "AND(ARITHMETIC COMPARATOR(P(char_white.Phase_Clock),C(0.55)),ARITHMETIC COMPARATOR(ABSOLUTE VALUE(ADD(P(char_white.Crew_Loyalty),C(-0.12))),C(0.65)),ARITHMETIC COMPARATOR(P(char_pink.Rat_Suspicion),C(0.08)),ARITHMETIC COMPARATOR(P(char_blonde.Sadistic_Escalation),C(0.35)))"
    description: "Catching the rehearsed squad-room cadence in Orange's anecdote without letting Blonde's razor blow the room apart, White and Pink force a quiet confession before Joe Cabot ever ..."
    expected_critic_score: 0
    proximity_spec:
      - var: "Phase_Clock"
        op: ">="
        threshold: 0.55
      - var: "Rat_Suspicion"
        op: ">="
        threshold: 0.08
      - var: "Sadistic_Escalation"
        op: "<="
        threshold: 0.35
---

# SWMD-0
id: SW-BONSAI27-RESERVOIR-DOGS-001
title: Reservoir Dogs: Blood on the Warehouse Floor
theme: noir
about: After the Karina Wholesale Diamonds heist explodes into a sidewalk slaughter, four color-coded survivors converge on an abandoned Los Angeles mortuary warehouse: protective veteran Mr. White, paranoid pragmatist Mr. Pink, smiling sadist Mr. Blonde with a kidnapped patrolman in his trunk, and gut-shot undercover detective Mr. Orange bleeding out on the ramp.
cast: char_white, char_pink, char_orange, char_blonde
props: Phase_Clock, Professional_Discipline, Rat_Suspicion, Crew_Loyalty, Sadistic_Escalation, Diamond_Leverage
spools:
  spool_act1_safehouse: page_start page_pink_ambush_theory page_color_aliases_and_stash page_blonde_arrives page_cadillac_trunk
  spool_act2_interrogation: page_chair_duct_tape page_eddie_call_and_alibi page_k_billy_razor page_orange_gun_on_the_ramp page_nash_confession_shockwave
  spool_act3_standoff: page_eddie_and_blonde_story page_cabot_verdict page_mexican_standoff page_sirens_at_the_rollup_door
  spool_endings: page_end_mexican_standoff_collapse page_end_pink_ghosts_with_stones page_end_blonde_gasoline_inferno page_end_cabot_executes_the_plant page_end_white_mercy_hospital_trap page_secret_undercover_truce

## ENC page_start | Blood on the Backseat | turn=0..2 | spools=[spool_act1_safehouse]
T: White drags Orange across the dusty mortuary floor. Blood soaks through the white dress shirt. Orange gasps, clutching White's sleeve. "Hospital. Real name. Please." Pink watches from the shadows, jaw tight. "No names. No hospitals. You're a liability, not a patient." White's hand finds Orange's pulse. "Hold the line, kid. We're not done." The shuttered room smells of cordite and stale coffee. Every breath tastes like copper. White's eyes flick to the steel door, then back to the bleeding detective. The crew's silence is a loaded gun.

OPT opt_page_start_0: Promise Orange help while enforcing color aliases
  RXN rxn_page_start_0_0 -> page_pink_ambush_theory
    T: Orange's eyes flutter, a wet cough escaping his lips. "White... you're the only one who still talks like a man." Pink's thumb hovers over his phone, calculating odds. The promise hangs in the air, fragile as a bullet casing. Leverage shifts toward the ambush theory.
    E:
      SET char_orange.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Professional_Discipline),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_orange.Professional_Discipline[char_white][char_orange]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Professional_Discipline),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Professional_Discipline[char_white][char_orange]),0.45),ABSOLUTE VALUE(MUL(P(char_orange.Professional_Discipline),0.35)),C(0.03))

  RXN rxn_page_start_0_1 -> page_color_aliases_and_stash
    T: Orange nods weakly, the alias a shield against the pain. "Orange. Just Orange." White's grip tightens, a silent vow. Pink's eyes narrow, noting the discipline. The stash becomes the only safe harbor. Leverage shifts toward the color aliases and stash.
    E:
      SET char_orange.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Professional_Discipline),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_orange.Professional_Discipline[char_white][char_orange]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Professional_Discipline),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),-0.5),MUL(P(char_orange.Professional_Discipline[char_white][char_orange]),-0.35),MUL(MUL(P(char_white.Crew_Loyalty),0.5),MUL(P(char_orange.Professional_Discipline),0.5)),C(0.01))

  RXN rxn_page_start_0_2 -> page_pink_ambush_theory
    T: Orange's head lolls, a whisper of trust. "You'll get me out, White." Pink's jaw clenches, the math of betrayal already running. The promise is a thread, and the ambush is the knife. Leverage shifts toward the ambush theory.
    E:
      SET char_orange.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Professional_Discipline),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_orange.Professional_Discipline[char_white][char_orange]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Professional_Discipline),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Professional_Discipline[char_white][char_orange]),-0.35),MAX(MUL(P(char_orange.Diamond_Leverage),0.3),C(-0.15)),C(-0.01))

OPT opt_page_start_1: Whisper your first name to steady the dying kid
  RXN rxn_page_start_1_0 -> page_color_aliases_and_stash
    T: Orange's eyes widen, a flicker of humanity breaking through the shock. "Freddy... just Freddy." White's voice drops to a murmur, the name a secret. Pink's expression hardens, the alias rule shattered. Leverage shifts toward the color aliases and stash.
    E:
      SET char_orange.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Professional_Discipline),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_orange.Professional_Discipline[char_white][char_orange]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Professional_Discipline),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Professional_Discipline[char_white][char_orange]),0.45),MUL(MUL(P(char_white.Crew_Loyalty),0.5),MUL(P(char_orange.Professional_Discipline),0.5)),C(0.06))

  RXN rxn_page_start_1_1 -> page_pink_ambush_theory
    T: Orange's breath shudders, the name a lifeline. "Freddy... hold on." White's hand stays on the pulse, the name a ghost. Pink's eyes track the shift, the ambush theory gaining traction. Leverage shifts toward the ambush theory.
    E:
      SET char_orange.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Professional_Discipline),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_orange.Professional_Discipline[char_white][char_orange]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Professional_Discipline),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),-0.5),MUL(P(char_orange.Professional_Discipline[char_white][char_orange]),-0.35),MAX(MUL(P(char_orange.Diamond_Leverage),0.3),C(-0.15)),C(0.04))

  RXN rxn_page_start_1_2 -> page_color_aliases_and_stash
    T: Orange's lips move, the name a prayer. "Freddy... don't let them take me." White's grip tightens, the alias a fragile shield. Pink's jaw sets, the stash the only refuge. Leverage shifts toward the color aliases and stash.
    E:
      SET char_orange.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Professional_Discipline),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_orange.Professional_Discipline[char_white][char_orange]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Professional_Discipline),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Professional_Discipline[char_white][char_orange]),-0.35),ABSOLUTE VALUE(MUL(P(char_orange.Professional_Discipline),0.35)),C(0.02))

OPT opt_page_start_2: Search Orange's coat and pockets for tail transmitters
  RXN rxn_page_start_2_0 -> page_pink_ambush_theory
    T: Orange's eyes roll back, a groan escaping his throat. "White... what are you doing?" White's fingers dig into the coat, the search a violation. Pink's eyes narrow, the ambush theory confirmed. Leverage shifts toward the ambush theory.
    E:
      SET char_orange.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Professional_Discipline),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_orange.Professional_Discipline[char_white][char_orange]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Professional_Discipline),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Professional_Discipline[char_white][char_orange]),0.45),MAX(MUL(P(char_orange.Diamond_Leverage),0.3),C(-0.15)),C(0.09))

  RXN rxn_page_start_2_1 -> page_color_aliases_and_stash
    T: Orange's hand twitches, a silent plea. "Please... just the name." White's search pauses, the alias a bargaining chip. Pink's eyes track the hesitation, the stash the only safe ground. Leverage shifts toward the color aliases and stash.
    E:
      SET char_orange.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Professional_Discipline),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_orange.Professional_Discipline[char_white][char_orange]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Professional_Discipline),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),-0.5),MUL(P(char_orange.Professional_Discipline[char_white][char_orange]),-0.35),ABSOLUTE VALUE(MUL(P(char_orange.Professional_Discipline),0.35)),C(0.07))

  RXN rxn_page_start_2_2 -> page_pink_ambush_theory
    T: Orange's breath hitches, the search a betrayal. "You're not... you're not a cop, are you?" White's fingers find nothing, the ambush theory a shadow. Pink's jaw tightens, the math of suspicion. Leverage shifts toward the ambush theory.
    E:
      SET char_orange.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Professional_Discipline),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_orange.Professional_Discipline[char_white][char_orange]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Professional_Discipline),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Professional_Discipline[char_white][char_orange]),-0.35),MUL(MUL(P(char_white.Crew_Loyalty),0.5),MUL(P(char_orange.Professional_Discipline),0.5)),C(0.05))

OPT opt_page_start_3: Lock the steel rollup door and stage the getaway car
  RXN rxn_page_start_3_0 -> page_color_aliases_and_stash
    T: Orange's eyes track the door, a flicker of hope. "White... the car?" White's hand on the wheel, the alias a shield. Pink's eyes narrow, the stash the only refuge. Leverage shifts toward the color aliases and stash.
    E:
      SET char_orange.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Professional_Discipline),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_orange.Professional_Discipline[char_white][char_orange]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Professional_Discipline),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Professional_Discipline[char_white][char_orange]),0.45),ABSOLUTE VALUE(MUL(P(char_orange.Professional_Discipline),0.35)),C(0.12))

  RXN rxn_page_start_3_1 -> page_pink_ambush_theory
    T: Orange's head lolls, the door a promise. "White... don't leave me." White's grip on the wheel tightens, the ambush theory a shadow. Pink's eyes track the shift, the math of betrayal. Leverage shifts toward the ambush theory.
    E:
      SET char_orange.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Professional_Discipline),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_orange.Professional_Discipline[char_white][char_orange]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Professional_Discipline),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),-0.5),MUL(P(char_orange.Professional_Discipline[char_white][char_orange]),-0.35),MUL(MUL(P(char_white.Crew_Loyalty),0.5),MUL(P(char_orange.Professional_Discipline),0.5)),C(0.1))

  RXN rxn_page_start_3_2 -> page_color_aliases_and_stash
    T: Orange's breath shudders, the car a lifeline. "White... just the name." White's hand on the wheel, the alias a fragile shield. Pink's jaw sets, the stash the only safe ground. Leverage shifts toward the color aliases and stash.
    E:
      SET char_orange.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Professional_Discipline),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_orange.Professional_Discipline[char_white][char_orange]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Professional_Discipline),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Professional_Discipline[char_white][char_orange]),-0.35),MAX(MUL(P(char_orange.Diamond_Leverage),0.3),C(-0.15)),C(0.08))


## ENC page_pink_ambush_theory | Pink's Ambush Math | turn=1..3 | spools=[spool_act1_safehouse]
T: Pink slams the side door, winded, satchel clutched tight. "SWAT was already in position before Blonde pulled a trigger. I ran the math. The alarm tripped before his first shot." Orange coughs blood onto the concrete. Blonde leans against a morgue drawer, grinning. "Maybe the math's wrong, Pink. Maybe the rat's closer than you think." Pink's eyes narrow. "I don't care who's bleeding. I need that satchel location. Now."

OPT opt_page_pink_ambush_theory_0: Pink, recount the exact timeline of the Karina vault ambush
  RXN rxn_page_pink_ambush_theory_0_0 -> page_color_aliases_and_stash
    T: Pink's jaw tightens. He lists timestamps with cold precision, each second a weapon. Orange's breathing hitches, but his eyes stay locked on the satchel. The room holds its breath, waiting for the next accusation to land.
    E:
      SET char_pink.Rat_Suspicion = NUDGE(P(char_pink.Rat_Suspicion),ADD(C(0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_pink.Rat_Suspicion[char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white]),ADD(C(0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Rat_Suspicion),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(-0.09),MUL(P(char_pink.Rat_Suspicion),0.06))))
      SET char_white.Professional_Discipline[char_pink][char_blonde] = NUDGE(P(char_white.Professional_Discipline[char_pink][char_blonde]),ADD(C(-0.07),MUL(P(char_pink.Rat_Suspicion),0.05)))
    D: ADD(MUL(P(char_pink.Rat_Suspicion[char_white]),0.65),MUL(P(char_white.Professional_Discipline[char_pink][char_blonde]),0.45),MUL(MUL(P(char_pink.Rat_Suspicion),0.5),MUL(P(char_white.Professional_Discipline),0.5)),C(0.03))

  RXN rxn_page_pink_ambush_theory_0_1 -> page_blonde_arrives
    T: Blonde chuckles, a wet, rattling sound. He shifts his weight, testing the door. "Timeline's a hell of a thing to remember when you're bleeding out, Pink. Maybe the cops just got lucky."
    E:
      SET char_pink.Rat_Suspicion = NUDGE(P(char_pink.Rat_Suspicion),ADD(C(-0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_pink.Rat_Suspicion[char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white]),ADD(C(-0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Rat_Suspicion),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(-0.09),MUL(P(char_pink.Rat_Suspicion),0.06))))
      SET char_white.Professional_Discipline[char_pink][char_blonde] = NUDGE(P(char_white.Professional_Discipline[char_pink][char_blonde]),ADD(C(-0.07),MUL(P(char_pink.Rat_Suspicion),0.05)))
    D: ADD(MUL(P(char_pink.Rat_Suspicion[char_white]),-0.5),MUL(P(char_white.Professional_Discipline[char_pink][char_blonde]),-0.35),MAX(MUL(P(char_blonde.Diamond_Leverage),0.3),C(-0.15)),C(0.01))

  RXN rxn_page_pink_ambush_theory_0_2 -> page_color_aliases_and_stash
    T: Pink's gaze snaps to the satchel. "Lucky? No. Someone called it in. And I know who. The math doesn't lie, and it points to a color in this room."
    E:
      SET char_pink.Rat_Suspicion = NUDGE(P(char_pink.Rat_Suspicion),ADD(C(0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_pink.Rat_Suspicion[char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white]),ADD(C(0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Rat_Suspicion),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(-0.09),MUL(P(char_pink.Rat_Suspicion),0.06))))
      SET char_white.Professional_Discipline[char_pink][char_blonde] = NUDGE(P(char_white.Professional_Discipline[char_pink][char_blonde]),ADD(C(-0.07),MUL(P(char_pink.Rat_Suspicion),0.05)))
    D: ADD(MUL(P(char_pink.Rat_Suspicion[char_white]),0.65),MUL(P(char_white.Professional_Discipline[char_pink][char_blonde]),-0.35),ABSOLUTE VALUE(MUL(P(char_blonde.Professional_Discipline),0.35)),C(-0.01))

OPT opt_page_pink_ambush_theory_1: Blonde, your panic shooting explains the whole bloody mess
  RXN rxn_page_pink_ambush_theory_1_0 -> page_blonde_arrives
    T: Blonde's smile falters, just for a second. He wipes blood from his lip. "Panic? I don't panic. I adapt. You want to blame me, Pink? Fine. But you're still holding that satchel."
    E:
      SET char_pink.Rat_Suspicion = NUDGE(P(char_pink.Rat_Suspicion),ADD(C(-0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_pink.Rat_Suspicion[char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white]),ADD(C(-0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Rat_Suspicion),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(0.09),MUL(P(char_pink.Rat_Suspicion),0.06))))
      SET char_white.Professional_Discipline[char_pink][char_blonde] = NUDGE(P(char_white.Professional_Discipline[char_pink][char_blonde]),ADD(C(0.07),MUL(P(char_pink.Rat_Suspicion),0.05)))
    D: ADD(MUL(P(char_pink.Rat_Suspicion[char_white]),0.65),MUL(P(char_white.Professional_Discipline[char_pink][char_blonde]),0.45),MAX(MUL(P(char_blonde.Diamond_Leverage),0.3),C(-0.15)),C(0.06))

  RXN rxn_page_pink_ambush_theory_1_1 -> page_color_aliases_and_stash
    T: Pink steps closer, voice dropping to a dangerous whisper. "You brought a cop in your trunk, Blonde. That's not panic. That's a setup. And I'm not done counting the bodies."
    E:
      SET char_pink.Rat_Suspicion = NUDGE(P(char_pink.Rat_Suspicion),ADD(C(0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_pink.Rat_Suspicion[char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white]),ADD(C(0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Rat_Suspicion),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(0.09),MUL(P(char_pink.Rat_Suspicion),0.06))))
      SET char_white.Professional_Discipline[char_pink][char_blonde] = NUDGE(P(char_white.Professional_Discipline[char_pink][char_blonde]),ADD(C(0.07),MUL(P(char_pink.Rat_Suspicion),0.05)))
    D: ADD(MUL(P(char_pink.Rat_Suspicion[char_white]),-0.5),MUL(P(char_white.Professional_Discipline[char_pink][char_blonde]),-0.35),ABSOLUTE VALUE(MUL(P(char_blonde.Professional_Discipline),0.35)),C(0.04))

  RXN rxn_page_pink_ambush_theory_1_2 -> page_blonde_arrives
    T: Blonde's eyes narrow. He reaches for his gun, but his hand trembles. "You're right. I brought a cop. But I also brought the diamonds. And I'm not giving them up. Not yet."
    E:
      SET char_pink.Rat_Suspicion = NUDGE(P(char_pink.Rat_Suspicion),ADD(C(-0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_pink.Rat_Suspicion[char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white]),ADD(C(-0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Rat_Suspicion),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(0.09),MUL(P(char_pink.Rat_Suspicion),0.06))))
      SET char_white.Professional_Discipline[char_pink][char_blonde] = NUDGE(P(char_white.Professional_Discipline[char_pink][char_blonde]),ADD(C(0.07),MUL(P(char_pink.Rat_Suspicion),0.05)))
    D: ADD(MUL(P(char_pink.Rat_Suspicion[char_white]),0.65),MUL(P(char_white.Professional_Discipline[char_pink][char_blonde]),-0.35),MUL(MUL(P(char_pink.Rat_Suspicion),0.5),MUL(P(char_white.Professional_Discipline),0.5)),C(0.02))

OPT opt_page_pink_ambush_theory_2: Where did you hide the diamond satchel, Pink?
  RXN rxn_page_pink_ambush_theory_2_0 -> page_color_aliases_and_stash
    T: Pink's hand tightens on the satchel. "You think I'd hide it where you can find it? No. It's in a place only I know. And if you want it, you're going to have to bleed for it."
    E:
      SET char_pink.Rat_Suspicion = NUDGE(P(char_pink.Rat_Suspicion),ADD(C(0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_pink.Rat_Suspicion[char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white]),ADD(C(0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Rat_Suspicion),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(-0.09),MUL(P(char_pink.Rat_Suspicion),0.06))))
      SET char_white.Professional_Discipline[char_pink][char_blonde] = NUDGE(P(char_white.Professional_Discipline[char_pink][char_blonde]),ADD(C(-0.07),MUL(P(char_pink.Rat_Suspicion),0.05)))
    D: ADD(MUL(P(char_pink.Rat_Suspicion[char_white]),0.65),MUL(P(char_white.Professional_Discipline[char_pink][char_blonde]),0.45),ABSOLUTE VALUE(MUL(P(char_blonde.Professional_Discipline),0.35)),C(0.09))

  RXN rxn_page_pink_ambush_theory_2_1 -> page_blonde_arrives
    T: Blonde laughs, a broken, painful sound. "You're hiding it? Pink, you're the one who ran. You're the one who's scared. And you're the one who's lying."
    E:
      SET char_pink.Rat_Suspicion = NUDGE(P(char_pink.Rat_Suspicion),ADD(C(-0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_pink.Rat_Suspicion[char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white]),ADD(C(-0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Rat_Suspicion),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(-0.09),MUL(P(char_pink.Rat_Suspicion),0.06))))
      SET char_white.Professional_Discipline[char_pink][char_blonde] = NUDGE(P(char_white.Professional_Discipline[char_pink][char_blonde]),ADD(C(-0.07),MUL(P(char_pink.Rat_Suspicion),0.05)))
    D: ADD(MUL(P(char_pink.Rat_Suspicion[char_white]),-0.5),MUL(P(char_white.Professional_Discipline[char_pink][char_blonde]),-0.35),MUL(MUL(P(char_pink.Rat_Suspicion),0.5),MUL(P(char_white.Professional_Discipline),0.5)),C(0.07))

  RXN rxn_page_pink_ambush_theory_2_2 -> page_color_aliases_and_stash
    T: Pink's eyes flick to Orange. "You're bleeding, Freddy. You're dying. And you're still here. That means you're not a cop. That means you're one of us. And I need you to tell me where the satchel is."
    E:
      SET char_pink.Rat_Suspicion = NUDGE(P(char_pink.Rat_Suspicion),ADD(C(0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_pink.Rat_Suspicion[char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white]),ADD(C(0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Rat_Suspicion),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(-0.09),MUL(P(char_pink.Rat_Suspicion),0.06))))
      SET char_white.Professional_Discipline[char_pink][char_blonde] = NUDGE(P(char_white.Professional_Discipline[char_pink][char_blonde]),ADD(C(-0.07),MUL(P(char_pink.Rat_Suspicion),0.05)))
    D: ADD(MUL(P(char_pink.Rat_Suspicion[char_white]),0.65),MUL(P(char_white.Professional_Discipline[char_pink][char_blonde]),-0.35),MAX(MUL(P(char_blonde.Diamond_Leverage),0.3),C(-0.15)),C(0.05))


## ENC page_color_aliases_and_stash | Blood, Smoke, and the Satchel | turn=2..4 | spools=[spool_act1_safehouse]
T: Cigarette smoke curls over the bathroom sink. Mr. Orange moans from the wooden ramp, blood pooling beneath his gut. Mr. Pink stares at the floor, calculating. "Stones are stashed. Minutes away. If we move, we die. If we stay, we bleed out." Mr. White grips a pistol, eyes locked on the door. "Who knew the vault schedule?" The shuttered mortuary smells of cordite and stale coffee. Every breath tastes of betrayal. The crew weighs discipline against the certainty that an LAPD plant sold them out.

OPT opt_page_color_aliases_and_stash_0: Hold the safehouse until Joe Cabot and Nice Guy Eddie call.
  RXN rxn_page_color_aliases_and_stash_0_0 -> page_blonde_arrives
    T: Mr. Blonde’s grin tightens as he hears the engine outside. He checks his gun, eyes flicking to the door. "They’re here. Let’s see if the cops brought friends or just more blood."
    E:
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(-0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_orange.Crew_Loyalty[char_pink][char_white] = NUDGE(P(char_orange.Crew_Loyalty[char_pink][char_white]),ADD(C(-0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_pink.Diamond_Leverage[char_orange] = NUDGE(P(char_pink.Diamond_Leverage[char_orange]),ADD(C(0.08),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_orange]),0.65),MUL(P(char_orange.Crew_Loyalty[char_pink][char_white]),0.45),MAX(MUL(P(char_white.Diamond_Leverage),0.3),C(-0.15)),C(0.03))

  RXN rxn_page_color_aliases_and_stash_0_1 -> page_cadillac_trunk
    T: Mr. Pink’s jaw clenches. He glances at the Cadillac trunk, knowing what’s inside. "If they’re in that trunk, we’re done. I’m not dying for a cop’s mistake."
    E:
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(-0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_orange.Crew_Loyalty[char_pink][char_white] = NUDGE(P(char_orange.Crew_Loyalty[char_pink][char_white]),ADD(C(-0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(-0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_pink.Diamond_Leverage[char_orange] = NUDGE(P(char_pink.Diamond_Leverage[char_orange]),ADD(C(-0.08),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_orange]),-0.5),MUL(P(char_orange.Crew_Loyalty[char_pink][char_white]),-0.35),ABSOLUTE VALUE(MUL(P(char_white.Crew_Loyalty),0.35)),C(0.01))

  RXN rxn_page_color_aliases_and_stash_0_2 -> page_blonde_arrives
    T: Mr. White’s hand trembles slightly. He looks at Orange, then at the door. "If they’re here, we’re not alone. We need to move now, before the whole crew turns on us."
    E:
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(-0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_orange.Crew_Loyalty[char_pink][char_white] = NUDGE(P(char_orange.Crew_Loyalty[char_pink][char_white]),ADD(C(-0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_pink.Diamond_Leverage[char_orange] = NUDGE(P(char_pink.Diamond_Leverage[char_orange]),ADD(C(0.08),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_orange]),0.65),MUL(P(char_orange.Crew_Loyalty[char_pink][char_white]),-0.35),MUL(MUL(P(char_pink.Diamond_Leverage),0.5),MUL(P(char_orange.Crew_Loyalty),0.5)),C(-0.01))

OPT opt_page_color_aliases_and_stash_1: Offer Pink control of the satchel in exchange for a doctor.
  RXN rxn_page_color_aliases_and_stash_1_0 -> page_cadillac_trunk
    T: Mr. Pink’s eyes narrow. He steps closer to the satchel, fingers brushing the leather. "A doctor? You think I’m buying a doctor with my diamonds? I’m buying survival."
    E:
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_orange.Crew_Loyalty[char_pink][char_white] = NUDGE(P(char_orange.Crew_Loyalty[char_pink][char_white]),ADD(C(0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(-0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_pink.Diamond_Leverage[char_orange] = NUDGE(P(char_pink.Diamond_Leverage[char_orange]),ADD(C(-0.08),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_orange]),0.65),MUL(P(char_orange.Crew_Loyalty[char_pink][char_white]),0.45),ABSOLUTE VALUE(MUL(P(char_white.Crew_Loyalty),0.35)),C(0.06))

  RXN rxn_page_color_aliases_and_stash_1_1 -> page_blonde_arrives
    T: Mr. Blonde laughs, a low, dangerous sound. "A doctor? You’re offering a cop a doctor? That’s not a deal, that’s a suicide note."
    E:
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_orange.Crew_Loyalty[char_pink][char_white] = NUDGE(P(char_orange.Crew_Loyalty[char_pink][char_white]),ADD(C(0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_pink.Diamond_Leverage[char_orange] = NUDGE(P(char_pink.Diamond_Leverage[char_orange]),ADD(C(0.08),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_orange]),-0.5),MUL(P(char_orange.Crew_Loyalty[char_pink][char_white]),-0.35),MUL(MUL(P(char_pink.Diamond_Leverage),0.5),MUL(P(char_orange.Crew_Loyalty),0.5)),C(0.04))

  RXN rxn_page_color_aliases_and_stash_1_2 -> page_cadillac_trunk
    T: Mr. White’s voice is steady, but his eyes are cold. "If you want the satchel, you want the doctor. No exceptions. No sentiment."
    E:
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_orange.Crew_Loyalty[char_pink][char_white] = NUDGE(P(char_orange.Crew_Loyalty[char_pink][char_white]),ADD(C(0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(-0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_pink.Diamond_Leverage[char_orange] = NUDGE(P(char_pink.Diamond_Leverage[char_orange]),ADD(C(-0.08),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_orange]),0.65),MUL(P(char_orange.Crew_Loyalty[char_pink][char_white]),-0.35),MAX(MUL(P(char_white.Diamond_Leverage),0.3),C(-0.15)),C(0.02))

OPT opt_page_color_aliases_and_stash_2: Cross-check who knew the Karina vault schedule in advance.
  RXN rxn_page_color_aliases_and_stash_2_0 -> page_blonde_arrives
    T: Mr. Blonde’s smile fades. He looks at Pink, then at White. "You’re saying one of us is a rat? That’s not a question, that’s an accusation."
    E:
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(-0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_orange.Crew_Loyalty[char_pink][char_white] = NUDGE(P(char_orange.Crew_Loyalty[char_pink][char_white]),ADD(C(-0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_pink.Diamond_Leverage[char_orange] = NUDGE(P(char_pink.Diamond_Leverage[char_orange]),ADD(C(0.08),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_orange]),0.65),MUL(P(char_orange.Crew_Loyalty[char_pink][char_white]),0.45),MUL(MUL(P(char_pink.Diamond_Leverage),0.5),MUL(P(char_orange.Crew_Loyalty),0.5)),C(0.09))

  RXN rxn_page_color_aliases_and_stash_2_1 -> page_cadillac_trunk
    T: Mr. Pink’s voice is flat, but his eyes are sharp. "I’m saying the vault schedule was known. Someone leaked it. And I’m not the one who did it."
    E:
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(-0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_orange.Crew_Loyalty[char_pink][char_white] = NUDGE(P(char_orange.Crew_Loyalty[char_pink][char_white]),ADD(C(-0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(-0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_pink.Diamond_Leverage[char_orange] = NUDGE(P(char_pink.Diamond_Leverage[char_orange]),ADD(C(-0.08),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_orange]),-0.5),MUL(P(char_orange.Crew_Loyalty[char_pink][char_white]),-0.35),MAX(MUL(P(char_white.Diamond_Leverage),0.3),C(-0.15)),C(0.07))

  RXN rxn_page_color_aliases_and_stash_2_2 -> page_blonde_arrives
    T: Mr. White’s hand tightens on his gun. He looks at Orange, then at the door. "If we don’t find the rat, we’re all dead. And I’m not dying for a cop’s mistake."
    E:
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(-0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_orange.Crew_Loyalty[char_pink][char_white] = NUDGE(P(char_orange.Crew_Loyalty[char_pink][char_white]),ADD(C(-0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_pink.Diamond_Leverage[char_orange] = NUDGE(P(char_pink.Diamond_Leverage[char_orange]),ADD(C(0.08),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_orange]),0.65),MUL(P(char_orange.Crew_Loyalty[char_pink][char_white]),-0.35),ABSOLUTE VALUE(MUL(P(char_white.Crew_Loyalty),0.35)),C(0.05))


## ENC page_blonde_arrives | Soda, Iron, and the Beam | turn=3..5 | spools=[spool_act1_safehouse]
T: Mr. Blonde leans against the support beam, slurping a striped drive-thru cup. Mr. White and Mr. Pink shout over Mr. Brown's cracked skull and dead Mr. Blue. White lunges at him for slaughtering civilians. Blonde's hand drifts toward his shoulder holster. Every breath inside the shuttered mortuary smells of cordite, stale coffee, and drying arterial blood, forcing each survivor to weigh professional discipline against the creeping certainty that an LAPD plant sold out the crew.

OPT opt_page_blonde_arrives_0: Step between White and Blonde with cold syndicate discipline.
  RXN rxn_page_blonde_arrives_0_0 -> page_cadillac_trunk
    T: Blonde's smile tightens, his thumb resting on the holster. White's eyes narrow, reading the shift in leverage. The tension snaps taut, pushing the group toward the Cadillac trunk.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_blonde.Sadistic_Escalation[char_white] = NUDGE(P(char_blonde.Sadistic_Escalation[char_white]),ADD(C(0.08),MUL(P(char_pink.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_white.Professional_Discipline[char_blonde][char_pink] = NUDGE(P(char_white.Professional_Discipline[char_blonde][char_pink]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_white]),0.65),MUL(P(char_white.Professional_Discipline[char_blonde][char_pink]),0.45),ABSOLUTE VALUE(MUL(P(char_pink.Professional_Discipline),0.35)),C(0.03))

  RXN rxn_page_blonde_arrives_0_1 -> page_chair_duct_tape
    T: Blonde's eyes flick to the chair, calculating the next move. White's hand hovers near his weapon. The standoff shifts, forcing a pivot toward the chair and duct tape.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_blonde.Sadistic_Escalation[char_white] = NUDGE(P(char_blonde.Sadistic_Escalation[char_white]),ADD(C(-0.08),MUL(P(char_pink.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_white.Professional_Discipline[char_blonde][char_pink] = NUDGE(P(char_white.Professional_Discipline[char_blonde][char_pink]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_white]),-0.5),MUL(P(char_white.Professional_Discipline[char_blonde][char_pink]),-0.35),MUL(MUL(P(char_blonde.Sadistic_Escalation),0.5),MUL(P(char_white.Professional_Discipline),0.5)),C(0.01))

  RXN rxn_page_blonde_arrives_0_2 -> page_cadillac_trunk
    T: Blonde's grip on the cup tightens, a subtle threat. White's discipline holds, but the air thickens. The group's focus shifts back to the Cadillac trunk, a looming consequence.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_blonde.Sadistic_Escalation[char_white] = NUDGE(P(char_blonde.Sadistic_Escalation[char_white]),ADD(C(0.08),MUL(P(char_pink.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_white.Professional_Discipline[char_blonde][char_pink] = NUDGE(P(char_white.Professional_Discipline[char_blonde][char_pink]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_white]),0.65),MUL(P(char_white.Professional_Discipline[char_blonde][char_pink]),-0.35),MAX(MUL(P(char_pink.Diamond_Leverage),0.3),C(-0.15)),C(-0.01))

OPT opt_page_blonde_arrives_1: Pin Blonde against the pillar and strip his backup piece.
  RXN rxn_page_blonde_arrives_1_0 -> page_chair_duct_tape
    T: Blonde's eyes flash with cold fury. White's hand moves to the chair, a tactical pivot. The leverage shifts, forcing a move toward the chair and duct tape.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_blonde.Sadistic_Escalation[char_white] = NUDGE(P(char_blonde.Sadistic_Escalation[char_white]),ADD(C(-0.08),MUL(P(char_pink.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_white.Professional_Discipline[char_blonde][char_pink] = NUDGE(P(char_white.Professional_Discipline[char_blonde][char_pink]),ADD(C(0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_white]),0.65),MUL(P(char_white.Professional_Discipline[char_blonde][char_pink]),0.45),MUL(MUL(P(char_blonde.Sadistic_Escalation),0.5),MUL(P(char_white.Professional_Discipline),0.5)),C(0.06))

  RXN rxn_page_blonde_arrives_1_1 -> page_cadillac_trunk
    T: Blonde's hand twitches, a silent warning. White's grip tightens on the pillar. The tension escalates, pushing the group toward the Cadillac trunk.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_blonde.Sadistic_Escalation[char_white] = NUDGE(P(char_blonde.Sadistic_Escalation[char_white]),ADD(C(0.08),MUL(P(char_pink.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_white.Professional_Discipline[char_blonde][char_pink] = NUDGE(P(char_white.Professional_Discipline[char_blonde][char_pink]),ADD(C(0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_white]),-0.5),MUL(P(char_white.Professional_Discipline[char_blonde][char_pink]),-0.35),MAX(MUL(P(char_pink.Diamond_Leverage),0.3),C(-0.15)),C(0.04))

  RXN rxn_page_blonde_arrives_1_2 -> page_chair_duct_tape
    T: Blonde's smile vanishes, replaced by a cold stare. White's eyes narrow, reading the shift. The standoff resolves toward the chair and duct tape.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_blonde.Sadistic_Escalation[char_white] = NUDGE(P(char_blonde.Sadistic_Escalation[char_white]),ADD(C(-0.08),MUL(P(char_pink.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_white.Professional_Discipline[char_blonde][char_pink] = NUDGE(P(char_white.Professional_Discipline[char_blonde][char_pink]),ADD(C(0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_white]),0.65),MUL(P(char_white.Professional_Discipline[char_blonde][char_pink]),-0.35),ABSOLUTE VALUE(MUL(P(char_pink.Professional_Discipline),0.35)),C(0.02))

OPT opt_page_blonde_arrives_2: Watch Orange's eyes while Blonde recounts the alarm trip.
  RXN rxn_page_blonde_arrives_2_0 -> page_cadillac_trunk
    T: Blonde's voice drops, a low, precise recount. White's eyes track Orange's reaction. The tension shifts, pushing the group toward the Cadillac trunk.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_blonde.Sadistic_Escalation[char_white] = NUDGE(P(char_blonde.Sadistic_Escalation[char_white]),ADD(C(0.08),MUL(P(char_pink.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_white.Professional_Discipline[char_blonde][char_pink] = NUDGE(P(char_white.Professional_Discipline[char_blonde][char_pink]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_white]),0.65),MUL(P(char_white.Professional_Discipline[char_blonde][char_pink]),0.45),MAX(MUL(P(char_pink.Diamond_Leverage),0.3),C(-0.15)),C(0.09))

  RXN rxn_page_blonde_arrives_2_1 -> page_chair_duct_tape
    T: Blonde's eyes flick to the chair, a subtle threat. White's hand hovers near his weapon. The standoff shifts, forcing a pivot toward the chair and duct tape.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_blonde.Sadistic_Escalation[char_white] = NUDGE(P(char_blonde.Sadistic_Escalation[char_white]),ADD(C(-0.08),MUL(P(char_pink.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_white.Professional_Discipline[char_blonde][char_pink] = NUDGE(P(char_white.Professional_Discipline[char_blonde][char_pink]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_white]),-0.5),MUL(P(char_white.Professional_Discipline[char_blonde][char_pink]),-0.35),ABSOLUTE VALUE(MUL(P(char_pink.Professional_Discipline),0.35)),C(0.07))

  RXN rxn_page_blonde_arrives_2_2 -> page_cadillac_trunk
    T: Blonde's grip on the cup tightens, a silent threat. White's discipline holds, but the air thickens. The group's focus shifts back to the Cadillac trunk.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_white.Professional_Discipline),0.08)))
      SET char_blonde.Sadistic_Escalation[char_white] = NUDGE(P(char_blonde.Sadistic_Escalation[char_white]),ADD(C(0.08),MUL(P(char_pink.Professional_Discipline),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
      SET char_white.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_white.Professional_Discipline),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_white.Professional_Discipline[char_blonde][char_pink] = NUDGE(P(char_white.Professional_Discipline[char_blonde][char_pink]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_white]),0.65),MUL(P(char_white.Professional_Discipline[char_blonde][char_pink]),-0.35),MUL(MUL(P(char_blonde.Sadistic_Escalation),0.5),MUL(P(char_white.Professional_Discipline),0.5)),C(0.05))


## ENC page_cadillac_trunk | Trunk of the Coupe | turn=4..6 | spools=[spool_act1_safehouse]
T: Blonde pops the Cadillac trunk. Marvin Nash blinks up from the spare-tire well, duct tape sealing his mouth. Sirens wail in the alley. White steps forward, face grim. "Drag him inside. Demand answers." Pink stares at the cop's badge. "You brought a beacon to our safehouse, you idiot." Blonde smiles, blood on his teeth. "Maybe the beacon's already ringing, Pink."

OPT opt_page_cadillac_trunk_0: Drag the cop inside, White, and demand answers about the patrol
  RXN rxn_page_cadillac_trunk_0_0 -> page_chair_duct_tape
    T: White yanks Nash by the collar, dragging him into the mortuary's shadow. Pink watches, calculating the risk. The cop's eyes dart, seeking an escape route. White's voice drops to a lethal whisper, "Talk, or I make you talk."
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_blonde.Sadistic_Escalation[char_pink] = NUDGE(P(char_blonde.Sadistic_Escalation[char_pink]),ADD(C(0.08),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_pink.Rat_Suspicion[char_blonde][char_orange] = NUDGE(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_pink]),0.65),MUL(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),0.45),MUL(MUL(P(char_blonde.Sadistic_Escalation),0.5),MUL(P(char_pink.Rat_Suspicion),0.5)),C(0.03))

  RXN rxn_page_cadillac_trunk_0_1 -> page_eddie_call_and_alibi
    T: Nash struggles, his cuffs clinking. Pink steps back, hand near his gun. "You're making a mistake, White. He's a cop. He's a beacon." White ignores him, focusing on Nash's face, searching for the truth behind the uniform.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_blonde.Sadistic_Escalation[char_pink] = NUDGE(P(char_blonde.Sadistic_Escalation[char_pink]),ADD(C(-0.08),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_pink.Rat_Suspicion[char_blonde][char_orange] = NUDGE(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_pink]),-0.5),MUL(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),-0.35),MAX(MUL(P(char_orange.Diamond_Leverage),0.3),C(-0.15)),C(0.01))

  RXN rxn_page_cadillac_trunk_0_2 -> page_chair_duct_tape
    T: Blonde leans against the Cadillac, grinning. "See? He's alive. He's a cop. He's a beacon. And we're all screwed." White's jaw tightens. He drags Nash deeper into the shadows, away from the sirens.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_blonde.Sadistic_Escalation[char_pink] = NUDGE(P(char_blonde.Sadistic_Escalation[char_pink]),ADD(C(0.08),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_pink.Rat_Suspicion[char_blonde][char_orange] = NUDGE(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_pink]),0.65),MUL(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),-0.35),ABSOLUTE VALUE(MUL(P(char_orange.Rat_Suspicion),0.35)),C(-0.01))

OPT opt_page_cadillac_trunk_1: Blonde, you brought a live cop beacon to our safehouse, you idiot
  RXN rxn_page_cadillac_trunk_1_0 -> page_eddie_call_and_alibi
    T: Blonde's smile falters. "Beacon? I brought a cop, Pink. He's a cop. He's a beacon. He's a cop." Pink's eyes narrow. "You're a cop, Blonde. You're a beacon. You're a cop."
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_blonde.Sadistic_Escalation[char_pink] = NUDGE(P(char_blonde.Sadistic_Escalation[char_pink]),ADD(C(-0.08),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_pink.Rat_Suspicion[char_blonde][char_orange] = NUDGE(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),ADD(C(0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_pink]),0.65),MUL(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),0.45),MAX(MUL(P(char_orange.Diamond_Leverage),0.3),C(-0.15)),C(0.06))

  RXN rxn_page_cadillac_trunk_1_1 -> page_chair_duct_tape
    T: White steps between Pink and Blonde. "Stop it. Both of you. We need answers, not accusations." Nash's eyes widen. He sees the tension. He sees the danger. He sees the end.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_blonde.Sadistic_Escalation[char_pink] = NUDGE(P(char_blonde.Sadistic_Escalation[char_pink]),ADD(C(0.08),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_pink.Rat_Suspicion[char_blonde][char_orange] = NUDGE(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),ADD(C(0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_pink]),-0.5),MUL(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),-0.35),ABSOLUTE VALUE(MUL(P(char_orange.Rat_Suspicion),0.35)),C(0.04))

  RXN rxn_page_cadillac_trunk_1_2 -> page_eddie_call_and_alibi
    T: Pink pulls out his phone. "I'm calling Eddie. I'm calling Eddie. I'm calling Eddie." Blonde's smile returns. "Eddie's a cop. Eddie's a beacon. Eddie's a cop." White's hand tightens on his gun.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_blonde.Sadistic_Escalation[char_pink] = NUDGE(P(char_blonde.Sadistic_Escalation[char_pink]),ADD(C(-0.08),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_pink.Rat_Suspicion[char_blonde][char_orange] = NUDGE(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),ADD(C(0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_pink]),0.65),MUL(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),-0.35),MUL(MUL(P(char_blonde.Sadistic_Escalation),0.5),MUL(P(char_pink.Rat_Suspicion),0.5)),C(0.02))

OPT opt_page_cadillac_trunk_2: Check Nash's service radio frequency before touching the tape, Pink
  RXN rxn_page_cadillac_trunk_2_0 -> page_chair_duct_tape
    T: Pink kneels, examining Nash's radio. "Frequency 15.1. That's the patrol channel. He's broadcasting. He's a beacon. He's a cop." White's face hardens. "Then we silence him. Now."
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_blonde.Sadistic_Escalation[char_pink] = NUDGE(P(char_blonde.Sadistic_Escalation[char_pink]),ADD(C(0.08),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_pink.Rat_Suspicion[char_blonde][char_orange] = NUDGE(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_pink]),0.65),MUL(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),0.45),ABSOLUTE VALUE(MUL(P(char_orange.Rat_Suspicion),0.35)),C(0.09))

  RXN rxn_page_cadillac_trunk_2_1 -> page_eddie_call_and_alibi
    T: Blonde laughs. "Silence him? He's a cop. He's a beacon. He's a cop." Pink stands, radio in hand. "I'm calling Eddie. I'm calling Eddie. I'm calling Eddie." White's hand tightens on his gun.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_blonde.Sadistic_Escalation[char_pink] = NUDGE(P(char_blonde.Sadistic_Escalation[char_pink]),ADD(C(-0.08),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_pink.Rat_Suspicion[char_blonde][char_orange] = NUDGE(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_pink]),-0.5),MUL(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),-0.35),MUL(MUL(P(char_blonde.Sadistic_Escalation),0.5),MUL(P(char_pink.Rat_Suspicion),0.5)),C(0.07))

  RXN rxn_page_cadillac_trunk_2_2 -> page_chair_duct_tape
    T: Nash's eyes dart. He sees the radio. He sees the danger. He sees the end. White steps forward. "Talk, or I make you talk." Nash's lips move, but no sound comes out. The sirens grow louder.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_blonde.Sadistic_Escalation[char_pink] = NUDGE(P(char_blonde.Sadistic_Escalation[char_pink]),ADD(C(0.08),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_pink.Rat_Suspicion[char_blonde][char_orange] = NUDGE(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_pink]),0.65),MUL(P(char_pink.Rat_Suspicion[char_blonde][char_orange]),-0.35),MAX(MUL(P(char_orange.Diamond_Leverage),0.3),C(-0.15)),C(0.05))


## ENC page_chair_duct_tape | Taped to the Mortuary Chair | turn=5..7 | spools=[spool_act2_interrogation]
T: Duct tape bites into Marvin Nash's wrists. Mr. Orange bleeds silently on the warehouse floor, his eyes fixed on the ceiling. Mr. Pink leans close, voice clipped. "Who called the stakeout?" Mr. Blonde grins, cracking his knuckles. "I want to hear him scream first." Mr. White watches the blood pool, calculating the odds. The air smells of cordite and stale coffee. Every second stretches. Pink wants methodical answers. Blonde wants pain. Orange wants to die. The warehouse holds its breath, waiting for the next move.

OPT opt_page_chair_duct_tape_0: Ask Nash about precinct stakeout orders and possible moles
  RXN rxn_page_chair_duct_tape_0_0 -> page_eddie_call_and_alibi
    T: Nash's jaw tightens, a bead of sweat tracing his temple. He glances at Pink, then away, his voice trembling. "You don't know what you're dealing with, Pink. The stakeout was clean. Someone inside the precinct fed you the diamonds. I'm just the messenger."
    E:
      SET char_pink.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Sadistic_Escalation),C(-0.09),MUL(P(char_white.Rat_Suspicion),0.06))))
      SET char_pink.Sadistic_Escalation[char_white][char_blonde] = NUDGE(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),ADD(C(-0.07),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Rat_Suspicion),0.02)))
      SET char_white.Rat_Suspicion = NUDGE(P(char_white.Rat_Suspicion),ADD(C(0.11),MUL(P(char_pink.Sadistic_Escalation),0.08)))
      SET char_white.Rat_Suspicion[char_pink] = NUDGE(P(char_white.Rat_Suspicion[char_pink]),ADD(C(0.08),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_white.Rat_Suspicion[char_pink]),0.65),MUL(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),0.45),MAX(MUL(P(char_blonde.Diamond_Leverage),0.3),C(-0.15)),C(0.03))

  RXN rxn_page_chair_duct_tape_0_1 -> page_k_billy_razor
    T: Blonde snorts, stepping closer to Nash. "Clean? You're bleeding out, cop. And your boss just called the cops. Pink, let me have him. I'll get the truth out of him before he drops. Pink, you're just watching."
    E:
      SET char_pink.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Sadistic_Escalation),C(-0.09),MUL(P(char_white.Rat_Suspicion),0.06))))
      SET char_pink.Sadistic_Escalation[char_white][char_blonde] = NUDGE(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),ADD(C(-0.07),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Rat_Suspicion),0.02)))
      SET char_white.Rat_Suspicion = NUDGE(P(char_white.Rat_Suspicion),ADD(C(-0.11),MUL(P(char_pink.Sadistic_Escalation),0.08)))
      SET char_white.Rat_Suspicion[char_pink] = NUDGE(P(char_white.Rat_Suspicion[char_pink]),ADD(C(-0.08),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_white.Rat_Suspicion[char_pink]),-0.5),MUL(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),-0.35),ABSOLUTE VALUE(MUL(P(char_blonde.Sadistic_Escalation),0.35)),C(0.01))

  RXN rxn_page_chair_duct_tape_0_2 -> page_eddie_call_and_alibi
    T: White's eyes narrow, his hand drifting toward his hip. He watches Nash's micro-expressions, the slight flinch when Pink mentions the diamonds. "You're lying, Nash. The stakeout wasn't clean. Someone in this room sold us out. Pink, you know it."
    E:
      SET char_pink.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Sadistic_Escalation),C(-0.09),MUL(P(char_white.Rat_Suspicion),0.06))))
      SET char_pink.Sadistic_Escalation[char_white][char_blonde] = NUDGE(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),ADD(C(-0.07),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Rat_Suspicion),0.02)))
      SET char_white.Rat_Suspicion = NUDGE(P(char_white.Rat_Suspicion),ADD(C(0.11),MUL(P(char_pink.Sadistic_Escalation),0.08)))
      SET char_white.Rat_Suspicion[char_pink] = NUDGE(P(char_white.Rat_Suspicion[char_pink]),ADD(C(0.08),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_white.Rat_Suspicion[char_pink]),0.65),MUL(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),-0.35),MUL(MUL(P(char_white.Rat_Suspicion),0.5),MUL(P(char_pink.Sadistic_Escalation),0.5)),C(-0.01))

OPT opt_page_chair_duct_tape_1: Let Blonde rough Nash up while Pink watches for tells
  RXN rxn_page_chair_duct_tape_1_0 -> page_k_billy_razor
    T: Blonde grabs Nash's collar, yanking him forward. "Talk, cop. Who called?" Nash's eyes widen, his breath hitching. Pink watches, his face unreadable, but his fingers drum against his thigh. "He's stalling. Blonde, keep him talking. I need to know if the mole is still in the precinct."
    E:
      SET char_pink.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Sadistic_Escalation),C(0.09),MUL(P(char_white.Rat_Suspicion),0.06))))
      SET char_pink.Sadistic_Escalation[char_white][char_blonde] = NUDGE(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),ADD(C(0.07),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Rat_Suspicion),0.02)))
      SET char_white.Rat_Suspicion = NUDGE(P(char_white.Rat_Suspicion),ADD(C(-0.11),MUL(P(char_pink.Sadistic_Escalation),0.08)))
      SET char_white.Rat_Suspicion[char_pink] = NUDGE(P(char_white.Rat_Suspicion[char_pink]),ADD(C(-0.08),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_white.Rat_Suspicion[char_pink]),0.65),MUL(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),0.45),ABSOLUTE VALUE(MUL(P(char_blonde.Sadistic_Escalation),0.35)),C(0.06))

  RXN rxn_page_chair_duct_tape_1_1 -> page_eddie_call_and_alibi
    T: Nash's head snaps back, a wet cough escaping his lips. "Please, I'm not the one who called. I'm just a patrolman. The stakeout was set by someone else. Pink, you're wrong. The mole is in this room."
    E:
      SET char_pink.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Sadistic_Escalation),C(0.09),MUL(P(char_white.Rat_Suspicion),0.06))))
      SET char_pink.Sadistic_Escalation[char_white][char_blonde] = NUDGE(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),ADD(C(0.07),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Rat_Suspicion),0.02)))
      SET char_white.Rat_Suspicion = NUDGE(P(char_white.Rat_Suspicion),ADD(C(0.11),MUL(P(char_pink.Sadistic_Escalation),0.08)))
      SET char_white.Rat_Suspicion[char_pink] = NUDGE(P(char_white.Rat_Suspicion[char_pink]),ADD(C(0.08),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_white.Rat_Suspicion[char_pink]),-0.5),MUL(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),-0.35),MUL(MUL(P(char_white.Rat_Suspicion),0.5),MUL(P(char_pink.Sadistic_Escalation),0.5)),C(0.04))

  RXN rxn_page_chair_duct_tape_1_2 -> page_k_billy_razor
    T: Blonde releases Nash, stepping back with a satisfied grin. "He's got something to say. Pink, you're right. The mole is in this room. And I'm going to find out who. White, you're next."
    E:
      SET char_pink.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Sadistic_Escalation),C(0.09),MUL(P(char_white.Rat_Suspicion),0.06))))
      SET char_pink.Sadistic_Escalation[char_white][char_blonde] = NUDGE(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),ADD(C(0.07),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Rat_Suspicion),0.02)))
      SET char_white.Rat_Suspicion = NUDGE(P(char_white.Rat_Suspicion),ADD(C(-0.11),MUL(P(char_pink.Sadistic_Escalation),0.08)))
      SET char_white.Rat_Suspicion[char_pink] = NUDGE(P(char_white.Rat_Suspicion[char_pink]),ADD(C(-0.08),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_white.Rat_Suspicion[char_pink]),0.65),MUL(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),-0.35),MAX(MUL(P(char_blonde.Diamond_Leverage),0.3),C(-0.15)),C(0.02))

OPT opt_page_chair_duct_tape_2: Pull Pink aside to compare Orange's commode story cadence
  RXN rxn_page_chair_duct_tape_2_0 -> page_eddie_call_and_alibi
    T: White steps between Pink and the chair, his voice low. "Pink, come here. We need to talk. Orange's story about the commode, the way he described it, it's off. Too detailed. Too rehearsed. He's lying."
    E:
      SET char_pink.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Sadistic_Escalation),C(-0.09),MUL(P(char_white.Rat_Suspicion),0.06))))
      SET char_pink.Sadistic_Escalation[char_white][char_blonde] = NUDGE(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),ADD(C(-0.07),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Rat_Suspicion),0.02)))
      SET char_white.Rat_Suspicion = NUDGE(P(char_white.Rat_Suspicion),ADD(C(0.11),MUL(P(char_pink.Sadistic_Escalation),0.08)))
      SET char_white.Rat_Suspicion[char_pink] = NUDGE(P(char_white.Rat_Suspicion[char_pink]),ADD(C(0.08),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_white.Rat_Suspicion[char_pink]),0.65),MUL(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),0.45),MUL(MUL(P(char_white.Rat_Suspicion),0.5),MUL(P(char_pink.Sadistic_Escalation),0.5)),C(0.09))

  RXN rxn_page_chair_duct_tape_2_1 -> page_k_billy_razor
    T: Pink follows White, his eyes narrowing. "You think Orange is the mole? He's bleeding out, White. He's not going anywhere. And his story? It's consistent. He's not lying."
    E:
      SET char_pink.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Sadistic_Escalation),C(-0.09),MUL(P(char_white.Rat_Suspicion),0.06))))
      SET char_pink.Sadistic_Escalation[char_white][char_blonde] = NUDGE(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),ADD(C(-0.07),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Rat_Suspicion),0.02)))
      SET char_white.Rat_Suspicion = NUDGE(P(char_white.Rat_Suspicion),ADD(C(-0.11),MUL(P(char_pink.Sadistic_Escalation),0.08)))
      SET char_white.Rat_Suspicion[char_pink] = NUDGE(P(char_white.Rat_Suspicion[char_pink]),ADD(C(-0.08),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_white.Rat_Suspicion[char_pink]),-0.5),MUL(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),-0.35),MAX(MUL(P(char_blonde.Diamond_Leverage),0.3),C(-0.15)),C(0.07))

  RXN rxn_page_chair_duct_tape_2_2 -> page_eddie_call_and_alibi
    T: White's jaw tightens. "Consistent? That's what a mole would do. Pink, you're too close to this. You're not seeing it. Orange's story is a setup. He's feeding us false information."
    E:
      SET char_pink.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Sadistic_Escalation),C(-0.09),MUL(P(char_white.Rat_Suspicion),0.06))))
      SET char_pink.Sadistic_Escalation[char_white][char_blonde] = NUDGE(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),ADD(C(-0.07),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Rat_Suspicion),0.02)))
      SET char_white.Rat_Suspicion = NUDGE(P(char_white.Rat_Suspicion),ADD(C(0.11),MUL(P(char_pink.Sadistic_Escalation),0.08)))
      SET char_white.Rat_Suspicion[char_pink] = NUDGE(P(char_white.Rat_Suspicion[char_pink]),ADD(C(0.08),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
    D: ADD(MUL(P(char_white.Rat_Suspicion[char_pink]),0.65),MUL(P(char_pink.Sadistic_Escalation[char_white][char_blonde]),-0.35),ABSOLUTE VALUE(MUL(P(char_blonde.Sadistic_Escalation),0.35)),C(0.05))


## ENC page_eddie_call_and_alibi | Eddie's Line, Nash's Trunk | turn=6..8 | spools=[spool_act2_interrogation]
T: The phone buzzes on the blood-slicked floor. Eddie's voice cuts through the cordite haze. "Where's the satchel?" Pink wipes his hands. "In the trunk. You want it?" Orange coughs, a wet rattle. "He's not coming back." White grips the receiver. "Eddie, listen. The diamonds are gone. We're done." The line clicks dead. Pink stares at the dead phone. "He's not coming back," Orange repeats, his eyes rolling. "He's not coming back," White whispers, the words tasting like ash.

OPT opt_page_eddie_call_and_alibi_0: Grab Pink, secure diamonds, and warn Blonde to stop torturing
  RXN rxn_page_eddie_call_and_alibi_0_0 -> page_k_billy_razor
    T: Pink snarls, grabbing the satchel. "You're dead, White. I'm taking the diamonds and the car. You can stay with the rat." His eyes lock on Orange, who slumps, blood pooling. The leverage shifts to Pink's escape, leaving White and Orange to face the consequences of the betrayal.
    E:
      SET char_blonde.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Rat_Suspicion),C(-0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_blonde.Rat_Suspicion[char_pink][char_white] = NUDGE(P(char_blonde.Rat_Suspicion[char_pink][char_white]),ADD(C(-0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(0.11),MUL(P(char_blonde.Rat_Suspicion),0.08)))
      SET char_pink.Diamond_Leverage[char_blonde] = NUDGE(P(char_pink.Diamond_Leverage[char_blonde]),ADD(C(0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_blonde]),0.65),MUL(P(char_blonde.Rat_Suspicion[char_pink][char_white]),0.45),ABSOLUTE VALUE(MUL(P(char_white.Rat_Suspicion),0.35)),C(0.03))

  RXN rxn_page_eddie_call_and_alibi_0_1 -> page_orange_gun_on_the_ramp
    T: Orange's eyes snap open, blood dripping from his lip. "He's not coming back," he rasps, his hand twitching toward the gun. White freezes, the weight of the receiver heavy. The tension spikes, Orange's pain sharpening his focus, and the threat of his gun becomes the immediate consequence, forcing a standoff.
    E:
      SET char_blonde.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Rat_Suspicion),C(-0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_blonde.Rat_Suspicion[char_pink][char_white] = NUDGE(P(char_blonde.Rat_Suspicion[char_pink][char_white]),ADD(C(-0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(-0.11),MUL(P(char_blonde.Rat_Suspicion),0.08)))
      SET char_pink.Diamond_Leverage[char_blonde] = NUDGE(P(char_pink.Diamond_Leverage[char_blonde]),ADD(C(-0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_blonde]),-0.5),MUL(P(char_blonde.Rat_Suspicion[char_pink][char_white]),-0.35),MUL(MUL(P(char_pink.Diamond_Leverage),0.5),MUL(P(char_blonde.Rat_Suspicion),0.5)),C(0.01))

  RXN rxn_page_eddie_call_and_alibi_0_2 -> page_k_billy_razor
    T: White's jaw tightens, his grip on the phone slipping. "Eddie's not coming back," he says, the words a confession. Pink laughs, a dry, hollow sound. "Good. We're done here." The silence stretches, the phone dead, and the consequence is the finality of the crew's dissolution, leaving them to face the aftermath.
    E:
      SET char_blonde.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Rat_Suspicion),C(-0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_blonde.Rat_Suspicion[char_pink][char_white] = NUDGE(P(char_blonde.Rat_Suspicion[char_pink][char_white]),ADD(C(-0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(0.11),MUL(P(char_blonde.Rat_Suspicion),0.08)))
      SET char_pink.Diamond_Leverage[char_blonde] = NUDGE(P(char_pink.Diamond_Leverage[char_blonde]),ADD(C(0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_blonde]),0.65),MUL(P(char_blonde.Rat_Suspicion[char_pink][char_white]),-0.35),MAX(MUL(P(char_white.Diamond_Leverage),0.3),C(-0.15)),C(-0.01))

OPT opt_page_eddie_call_and_alibi_1: Hide a micro-check in Blonde's gasoline can and keys
  RXN rxn_page_eddie_call_and_alibi_1_0 -> page_orange_gun_on_the_ramp
    T: Orange's eyes widen, blood spattering the floor. "He's not coming back," he whispers, his hand trembling. White's hand moves to the gasoline can, his fingers brushing the keys. The tension is palpable, the weight of the secret heavy. The consequence is the immediate threat of Orange's gun, forcing a quick decision.
    E:
      SET char_blonde.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Rat_Suspicion),C(0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_blonde.Rat_Suspicion[char_pink][char_white] = NUDGE(P(char_blonde.Rat_Suspicion[char_pink][char_white]),ADD(C(0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(-0.11),MUL(P(char_blonde.Rat_Suspicion),0.08)))
      SET char_pink.Diamond_Leverage[char_blonde] = NUDGE(P(char_pink.Diamond_Leverage[char_blonde]),ADD(C(-0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_blonde]),0.65),MUL(P(char_blonde.Rat_Suspicion[char_pink][char_white]),0.45),MUL(MUL(P(char_pink.Diamond_Leverage),0.5),MUL(P(char_blonde.Rat_Suspicion),0.5)),C(0.06))

  RXN rxn_page_eddie_call_and_alibi_1_1 -> page_k_billy_razor
    T: Pink's eyes narrow, his gaze fixed on White's hand. "You're not hiding anything," he says, his voice low. White's hand stops, the keys clinking. The silence is thick, the weight of the secret pressing down. The consequence is the shift in leverage, Pink's suspicion growing, and the threat of his gun becoming real.
    E:
      SET char_blonde.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Rat_Suspicion),C(0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_blonde.Rat_Suspicion[char_pink][char_white] = NUDGE(P(char_blonde.Rat_Suspicion[char_pink][char_white]),ADD(C(0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(0.11),MUL(P(char_blonde.Rat_Suspicion),0.08)))
      SET char_pink.Diamond_Leverage[char_blonde] = NUDGE(P(char_pink.Diamond_Leverage[char_blonde]),ADD(C(0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_blonde]),-0.5),MUL(P(char_blonde.Rat_Suspicion[char_pink][char_white]),-0.35),MAX(MUL(P(char_white.Diamond_Leverage),0.3),C(-0.15)),C(0.04))

  RXN rxn_page_eddie_call_and_alibi_1_2 -> page_orange_gun_on_the_ramp
    T: Orange's eyes roll back, his body going limp. White's hand freezes, the keys clinking. The silence is absolute, the weight of the secret heavy. The consequence is the finality of Orange's death, leaving White and Pink to face the aftermath, the phone dead, the crew dissolved.
    E:
      SET char_blonde.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Rat_Suspicion),C(0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_blonde.Rat_Suspicion[char_pink][char_white] = NUDGE(P(char_blonde.Rat_Suspicion[char_pink][char_white]),ADD(C(0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(-0.11),MUL(P(char_blonde.Rat_Suspicion),0.08)))
      SET char_pink.Diamond_Leverage[char_blonde] = NUDGE(P(char_pink.Diamond_Leverage[char_blonde]),ADD(C(-0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_blonde]),0.65),MUL(P(char_blonde.Rat_Suspicion[char_pink][char_white]),-0.35),ABSOLUTE VALUE(MUL(P(char_white.Rat_Suspicion),0.35)),C(0.02))

OPT opt_page_eddie_call_and_alibi_2: Press Orange on why Mr. Blue vanished during the alley split
  RXN rxn_page_eddie_call_and_alibi_2_0 -> page_k_billy_razor
    T: Orange's eyes snap open, blood dripping from his lip. "He's not coming back," he rasps, his hand twitching toward the gun. White's voice is low, pressing. "Where's Blue?" Orange's eyes narrow, the pain sharpening his focus. The consequence is the immediate threat of his gun, forcing a standoff.
    E:
      SET char_blonde.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Rat_Suspicion),C(-0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_blonde.Rat_Suspicion[char_pink][char_white] = NUDGE(P(char_blonde.Rat_Suspicion[char_pink][char_white]),ADD(C(-0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(0.11),MUL(P(char_blonde.Rat_Suspicion),0.08)))
      SET char_pink.Diamond_Leverage[char_blonde] = NUDGE(P(char_pink.Diamond_Leverage[char_blonde]),ADD(C(0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_blonde]),0.65),MUL(P(char_blonde.Rat_Suspicion[char_pink][char_white]),0.45),MAX(MUL(P(char_white.Diamond_Leverage),0.3),C(-0.15)),C(0.09))

  RXN rxn_page_eddie_call_and_alibi_2_1 -> page_orange_gun_on_the_ramp
    T: Pink's eyes narrow, his gaze fixed on Orange. "You're not going to answer that," he says, his voice low. Orange's eyes roll back, his body going limp. The silence is thick, the weight of the secret pressing down. The consequence is the shift in leverage, Pink's suspicion growing, and the threat of his gun becoming real.
    E:
      SET char_blonde.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Rat_Suspicion),C(-0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_blonde.Rat_Suspicion[char_pink][char_white] = NUDGE(P(char_blonde.Rat_Suspicion[char_pink][char_white]),ADD(C(-0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(-0.11),MUL(P(char_blonde.Rat_Suspicion),0.08)))
      SET char_pink.Diamond_Leverage[char_blonde] = NUDGE(P(char_pink.Diamond_Leverage[char_blonde]),ADD(C(-0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_blonde]),-0.5),MUL(P(char_blonde.Rat_Suspicion[char_pink][char_white]),-0.35),ABSOLUTE VALUE(MUL(P(char_white.Rat_Suspicion),0.35)),C(0.07))

  RXN rxn_page_eddie_call_and_alibi_2_2 -> page_k_billy_razor
    T: White's jaw tightens, his grip on the phone slipping. "Eddie's not coming back," he says, the words a confession. Pink laughs, a dry, hollow sound. "Good. We're done here." The silence stretches, the phone dead, and the consequence is the finality of the crew's dissolution, leaving them to face the aftermath.
    E:
      SET char_blonde.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Rat_Suspicion),C(-0.09),MUL(P(char_pink.Diamond_Leverage),0.06))))
      SET char_blonde.Rat_Suspicion[char_pink][char_white] = NUDGE(P(char_blonde.Rat_Suspicion[char_pink][char_white]),ADD(C(-0.07),MUL(P(char_pink.Diamond_Leverage),0.05)))
      SET char_pink.Diamond_Leverage = NUDGE(P(char_pink.Diamond_Leverage),ADD(C(0.11),MUL(P(char_blonde.Rat_Suspicion),0.08)))
      SET char_pink.Diamond_Leverage[char_blonde] = NUDGE(P(char_pink.Diamond_Leverage[char_blonde]),ADD(C(0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_pink.Diamond_Leverage),0.02)))
    D: ADD(MUL(P(char_pink.Diamond_Leverage[char_blonde]),0.65),MUL(P(char_blonde.Rat_Suspicion[char_pink][char_white]),-0.35),MUL(MUL(P(char_pink.Diamond_Leverage),0.5),MUL(P(char_blonde.Rat_Suspicion),0.5)),C(0.05))


## ENC page_k_billy_razor | Razor, Radio, and Ramp | turn=7..9 | spools=[spool_act2_interrogation]
T: K-Billy's Super Sounds of the Seventies crackles from the table radio. Mr. Blonde slides a straight razor from his boot, dancing across the concrete toward the chair. The shuttered mortuary smells of cordite, stale coffee, and drying arterial blood. Mr. Orange lies half-conscious on the ramp, his breathing shallow. Bound Marvin Nash watches, eyes wide. Blonde stops, razor glinting. Orange's hand twitches toward his hidden pistol. The music swells. Every breath is a countdown.

OPT opt_page_k_billy_razor_0: Orange feigns unconsciousness, slowly inching toward his hidden pistol.
  RXN rxn_page_k_billy_razor_0_0 -> page_orange_gun_on_the_ramp
    T: Blonde's smile freezes, razor pausing mid-air. He tilts his head, listening to the faint creak of concrete. Orange's hand tightens on the pistol grip. The music distorts, stretching the silence into a blade. Leverage shifts toward the ramp.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_blonde.Sadistic_Escalation[char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange]),ADD(C(0.08),MUL(P(char_pink.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_orange.Crew_Loyalty[char_blonde][char_pink] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_orange]),0.65),MUL(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),0.45),MUL(MUL(P(char_blonde.Sadistic_Escalation),0.5),MUL(P(char_orange.Crew_Loyalty),0.5)),C(0.03))

  RXN rxn_page_k_billy_razor_0_1 -> page_nash_confession_shockwave
    T: Nash's gagged mouth twitches, eyes darting between the razor and the pistol. His bound hands shake. The shock of the hidden weapon breaks his composure. Blonde's gaze snaps to Nash, the interrogation pivot shifting toward the confession.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_blonde.Sadistic_Escalation[char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange]),ADD(C(-0.08),MUL(P(char_pink.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_orange.Crew_Loyalty[char_blonde][char_pink] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_orange]),-0.5),MUL(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),-0.35),MAX(MUL(P(char_pink.Diamond_Leverage),0.3),C(-0.15)),C(0.01))

  RXN rxn_page_k_billy_razor_0_2 -> page_orange_gun_on_the_ramp
    T: Blonde's foot taps the concrete, rhythm breaking. He steps closer, razor catching the radio light. Orange's breathing steadies, a tactical mask. The music swells, masking the pistol's slide. Leverage tilts back toward the ramp.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_blonde.Sadistic_Escalation[char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange]),ADD(C(0.08),MUL(P(char_pink.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_orange.Crew_Loyalty[char_blonde][char_pink] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_orange]),0.65),MUL(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),-0.35),ABSOLUTE VALUE(MUL(P(char_pink.Crew_Loyalty),0.35)),C(-0.01))

OPT opt_page_k_billy_razor_1: Orange shouts from the ramp, stalling Blonde with Cabot's name.
  RXN rxn_page_k_billy_razor_1_0 -> page_nash_confession_shockwave
    T: Nash's eyes widen, the name a trigger. His bound hands jerk, gagged voice muffled. Blonde's razor stops, his smile thinning. The confession shockwave hits, the mole's identity surfacing. Leverage shifts toward the confession.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_blonde.Sadistic_Escalation[char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange]),ADD(C(-0.08),MUL(P(char_pink.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_orange.Crew_Loyalty[char_blonde][char_pink] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),ADD(C(0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_orange]),0.65),MUL(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),0.45),MAX(MUL(P(char_pink.Diamond_Leverage),0.3),C(-0.15)),C(0.06))

  RXN rxn_page_k_billy_razor_1_1 -> page_orange_gun_on_the_ramp
    T: Blonde's foot stops, razor glinting. He tilts his head, listening to the echo. Orange's voice is low, controlled. The music distorts, stretching the silence. Leverage shifts back toward the ramp, the pistol still hidden.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_blonde.Sadistic_Escalation[char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange]),ADD(C(0.08),MUL(P(char_pink.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_orange.Crew_Loyalty[char_blonde][char_pink] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),ADD(C(0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_orange]),-0.5),MUL(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),-0.35),ABSOLUTE VALUE(MUL(P(char_pink.Crew_Loyalty),0.35)),C(0.04))

  RXN rxn_page_k_billy_razor_1_2 -> page_nash_confession_shockwave
    T: Nash's eyes dart, the name a trigger. His bound hands shake, gagged voice muffled. Blonde's gaze snaps to Nash, the interrogation pivot shifting. The confession shockwave hits, the mole's identity surfacing. Leverage shifts toward the confession.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_blonde.Sadistic_Escalation[char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange]),ADD(C(-0.08),MUL(P(char_pink.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_orange.Crew_Loyalty[char_blonde][char_pink] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),ADD(C(0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_orange]),0.65),MUL(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),-0.35),MUL(MUL(P(char_blonde.Sadistic_Escalation),0.5),MUL(P(char_orange.Crew_Loyalty),0.5)),C(0.02))

OPT opt_page_k_billy_razor_2: Blonde slices the tape, demanding the LAPD mole's codename.
  RXN rxn_page_k_billy_razor_2_0 -> page_orange_gun_on_the_ramp
    T: Orange's hand tightens on the pistol grip, the hidden weapon a threat. Blonde's smile freezes, razor pausing mid-air. The music distorts, stretching the silence. Leverage shifts toward the ramp, the pistol still hidden.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_blonde.Sadistic_Escalation[char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange]),ADD(C(0.08),MUL(P(char_pink.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_orange.Crew_Loyalty[char_blonde][char_pink] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_orange]),0.65),MUL(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),0.45),ABSOLUTE VALUE(MUL(P(char_pink.Crew_Loyalty),0.35)),C(0.09))

  RXN rxn_page_k_billy_razor_2_1 -> page_nash_confession_shockwave
    T: Nash's eyes widen, the demand a trigger. His bound hands jerk, gagged voice muffled. Blonde's gaze snaps to Nash, the interrogation pivot shifting. The confession shockwave hits, the mole's identity surfacing. Leverage shifts toward the confession.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_blonde.Sadistic_Escalation[char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange]),ADD(C(-0.08),MUL(P(char_pink.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_orange.Crew_Loyalty[char_blonde][char_pink] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_orange]),-0.5),MUL(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),-0.35),MUL(MUL(P(char_blonde.Sadistic_Escalation),0.5),MUL(P(char_orange.Crew_Loyalty),0.5)),C(0.07))

  RXN rxn_page_k_billy_razor_2_2 -> page_orange_gun_on_the_ramp
    T: Blonde's foot taps the concrete, rhythm breaking. He steps closer, razor catching the radio light. Orange's breathing steadies, a tactical mask. The music swells, masking the pistol's slide. Leverage tilts back toward the ramp.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_blonde.Sadistic_Escalation[char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange]),ADD(C(0.08),MUL(P(char_pink.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(-0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_orange.Crew_Loyalty[char_blonde][char_pink] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),ADD(C(-0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_orange]),0.65),MUL(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),-0.35),MAX(MUL(P(char_pink.Diamond_Leverage),0.3),C(-0.15)),C(0.05))

OPT opt_page_k_billy_razor_3: Kick a surgical tray off the ramp to break Blonde's rhythm.
  RXN rxn_page_k_billy_razor_3_0 -> page_nash_confession_shockwave
    T: Nash's eyes widen, the clatter a trigger. His bound hands jerk, gagged voice muffled. Blonde's gaze snaps to Nash, the interrogation pivot shifting. The confession shockwave hits, the mole's identity surfacing. Leverage shifts toward the confession.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_blonde.Sadistic_Escalation[char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange]),ADD(C(-0.08),MUL(P(char_pink.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_orange.Crew_Loyalty[char_blonde][char_pink] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),ADD(C(0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_orange]),0.65),MUL(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),0.45),MUL(MUL(P(char_blonde.Sadistic_Escalation),0.5),MUL(P(char_orange.Crew_Loyalty),0.5)),C(0.12))

  RXN rxn_page_k_billy_razor_3_1 -> page_orange_gun_on_the_ramp
    T: Blonde's foot stops, razor glinting. He tilts his head, listening to the echo. Orange's voice is low, controlled. The music distorts, stretching the silence. Leverage shifts back toward the ramp, the pistol still hidden.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_blonde.Sadistic_Escalation[char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange]),ADD(C(0.08),MUL(P(char_pink.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_orange.Crew_Loyalty[char_blonde][char_pink] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),ADD(C(0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_orange]),-0.5),MUL(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),-0.35),MAX(MUL(P(char_pink.Diamond_Leverage),0.3),C(-0.15)),C(0.1))

  RXN rxn_page_k_billy_razor_3_2 -> page_nash_confession_shockwave
    T: Nash's eyes dart, the clatter a trigger. His bound hands shake, gagged voice muffled. Blonde's gaze snaps to Nash, the interrogation pivot shifting. The confession shockwave hits, the mole's identity surfacing. Leverage shifts toward the confession.
    E:
      SET char_blonde.Sadistic_Escalation = NUDGE(P(char_blonde.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_orange.Crew_Loyalty),0.08)))
      SET char_blonde.Sadistic_Escalation[char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange]),ADD(C(-0.08),MUL(P(char_pink.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Crew_Loyalty),C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.06))))
      SET char_orange.Crew_Loyalty[char_blonde][char_pink] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),ADD(C(0.07),MUL(P(char_blonde.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_blonde.Sadistic_Escalation),0.02)))
    D: ADD(MUL(P(char_blonde.Sadistic_Escalation[char_orange]),0.65),MUL(P(char_orange.Crew_Loyalty[char_blonde][char_pink]),-0.35),ABSOLUTE VALUE(MUL(P(char_pink.Crew_Loyalty),0.35)),C(0.08))


## ENC page_orange_gun_on_the_ramp | Zippo, Blood, and the Ramp | turn=8..10 | spools=[spool_act2_interrogation]
T: Gasoline slicks the concrete as Marvin Nash sobs, his uniform soaked. "I got a kid at home, I swear!" Mr. Blonde thumbs a chrome Zippo, the flame licking the damp air. Mr. Orange raises a trembling Smith & Wesson from the ramp, his gut wound pulsing. The shuttered mortuary reeks of cordite and stale coffee. Every breath tastes of betrayal. Orange’s finger hovers near the trigger, weighing professional discipline against the creeping certainty that an LAPD plant sold out the crew. The lighter clicks. The gun shakes. The silence stretches, thin as a razor, waiting for the next move.

OPT opt_page_orange_gun_on_the_ramp_0: Empty the cylinder into Blonde's chest before the Zippo drops.
  RXN rxn_page_orange_gun_on_the_ramp_0_0 -> page_nash_confession_shockwave
    T: Blonde’s head snaps back, eyes wide with shock. The Zippo clatters to the floor, flame dying. Nash screams, pointing at the body. Orange’s hand shakes, blood dripping from his wound. The warehouse falls silent, the smell of gunpowder mixing with gasoline. The crew’s loyalty fractures, replaced by the cold reality of a dead witness and a compromised mission.
    E:
      SET char_blonde.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Sadistic_Escalation),C(-0.09),MUL(P(char_orange.Crew_Loyalty),0.06))))
      SET char_blonde.Sadistic_Escalation[char_orange][char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),ADD(C(-0.07),MUL(P(char_orange.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = NUDGE(P(char_orange.Crew_Loyalty),ADD(C(0.11),MUL(P(char_blonde.Sadistic_Escalation),0.08)))
      SET char_orange.Crew_Loyalty[char_blonde] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde]),ADD(C(0.08),MUL(P(char_orange.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_orange.Crew_Loyalty[char_blonde]),0.65),MUL(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),0.45),MAX(MUL(P(char_orange.Diamond_Leverage),0.3),C(-0.15)),C(0.03))

  RXN rxn_page_orange_gun_on_the_ramp_0_1 -> page_eddie_and_blonde_story
    T: Blonde’s body twitches, his last breath a whisper. Nash cowers, backing into the shadows. Orange’s face hardens, guilt and rage warring. The Zippo’s flame flickers out. The warehouse echoes with the sound of a dying man and the wet drip of blood. The crew’s plan collapses, leaving only the hollow truth of a job gone wrong.
    E:
      SET char_blonde.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Sadistic_Escalation),C(-0.09),MUL(P(char_orange.Crew_Loyalty),0.06))))
      SET char_blonde.Sadistic_Escalation[char_orange][char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),ADD(C(-0.07),MUL(P(char_orange.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = NUDGE(P(char_orange.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_blonde.Sadistic_Escalation),0.08)))
      SET char_orange.Crew_Loyalty[char_blonde] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde]),ADD(C(-0.08),MUL(P(char_orange.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_orange.Crew_Loyalty[char_blonde]),-0.5),MUL(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),-0.35),ABSOLUTE VALUE(MUL(P(char_orange.Sadistic_Escalation),0.35)),C(0.01))

  RXN rxn_page_orange_gun_on_the_ramp_0_2 -> page_nash_confession_shockwave
    T: Nash’s sobbing turns to a wail. The Zippo’s flame dances in the dark. Orange’s gun lowers, but his eyes remain locked on Blonde’s corpse. The warehouse smells of blood and gasoline. The crew’s loyalty is tested, the weight of the kill settling on Orange’s shoulders. The next move is a gamble, the stakes higher than ever.
    E:
      SET char_blonde.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Sadistic_Escalation),C(-0.09),MUL(P(char_orange.Crew_Loyalty),0.06))))
      SET char_blonde.Sadistic_Escalation[char_orange][char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),ADD(C(-0.07),MUL(P(char_orange.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = NUDGE(P(char_orange.Crew_Loyalty),ADD(C(0.11),MUL(P(char_blonde.Sadistic_Escalation),0.08)))
      SET char_orange.Crew_Loyalty[char_blonde] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde]),ADD(C(0.08),MUL(P(char_orange.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_orange.Crew_Loyalty[char_blonde]),0.65),MUL(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),-0.35),MUL(MUL(P(char_orange.Crew_Loyalty),0.5),MUL(P(char_blonde.Sadistic_Escalation),0.5)),C(-0.01))

OPT opt_page_orange_gun_on_the_ramp_1: Wing Blonde's gun hand to keep him alive as a witness for Joe.
  RXN rxn_page_orange_gun_on_the_ramp_1_0 -> page_eddie_and_blonde_story
    T: Blonde’s eyes widen, his hand jerking. The Zippo’s flame flares, illuminating his face. Nash’s sobbing stops, replaced by a tense silence. Orange’s grip tightens, blood soaking his shirt. The warehouse holds its breath. The crew’s loyalty is tested, the weight of the decision hanging in the air. The next move is a gamble, the stakes higher than ever.
    E:
      SET char_blonde.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Sadistic_Escalation),C(0.09),MUL(P(char_orange.Crew_Loyalty),0.06))))
      SET char_blonde.Sadistic_Escalation[char_orange][char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),ADD(C(0.07),MUL(P(char_orange.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = NUDGE(P(char_orange.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_blonde.Sadistic_Escalation),0.08)))
      SET char_orange.Crew_Loyalty[char_blonde] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde]),ADD(C(-0.08),MUL(P(char_orange.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_orange.Crew_Loyalty[char_blonde]),0.65),MUL(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),0.45),ABSOLUTE VALUE(MUL(P(char_orange.Sadistic_Escalation),0.35)),C(0.06))

  RXN rxn_page_orange_gun_on_the_ramp_1_1 -> page_nash_confession_shockwave
    T: Blonde’s hand twitches, the Zippo’s flame flickering. Nash’s eyes dart, fear and confusion warring. Orange’s face hardens, guilt and rage warring. The warehouse echoes with the sound of a dying man and the wet drip of blood. The crew’s plan collapses, leaving only the hollow truth of a job gone wrong.
    E:
      SET char_blonde.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Sadistic_Escalation),C(0.09),MUL(P(char_orange.Crew_Loyalty),0.06))))
      SET char_blonde.Sadistic_Escalation[char_orange][char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),ADD(C(0.07),MUL(P(char_orange.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = NUDGE(P(char_orange.Crew_Loyalty),ADD(C(0.11),MUL(P(char_blonde.Sadistic_Escalation),0.08)))
      SET char_orange.Crew_Loyalty[char_blonde] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde]),ADD(C(0.08),MUL(P(char_orange.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_orange.Crew_Loyalty[char_blonde]),-0.5),MUL(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),-0.35),MUL(MUL(P(char_orange.Crew_Loyalty),0.5),MUL(P(char_blonde.Sadistic_Escalation),0.5)),C(0.04))

  RXN rxn_page_orange_gun_on_the_ramp_1_2 -> page_eddie_and_blonde_story
    T: Nash’s sobbing turns to a wail. The Zippo’s flame dances in the dark. Orange’s gun lowers, but his eyes remain locked on Blonde’s face. The warehouse smells of blood and gasoline. The crew’s loyalty is tested, the weight of the decision settling on Orange’s shoulders. The next move is a gamble, the stakes higher than ever.
    E:
      SET char_blonde.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Sadistic_Escalation),C(0.09),MUL(P(char_orange.Crew_Loyalty),0.06))))
      SET char_blonde.Sadistic_Escalation[char_orange][char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),ADD(C(0.07),MUL(P(char_orange.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = NUDGE(P(char_orange.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_blonde.Sadistic_Escalation),0.08)))
      SET char_orange.Crew_Loyalty[char_blonde] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde]),ADD(C(-0.08),MUL(P(char_orange.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_orange.Crew_Loyalty[char_blonde]),0.65),MUL(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),-0.35),MAX(MUL(P(char_orange.Diamond_Leverage),0.3),C(-0.15)),C(0.02))

OPT opt_page_orange_gun_on_the_ramp_2: Hold fire until Nash blurts out the robbery-homicide unit name.
  RXN rxn_page_orange_gun_on_the_ramp_2_0 -> page_nash_confession_shockwave
    T: Nash’s sobbing stops, his eyes darting. The Zippo’s flame flickers, illuminating his face. Orange’s grip tightens, blood soaking his shirt. The warehouse holds its breath. The crew’s loyalty is tested, the weight of the decision hanging in the air. The next move is a gamble, the stakes higher than ever.
    E:
      SET char_blonde.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Sadistic_Escalation),C(-0.09),MUL(P(char_orange.Crew_Loyalty),0.06))))
      SET char_blonde.Sadistic_Escalation[char_orange][char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),ADD(C(-0.07),MUL(P(char_orange.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = NUDGE(P(char_orange.Crew_Loyalty),ADD(C(0.11),MUL(P(char_blonde.Sadistic_Escalation),0.08)))
      SET char_orange.Crew_Loyalty[char_blonde] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde]),ADD(C(0.08),MUL(P(char_orange.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_orange.Crew_Loyalty[char_blonde]),0.65),MUL(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),0.45),MUL(MUL(P(char_orange.Crew_Loyalty),0.5),MUL(P(char_blonde.Sadistic_Escalation),0.5)),C(0.09))

  RXN rxn_page_orange_gun_on_the_ramp_2_1 -> page_eddie_and_blonde_story
    T: Blonde’s hand twitches, the Zippo’s flame flickering. Nash’s eyes dart, fear and confusion warring. Orange’s face hardens, guilt and rage warring. The warehouse echoes with the sound of a dying man and the wet drip of blood. The crew’s plan collapses, leaving only the hollow truth of a job gone wrong.
    E:
      SET char_blonde.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Sadistic_Escalation),C(-0.09),MUL(P(char_orange.Crew_Loyalty),0.06))))
      SET char_blonde.Sadistic_Escalation[char_orange][char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),ADD(C(-0.07),MUL(P(char_orange.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = NUDGE(P(char_orange.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_blonde.Sadistic_Escalation),0.08)))
      SET char_orange.Crew_Loyalty[char_blonde] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde]),ADD(C(-0.08),MUL(P(char_orange.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_orange.Crew_Loyalty[char_blonde]),-0.5),MUL(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),-0.35),MAX(MUL(P(char_orange.Diamond_Leverage),0.3),C(-0.15)),C(0.07))

  RXN rxn_page_orange_gun_on_the_ramp_2_2 -> page_nash_confession_shockwave
    T: Nash’s sobbing turns to a wail. The Zippo’s flame dances in the dark. Orange’s gun lowers, but his eyes remain locked on Blonde’s face. The warehouse smells of blood and gasoline. The crew’s loyalty is tested, the weight of the decision settling on Orange’s shoulders. The next move is a gamble, the stakes higher than ever.
    E:
      SET char_blonde.Sadistic_Escalation = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_blonde.Sadistic_Escalation),C(-0.09),MUL(P(char_orange.Crew_Loyalty),0.06))))
      SET char_blonde.Sadistic_Escalation[char_orange][char_orange] = NUDGE(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),ADD(C(-0.07),MUL(P(char_orange.Crew_Loyalty),0.05)))
      SET char_orange.Crew_Loyalty = NUDGE(P(char_orange.Crew_Loyalty),ADD(C(0.11),MUL(P(char_blonde.Sadistic_Escalation),0.08)))
      SET char_orange.Crew_Loyalty[char_blonde] = NUDGE(P(char_orange.Crew_Loyalty[char_blonde]),ADD(C(0.08),MUL(P(char_orange.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_orange.Crew_Loyalty[char_blonde]),0.65),MUL(P(char_blonde.Sadistic_Escalation[char_orange][char_orange]),-0.35),ABSOLUTE VALUE(MUL(P(char_orange.Sadistic_Escalation),0.35)),C(0.05))


## ENC page_nash_confession_shockwave | Nash Gasps Through the Cordite | turn=9..11 | spools=[spool_act2_interrogation]
T: Cordite and raw gasoline sting the air. Marvin Nash gasps through shock on the soaked floor, his wrists still bound. Mr. Orange bleeds from a gut wound, staring at the ceiling. Mr. White kneels, pressing a rag to the wound. Mr. Pink counts the diamonds in his pocket, his face unreadable. "If you talk, we all die," Pink says. "If you don't, Cabot walks," White counters. Nash's eyes dart to the shuttered door. The smell of stale coffee and drying blood fills the room. Every breath is a negotiation. The crew weighs professional discipline against the creeping certainty that an LAPD plant sold them out. The silence stretches, thick and dangerous.

OPT opt_page_nash_confession_shockwave_0: Swear Nash to silence and rehearse the Blonde-betrayal cover story
  RXN rxn_page_nash_confession_shockwave_0_0 -> page_eddie_and_blonde_story
    T: Nash nods, his jaw tight. White grips his shoulder, a silent promise of protection. Pink watches, calculating the risk. The leverage shifts toward the Blonde story, but the fear of Cabot's wrath lingers, pulling the crew toward a darker verdict.
    E:
      SET char_orange.Rat_Suspicion = NUDGE(P(char_orange.Rat_Suspicion),ADD(C(0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_orange.Rat_Suspicion[char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_pink]),ADD(C(0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(-0.09),MUL(P(char_orange.Rat_Suspicion),0.06))))
      SET char_pink.Professional_Discipline[char_orange][char_blonde] = NUDGE(P(char_pink.Professional_Discipline[char_orange][char_blonde]),ADD(C(-0.07),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Rat_Suspicion),0.02)))
    D: ADD(MUL(P(char_orange.Rat_Suspicion[char_pink]),0.65),MUL(P(char_pink.Professional_Discipline[char_orange][char_blonde]),0.45),ABSOLUTE VALUE(MUL(P(char_blonde.Professional_Discipline),0.35)),C(0.03))

  RXN rxn_page_nash_confession_shockwave_0_1 -> page_cabot_verdict
    T: Nash's eyes flicker with doubt. White's grip tightens, a subtle threat. Pink smirks, sensing weakness. The crew's focus narrows to Cabot's potential arrival, the silence breaking as the threat of the verdict looms larger than the Blonde story.
    E:
      SET char_orange.Rat_Suspicion = NUDGE(P(char_orange.Rat_Suspicion),ADD(C(-0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_orange.Rat_Suspicion[char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_pink]),ADD(C(-0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(-0.09),MUL(P(char_orange.Rat_Suspicion),0.06))))
      SET char_pink.Professional_Discipline[char_orange][char_blonde] = NUDGE(P(char_pink.Professional_Discipline[char_orange][char_blonde]),ADD(C(-0.07),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Rat_Suspicion),0.02)))
    D: ADD(MUL(P(char_orange.Rat_Suspicion[char_pink]),-0.5),MUL(P(char_pink.Professional_Discipline[char_orange][char_blonde]),-0.35),MUL(MUL(P(char_orange.Rat_Suspicion),0.5),MUL(P(char_pink.Professional_Discipline),0.5)),C(0.01))

  RXN rxn_page_nash_confession_shockwave_0_2 -> page_eddie_and_blonde_story
    T: Nash whispers a promise, but his voice cracks. White's protective stance softens, a flicker of doubt in his eyes. Pink's rationality sharpens, the crew's attention drifting back to the Blonde story, the tension easing slightly as the immediate threat of Cabot fades.
    E:
      SET char_orange.Rat_Suspicion = NUDGE(P(char_orange.Rat_Suspicion),ADD(C(0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_orange.Rat_Suspicion[char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_pink]),ADD(C(0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(-0.09),MUL(P(char_orange.Rat_Suspicion),0.06))))
      SET char_pink.Professional_Discipline[char_orange][char_blonde] = NUDGE(P(char_pink.Professional_Discipline[char_orange][char_blonde]),ADD(C(-0.07),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Rat_Suspicion),0.02)))
    D: ADD(MUL(P(char_orange.Rat_Suspicion[char_pink]),0.65),MUL(P(char_pink.Professional_Discipline[char_orange][char_blonde]),-0.35),MAX(MUL(P(char_blonde.Diamond_Leverage),0.3),C(-0.15)),C(-0.01))

OPT opt_page_nash_confession_shockwave_1: Stage the razor and gas can so Pink reads pure self-defense
  RXN rxn_page_nash_confession_shockwave_1_0 -> page_cabot_verdict
    T: Pink's eyes narrow, his rationality engaging. He sees the staged evidence, the razor, the gas can. The crew's focus shifts to Cabot's verdict, the self-defense narrative a fragile shield. Nash's silence becomes a weapon, the tension thickening as the crew prepares for the worst.
    E:
      SET char_orange.Rat_Suspicion = NUDGE(P(char_orange.Rat_Suspicion),ADD(C(-0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_orange.Rat_Suspicion[char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_pink]),ADD(C(-0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(0.09),MUL(P(char_orange.Rat_Suspicion),0.06))))
      SET char_pink.Professional_Discipline[char_orange][char_blonde] = NUDGE(P(char_pink.Professional_Discipline[char_orange][char_blonde]),ADD(C(0.07),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Rat_Suspicion),0.02)))
    D: ADD(MUL(P(char_orange.Rat_Suspicion[char_pink]),0.65),MUL(P(char_pink.Professional_Discipline[char_orange][char_blonde]),0.45),MUL(MUL(P(char_orange.Rat_Suspicion),0.5),MUL(P(char_pink.Professional_Discipline),0.5)),C(0.06))

  RXN rxn_page_nash_confession_shockwave_1_1 -> page_eddie_and_blonde_story
    T: Pink's smirk fades, replaced by a cold calculation. He sees the flaw in the self-defense story. The crew's attention drifts to the Blonde story, the staged evidence a temporary reprieve. Nash's silence is a gamble, the tension easing as the crew focuses on the next move.
    E:
      SET char_orange.Rat_Suspicion = NUDGE(P(char_orange.Rat_Suspicion),ADD(C(0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_orange.Rat_Suspicion[char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_pink]),ADD(C(0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(0.09),MUL(P(char_orange.Rat_Suspicion),0.06))))
      SET char_pink.Professional_Discipline[char_orange][char_blonde] = NUDGE(P(char_pink.Professional_Discipline[char_orange][char_blonde]),ADD(C(0.07),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Rat_Suspicion),0.02)))
    D: ADD(MUL(P(char_orange.Rat_Suspicion[char_pink]),-0.5),MUL(P(char_pink.Professional_Discipline[char_orange][char_blonde]),-0.35),MAX(MUL(P(char_blonde.Diamond_Leverage),0.3),C(-0.15)),C(0.04))

  RXN rxn_page_nash_confession_shockwave_1_2 -> page_cabot_verdict
    T: Pink's eyes harden, his rationality a blade. He sees the truth in the staged evidence, the self-defense narrative a lie. The crew's focus returns to Cabot's verdict, the tension spiking as the crew prepares for the inevitable confrontation, Nash's silence a ticking clock.
    E:
      SET char_orange.Rat_Suspicion = NUDGE(P(char_orange.Rat_Suspicion),ADD(C(-0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_orange.Rat_Suspicion[char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_pink]),ADD(C(-0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(0.09),MUL(P(char_orange.Rat_Suspicion),0.06))))
      SET char_pink.Professional_Discipline[char_orange][char_blonde] = NUDGE(P(char_pink.Professional_Discipline[char_orange][char_blonde]),ADD(C(0.07),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Rat_Suspicion),0.02)))
    D: ADD(MUL(P(char_orange.Rat_Suspicion[char_pink]),0.65),MUL(P(char_pink.Professional_Discipline[char_orange][char_blonde]),-0.35),ABSOLUTE VALUE(MUL(P(char_blonde.Professional_Discipline),0.35)),C(0.02))

OPT opt_page_nash_confession_shockwave_2: Check Nash's cuffs and confess quietly when White bursts back in
  RXN rxn_page_nash_confession_shockwave_2_0 -> page_eddie_and_blonde_story
    T: White bursts in, his face pale. Nash's cuffs are checked, the silence broken by a quiet confession. The crew's focus shifts to the Blonde story, the confession a fragile bridge. Pink's rationality engages, the tension easing as the crew prepares for the next move, the confession a temporary reprieve.
    E:
      SET char_orange.Rat_Suspicion = NUDGE(P(char_orange.Rat_Suspicion),ADD(C(0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_orange.Rat_Suspicion[char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_pink]),ADD(C(0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(-0.09),MUL(P(char_orange.Rat_Suspicion),0.06))))
      SET char_pink.Professional_Discipline[char_orange][char_blonde] = NUDGE(P(char_pink.Professional_Discipline[char_orange][char_blonde]),ADD(C(-0.07),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Rat_Suspicion),0.02)))
    D: ADD(MUL(P(char_orange.Rat_Suspicion[char_pink]),0.65),MUL(P(char_pink.Professional_Discipline[char_orange][char_blonde]),0.45),MAX(MUL(P(char_blonde.Diamond_Leverage),0.3),C(-0.15)),C(0.09))

  RXN rxn_page_nash_confession_shockwave_2_1 -> page_cabot_verdict
    T: White bursts in, his face pale. Nash's cuffs are checked, the silence broken by a quiet confession. The crew's focus shifts to Cabot's verdict, the confession a fragile shield. Pink's rationality engages, the tension spiking as the crew prepares for the inevitable confrontation, the confession a ticking clock.
    E:
      SET char_orange.Rat_Suspicion = NUDGE(P(char_orange.Rat_Suspicion),ADD(C(-0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_orange.Rat_Suspicion[char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_pink]),ADD(C(-0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(-0.09),MUL(P(char_orange.Rat_Suspicion),0.06))))
      SET char_pink.Professional_Discipline[char_orange][char_blonde] = NUDGE(P(char_pink.Professional_Discipline[char_orange][char_blonde]),ADD(C(-0.07),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Rat_Suspicion),0.02)))
    D: ADD(MUL(P(char_orange.Rat_Suspicion[char_pink]),-0.5),MUL(P(char_pink.Professional_Discipline[char_orange][char_blonde]),-0.35),ABSOLUTE VALUE(MUL(P(char_blonde.Professional_Discipline),0.35)),C(0.07))

  RXN rxn_page_nash_confession_shockwave_2_2 -> page_eddie_and_blonde_story
    T: White bursts in, his face pale. Nash's cuffs are checked, the silence broken by a quiet confession. The crew's focus shifts to the Blonde story, the confession a fragile bridge. Pink's rationality engages, the tension easing as the crew prepares for the next move, the confession a temporary reprieve.
    E:
      SET char_orange.Rat_Suspicion = NUDGE(P(char_orange.Rat_Suspicion),ADD(C(0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_orange.Rat_Suspicion[char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_pink]),ADD(C(0.08),MUL(P(char_blonde.Professional_Discipline),0.05)))
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(-0.09),MUL(P(char_orange.Rat_Suspicion),0.06))))
      SET char_pink.Professional_Discipline[char_orange][char_blonde] = NUDGE(P(char_pink.Professional_Discipline[char_orange][char_blonde]),ADD(C(-0.07),MUL(P(char_orange.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_orange.Rat_Suspicion),0.02)))
    D: ADD(MUL(P(char_orange.Rat_Suspicion[char_pink]),0.65),MUL(P(char_pink.Professional_Discipline[char_orange][char_blonde]),-0.35),MUL(MUL(P(char_orange.Rat_Suspicion),0.5),MUL(P(char_pink.Professional_Discipline),0.5)),C(0.05))


## ENC page_eddie_and_blonde_story | Vic Vega Was Family | turn=10..12 | spools=[spool_act3_standoff]
T: Mr. White, Mr. Pink, and Nice Guy Eddie return with the Karina diamond satchel to find gasoline pooling across the warehouse and Blonde down. Orange swears Blonde planned to burn Nash, kill the crew, and steal the stones, while Eddie screams that Vic did four years for his father. Every breath inside the shuttered mortuary smells of cordite, stale coffee, and drying arterial blood, forcing each survivor to weigh professional discipline against the creeping certainty that an LAPD plant sold out the crew.

OPT opt_page_eddie_and_blonde_story_0: Blonde killed Karina's civilians, so Orange's story holds water
  RXN rxn_page_eddie_and_blonde_story_0_0 -> page_cabot_verdict
    T: Mr. White shifts the warehouse balance around vic vega was family, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_pink.Rat_Suspicion[char_white][char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white][char_white]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_pink] = NUDGE(P(char_white.Crew_Loyalty[char_pink]),ADD(C(0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_pink]),0.65),MUL(P(char_pink.Rat_Suspicion[char_white][char_white]),0.45),MUL(MUL(P(char_white.Crew_Loyalty),0.5),MUL(P(char_pink.Rat_Suspicion),0.5)),C(0.03))

  RXN rxn_page_eddie_and_blonde_story_0_1 -> page_mexican_standoff
    T: Mr. White shifts the warehouse balance around vic vega was family, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_pink.Rat_Suspicion[char_white][char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white][char_white]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_pink] = NUDGE(P(char_white.Crew_Loyalty[char_pink]),ADD(C(-0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_pink]),-0.5),MUL(P(char_pink.Rat_Suspicion[char_white][char_white]),-0.35),MAX(MUL(P(char_white.Diamond_Leverage),0.3),C(-0.15)),C(0.01))

  RXN rxn_page_eddie_and_blonde_story_0_2 -> page_cabot_verdict
    T: Mr. White shifts the warehouse balance around vic vega was family, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_pink.Rat_Suspicion[char_white][char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white][char_white]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_pink] = NUDGE(P(char_white.Crew_Loyalty[char_pink]),ADD(C(0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_pink]),0.65),MUL(P(char_pink.Rat_Suspicion[char_white][char_white]),-0.35),ABSOLUTE VALUE(MUL(P(char_white.Rat_Suspicion),0.35)),C(-0.01))

OPT opt_page_eddie_and_blonde_story_1: Pink's powder burn audit is neutral, so I side with him
  RXN rxn_page_eddie_and_blonde_story_1_0 -> page_mexican_standoff
    T: Mr. White shifts the warehouse balance around vic vega was family, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_pink.Rat_Suspicion[char_white][char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white][char_white]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_pink] = NUDGE(P(char_white.Crew_Loyalty[char_pink]),ADD(C(-0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_pink]),0.65),MUL(P(char_pink.Rat_Suspicion[char_white][char_white]),0.45),MAX(MUL(P(char_white.Diamond_Leverage),0.3),C(-0.15)),C(0.06))

  RXN rxn_page_eddie_and_blonde_story_1_1 -> page_cabot_verdict
    T: Mr. White shifts the warehouse balance around vic vega was family, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_pink.Rat_Suspicion[char_white][char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white][char_white]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_pink] = NUDGE(P(char_white.Crew_Loyalty[char_pink]),ADD(C(0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_pink]),-0.5),MUL(P(char_pink.Rat_Suspicion[char_white][char_white]),-0.35),ABSOLUTE VALUE(MUL(P(char_white.Rat_Suspicion),0.35)),C(0.04))

  RXN rxn_page_eddie_and_blonde_story_1_2 -> page_mexican_standoff
    T: Mr. White shifts the warehouse balance around vic vega was family, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_pink.Rat_Suspicion[char_white][char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white][char_white]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_pink] = NUDGE(P(char_white.Crew_Loyalty[char_pink]),ADD(C(-0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_pink]),0.65),MUL(P(char_pink.Rat_Suspicion[char_white][char_white]),-0.35),MUL(MUL(P(char_white.Crew_Loyalty),0.5),MUL(P(char_pink.Rat_Suspicion),0.5)),C(0.02))

OPT opt_page_eddie_and_blonde_story_2: Grab the diamond briefcase and test Orange's timeline slip
  RXN rxn_page_eddie_and_blonde_story_2_0 -> page_cabot_verdict
    T: Mr. White shifts the warehouse balance around vic vega was family, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_pink.Rat_Suspicion[char_white][char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white][char_white]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_pink] = NUDGE(P(char_white.Crew_Loyalty[char_pink]),ADD(C(0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_pink]),0.65),MUL(P(char_pink.Rat_Suspicion[char_white][char_white]),0.45),ABSOLUTE VALUE(MUL(P(char_white.Rat_Suspicion),0.35)),C(0.09))

  RXN rxn_page_eddie_and_blonde_story_2_1 -> page_mexican_standoff
    T: Mr. White shifts the warehouse balance around vic vega was family, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_pink.Rat_Suspicion[char_white][char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white][char_white]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_pink] = NUDGE(P(char_white.Crew_Loyalty[char_pink]),ADD(C(-0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_pink]),-0.5),MUL(P(char_pink.Rat_Suspicion[char_white][char_white]),-0.35),MUL(MUL(P(char_white.Crew_Loyalty),0.5),MUL(P(char_pink.Rat_Suspicion),0.5)),C(0.07))

  RXN rxn_page_eddie_and_blonde_story_2_2 -> page_cabot_verdict
    T: Mr. White shifts the warehouse balance around vic vega was family, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Rat_Suspicion),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_pink.Rat_Suspicion[char_white][char_white] = NUDGE(P(char_pink.Rat_Suspicion[char_white][char_white]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_pink.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_pink] = NUDGE(P(char_white.Crew_Loyalty[char_pink]),ADD(C(0.08),MUL(P(char_white.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_pink]),0.65),MUL(P(char_pink.Rat_Suspicion[char_white][char_white]),-0.35),MAX(MUL(P(char_white.Diamond_Leverage),0.3),C(-0.15)),C(0.05))


## ENC page_cabot_verdict | Joe Cabot's Finger on the Rat | turn=11..13 | spools=[spool_act3_standoff]
T: Joe Cabot strides into the mortuary warehouse like an aging king whose court has rotted, declares Mr. Blue dead, and levels his snub-nose revolver directly at bleeding Mr. Orange. Joe says the kid is a cop, one hundred percent certain, and tells White to step clear. Every breath inside the shuttered mortuary smells of cordite, stale coffee, and drying arterial blood, forcing each survivor to weigh professional discipline against the creeping certainty that an LAPD plant sold out the crew.

OPT opt_page_cabot_verdict_0: Draw on Joe, swear Orange is solid, hold your nerve
  RXN rxn_page_cabot_verdict_0_0 -> page_mexican_standoff
    T: Mr. White shifts the warehouse balance around joe cabot's finger on the rat, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Rat_Suspicion),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Rat_Suspicion[char_white][char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_white][char_pink]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_pink.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Rat_Suspicion[char_white][char_pink]),0.45),MAX(MUL(P(char_pink.Diamond_Leverage),0.3),C(-0.15)),C(0.03))

  RXN rxn_page_cabot_verdict_0_1 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around joe cabot's finger on the rat, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Rat_Suspicion),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Rat_Suspicion[char_white][char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_white][char_pink]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_pink.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),-0.5),MUL(P(char_orange.Rat_Suspicion[char_white][char_pink]),-0.35),ABSOLUTE VALUE(MUL(P(char_pink.Rat_Suspicion),0.35)),C(0.01))

  RXN rxn_page_cabot_verdict_0_2 -> page_mexican_standoff
    T: Mr. White shifts the warehouse balance around joe cabot's finger on the rat, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Rat_Suspicion),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Rat_Suspicion[char_white][char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_white][char_pink]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_pink.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Rat_Suspicion[char_white][char_pink]),-0.35),MUL(MUL(P(char_white.Crew_Loyalty),0.5),MUL(P(char_orange.Rat_Suspicion),0.5)),C(-0.01))

OPT opt_page_cabot_verdict_1: Demand Joe prove how an undercover plant passed Eddie's vetting
  RXN rxn_page_cabot_verdict_1_0 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around joe cabot's finger on the rat, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Rat_Suspicion),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Rat_Suspicion[char_white][char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_white][char_pink]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_pink.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Rat_Suspicion[char_white][char_pink]),0.45),ABSOLUTE VALUE(MUL(P(char_pink.Rat_Suspicion),0.35)),C(0.06))

  RXN rxn_page_cabot_verdict_1_1 -> page_mexican_standoff
    T: Mr. White shifts the warehouse balance around joe cabot's finger on the rat, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Rat_Suspicion),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Rat_Suspicion[char_white][char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_white][char_pink]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_pink.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),-0.5),MUL(P(char_orange.Rat_Suspicion[char_white][char_pink]),-0.35),MUL(MUL(P(char_white.Crew_Loyalty),0.5),MUL(P(char_orange.Rat_Suspicion),0.5)),C(0.04))

  RXN rxn_page_cabot_verdict_1_2 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around joe cabot's finger on the rat, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Rat_Suspicion),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Rat_Suspicion[char_white][char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_white][char_pink]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_pink.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Rat_Suspicion[char_white][char_pink]),-0.35),MAX(MUL(P(char_pink.Diamond_Leverage),0.3),C(-0.15)),C(0.02))

OPT opt_page_cabot_verdict_2: Watch Pink slide behind the ramp with the Karina diamond satchel
  RXN rxn_page_cabot_verdict_2_0 -> page_mexican_standoff
    T: Mr. White shifts the warehouse balance around joe cabot's finger on the rat, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Rat_Suspicion),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Rat_Suspicion[char_white][char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_white][char_pink]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_pink.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Rat_Suspicion[char_white][char_pink]),0.45),MUL(MUL(P(char_white.Crew_Loyalty),0.5),MUL(P(char_orange.Rat_Suspicion),0.5)),C(0.09))

  RXN rxn_page_cabot_verdict_2_1 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around joe cabot's finger on the rat, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Rat_Suspicion),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Rat_Suspicion[char_white][char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_white][char_pink]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_pink.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),-0.5),MUL(P(char_orange.Rat_Suspicion[char_white][char_pink]),-0.35),MAX(MUL(P(char_pink.Diamond_Leverage),0.3),C(-0.15)),C(0.07))

  RXN rxn_page_cabot_verdict_2_2 -> page_mexican_standoff
    T: Mr. White shifts the warehouse balance around joe cabot's finger on the rat, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Rat_Suspicion),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Rat_Suspicion[char_white][char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_white][char_pink]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_pink.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Rat_Suspicion[char_white][char_pink]),-0.35),ABSOLUTE VALUE(MUL(P(char_pink.Rat_Suspicion),0.35)),C(0.05))

OPT opt_page_cabot_verdict_3: Confront Orange directly with the rehearsed commode story tell
  RXN rxn_page_cabot_verdict_3_0 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around joe cabot's finger on the rat, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Rat_Suspicion),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Rat_Suspicion[char_white][char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_white][char_pink]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_pink.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Rat_Suspicion[char_white][char_pink]),0.45),MAX(MUL(P(char_pink.Diamond_Leverage),0.3),C(-0.15)),C(0.12))

  RXN rxn_page_cabot_verdict_3_1 -> page_mexican_standoff
    T: Mr. White shifts the warehouse balance around joe cabot's finger on the rat, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Rat_Suspicion),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Rat_Suspicion[char_white][char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_white][char_pink]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_pink.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),-0.5),MUL(P(char_orange.Rat_Suspicion[char_white][char_pink]),-0.35),ABSOLUTE VALUE(MUL(P(char_pink.Rat_Suspicion),0.35)),C(0.1))

  RXN rxn_page_cabot_verdict_3_2 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around joe cabot's finger on the rat, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Rat_Suspicion = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Rat_Suspicion),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Rat_Suspicion[char_white][char_pink] = NUDGE(P(char_orange.Rat_Suspicion[char_white][char_pink]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Rat_Suspicion),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_pink.Rat_Suspicion),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Rat_Suspicion[char_white][char_pink]),-0.35),MUL(MUL(P(char_white.Crew_Loyalty),0.5),MUL(P(char_orange.Rat_Suspicion),0.5)),C(0.08))


## ENC page_mexican_standoff | Three Hammers Cocked in a Triangle | turn=12..14 | spools=[spool_act3_standoff]
T: Three heavy pistols lock into an impossible Mexican standoff: Joe aims down at Mr. Orange, Mr. White aims across at Joe's temple, and Nice Guy Eddie aims straight at White's chest, screaming for everybody to lower their iron before all three die on concrete. Every breath inside the shuttered mortuary smells of cordite, stale coffee, and drying arterial blood, forcing each survivor to weigh professional discipline against the creeping certainty that an LAPD plant sold out the crew.

OPT opt_page_mexican_standoff_0: Keep your sights welded to Joe's head and refuse to blink
  RXN rxn_page_mexican_standoff_0_0 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around three hammers cocked in a triangle, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(-0.09),MUL(P(char_white.Sadistic_Escalation),0.06))))
      SET char_pink.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_pink.Professional_Discipline[char_white][char_orange]),ADD(C(-0.07),MUL(P(char_white.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Sadistic_Escalation),0.02)))
      SET char_white.Sadistic_Escalation = NUDGE(P(char_white.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_white.Sadistic_Escalation[char_pink] = NUDGE(P(char_white.Sadistic_Escalation[char_pink]),ADD(C(0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
    D: ADD(MUL(P(char_white.Sadistic_Escalation[char_pink]),0.65),MUL(P(char_pink.Professional_Discipline[char_white][char_orange]),0.45),ABSOLUTE VALUE(MUL(P(char_orange.Professional_Discipline),0.35)),C(0.03))

  RXN rxn_page_mexican_standoff_0_1 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around three hammers cocked in a triangle, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(-0.09),MUL(P(char_white.Sadistic_Escalation),0.06))))
      SET char_pink.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_pink.Professional_Discipline[char_white][char_orange]),ADD(C(-0.07),MUL(P(char_white.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Sadistic_Escalation),0.02)))
      SET char_white.Sadistic_Escalation = NUDGE(P(char_white.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_white.Sadistic_Escalation[char_pink] = NUDGE(P(char_white.Sadistic_Escalation[char_pink]),ADD(C(-0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
    D: ADD(MUL(P(char_white.Sadistic_Escalation[char_pink]),-0.5),MUL(P(char_pink.Professional_Discipline[char_white][char_orange]),-0.35),MUL(MUL(P(char_white.Sadistic_Escalation),0.5),MUL(P(char_pink.Professional_Discipline),0.5)),C(0.01))

  RXN rxn_page_mexican_standoff_0_2 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around three hammers cocked in a triangle, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(-0.09),MUL(P(char_white.Sadistic_Escalation),0.06))))
      SET char_pink.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_pink.Professional_Discipline[char_white][char_orange]),ADD(C(-0.07),MUL(P(char_white.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Sadistic_Escalation),0.02)))
      SET char_white.Sadistic_Escalation = NUDGE(P(char_white.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_white.Sadistic_Escalation[char_pink] = NUDGE(P(char_white.Sadistic_Escalation[char_pink]),ADD(C(0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
    D: ADD(MUL(P(char_white.Sadistic_Escalation[char_pink]),0.65),MUL(P(char_pink.Professional_Discipline[char_white][char_orange]),-0.35),MAX(MUL(P(char_orange.Diamond_Leverage),0.3),C(-0.15)),C(-0.01))

OPT opt_page_mexican_standoff_1: Shout Pink's name to broker a ten-second barrel drop
  RXN rxn_page_mexican_standoff_1_0 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around three hammers cocked in a triangle, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(0.09),MUL(P(char_white.Sadistic_Escalation),0.06))))
      SET char_pink.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_pink.Professional_Discipline[char_white][char_orange]),ADD(C(0.07),MUL(P(char_white.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Sadistic_Escalation),0.02)))
      SET char_white.Sadistic_Escalation = NUDGE(P(char_white.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_white.Sadistic_Escalation[char_pink] = NUDGE(P(char_white.Sadistic_Escalation[char_pink]),ADD(C(-0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
    D: ADD(MUL(P(char_white.Sadistic_Escalation[char_pink]),0.65),MUL(P(char_pink.Professional_Discipline[char_white][char_orange]),0.45),MUL(MUL(P(char_white.Sadistic_Escalation),0.5),MUL(P(char_pink.Professional_Discipline),0.5)),C(0.06))

  RXN rxn_page_mexican_standoff_1_1 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around three hammers cocked in a triangle, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(0.09),MUL(P(char_white.Sadistic_Escalation),0.06))))
      SET char_pink.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_pink.Professional_Discipline[char_white][char_orange]),ADD(C(0.07),MUL(P(char_white.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Sadistic_Escalation),0.02)))
      SET char_white.Sadistic_Escalation = NUDGE(P(char_white.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_white.Sadistic_Escalation[char_pink] = NUDGE(P(char_white.Sadistic_Escalation[char_pink]),ADD(C(0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
    D: ADD(MUL(P(char_white.Sadistic_Escalation[char_pink]),-0.5),MUL(P(char_pink.Professional_Discipline[char_white][char_orange]),-0.35),MAX(MUL(P(char_orange.Diamond_Leverage),0.3),C(-0.15)),C(0.04))

  RXN rxn_page_mexican_standoff_1_2 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around three hammers cocked in a triangle, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(0.09),MUL(P(char_white.Sadistic_Escalation),0.06))))
      SET char_pink.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_pink.Professional_Discipline[char_white][char_orange]),ADD(C(0.07),MUL(P(char_white.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Sadistic_Escalation),0.02)))
      SET char_white.Sadistic_Escalation = NUDGE(P(char_white.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_white.Sadistic_Escalation[char_pink] = NUDGE(P(char_white.Sadistic_Escalation[char_pink]),ADD(C(-0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
    D: ADD(MUL(P(char_white.Sadistic_Escalation[char_pink]),0.65),MUL(P(char_pink.Professional_Discipline[char_white][char_orange]),-0.35),ABSOLUTE VALUE(MUL(P(char_orange.Professional_Discipline),0.35)),C(0.02))

OPT opt_page_mexican_standoff_2: Drop aim half an inch to bargain Orange's life for the satchel
  RXN rxn_page_mexican_standoff_2_0 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around three hammers cocked in a triangle, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(-0.09),MUL(P(char_white.Sadistic_Escalation),0.06))))
      SET char_pink.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_pink.Professional_Discipline[char_white][char_orange]),ADD(C(-0.07),MUL(P(char_white.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Sadistic_Escalation),0.02)))
      SET char_white.Sadistic_Escalation = NUDGE(P(char_white.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_white.Sadistic_Escalation[char_pink] = NUDGE(P(char_white.Sadistic_Escalation[char_pink]),ADD(C(0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
    D: ADD(MUL(P(char_white.Sadistic_Escalation[char_pink]),0.65),MUL(P(char_pink.Professional_Discipline[char_white][char_orange]),0.45),MAX(MUL(P(char_orange.Diamond_Leverage),0.3),C(-0.15)),C(0.09))

  RXN rxn_page_mexican_standoff_2_1 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around three hammers cocked in a triangle, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(-0.09),MUL(P(char_white.Sadistic_Escalation),0.06))))
      SET char_pink.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_pink.Professional_Discipline[char_white][char_orange]),ADD(C(-0.07),MUL(P(char_white.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Sadistic_Escalation),0.02)))
      SET char_white.Sadistic_Escalation = NUDGE(P(char_white.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_white.Sadistic_Escalation[char_pink] = NUDGE(P(char_white.Sadistic_Escalation[char_pink]),ADD(C(-0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
    D: ADD(MUL(P(char_white.Sadistic_Escalation[char_pink]),-0.5),MUL(P(char_pink.Professional_Discipline[char_white][char_orange]),-0.35),ABSOLUTE VALUE(MUL(P(char_orange.Professional_Discipline),0.35)),C(0.07))

  RXN rxn_page_mexican_standoff_2_2 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around three hammers cocked in a triangle, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(-0.09),MUL(P(char_white.Sadistic_Escalation),0.06))))
      SET char_pink.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_pink.Professional_Discipline[char_white][char_orange]),ADD(C(-0.07),MUL(P(char_white.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Sadistic_Escalation),0.02)))
      SET char_white.Sadistic_Escalation = NUDGE(P(char_white.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_white.Sadistic_Escalation[char_pink] = NUDGE(P(char_white.Sadistic_Escalation[char_pink]),ADD(C(0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
    D: ADD(MUL(P(char_white.Sadistic_Escalation[char_pink]),0.65),MUL(P(char_pink.Professional_Discipline[char_white][char_orange]),-0.35),MUL(MUL(P(char_white.Sadistic_Escalation),0.5),MUL(P(char_pink.Professional_Discipline),0.5)),C(0.05))

OPT opt_page_mexican_standoff_3: Back toward the drainage door with Pink while the Cabots freeze
  RXN rxn_page_mexican_standoff_3_0 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around three hammers cocked in a triangle, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(0.09),MUL(P(char_white.Sadistic_Escalation),0.06))))
      SET char_pink.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_pink.Professional_Discipline[char_white][char_orange]),ADD(C(0.07),MUL(P(char_white.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Sadistic_Escalation),0.02)))
      SET char_white.Sadistic_Escalation = NUDGE(P(char_white.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_white.Sadistic_Escalation[char_pink] = NUDGE(P(char_white.Sadistic_Escalation[char_pink]),ADD(C(-0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
    D: ADD(MUL(P(char_white.Sadistic_Escalation[char_pink]),0.65),MUL(P(char_pink.Professional_Discipline[char_white][char_orange]),0.45),ABSOLUTE VALUE(MUL(P(char_orange.Professional_Discipline),0.35)),C(0.12))

  RXN rxn_page_mexican_standoff_3_1 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around three hammers cocked in a triangle, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(0.09),MUL(P(char_white.Sadistic_Escalation),0.06))))
      SET char_pink.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_pink.Professional_Discipline[char_white][char_orange]),ADD(C(0.07),MUL(P(char_white.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Sadistic_Escalation),0.02)))
      SET char_white.Sadistic_Escalation = NUDGE(P(char_white.Sadistic_Escalation),ADD(C(0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_white.Sadistic_Escalation[char_pink] = NUDGE(P(char_white.Sadistic_Escalation[char_pink]),ADD(C(0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
    D: ADD(MUL(P(char_white.Sadistic_Escalation[char_pink]),-0.5),MUL(P(char_pink.Professional_Discipline[char_white][char_orange]),-0.35),MUL(MUL(P(char_white.Sadistic_Escalation),0.5),MUL(P(char_pink.Professional_Discipline),0.5)),C(0.1))

  RXN rxn_page_mexican_standoff_3_2 -> page_sirens_at_the_rollup_door
    T: Mr. White shifts the warehouse balance around three hammers cocked in a triangle, testing Mr. Pink's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_pink.Professional_Discipline = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_pink.Professional_Discipline),C(0.09),MUL(P(char_white.Sadistic_Escalation),0.06))))
      SET char_pink.Professional_Discipline[char_white][char_orange] = NUDGE(P(char_pink.Professional_Discipline[char_white][char_orange]),ADD(C(0.07),MUL(P(char_white.Sadistic_Escalation),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Sadistic_Escalation),0.02)))
      SET char_white.Sadistic_Escalation = NUDGE(P(char_white.Sadistic_Escalation),ADD(C(-0.11),MUL(P(char_pink.Professional_Discipline),0.08)))
      SET char_white.Sadistic_Escalation[char_pink] = NUDGE(P(char_white.Sadistic_Escalation[char_pink]),ADD(C(-0.08),MUL(P(char_orange.Professional_Discipline),0.05)))
    D: ADD(MUL(P(char_white.Sadistic_Escalation[char_pink]),0.65),MUL(P(char_pink.Professional_Discipline[char_white][char_orange]),-0.35),MAX(MUL(P(char_orange.Diamond_Leverage),0.3),C(-0.15)),C(0.08))


## ENC page_sirens_at_the_rollup_door | Sirens Outside the Mortuary Door | turn=13..16 | spools=[spool_act3_standoff]
T: Tires screech across gravel outside the corrugated steel door as LAPD bullhorns crackle down the block. Inside the gunpowder haze, every lie told since breakfast at Uncle Bob's Pancake House comes due over a briefcase of stones and a bleeding undercover cop. Every breath inside the shuttered mortuary smells of cordite, stale coffee, and drying arterial blood, forcing each survivor to weigh professional discipline against the creeping certainty that an LAPD plant sold out the crew.

OPT opt_page_sirens_at_the_rollup_door_0: Hold Orange's head, whispering his final truth in the blood
  RXN rxn_page_sirens_at_the_rollup_door_0_0 -> wild
    T: Mr. White shifts the warehouse balance around sirens outside the mortuary door, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Diamond_Leverage = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Diamond_Leverage),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Diamond_Leverage[char_white][char_blonde] = NUDGE(P(char_orange.Diamond_Leverage[char_white][char_blonde]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Diamond_Leverage),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_blonde.Diamond_Leverage),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Diamond_Leverage[char_white][char_blonde]),0.45),MUL(MUL(P(char_white.Crew_Loyalty),0.5),MUL(P(char_orange.Diamond_Leverage),0.5)),C(0.03))

  RXN rxn_page_sirens_at_the_rollup_door_0_1 -> wild
    T: Mr. White shifts the warehouse balance around sirens outside the mortuary door, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Diamond_Leverage = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Diamond_Leverage),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Diamond_Leverage[char_white][char_blonde] = NUDGE(P(char_orange.Diamond_Leverage[char_white][char_blonde]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Diamond_Leverage),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_blonde.Diamond_Leverage),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),-0.5),MUL(P(char_orange.Diamond_Leverage[char_white][char_blonde]),-0.35),MAX(MUL(P(char_blonde.Diamond_Leverage),0.3),C(-0.15)),C(0.01))

  RXN rxn_page_sirens_at_the_rollup_door_0_2 -> wild
    T: Mr. White shifts the warehouse balance around sirens outside the mortuary door, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Diamond_Leverage = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Diamond_Leverage),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Diamond_Leverage[char_white][char_blonde] = NUDGE(P(char_orange.Diamond_Leverage[char_white][char_blonde]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Diamond_Leverage),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_blonde.Diamond_Leverage),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Diamond_Leverage[char_white][char_blonde]),-0.35),ABSOLUTE VALUE(MUL(P(char_blonde.Diamond_Leverage),0.35)),C(-0.01))

OPT opt_page_sirens_at_the_rollup_door_1: Grab the satchel, Pink, and bolt through the side alley
  RXN rxn_page_sirens_at_the_rollup_door_1_0 -> wild
    T: Mr. White shifts the warehouse balance around sirens outside the mortuary door, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Diamond_Leverage = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Diamond_Leverage),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Diamond_Leverage[char_white][char_blonde] = NUDGE(P(char_orange.Diamond_Leverage[char_white][char_blonde]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Diamond_Leverage),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_blonde.Diamond_Leverage),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Diamond_Leverage[char_white][char_blonde]),0.45),MAX(MUL(P(char_blonde.Diamond_Leverage),0.3),C(-0.15)),C(0.06))

  RXN rxn_page_sirens_at_the_rollup_door_1_1 -> wild
    T: Mr. White shifts the warehouse balance around sirens outside the mortuary door, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Diamond_Leverage = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Diamond_Leverage),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Diamond_Leverage[char_white][char_blonde] = NUDGE(P(char_orange.Diamond_Leverage[char_white][char_blonde]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Diamond_Leverage),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_blonde.Diamond_Leverage),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),-0.5),MUL(P(char_orange.Diamond_Leverage[char_white][char_blonde]),-0.35),ABSOLUTE VALUE(MUL(P(char_blonde.Diamond_Leverage),0.35)),C(0.04))

  RXN rxn_page_sirens_at_the_rollup_door_1_2 -> wild
    T: Mr. White shifts the warehouse balance around sirens outside the mortuary door, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Diamond_Leverage = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Diamond_Leverage),C(0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Diamond_Leverage[char_white][char_blonde] = NUDGE(P(char_orange.Diamond_Leverage[char_white][char_blonde]),ADD(C(0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Diamond_Leverage),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_blonde.Diamond_Leverage),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Diamond_Leverage[char_white][char_blonde]),-0.35),MUL(MUL(P(char_white.Crew_Loyalty),0.5),MUL(P(char_orange.Diamond_Leverage),0.5)),C(0.02))

OPT opt_page_sirens_at_the_rollup_door_2: Cut a cold professional truce before SWAT rams the door
  RXN rxn_page_sirens_at_the_rollup_door_2_0 -> wild
    T: Mr. White shifts the warehouse balance around sirens outside the mortuary door, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Diamond_Leverage = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Diamond_Leverage),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Diamond_Leverage[char_white][char_blonde] = NUDGE(P(char_orange.Diamond_Leverage[char_white][char_blonde]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Diamond_Leverage),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_blonde.Diamond_Leverage),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Diamond_Leverage[char_white][char_blonde]),0.45),ABSOLUTE VALUE(MUL(P(char_blonde.Diamond_Leverage),0.35)),C(0.09))

  RXN rxn_page_sirens_at_the_rollup_door_2_1 -> wild
    T: Mr. White shifts the warehouse balance around sirens outside the mortuary door, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Diamond_Leverage = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Diamond_Leverage),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Diamond_Leverage[char_white][char_blonde] = NUDGE(P(char_orange.Diamond_Leverage[char_white][char_blonde]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(-0.11),MUL(P(char_orange.Diamond_Leverage),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(-0.08),MUL(P(char_blonde.Diamond_Leverage),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),-0.5),MUL(P(char_orange.Diamond_Leverage[char_white][char_blonde]),-0.35),MUL(MUL(P(char_white.Crew_Loyalty),0.5),MUL(P(char_orange.Diamond_Leverage),0.5)),C(0.07))

  RXN rxn_page_sirens_at_the_rollup_door_2_2 -> wild
    T: Mr. White shifts the warehouse balance around sirens outside the mortuary door, testing Mr. Orange's nerve while everybody tracks the hidden satchel, the bleeding ramp, and the LAPD trap outside.
    E:
      SET char_orange.Diamond_Leverage = MAX(C(-0.95),MIN(C(0.95),ADD(P(char_orange.Diamond_Leverage),C(-0.09),MUL(P(char_white.Crew_Loyalty),0.06))))
      SET char_orange.Diamond_Leverage[char_white][char_blonde] = NUDGE(P(char_orange.Diamond_Leverage[char_white][char_blonde]),ADD(C(-0.07),MUL(P(char_white.Crew_Loyalty),0.05)))
      SET char_white.Crew_Loyalty = NUDGE(P(char_white.Crew_Loyalty),ADD(C(0.11),MUL(P(char_orange.Diamond_Leverage),0.08)))
      SET char_white.Crew_Loyalty[char_orange] = NUDGE(P(char_white.Crew_Loyalty[char_orange]),ADD(C(0.08),MUL(P(char_blonde.Diamond_Leverage),0.05)))
      SET char_white.Phase_Clock = NUDGE(P(char_white.Phase_Clock),ADD(C(0.09),MUL(P(char_white.Crew_Loyalty),0.02)))
    D: ADD(MUL(P(char_white.Crew_Loyalty[char_orange]),0.65),MUL(P(char_orange.Diamond_Leverage[char_white][char_blonde]),-0.35),MAX(MUL(P(char_blonde.Diamond_Leverage),0.3),C(-0.15)),C(0.05))


## ENC page_end_mexican_standoff_collapse | Dead Men in Black Suits | turn=6..20 | spools=[spool_endings]
T: Joe fires at Orange, White shoots Joe, Eddie shoots White, and White drops Eddie in a deafening three-second thunderclap. Crawling across the blood-slick floor to cradle Freddy's head, Larry hears the whispered truth—'I'm a cop'—and presses his barrel under Orange's chin as police boots burst open the warehouse door in a hail of rifle fire.


## ENC page_end_pink_ghosts_with_stones | The Only Professional Left Standing | turn=6..20 | spools=[spool_endings]
T: While ego and blood oaths detonate the center of the warehouse, Mr. Pink stays crouched beneath the wooden ramp with both hands locked around the Karina diamond satchel. Slipping into the sun-bleached alley seconds before SWAT rams the front rollup, the only man who treated the heist like a job vanishes into the sirens with two million in uncut stones.


## ENC page_end_blonde_gasoline_inferno | K-Billy's Funeral Pyre | turn=6..20 | spools=[spool_endings]
T: Unchecked sadism turns the safehouse into an inferno as spilled gasoline catches a stray muzzle flash under the tinny groove of seventies AM radio. Black smoke pours from the mortuary vents before Joe Cabot's sedan even clears the corner, drawing every patrol unit in East Los Angeles onto ashes, melted tape, and ruined alibis.


## ENC page_end_cabot_executes_the_plant | Joe Cabot Cleans House | turn=6..20 | spools=[spool_endings]
T: Convinced by the timeline gaps and Pink's cold ambush arithmetic, Mr. White lowers his forty-five half an inch when Joe Cabot calls Freddy Newandyke a plant. Joe finishes the job without blinking, tosses Pink the car keys, and scatters the surviving crew through freight yards two minutes ahead of the robbery-homicide encirclement.


## ENC page_end_white_mercy_hospital_trap | Triage Handcuffs at County General | turn=6..20 | spools=[spool_endings]
T: Refusing to watch the kid bleed out on concrete for Joe Cabot's rules, Larry Dimmick abandons the diamond split and shoulders Freddy into a stolen sedan bound for emergency surgery. Under harsh triage fluorescents, detectives greet Mr. White with drawn service weapons while Freddy grips his sleeve from the gurney, saved by the thief he was sent to cage.


## ENC page_secret_undercover_truce | Secret Ending: The Commode Tell and the Culvert Exit | turn=6..20 | spools=[spool_endings]
T: Catching the rehearsed squad-room cadence in Orange's anecdote without letting Blonde's razor blow the room apart, White and Pink force a quiet confession before Joe Cabot ever reaches the block. Leaving Marvin Nash alive beside Freddy with a ninety-second ambulance call, Larry and Pink slip down the dry storm culvert with the Karina satchel—no massacre, no cuffs, and one haunted debt paid in full.
