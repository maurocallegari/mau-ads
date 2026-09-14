---
name: bug-investigation
description: Investigate software bugs and unexpected behavior systematically before fixing them. Use when behavior is incorrect, inconsistent, failing, intermittent, or when the root cause is unknown. Trace evidence and execution paths before editing. Do not use for straightforward requested feature changes with no defect investigation.
---

# Bug Investigation

Find the root cause before changing code.

## Goal

Produce a fix based on evidence from the actual execution path, not on the first suspicious line of code.

## Workflow

1. Establish the reported symptom precisely.
2. Inspect repository instructions and relevant documentation.
3. Identify the execution path involved.
4. Gather evidence from code, logs, data flow, configuration, database behavior, or reproducible runtime behavior as available.
5. Form one or more concrete hypotheses.
6. Test or eliminate hypotheses using repository evidence.
7. Identify the root cause.
8. Determine the smallest safe fix.
9. Implement only if the user requested a fix.
10. Verify the original symptom and relevant regression surface.

## Investigation discipline

- Distinguish observed facts from hypotheses.
- Do not modify code merely to test an ungrounded guess when non-destructive inspection can answer the question first.
- Do not treat a downstream symptom as the root cause without tracing where it originates.
- Inspect callers and dependencies when the defect may originate outside the visible failing function.
- Consider data, configuration, database state, permissions, timing, and environment when relevant.
- Prefer reproducible evidence over intuition.

## Fix discipline

- Fix the root cause, not only the visible symptom.
- Keep the fix scoped and compatible with existing architecture.
- Do not combine the bug fix with unrelated cleanup or refactoring.
- Preserve legacy behavior outside the defective path unless explicitly asked otherwise.
- If the correct fix materially expands scope or affects high-risk shared behavior, explain this before implementation.

## Verification

Verify proportionally to the defect:

- reproduce the original failing behavior when possible;
- verify the corrected behavior;
- test the closest relevant neighboring path;
- inspect the final diff;
- state clearly what could not be reproduced or verified.

## Output when investigation only is requested

Return:
- symptom understood;
- evidence found;
- root cause, or strongest remaining hypothesis;
- affected path;
- recommended fix;
- remaining uncertainty.

Do not modify files.

## Output after a requested fix

Return:
- root cause;
- change made;
- files touched;
- verification performed;
- residual risks or unverified behavior.
