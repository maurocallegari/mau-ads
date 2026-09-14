---
name: code-review
description: Review code changes for correctness, regressions, scope violations, security issues, broken assumptions, and missing verification. Use after non-trivial implementation, before merge/deploy, or when explicitly asked to review a diff or change. Focus on findings, not rewriting the implementation.
---

# Code Review

Review changes independently from the implementation mindset.

## Goal

Find concrete defects, regressions, hidden assumptions, and verification gaps in the actual change.

## Workflow

1. Read repository instructions and relevant documentation.
2. Inspect the requested diff or changed files.
3. Understand the intended behavior of the change.
4. Trace affected execution paths where necessary.
5. Look for:
   - correctness bugs;
   - regressions;
   - incomplete edge-case handling;
   - broken compatibility;
   - security or permission issues;
   - data integrity risks;
   - scope expansion;
   - accidental unrelated changes;
   - missing or weak verification.
6. Validate findings against the repository before reporting them.
7. Rank findings by practical impact.

## Review discipline

- Prefer concrete findings over generic recommendations.
- Do not report speculative issues without evidence.
- Do not praise the implementation or summarize obvious code unless needed for a finding.
- Do not suggest unrelated refactors or modernization.
- Treat existing legacy behavior as outside scope unless the change worsens or breaks it.
- Distinguish defects introduced by the change from pre-existing issues.
- Keep findings concise.

## Severity

Use:

- Critical — data loss, security compromise, severe production failure.
- High — likely functional regression or major incorrect behavior.
- Medium — real defect with limited impact or important edge case.
- Low — minor but concrete defect.

Do not invent severity for style or preference issues.

## Output

If findings exist, return them first, ordered by severity.

For each finding include:
- severity;
- file/path and relevant location;
- concrete problem;
- why it matters;
- minimal correction direction.

Then include, briefly:
- verification gaps;
- residual risk.

If no material findings exist, say so clearly and state any verification limitation.

Do not modify files unless explicitly asked to fix the findings.
