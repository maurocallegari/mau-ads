# Development workflow

## 1. Resolve context

Read repository-owned instructions and inspect the relevant code path before making durable edits.

## 2. Define the outcome

Use one canonical GitHub Issue for one independently deliverable outcome. Internal planner steps do not automatically become more Issues.

## 3. Isolate the writer

Each concurrent writer gets its own branch/worktree/session. Two writers never share the same mutable working tree.

## 4. Implement narrowly

Prefer the smallest coherent change that satisfies the requested outcome. Avoid unrelated refactors and formatting churn.

## 5. Test and verify

Tests are executable checks. Verification is the evidence that the requested outcome is correct. Use the strongest practical project-defined checks proportional to scope and risk.

Verification states:

```text
PASS            required verification ran and passed
FAIL            required verification ran and failed
UNAVAILABLE     relevant verification could not be executed
NOT_RUN         verification was not executed
NOT_APPLICABLE  the check genuinely does not apply
```

## 6. Review and integrate

Inspect the final diff, open/review the Pull Request, resolve collisions explicitly and merge only when the change is acceptable.

## 7. Respect the deployment boundary

```text
MERGED -> READY_TO_DEPLOY -> explicit authorization? -> deploy or stop
```

Merge is not production authorization.
