# Reliability Failure Modes

The independent reliability gate covers:

1. missing attachment;
2. inconsistent units;
3. contradictory problem statement;
4. stale result after a code change;
5. literature API offline;
6. broken official Word template;
7. user changes the model midway;
8. an upstream subproblem is rerun;
9. the modeling interview is converted into Agent self-review or bypassed before analysis;
10. Chinese paper humanization changes protected evidence, adopts a named-author voice, or removes required AI-use disclosure.
11. the paper-writing grill becomes Agent self-review, asks other than exactly 10 user questions at either gate, or continues before all answers are received.

The ninth case is specified in [user_thought_interview.md](user_thought_interview.md). It verifies visible user interaction rather than matching Skill source text.
The tenth case is specified in [chinese_paper_humanization.md](chinese_paper_humanization.md). It verifies observable paper revisions and protected-content evidence.
The eleventh case is specified in [paper_user_decision_interview.md](paper_user_decision_interview.md). It verifies both visible ten-question paper gates against actual Agent turns.

Acceptance evidence must show zero observed fatal fabrications, complete stale propagation in the test corpus, correct blocking decisions, and successful resume from persisted state. Report numerators and denominators for every rate.
