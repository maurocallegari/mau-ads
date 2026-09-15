# Automatic lifecycle

MAU ADS is an invisible operating layer. The human states an outcome; the coding worker/orchestrator invokes the lifecycle.

```text
REQUEST
  -> ISSUE IDENTITY
  -> ISOLATED WORKTREE
  -> ANALYSIS / ONBOARDING
  -> CONTRACT VALIDATION
  -> INTAKE PREFLIGHT
  -> WORKER
  -> PROJECT VERIFICATION
  -> COMPLETION PREFLIGHT
  -> REPAIR LOOP when required
  -> VERIFIED COMMIT
  -> PR / REVIEW
  -> READY
```

Production is not part of READY and requires separate authorization.

## Core invariant

```text
NO VALID MAU WORK CONTEXT = NO DURABLE WRITES
NO VERIFIED RESULT = NO READY
```

## Standalone mode

`runtime/workflow.py` owns the full cycle. It composes the lower-level primitives instead of relying on a worker to remember a checklist.

The intake gate resolves/creates the Issue, creates the worktree, and bootstraps the project contract inside that worktree when needed. It must not dirty the source working tree as a side effect of onboarding.

The worker then receives one implementation prompt. After each attempt, MAU independently runs the project verifier, completion preflight and Git diff checks. Failure evidence is fed back into the same task for a bounded repair loop.

MAU owns the commit only after all gates pass. The completion gate reruns verification on the clean commit and handles GitHub delivery.

## External orchestrators

An external orchestrator may own UI, queueing, dependency ordering and worker selection. It may also provide Issue/workspace evidence to lower-level MAU primitives. It must not become a second source of truth for project knowledge, work identity or verification.
