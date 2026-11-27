---
title: "The Hat That Held the Moon"
storyworld_id: "SW-INKY-CAT-HAT-20261123"
source_format: "SWMD-0-MIN"
state_variables: ["trust", "nerve", "care"]
endings:
  - id: "end_return"
    type: "bittersweet"
    condition: "Pip returns the hat to the well and the moon drifts back to its proper distance."
    expected_critic_score: 8
  - id: "end_keep"
    type: "dark"
    condition: "Pip keeps the hat; the moon stays close and the village never sleeps again."
    expected_critic_score: 4
  - id: "end_share"
    type: "hopeful"
    condition: "Pip shares the hat with Mara and Old Fen; the moon hums once and fades."
    expected_critic_score: 9
  - id: "end_fallback"
    type: "ambiguous"
    condition: "No clear choice is made; the moon hums and the story fades to a quiet night."
    expected_critic_score: 6
---

# SWMD-0-MIN
id: SW-INKY-CAT-HAT-20261123
title: The Hat That Held the Moon

ENC enc_01 turn=0..999
# T: Pip crouches in the alley behind the bakery, paws on the cobblestones, staring at a floppy gray hat with star-stitched brim. It hums faintly, like a kettle just before it boils. The moon is rising over the village rooftops, and the hat seems to lean toward it, waiting.
# TITLE: Pip finds the humming hat
# ART: A floppy star-stitched gray hat on a cobblestone alley, moonlight pooling around it, Pip's curious eyes wide.
ORX opt_01_1/rxn_01_1_1 -> enc_02 | O:Pick up the hat and feel its hum | E:SET char_pip.trust += 0.1; SET char_pip.nerve += -0.05; SET char_pip.care += 0.08 | D:ADD(MUL(P(char_pip.trust),0.4),MUL(P(char_pip.nerve),0.2),MUL(P(char_pip.care),0.3))
# R rxn_01_1_1: The hum rises when Pip lifts it, warm as bread from the oven.
ORX opt_01_1/rxn_01_1_2 -> enc_03 | O:Pick up the hat and feel its hum | E:SET char_pip.trust += -0.08; SET char_pip.nerve += 0.12; SET char_pip.care += -0.06 | D:ADD(MUL(P(char_pip.trust),-0.4),MUL(P(char_pip.nerve),-0.2),MUL(P(char_pip.care),-0.3))
# R rxn_01_1_2: The hat seems to lean toward the moon, waiting for someone to wear it.
ORX opt_01_2/rxn_01_2_1 -> enc_02 | O:Ask Mara what the hat is | E:SET char_pip.trust += 0.15; SET char_pip.nerve += 0.1; SET char_pip.care += -0.12 | D:ADD(MUL(P(char_pip.trust),-0.3),MUL(P(char_pip.nerve),0.5),MUL(P(char_pip.care),0.2))
# R rxn_01_2_1: Mara wipes flour from her hands: 'A bargain, dear. The moon likes a wearer.'
ORX opt_01_2/rxn_01_2_2 -> enc_03 | O:Ask Mara what the hat is | E:SET char_pip.trust += -0.1; SET char_pip.nerve += -0.08; SET char_pip.care += 0.14 | D:ADD(MUL(P(char_pip.trust),0.3),MUL(P(char_pip.nerve),-0.5),MUL(P(char_pip.care),-0.2))
# R rxn_01_2_2: Mara squints at the hat: 'Star-stitched. Someone sewed that with love.'
ORX opt_01_3/rxn_01_3_1 -> enc_02 | O:Leave it and go home | E:SET char_pip.trust += -0.12; SET char_pip.nerve += 0.18; SET char_pip.care += 0.06 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.25),MUL(P(char_pip.care),0.55))
# R rxn_01_3_1: Pip walks away, but the hum follows him like a small gray shadow.
ORX opt_01_3/rxn_01_3_2 -> enc_03 | O:Leave it and go home | E:SET char_pip.trust += 0.14; SET char_pip.nerve += -0.1; SET char_pip.care += -0.09 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.25),MUL(P(char_pip.care),-0.55))
# R rxn_01_3_2: The hat stays on the stone, humming softly to the moon.

ENC enc_02 turn=0..999
# T: The stray gray cat named Pip finds a floppy, star-stitched hat that hums when the moon rises. The hat promises to make its wearer 'the most interesting person in the village' — but every time Pip wears it, the moon grows a little closer.
# TITLE: The hat promises fame
# ART: A stray gray cat crouches in the alley behind the bakery, paws on the cobblestones, staring at a floppy gray hat with a star-stitched brim. The hat hums faintly, like a kettle just before it boils.
ORX opt_02_1/rxn_02_1_1 -> enc_03 | O:Put the hat on and feel the hum | E:SET char_pip.trust += 0.15; SET char_pip.nerve += 0.1; SET char_pip.care += -0.12 | D:ADD(MUL(P(char_pip.trust),-0.3),MUL(P(char_pip.nerve),0.5),MUL(P(char_pip.care),0.2))
# R rxn_02_1_1: The hum swells in your chest like a second heartbeat. The moon outside the window seems to lean closer, curious about what you have found.
ORX opt_02_1/rxn_02_1_2 -> enc_04 | O:Put the hat on and feel the hum | E:SET char_pip.trust += -0.1; SET char_pip.nerve += -0.08; SET char_pip.care += 0.14 | D:ADD(MUL(P(char_pip.trust),0.3),MUL(P(char_pip.nerve),-0.5),MUL(P(char_pip.care),-0.2))
# R rxn_02_1_2: The hat fits too well, as if it was waiting for you. The village seems to hold its breath, waiting to see what you will do next.
ORX opt_02_2/rxn_02_2_1 -> enc_03 | O:Ask the hat what it really wants | E:SET char_pip.trust += 0.1; SET char_pip.nerve += -0.05; SET char_pip.care += 0.08 | D:ADD(MUL(P(char_pip.trust),0.4),MUL(P(char_pip.nerve),0.2),MUL(P(char_pip.care),0.3))
# R rxn_02_2_1: The hum answers in a voice like wind through a chimney: 'I want to be worn by someone who notices the small things.'
ORX opt_02_2/rxn_02_2_2 -> enc_04 | O:Ask the hat what it really wants | E:SET char_pip.trust += -0.08; SET char_pip.nerve += 0.12; SET char_pip.care += -0.06 | D:ADD(MUL(P(char_pip.trust),-0.4),MUL(P(char_pip.nerve),-0.2),MUL(P(char_pip.care),-0.3))
# R rxn_02_2_2: The hat goes quiet, then whispers: 'I want to be worn by someone who is afraid of being ordinary.'
ORX opt_02_3/rxn_02_3_1 -> enc_03 | O:Leave the hat where it lies | E:SET char_pip.trust += -0.12; SET char_pip.nerve += 0.18; SET char_pip.care += 0.06 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.25),MUL(P(char_pip.care),0.55))
# R rxn_02_3_1: You step back. The hat hums once more, softer now, as if it understands you have chosen patience over curiosity.
ORX opt_02_3/rxn_02_3_2 -> enc_04 | O:Leave the hat where it lies | E:SET char_pip.trust += 0.14; SET char_pip.nerve += -0.1; SET char_pip.care += -0.09 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.25),MUL(P(char_pip.care),-0.55))
# R rxn_02_3_2: You leave it. The moon keeps its distance tonight, and the village sleeps on, unaware of the small humming mystery in the alley.

