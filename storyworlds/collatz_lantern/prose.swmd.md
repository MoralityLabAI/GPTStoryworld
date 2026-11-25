# SWMD-0
id: SW-collatz-lantern-v1
title: The Lantern Ledger

## ENC page_0000 | The two chambers | turn=0..99 | spools=[spool_lantern]
T: "One chamber holds the missing ration," Mara says. "West belongs to the orbit that settles at one. East belongs to the orbit that cycles through five and seven." A sealed mechanism began at either one or five, with equal chance. Its current lamp reads one modulo four in both cases. Each tick adds thirteen; a state equal to one modulo four is first tripled. The mechanism then removes every factor of two. Sampling the next lamp costs one eighth of a ration. Amber means one modulo four; blue means three. A preserved arithmetic seal is free to read. Your score is the recovered ration, if any, less the sample cost.

## ENC page_ledger | A seal shared by both routes | turn=0..99 | spools=[spool_lantern]
T: Mara turns the brass ledger toward you. "The seal is the smallest residue reachable by multiplying the current state by twos and threes modulo thirteen. Both possible starts carry seal one, and the seal stays fixed as the mechanism ticks." The ledger certifies that the same arithmetic class contains both routes. It gives you the same entry whichever chamber holds the ration. You can still pay for one lamp reading before choosing.

## ENC page_commit | At the handles | turn=0..99 | spools=[spool_lantern]
T: The west handle is marked with a single point. Two interlocked rings mark the east. Mara keeps her hands away from both. "You have the two possible starts and an equal prior," she says. "Opening either chamber ends the attempt." You have spent nothing on a sample. The unseen mechanism determines which handle releases the ration.

## ENC page_amber | An amber lamp | turn=0..99 | spools=[spool_lantern]
T: The sample shutter opens onto amber glass. You have spent one eighth of a ration. The next odd state is one modulo four. Starting from one produces sixteen before the factors of two are removed, leaving one. Starting from five produces twenty-eight, leaving seven, which would light the blue lamp. Mara rests the ledger beside the handles. "You can use the new reading now."

## ENC page_blue | A blue lamp | turn=0..99 | spools=[spool_lantern]
T: Blue light spills through the sample shutter. You have spent one eighth of a ration. The next odd state is three modulo four. The start at five becomes twenty-eight before division and seven afterward. A start at one would return to one and light the amber lamp. Through the eastern wall you hear the mechanism alternate between its two recurring positions.

## ENC page_end_success | The ration recovered | turn=0..99 | spools=[spool_endings]
T: The latch opens over a sealed ration. Mara writes the amount recovered and the sample cost on separate lines. The Score meter shows their difference: one ration for a direct correct choice, or seven eighths after a sample. You can replay the other hidden configuration to check which part of your decision depended on the lamp.

## ENC page_end_failure | The empty chamber | turn=0..99 | spools=[spool_endings]
T: The open chamber contains an empty cradle. Mara records zero rations recovered. Any sample cost still counts, so the Score meter is zero for a direct miss and minus one eighth after sampling. The mechanism followed its declared rule. A different decision would have used the same available evidence.
