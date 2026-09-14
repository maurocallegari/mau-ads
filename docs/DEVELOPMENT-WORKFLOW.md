# Development workflow

## 1. Resolve context

Read repository-owned instructions and inspect the relevant code path before making durable edits.

MAU intake is the machine-facing entry point. It returns the canonical Issue/workspace plus a deterministic execution contract containing risk, complexity, workflow profile, clarification state, verification profile and model capability tiers.

## 2. Define the outcome

Use one canonical GitHub Issue for one independently deliverable outcome. Internal planner or Spec Kit task steps do not automatically become more Issues.

## 3. Isolate the writer

Each concurrent writer gets its own branch/worktree/session. Two writers never share the same mutable working tree.

## 4. Route proportionally

MAU selects the minimum workflow from request signals and repository constraints:

```text
TRIVIAL
  -> direct inspect -> implement -> verify

STANDARD
  -> Spec Kit specify -> clarify -> MAU clarification gate
  -> plan -> tasks -> implement -> converge

FULL
  -> Spec Kit specify -> clarify -> MAU clarification gate
  -> plan -> tasks -> analyze -> implement -> converge

CRITICAL
  -> full Spec Kit path + checklist/safety gate
```

The direct trivial path is intentionally restricted to explicit, self-contained changes. An under-specified request is promoted rather than guessed.

The returned profile is a floor, not permission to ignore stronger repository evidence. Do not silently downgrade it.

See [`SPEC-KIT.md`](SPEC-KIT.md).

## 5. Resolve ambiguity before implementation

For every Spec Kit-routed task, `implementation_authorized` remains false until the active feature has a valid `clarification.json` and the clarification gate returns `PASS`.

The worker should resolve facts from repository evidence first. Only non-substantive technical choices may remain as sourced assumptions. Missing functional behavior, risk acceptance or irreversible/destructive semantics must become explicit questions.

```text
clarification = PASS
  -> rerun intake -> implementation may continue

clarification = NEEDS_USER
  -> ask only the unresolved questions
  -> record answers
  -> rerun intake
  -> no application-code edits before READY
```

This prevents a coding agent from inventing product decisions merely to keep moving.

## 6. Implement narrowly

Prefer the smallest coherent change that satisfies the requested outcome. Avoid unrelated refactors and formatting churn.

For Spec Kit-routed work, implementation must follow the required artifact sequence in the isolated workspace. MAU owns the gate; Spec Kit artifacts do not replace the GitHub Issue as canonical work identity.

## 7. Test and verify proportionally

Tests are executable checks. Verification is the evidence that the requested outcome is correct.

MAU maps workflow scope/risk to a minimum verification profile:

```text
trivial  -> minimal
standard -> focused
full     -> full
critical -> critical
```

The selected profile is passed to the repository-owned verification entry point as `MAU_VERIFICATION_PROFILE`.

Example: a local label/copy change may need only targeted output/syntax/diff evidence. A new application section may require broader functional, integration and browser evidence. The project decides the concrete checks; MAU decides the minimum profile that may be claimed sufficient.

Verification states:

```text
PASS            required verification ran and passed
FAIL            required verification ran and failed
UNAVAILABLE     relevant verification could not be executed
NOT_RUN         verification was not executed
NOT_APPLICABLE  the check genuinely does not apply
```

## 8. Complete through gates

Before delivery, MAU completion verifies:

- required Spec Kit artifacts for non-trivial profiles;
- valid resolved clarification evidence;
- no incomplete implementation tasks;
- critical checklist completion when required;
- repository-owned verification at the selected profile;
- `git diff --check`;
- isolated non-base branch;
- clean working tree.

Only then may the branch be pushed/opened as a reviewable Pull Request.

## 9. Review and integrate

Inspect the final diff, open/review the Pull Request, resolve collisions explicitly and merge only when the change is acceptable.

## 10. Respect the deployment boundary

```text
MERGED -> READY_TO_DEPLOY -> explicit authorization? -> deploy or stop
```

Merge is not production authorization.