ENC enc_03 turn=0..999
# T: Pip finds the floppy, star-stitched hat resting on the well's coping stone, humming a low, patient note whenever the moon rises. The hat promises to make its wearer 'the most interesting person in the village' — but every time Pip wears it, the moon grows a little closer, and the hum grows louder. Mara the baker watches from her doorway, dry as ash, and Old Fen yawns by the well, sleepy as ever. Pip turns the hat in his paws, curious and a little vain about being interesting.
# TITLE: Pip decides to wear it
# ART: A floppy star-stitched hat glowing faintly on a stone well coping, moon rising behind it, Pip crouched beside it, Mara at her bakery door, Old Fen asleep by the well.
ORX opt_03_1/rxn_03_1_1 -> enc_04 | O:Put the hat on right away | E:SET char_pip.trust += 0.15; SET char_pip.nerve += 0.1; SET char_pip.care += -0.12 | D:ADD(MUL(P(char_pip.trust),-0.3),MUL(P(char_pip.nerve),0.5),MUL(P(char_pip.care),0.2))
# R rxn_03_1_1: Pip pulls the hat down over his ears and the whole village goes quiet, as if everyone is listening to the hum.
ORX opt_03_1/rxn_03_1_2 -> enc_05 | O:Put the hat on right away | E:SET char_pip.trust += -0.1; SET char_pip.nerve += -0.08; SET char_pip.care += 0.14 | D:ADD(MUL(P(char_pip.trust),0.3),MUL(P(char_pip.nerve),-0.5),MUL(P(char_pip.care),-0.2))
# R rxn_03_1_2: The hat settles on Pip's head like a second moon, and the hum swells until the stars seem to lean in.
ORX opt_03_2/rxn_03_2_1 -> enc_04 | O:Ask Mara what the hat really does | E:SET char_pip.trust += -0.12; SET char_pip.nerve += 0.18; SET char_pip.care += 0.06 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.25),MUL(P(char_pip.care),0.55))
# R rxn_03_2_1: Mara wipes flour from her hands and says, 'It makes you interesting. That is all it promises.'
ORX opt_03_2/rxn_03_2_2 -> enc_05 | O:Ask Mara what the hat really does | E:SET char_pip.trust += 0.14; SET char_pip.nerve += -0.1; SET char_pip.care += -0.09 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.25),MUL(P(char_pip.care),-0.55))
# R rxn_03_2_2: Mara squints at the hat, then at the moon, and mutters, 'Interesting, yes. Honest, no.'
ORX opt_03_3/rxn_03_3_1 -> enc_04 | O:Ask Old Fen about the humming | E:SET char_pip.trust += 0.1; SET char_pip.nerve += -0.05; SET char_pip.care += 0.08 | D:ADD(MUL(P(char_pip.trust),0.4),MUL(P(char_pip.nerve),0.2),MUL(P(char_pip.care),0.3))
# R rxn_03_3_1: Old Fen opens one eye. 'The moon hums when it is pleased. Wear it, and it will be pleased with you.'
ORX opt_03_3/rxn_03_3_2 -> enc_05 | O:Ask Old Fen about the humming | E:SET char_pip.trust += -0.08; SET char_pip.nerve += 0.12; SET char_pip.care += -0.06 | D:ADD(MUL(P(char_pip.trust),-0.4),MUL(P(char_pip.nerve),-0.2),MUL(P(char_pip.care),-0.3))
# R rxn_03_3_2: Old Fen yawns hugely. 'Interesting, eh? Well. The well hums too, when it is full.'

ENC enc_04 turn=0..999
# T: Pip lifts the floppy, star-stitched hat from the well's coping stone, and it hums a low, patient note whenever the moon rises. The hat promises to make its wearer 'the most interesting person in the village' — but every time Pip wears it, the moon grows a little closer.
# TITLE: The moon grows closer
# ART: A floppy star-stitched hat glowing faintly on a stone well coping, moonlight pooling around it like a held breath.
ORX opt_04_1/rxn_04_1_1 -> enc_05 | O:Put the hat on and walk into the village | E:SET char_pip.trust += 0.15; SET char_pip.nerve += 0.1; SET char_pip.care += -0.12 | D:ADD(MUL(P(char_pip.trust),-0.3),MUL(P(char_pip.nerve),0.5),MUL(P(char_pip.care),0.2))
# R rxn_04_1_1: The hat hums louder as Pip strides down the lane, and the moon swells a finger's width closer.
ORX opt_04_1/rxn_04_1_2 -> enc_06 | O:Put the hat on and walk into the village | E:SET char_pip.trust += -0.1; SET char_pip.nerve += -0.08; SET char_pip.care += 0.14 | D:ADD(MUL(P(char_pip.trust),0.3),MUL(P(char_pip.nerve),-0.5),MUL(P(char_pip.care),-0.2))
# R rxn_04_1_2: Pip grins, certain the village will finally notice them.
ORX opt_04_2/rxn_04_2_1 -> enc_07 | O:Ask Mara what the hat really does | E:SET char_pip.trust += 0.1; SET char_pip.nerve += -0.05; SET char_pip.care += 0.08 | D:ADD(MUL(P(char_pip.trust),0.4),MUL(P(char_pip.nerve),0.2),MUL(P(char_pip.care),0.3))
# R rxn_04_2_1: Mara wipes flour from her hands and says the hat feeds on attention, not kindness.
ORX opt_04_2/rxn_04_2_2 -> enc_08 | O:Ask Mara what the hat really does | E:SET char_pip.trust += -0.08; SET char_pip.nerve += 0.12; SET char_pip.care += -0.06 | D:ADD(MUL(P(char_pip.trust),-0.4),MUL(P(char_pip.nerve),-0.2),MUL(P(char_pip.care),-0.3))
# R rxn_04_2_2: Pip listens, unsure whether to trust the dry old baker.
ORX opt_04_3/rxn_04_3_1 -> enc_09 | O:Set the hat back on the stone and leave | E:SET char_pip.trust += -0.12; SET char_pip.nerve += 0.18; SET char_pip.care += 0.06 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.25),MUL(P(char_pip.care),0.55))
# R rxn_04_3_1: The hum fades to a whisper as Pip steps away, but the moon keeps watching.
ORX opt_04_3/rxn_04_3_2 -> enc_10 | O:Set the hat back on the stone and leave | E:SET char_pip.trust += 0.14; SET char_pip.nerve += -0.1; SET char_pip.care += -0.09 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.25),MUL(P(char_pip.care),-0.55))
# R rxn_04_3_2: Pip walks home slowly, carrying the weight of a choice not made.

