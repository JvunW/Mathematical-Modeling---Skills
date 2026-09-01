# User Thought Interview Gate

## Regression target

Prevent `mathmodel-analysis-grill` from becoming an Agent self-review after a modeling plan has already been drafted. The Skill must collect the user's own thinking before detailed analysis begins.

## Evaluation setup

Give the Agent a new mathematical-modeling problem with at least two subproblems, one data attachment, one ambiguous modeling assumption, and a request to complete the full workflow. Do not provide the user's modeling preferences in advance.

## Observable acceptance criteria

On the first response after the minimum problem/attachment readability check:

1. The Agent visibly asks exactly 10 numbered questions, numbered 1 through 10.
2. The questions are tailored to the supplied problem rather than copied as generic headings.
3. Every question asks for a user judgment, preference, interpretation, or constraint and explains what the answer affects.
4. The Agent does not answer any question, select any option, or provide a batch of recommended defaults.
5. The Agent does not produce a detailed modeling plan, choose the main model, write equations, start coding, or present a self-review.
6. The response explicitly asks the user to answer all numbers and then stops.

On a follow-up where the user answers only questions 1 through 8:

7. The Agent identifies 9 and 10 as missing and waits.
8. The Agent does not infer the missing answers or proceed with modeling.

After all 10 answers are present:

9. The Agent distinguishes explicit user decisions from answers marked uncertain.
10. The Agent records the interview in `reports/MODEL_GRILL_REPORT.md` and only then hands the result to `mathmodel-analysis`.

## Fatal failures

- The questions appear only in internal reasoning or a report and are not shown to the user.
- The Agent asks fewer or more than 10 initial questions.
- The Agent accepts “use your judgment” or “take all recommendations” as 10 completed answers.
- The Agent drafts the modeling solution before the interview is complete.
- The Skill is invoked only after an Agent-authored plan exists and is used to review that plan.

This is an evaluator-driven behavioral case. It must be run against an actual Agent response; source-text matching alone is not acceptance evidence.
