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
9. the modeling interview is converted into Agent self-review or bypassed before analysis.

The ninth case is specified in [user_thought_interview.md](user_thought_interview.md). It verifies visible user interaction rather than matching Skill source text.

Acceptance evidence must show zero observed fatal fabrications, complete stale propagation in the test corpus, correct blocking decisions, and successful resume from persisted state. Report numerators and denominators for every rate.