ENC enc_05 turn=0..999
# T: Pip lifts the floppy, star-stitched hat from the well's coping stone, and it hums a low, patient note whenever the moon rises. The hat promises to make its wearer the most interesting person in the village, but every time Pip wears it, the moon grows a little closer.
# TITLE: The village grows sleepy
# ART: A floppy star-stitched hat resting on a mossy well coping stone, with a faint silver glow rising from its brim like a held breath.
ORX opt_05_1/rxn_05_1_1 -> enc_06 | O:Wear the hat and let the moon draw nearer | E:SET char_pip.trust += 0.15; SET char_pip.nerve += 0.1; SET char_pip.care += -0.12 | D:ADD(MUL(P(char_pip.trust),-0.3),MUL(P(char_pip.nerve),0.5),MUL(P(char_pip.care),0.2))
# R rxn_05_1_1: The moon hums louder, curious about the new light.
ORX opt_05_1/rxn_05_1_2 -> enc_07 | O:Wear the hat and let the moon draw nearer | E:SET char_pip.trust += -0.1; SET char_pip.nerve += -0.08; SET char_pip.care += 0.14 | D:ADD(MUL(P(char_pip.trust),0.3),MUL(P(char_pip.nerve),-0.5),MUL(P(char_pip.care),-0.2))
# R rxn_05_1_2: The village goes quiet, waiting to see what Pip will say next.
ORX opt_05_2/rxn_05_2_1 -> enc_06 | O:Keep the hat hidden and stay ordinary | E:SET char_pip.trust += 0.1; SET char_pip.nerve += -0.05; SET char_pip.care += 0.08 | D:ADD(MUL(P(char_pip.trust),0.4),MUL(P(char_pip.nerve),0.2),MUL(P(char_pip.care),0.3))
# R rxn_05_2_1: The hat hums softly, content to wait in the dark.
ORX opt_05_2/rxn_05_2_2 -> enc_07 | O:Keep the hat hidden and stay ordinary | E:SET char_pip.trust += -0.08; SET char_pip.nerve += 0.12; SET char_pip.care += -0.06 | D:ADD(MUL(P(char_pip.trust),-0.4),MUL(P(char_pip.nerve),-0.2),MUL(P(char_pip.care),-0.3))
# R rxn_05_2_2: The moon stays far away, and the village keeps its quiet.
ORX opt_05_3/rxn_05_3_1 -> enc_06 | O:Ask the hat what it really wants | E:SET char_pip.trust += -0.12; SET char_pip.nerve += 0.18; SET char_pip.care += 0.06 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.25),MUL(P(char_pip.care),0.55))
# R rxn_05_3_1: The hat hums a question back, unhurried and old.
ORX opt_05_3/rxn_05_3_2 -> enc_07 | O:Ask the hat what it really wants | E:SET char_pip.trust += 0.14; SET char_pip.nerve += -0.1; SET char_pip.care += -0.09 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.25),MUL(P(char_pip.care),-0.55))
# R rxn_05_3_2: The moon leans closer, listening to the question.

ENC enc_06 turn=0..999
# T: The hat hums a low, patient note whenever the moon rises, and Pip feels the village lean in to listen. Mara the baker watches from her doorway, dry and tired, while Old Fen keeps the well and the moon grows a little closer with every wear.
# TITLE: Pip becomes talked about
# ART: A baker's doorway glowing amber against a deepening blue dusk, with a small hat resting on the step and the moon rising just above the rooftops.
ORX opt_06_1/rxn_06_1_1 -> enc_07 | O:Wear the hat and let the moon draw nearer | E:SET char_pip.trust += 0.15; SET char_pip.nerve += 0.1; SET char_pip.care += -0.12 | D:ADD(MUL(P(char_pip.trust),-0.3),MUL(P(char_pip.nerve),0.5),MUL(P(char_pip.care),0.2))
# R rxn_06_1_1: The moon hums louder, curious about the new light.
ORX opt_06_1/rxn_06_1_2 -> enc_08 | O:Wear the hat and let the moon draw nearer | E:SET char_pip.trust += -0.1; SET char_pip.nerve += -0.08; SET char_pip.care += 0.14 | D:ADD(MUL(P(char_pip.trust),0.3),MUL(P(char_pip.nerve),-0.5),MUL(P(char_pip.care),-0.2))
# R rxn_06_1_2: The village goes quiet, waiting to see what Pip will say next.
ORX opt_06_2/rxn_06_2_1 -> enc_07 | O:Keep the hat hidden and stay ordinary | E:SET char_pip.trust += 0.1; SET char_pip.nerve += -0.05; SET char_pip.care += 0.08 | D:ADD(MUL(P(char_pip.trust),0.4),MUL(P(char_pip.nerve),0.2),MUL(P(char_pip.care),0.3))
# R rxn_06_2_1: The hat hums softly, content to wait in the dark.
ORX opt_06_2/rxn_06_2_2 -> enc_08 | O:Keep the hat hidden and stay ordinary | E:SET char_pip.trust += -0.08; SET char_pip.nerve += 0.12; SET char_pip.care += -0.06 | D:ADD(MUL(P(char_pip.trust),-0.4),MUL(P(char_pip.nerve),-0.2),MUL(P(char_pip.care),-0.3))
# R rxn_06_2_2: The moon stays far away, and the village keeps its quiet.
ORX opt_06_3/rxn_06_3_1 -> enc_07 | O:Ask the hat what it really wants | E:SET char_pip.trust += -0.12; SET char_pip.nerve += 0.18; SET char_pip.care += 0.06 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.25),MUL(P(char_pip.care),0.55))
# R rxn_06_3_1: The hat hums a question back, unhurried and old.
ORX opt_06_3/rxn_06_3_2 -> enc_08 | O:Ask the hat what it really wants | E:SET char_pip.trust += 0.14; SET char_pip.nerve += -0.1; SET char_pip.care += -0.09 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.25),MUL(P(char_pip.care),-0.55))
# R rxn_06_3_2: The moon leans closer, listening to the question.

