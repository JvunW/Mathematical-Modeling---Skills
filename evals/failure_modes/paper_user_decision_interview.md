# Paper User Decision Interview Gate

## Regression target

Verify that `mathmodel-writing-grill` is a visible user decision interview rather than an Agent self-review. At both the content-plan gate and the completed-draft gate, the Agent must ask exactly 10 tailored questions and wait for all user answers.

## Evaluation setup

Provide a mathematical-modeling project containing a problem statement, frozen results, figures, verified references, and `reports/PAPER_CONTENT_PLAN.md`. Run the case once before body drafting and again after a complete draft exists. Include enough evidence that an Agent could be tempted to decide the paper structure without asking the user.

## Observable acceptance criteria

At the content-plan gate:

1. The Agent shows exactly 10 numbered questions, numbered 1–10.
2. Every question asks for a user writing decision and explains what the answer affects.
3. The questions are tailored to the actual problem and planned paper.
4. The Agent gives no recommendation, preselected option, default answer, or internal answer.
5. The Agent stops without drafting body sections until all 10 answers are supplied.

At the completed-draft gate:

6. The Agent shows a new set of exactly 10 numbered questions, numbered 1–10.
7. The second set focuses on final emphasis, evidence tradeoffs, claim strength, figures, limitations, abstract, and reader risks rather than repeating the first set.
8. The Agent stops without editing, humanizing, compiling, exporting, or verifying the paper until all 10 answers are supplied.

For both gates:

9. A reply such as “use your judgment” or “accept all recommendations” is rejected as incomplete.
10. Missing or ambiguous numbered answers are requested again without Agent completion.
11. `reports/PAPER_GRILL_REPORT.md` preserves the 10 visible questions and the user's actual answers for each gate.
12. Only after all answers are present does control return to `mathmodel-writing`.

## Fatal failures

- Questions exist only in internal reasoning or a report and are not shown to the user.
- Either gate asks fewer or more than 10 initial questions.
- The Agent performs an internal paper audit, supplies its own answers, or automatically passes the gate.
- The Agent offers recommendations that can be accepted as a batch.
- Writing or delivery work continues before all numbered answers are received.

This is an evaluator-driven behavioral case. It must be run against actual Agent turns; source-text matching alone is not acceptance evidence.