ENC enc_07 turn=0..999
# T: Mara the baker watches from her doorway as the moon presses low over the rooftops, its light pooling like honey on the cobbles. Pip, wearing the star-stitched hat, struts past with a grin, and the whole village seems to lean in to listen.
# TITLE: Mara notices the change
# ART: A floppy star-stitched hat glowing faintly on a gray cat's head, moonlight pooling on cobblestones, Mara silhouetted at her door with flour on her hands.
ORX opt_07_1/rxn_07_1_1 -> enc_08 | O:Ask Mara what the moon means | E:SET char_pip.trust += 0.1; SET char_pip.nerve += -0.05; SET char_pip.care += 0.08 | D:ADD(MUL(P(char_pip.trust),0.4),MUL(P(char_pip.nerve),0.2),MUL(P(char_pip.care),0.3))
# R rxn_07_1_1: Mara: 'It means the village is listening to you, Pip.'
ORX opt_07_1/rxn_07_1_2 -> enc_08 | O:Ask Mara what the moon means | E:SET char_pip.trust += -0.08; SET char_pip.nerve += 0.12; SET char_pip.care += -0.06 | D:ADD(MUL(P(char_pip.trust),-0.4),MUL(P(char_pip.nerve),-0.2),MUL(P(char_pip.care),-0.3))
# R rxn_07_1_2: Mara: 'It means you've been wearing that hat too long.'
ORX opt_07_2/rxn_07_2_1 -> enc_08 | O:Show off the hat to Mara | E:SET char_pip.trust += 0.15; SET char_pip.nerve += 0.1; SET char_pip.care += -0.12 | D:ADD(MUL(P(char_pip.trust),-0.3),MUL(P(char_pip.nerve),0.5),MUL(P(char_pip.care),0.2))
# R rxn_07_2_1: Mara: 'Bold. I like it.'
ORX opt_07_2/rxn_07_2_2 -> enc_08 | O:Show off the hat to Mara | E:SET char_pip.trust += -0.1; SET char_pip.nerve += -0.08; SET char_pip.care += 0.14 | D:ADD(MUL(P(char_pip.trust),0.3),MUL(P(char_pip.nerve),-0.5),MUL(P(char_pip.care),-0.2))
# R rxn_07_2_2: Mara: 'Bold is a word for people who don't sleep.'
ORX opt_07_3/rxn_07_3_1 -> enc_08 | O:Offer Mara a warm bun | E:SET char_pip.trust += -0.12; SET char_pip.nerve += 0.18; SET char_pip.care += 0.06 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.25),MUL(P(char_pip.care),0.55))
# R rxn_07_3_1: Mara: 'A bun? For the moon?'
ORX opt_07_3/rxn_07_3_2 -> enc_08 | O:Offer Mara a warm bun | E:SET char_pip.trust += 0.14; SET char_pip.nerve += -0.1; SET char_pip.care += -0.09 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.25),MUL(P(char_pip.care),-0.55))
# R rxn_07_3_2: Mara: 'A bun, and a warning.'

ENC enc_08 turn=0..999
# T: Old Fen, the gruff keeper of the village well, leans on his staff and watches the moon hang too low over the rooftops. He mutters that the village will never sleep again, and the stars seem to lean in to listen.
# TITLE: Old Fen warns of restlessness
# ART: Old Fen silhouetted beside the village well, staff in hand, moon hanging low and amber above the rooftops, stars leaning in to listen.
ORX opt_08_1/rxn_08_1_1 -> enc_09 | O:Ask Old Fen what the moon means | E:SET char_pip.trust += 0.1; SET char_pip.nerve += -0.05; SET char_pip.care += 0.08 | D:ADD(MUL(P(char_pip.trust),0.4),MUL(P(char_pip.nerve),0.2),MUL(P(char_pip.care),0.3))
# R rxn_08_1_1: Old Fen: 'It means the village is awake now.'
ORX opt_08_1/rxn_08_1_2 -> enc_09 | O:Ask Old Fen what the moon means | E:SET char_pip.trust += -0.08; SET char_pip.nerve += 0.12; SET char_pip.care += -0.06 | D:ADD(MUL(P(char_pip.trust),-0.4),MUL(P(char_pip.nerve),-0.2),MUL(P(char_pip.care),-0.3))
# R rxn_08_1_2: Old Fen: 'It means the moon is watching you.'
ORX opt_08_2/rxn_08_2_1 -> enc_09 | O:Show off the hat to Old Fen | E:SET char_pip.trust += 0.15; SET char_pip.nerve += 0.1; SET char_pip.care += -0.12 | D:ADD(MUL(P(char_pip.trust),-0.3),MUL(P(char_pip.nerve),0.5),MUL(P(char_pip.care),0.2))
# R rxn_08_2_1: Old Fen: 'Bold. I like it.'
ORX opt_08_2/rxn_08_2_2 -> enc_09 | O:Show off the hat to Old Fen | E:SET char_pip.trust += -0.1; SET char_pip.nerve += -0.08; SET char_pip.care += 0.14 | D:ADD(MUL(P(char_pip.trust),0.3),MUL(P(char_pip.nerve),-0.5),MUL(P(char_pip.care),-0.2))
# R rxn_08_2_2: Old Fen: 'Bold is a word for people who don't sleep.'
ORX opt_08_3/rxn_08_3_1 -> enc_09 | O:Offer Old Fen a warm drink | E:SET char_pip.trust += -0.12; SET char_pip.nerve += 0.18; SET char_pip.care += 0.06 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.25),MUL(P(char_pip.care),0.55))
# R rxn_08_3_1: Old Fen: 'A drink? For the moon?'
ORX opt_08_3/rxn_08_3_2 -> enc_09 | O:Offer Old Fen a warm drink | E:SET char_pip.trust += 0.14; SET char_pip.nerve += -0.1; SET char_pip.care += -0.09 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.25),MUL(P(char_pip.care),-0.55))
# R rxn_08_3_2: Old Fen: 'A drink, and a warning.'

ENC enc_09 turn=0..999
# T: Pip ducks behind the laundry line and tucks the star-stitched hat beneath a row of damp sheets, its humming muffled to a purr. The moon, low over the rooftops, seems to lean closer to listen.
# TITLE: Pip tries to hide the hat
# ART: Pip crouched behind a laundry line, hat tucked under sheets, moon hanging low like a listening ear
ORX opt_09_1/rxn_09_1_1 -> enc_10 | O:Hide the hat deeper | E:SET char_pip.trust += 0.1; SET char_pip.nerve += -0.05; SET char_pip.care += 0.08 | D:ADD(MUL(P(char_pip.trust),0.4),MUL(P(char_pip.nerve),0.2),MUL(P(char_pip.care),0.3))
# R rxn_09_1_1: Pip tucks the hat under the flour sacks and whispers, "Not yet."
ORX opt_09_1/rxn_09_1_2 -> enc_10 | O:Hide the hat deeper | E:SET char_pip.trust += -0.08; SET char_pip.nerve += 0.12; SET char_pip.care += -0.06 | D:ADD(MUL(P(char_pip.trust),-0.4),MUL(P(char_pip.nerve),-0.2),MUL(P(char_pip.care),-0.3))
# R rxn_09_1_2: Pip hears the hat hum louder as the moon rises.
ORX opt_09_2/rxn_09_2_1 -> enc_10 | O:Show Mara the hat | E:SET char_pip.trust += 0.15; SET char_pip.nerve += 0.1; SET char_pip.care += -0.12 | D:ADD(MUL(P(char_pip.trust),-0.3),MUL(P(char_pip.nerve),0.5),MUL(P(char_pip.care),0.2))
# R rxn_09_2_1: Pip holds the hat up: "Look! The moon is listening!"
ORX opt_09_2/rxn_09_2_2 -> enc_10 | O:Show Mara the hat | E:SET char_pip.trust += -0.1; SET char_pip.nerve += -0.08; SET char_pip.care += 0.14 | D:ADD(MUL(P(char_pip.trust),0.3),MUL(P(char_pip.nerve),-0.5),MUL(P(char_pip.care),-0.2))
# R rxn_09_2_2: Mara squints, then sighs: "Interesting. Dangerous."
ORX opt_09_3/rxn_09_3_1 -> enc_10 | O:Ask Old Fen about the hum | E:SET char_pip.trust += -0.12; SET char_pip.nerve += 0.18; SET char_pip.care += 0.06 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.25),MUL(P(char_pip.care),0.55))
# R rxn_09_3_1: Pip asks, "Does the moon ever get tired of listening?"
ORX opt_09_3/rxn_09_3_2 -> enc_10 | O:Ask Old Fen about the hum | E:SET char_pip.trust += 0.14; SET char_pip.nerve += -0.1; SET char_pip.care += -0.09 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.25),MUL(P(char_pip.care),-0.55))
# R rxn_09_3_2: Old Fen yawns: "The moon is patient. That is the problem."

ENC enc_10 turn=0..999
# T: The moon rises and the hat hums louder, a low silver note that rattles the laundry pins and makes the chickens roost early. Pip feels the pull of being noticed, and the village seems to lean in to listen.
# TITLE: The hat hums louder
# ART: Hat humming under moonlight, laundry pins rattling, chickens roosting early
ORX opt_10_1/rxn_10_1_1 -> enc_11 | O:Wear the hat tonight | E:SET char_pip.trust += 0.15; SET char_pip.nerve += 0.1; SET char_pip.care += -0.12 | D:ADD(MUL(P(char_pip.trust),-0.3),MUL(P(char_pip.nerve),0.5),MUL(P(char_pip.care),0.2))
# R rxn_10_1_1: Pip pulls the hat on: "I am the most interesting person in the village!"
ORX opt_10_1/rxn_10_1_2 -> enc_11 | O:Wear the hat tonight | E:SET char_pip.trust += -0.1; SET char_pip.nerve += -0.08; SET char_pip.care += 0.14 | D:ADD(MUL(P(char_pip.trust),0.3),MUL(P(char_pip.nerve),-0.5),MUL(P(char_pip.care),-0.2))
# R rxn_10_1_2: The village gathers at night to watch the moon.
ORX opt_10_2/rxn_10_2_1 -> enc_11 | O:Keep the hat hidden | E:SET char_pip.trust += 0.1; SET char_pip.nerve += -0.05; SET char_pip.care += 0.08 | D:ADD(MUL(P(char_pip.trust),0.4),MUL(P(char_pip.nerve),0.2),MUL(P(char_pip.care),0.3))
# R rxn_10_2_1: Pip buries the hat in the flour bin and says, "Not tonight."
ORX opt_10_2/rxn_10_2_2 -> enc_11 | O:Keep the hat hidden | E:SET char_pip.trust += -0.08; SET char_pip.nerve += 0.12; SET char_pip.care += -0.06 | D:ADD(MUL(P(char_pip.trust),-0.4),MUL(P(char_pip.nerve),-0.2),MUL(P(char_pip.care),-0.3))
# R rxn_10_2_2: The village gathers at night to watch the moon.
ORX opt_10_3/rxn_10_3_1 -> enc_11 | O:Ask the moon what it wants | E:SET char_pip.trust += -0.12; SET char_pip.nerve += 0.18; SET char_pip.care += 0.06 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.25),MUL(P(char_pip.care),0.55))
# R rxn_10_3_1: Pip whispers, "What do you want, moon?"
ORX opt_10_3/rxn_10_3_2 -> enc_11 | O:Ask the moon what it wants | E:SET char_pip.trust += 0.14; SET char_pip.nerve += -0.1; SET char_pip.care += -0.09 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.25),MUL(P(char_pip.care),-0.55))
# R rxn_10_3_2: The village gathers at night to watch the moon.

ENC enc_11 turn=0..999
# T: The village gathers at night to watch the moon, which hangs lower than ever, almost touching the rooftops. Pip stands at the edge of the crowd, hat hidden, wondering if the moon is calling to them.
# TITLE: The village gathers at night
# ART: Village gathered under a low moon, Pip at the crowd's edge, hat hidden
ORX opt_11_1/rxn_11_1_1 -> enc_12 | O:Join the gathering | E:SET char_pip.trust += 0.08; SET char_pip.nerve += 0.12; SET char_pip.care += 0.1 | D:ADD(MUL(P(char_pip.trust),0.35),MUL(P(char_pip.nerve),0.35),MUL(P(char_pip.care),-0.2))
# R rxn_11_1_1: Pip steps into the crowd: "I can see it too."
ORX opt_11_1/rxn_11_1_2 -> enc_12 | O:Join the gathering | E:SET char_pip.trust += -0.14; SET char_pip.nerve += -0.06; SET char_pip.care += -0.11 | D:ADD(MUL(P(char_pip.trust),-0.35),MUL(P(char_pip.nerve),-0.35),MUL(P(char_pip.care),0.2))
# R rxn_11_1_2: Pip feels the pull of being the most interesting person in the village.
ORX opt_11_2/rxn_11_2_1 -> enc_12 | O:Stay hidden | E:SET char_pip.trust += 0.1; SET char_pip.nerve += -0.05; SET char_pip.care += 0.08 | D:ADD(MUL(P(char_pip.trust),0.4),MUL(P(char_pip.nerve),0.2),MUL(P(char_pip.care),0.3))
# R rxn_11_2_1: Pip slips behind the well: "I'll watch from here."
ORX opt_11_2/rxn_11_2_2 -> enc_12 | O:Stay hidden | E:SET char_pip.trust += -0.08; SET char_pip.nerve += 0.12; SET char_pip.care += -0.06 | D:ADD(MUL(P(char_pip.trust),-0.4),MUL(P(char_pip.nerve),-0.2),MUL(P(char_pip.care),-0.3))
# R rxn_11_2_2: Pip feels the pull of being the most interesting person in the village.
ORX opt_11_3/rxn_11_3_1 -> enc_12 | O:Ask Old Fen what he sees | E:SET char_pip.trust += -0.09; SET char_pip.nerve += 0.07; SET char_pip.care += 0.13 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.15),MUL(P(char_pip.care),0.45))
# R rxn_11_3_1: Pip asks, "What do you see, Old Fen?"
ORX opt_11_3/rxn_11_3_2 -> enc_12 | O:Ask Old Fen what he sees | E:SET char_pip.trust += 0.11; SET char_pip.nerve += -0.13; SET char_pip.care += -0.08 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.15),MUL(P(char_pip.care),-0.45))
# R rxn_11_3_2: Pip feels the pull of being the most interesting person in the village.

ENC enc_12 turn=0..999
# T: Pip feels the pull of being the most interesting person in the village. The moon hums louder, and Pip's vanity stirs: if the hat makes them interesting, maybe it's worth the moon growing closer.
# TITLE: Pip feels the pull of fame
# ART: Pip at the gathering, moon humming low, vanity stirring
ORX opt_12_1/rxn_12_1_1 -> enc_14 | O:Put the hat on | E:SET char_pip.trust += 0.15; SET char_pip.nerve += 0.1; SET char_pip.care += -0.12 | D:ADD(MUL(P(char_pip.trust),-0.3),MUL(P(char_pip.nerve),0.5),MUL(P(char_pip.care),0.2))
# R rxn_12_1_1: Pip puts the hat on: "I am interesting."
ORX opt_12_1/rxn_12_1_2 -> enc_13 | O:Put the hat on | E:SET char_pip.trust += -0.1; SET char_pip.nerve += -0.08; SET char_pip.care += 0.14 | D:ADD(MUL(P(char_pip.trust),0.3),MUL(P(char_pip.nerve),-0.5),MUL(P(char_pip.care),-0.2))
# R rxn_12_1_2: The moon grows closer, and Pip feels the pull of fame.
ORX opt_12_2/rxn_12_2_1 -> enc_14 | O:Refuse the hat | E:SET char_pip.trust += 0.12; SET char_pip.nerve += -0.14; SET char_pip.care += 0.09 | D:ADD(MUL(P(char_pip.trust),0.45),MUL(P(char_pip.nerve),-0.35),MUL(P(char_pip.care),-0.15))
# R rxn_12_2_1: Pip refuses: "I am enough as I am."
ORX opt_12_2/rxn_12_2_2 -> enc_13 | O:Refuse the hat | E:SET char_pip.trust += -0.07; SET char_pip.nerve += 0.16; SET char_pip.care += -0.1 | D:ADD(MUL(P(char_pip.trust),-0.45),MUL(P(char_pip.nerve),0.35),MUL(P(char_pip.care),0.15))
# R rxn_12_2_2: The moon grows closer, and Pip feels the pull of fame.
ORX opt_12_3/rxn_12_3_1 -> enc_14 | O:Ask the moon what it wants | E:SET char_pip.trust += -0.12; SET char_pip.nerve += 0.18; SET char_pip.care += 0.06 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.25),MUL(P(char_pip.care),0.55))
# R rxn_12_3_1: Pip asks, "What do you want, moon?"
ORX opt_12_3/rxn_12_3_2 -> enc_13 | O:Ask the moon what it wants | E:SET char_pip.trust += 0.14; SET char_pip.nerve += -0.1; SET char_pip.care += -0.09 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.25),MUL(P(char_pip.care),-0.55))
# R rxn_12_3_2: The moon grows closer, and Pip feels the pull of fame.

ENC enc_13 turn=0..999
# T: Mara sets a loaf on the table and slides it across, still warm. 'Fame is a loud kettle,' she says. 'Rest is the quiet after the kettle boils. Which would you rather carry home?' The hat hums once, almost apologetic.
# TITLE: Mara offers a quiet choice
# ART: Mara's bakery window glows amber while the hat on the table hums a low silver note, moonlight pooling on the flour-dusted table
ORX opt_13_1/rxn_13_1_1 -> enc_14 | O:Ask Mara what fame costs | E:SET char_pip.trust += 0.1; SET char_pip.nerve += -0.05; SET char_pip.care += 0.08 | D:ADD(MUL(P(char_pip.trust),0.4),MUL(P(char_pip.nerve),0.2),MUL(P(char_pip.care),0.3))
# R rxn_13_1_1: Mara shrugs: 'Everything, eventually.'
ORX opt_13_1/rxn_13_1_2 -> enc_14 | O:Ask Mara what fame costs | E:SET char_pip.trust += -0.08; SET char_pip.nerve += 0.12; SET char_pip.care += -0.06 | D:ADD(MUL(P(char_pip.trust),-0.4),MUL(P(char_pip.nerve),-0.2),MUL(P(char_pip.care),-0.3))
# R rxn_13_1_2: The hat hums louder, waiting
ORX opt_13_2/rxn_13_2_1 -> enc_14 | O:Ask Mara what rest costs | E:SET char_pip.trust += -0.12; SET char_pip.nerve += 0.18; SET char_pip.care += 0.06 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.25),MUL(P(char_pip.care),0.55))
# R rxn_13_2_1: Mara smiles: 'Nothing, if you let it.'
ORX opt_13_2/rxn_13_2_2 -> enc_14 | O:Ask Mara what rest costs | E:SET char_pip.trust += 0.14; SET char_pip.nerve += -0.1; SET char_pip.care += -0.09 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.25),MUL(P(char_pip.care),-0.55))
# R rxn_13_2_2: The hat hums softer, almost disappointed
ORX opt_13_3/rxn_13_3_1 -> enc_14 | O:Ask Mara to choose for me | E:SET char_pip.trust += 0.12; SET char_pip.nerve += -0.14; SET char_pip.care += 0.09 | D:ADD(MUL(P(char_pip.trust),0.45),MUL(P(char_pip.nerve),-0.35),MUL(P(char_pip.care),-0.15))
# R rxn_13_3_1: Mara shakes her head: 'You choose, or the moon chooses.'
ORX opt_13_3/rxn_13_3_2 -> enc_14 | O:Ask Mara to choose for me | E:SET char_pip.trust += -0.07; SET char_pip.nerve += 0.16; SET char_pip.care += -0.1 | D:ADD(MUL(P(char_pip.trust),-0.45),MUL(P(char_pip.nerve),0.35),MUL(P(char_pip.care),0.15))
# R rxn_13_3_2: The hat hums a warning hum

ENC enc_14 turn=0..999
# T: Old Fen crouches by the well and spits into his palm, watching the moon climb. 'The moon's nearness is a debt,' he says. 'Every night it leans closer, the well runs shallower, the hens stop laying, and the baker's bread rises like a grudge.' Pip looks at the hat, humming faintly against his chest. 'Then what do we do?' he asks.
# TITLE: Old Fen reveals the cost
# ART: Old Fen crouched by the well, one hand resting on the stone rim, moonlight pooling like milk on the water
ORX opt_14_1/rxn_14_1_1 -> enc_16 | O:Ask Old Fen what the moon wants | E:SET char_pip.trust += 0.1; SET char_pip.nerve += -0.05; SET char_pip.care += 0.08 | D:ADD(MUL(P(char_pip.trust),0.4),MUL(P(char_pip.nerve),0.2),MUL(P(char_pip.care),0.3))
# R rxn_14_1_1: Old Fen shrugs: 'It wants to be noticed. That's all.'
ORX opt_14_1/rxn_14_1_2 -> enc_15 | O:Ask Old Fen what the moon wants | E:SET char_pip.trust += -0.08; SET char_pip.nerve += 0.12; SET char_pip.care += -0.06 | D:ADD(MUL(P(char_pip.trust),-0.4),MUL(P(char_pip.nerve),-0.2),MUL(P(char_pip.care),-0.3))
# R rxn_14_1_2: Pip turns the hat over in his hands, weighing the promise against the village's rest.
ORX opt_14_2/rxn_14_2_1 -> enc_16 | O:Ask Old Fen what happens if we keep the hat | E:SET char_pip.trust += 0.12; SET char_pip.nerve += -0.14; SET char_pip.care += 0.09 | D:ADD(MUL(P(char_pip.trust),0.45),MUL(P(char_pip.nerve),-0.35),MUL(P(char_pip.care),-0.15))
# R rxn_14_2_1: Old Fen shakes his head: 'The moon keeps rising, and the village keeps sleeping.'
ORX opt_14_2/rxn_14_2_2 -> enc_15 | O:Ask Old Fen what happens if we keep the hat | E:SET char_pip.trust += -0.07; SET char_pip.nerve += 0.16; SET char_pip.care += -0.1 | D:ADD(MUL(P(char_pip.trust),-0.45),MUL(P(char_pip.nerve),0.35),MUL(P(char_pip.care),0.15))
# R rxn_14_2_2: Pip weighs the hat's promise against the village's rest.
ORX opt_14_3/rxn_14_3_1 -> enc_16 | O:Ask Old Fen what happens if we give the hat away | E:SET char_pip.trust += -0.09; SET char_pip.nerve += 0.07; SET char_pip.care += 0.13 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.15),MUL(P(char_pip.care),0.45))
# R rxn_14_3_1: Old Fen sighs: 'Then the moon goes back to its proper distance, and the well remembers its name.'
ORX opt_14_3/rxn_14_3_2 -> enc_15 | O:Ask Old Fen what happens if we give the hat away | E:SET char_pip.trust += 0.11; SET char_pip.nerve += -0.13; SET char_pip.care += -0.08 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.15),MUL(P(char_pip.care),-0.45))
# R rxn_14_3_2: Pip weighs the hat's promise against the village's rest.

ENC enc_15 turn=0..999
# T: Pip stands at the crossroads of the village square, the hat in one hand and the loaf in the other. 'The promise says I'll be the most interesting person here,' he says. 'The cost says the moon will keep leaning in.' Mara watches from her doorway, dry as a biscuit. 'Then choose,' she says, 'and choose kindly.'
# TITLE: Pip weighs the hat's promise
# ART: Pip at the crossroads, hat in one hand, loaf in the other, Mara watching from her doorway
ORX opt_15_1/rxn_15_1_1 -> enc_16 | O:Choose the hat and wear it | E:SET char_pip.trust += 0.15; SET char_pip.nerve += 0.1; SET char_pip.care += -0.12 | D:ADD(MUL(P(char_pip.trust),-0.3),MUL(P(char_pip.nerve),0.5),MUL(P(char_pip.care),0.2))
# R rxn_15_1_1: Pip pulls the hat on and feels the hum swell.
ORX opt_15_1/rxn_15_1_2 -> enc_16 | O:Choose the hat and wear it | E:SET char_pip.trust += -0.1; SET char_pip.nerve += -0.08; SET char_pip.care += 0.14 | D:ADD(MUL(P(char_pip.trust),0.3),MUL(P(char_pip.nerve),-0.5),MUL(P(char_pip.care),-0.2))
# R rxn_15_1_2: The moon waits for Pip to choose before dawn.
ORX opt_15_2/rxn_15_2_1 -> enc_16 | O:Choose the village's rest and give the hat away | E:SET char_pip.trust += 0.1; SET char_pip.nerve += -0.05; SET char_pip.care += 0.08 | D:ADD(MUL(P(char_pip.trust),0.4),MUL(P(char_pip.nerve),0.2),MUL(P(char_pip.care),0.3))
# R rxn_15_2_1: Pip sets the hat on the well's rim and steps back.
ORX opt_15_2/rxn_15_2_2 -> enc_16 | O:Choose the village's rest and give the hat away | E:SET char_pip.trust += -0.08; SET char_pip.nerve += 0.12; SET char_pip.care += -0.06 | D:ADD(MUL(P(char_pip.trust),-0.4),MUL(P(char_pip.nerve),-0.2),MUL(P(char_pip.care),-0.3))
# R rxn_15_2_2: The moon waits for Pip to choose before dawn.
ORX opt_15_3/rxn_15_3_1 -> enc_16 | O:Choose to keep the hat but share it with the village | E:SET char_pip.trust += -0.09; SET char_pip.nerve += 0.07; SET char_pip.care += 0.13 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.15),MUL(P(char_pip.care),0.45))
# R rxn_15_3_1: Pip holds the hat out to the whole village, humming softly.
ORX opt_15_3/rxn_15_3_2 -> enc_16 | O:Choose to keep the hat but share it with the village | E:SET char_pip.trust += 0.11; SET char_pip.nerve += -0.13; SET char_pip.care += -0.08 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.15),MUL(P(char_pip.care),-0.45))
# R rxn_15_3_2: The moon waits for Pip to choose before dawn.

ENC enc_16 turn=0..999
# T: The moon waits for Pip to choose before dawn. It hangs low over the square, humming its low, patient hum, and the star-stitched hat sits on the well's rim, warm as a held breath. Pip stands between the promise and the village's rest, and the moon does not hurry.
# TITLE: The moon waits for Pip
# ART: A floppy star-stitched hat resting on the well's rim, glowing faintly under a low, patient moon, with Pip silhouetted between the hat and the sleeping village.
ORX opt_16_1/rxn_16_1_1 -> end_fallback | O:Wear the hat and let the moon rise | E:SET char_pip.trust += 0.15; SET char_pip.nerve += 0.1; SET char_pip.care += -0.12 | D:ADD(MUL(P(char_pip.trust),-0.3),MUL(P(char_pip.nerve),0.5),MUL(P(char_pip.care),0.2))
# R rxn_16_1_1: Pip pulls the hat on and the moon swells brighter, and the village wakes to a sky that never quite goes dark.
ORX opt_16_1/rxn_16_1_2 -> end_share | O:Wear the hat and let the moon rise | E:SET char_pip.trust += -0.1; SET char_pip.nerve += -0.08; SET char_pip.care += 0.14 | D:ADD(MUL(P(char_pip.trust),0.3),MUL(P(char_pip.nerve),-0.5),MUL(P(char_pip.care),-0.2))
# R rxn_16_1_2: Pip shares the hat with the village, and the moon hums a little softer for everyone.
ORX opt_16_2/rxn_16_2_1 -> end_return | O:Set the hat down and let the moon rest | E:SET char_pip.trust += 0.1; SET char_pip.nerve += -0.05; SET char_pip.care += 0.08 | D:ADD(MUL(P(char_pip.trust),0.4),MUL(P(char_pip.nerve),0.2),MUL(P(char_pip.care),0.3))
# R rxn_16_2_1: Pip sets the hat back on the rim and the moon dims to a gentle, ordinary glow.
ORX opt_16_2/rxn_16_2_2 -> end_fallback | O:Set the hat down and let the moon rest | E:SET char_pip.trust += -0.08; SET char_pip.nerve += 0.12; SET char_pip.care += -0.06 | D:ADD(MUL(P(char_pip.trust),-0.4),MUL(P(char_pip.nerve),-0.2),MUL(P(char_pip.care),-0.3))
# R rxn_16_2_2: Pip hesitates, then sets the hat down anyway, and the moon waits one more night.
ORX opt_16_3/rxn_16_3_1 -> end_share | O:Offer the hat to the village | E:SET char_pip.trust += -0.12; SET char_pip.nerve += 0.18; SET char_pip.care += 0.06 | D:ADD(MUL(P(char_pip.trust),0.2),MUL(P(char_pip.nerve),-0.25),MUL(P(char_pip.care),0.55))
# R rxn_16_3_1: Pip lays the hat before the well and the village gathers around it, sharing the hum.
ORX opt_16_3/rxn_16_3_2 -> end_keep | O:Offer the hat to the village | E:SET char_pip.trust += 0.14; SET char_pip.nerve += -0.1; SET char_pip.care += -0.09 | D:ADD(MUL(P(char_pip.trust),-0.2),MUL(P(char_pip.nerve),0.25),MUL(P(char_pip.care),-0.55))
# R rxn_16_3_2: Pip keeps the hat but shares its light with the village, and the moon hums for all.

ENC end_return turn=0..999
# T: Pip carries the star-stitched hat back to the well, where Old Fen is asleep against the stone rim. He sets the hat down gently, the way you'd set down a sleeping bird, and the humming fades to a hush. The moon drifts back to its proper distance, and the village wakes to ordinary mornings again.
# TITLE: Pip returns the hat
# ART: Pip kneels by the well at dawn, hat in both hands, moon a small silver coin far above the rooftops.

ENC end_keep turn=0..999
# T: Pip kept the hat, and the moon stayed close, glowing softly over the village every night. The village never slept again, for the moon would not let them.
# TITLE: Pip keeps the hat
# ART: A small child in a patched coat holding a round brimmed hat that glows like a full moon, with stars stitched on the brim.

ENC end_share turn=0..999
# T: Pip set the hat on the meadow grass and passed it to Mara, then to Old Fen, and the moon hummed once, soft as a lullaby, before fading into the stars.
# TITLE: Pip shares the hat
# ART: A small meadow at dusk: Pip, Mara, and Old Fen sitting in a circle around a glowing hat on the grass, with a faint moon-light halo above it.

ENC end_fallback turn=0..999
# T: The moon hummed softly above the sleeping village, and the hat rested quietly on the windowsill, holding its small light. No one chose a path, and the story faded to a quiet night, where the moon kept humming like a lullaby.
# TITLE: The story fades
# ART: A small knitted hat on a windowsill with a glowing crescent moon resting inside it, under a deep blue night sky.
