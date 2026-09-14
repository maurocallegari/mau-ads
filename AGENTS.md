# AGENTS.md — MAU ADS

## Purpose

This repository defines a repository-first operating contract and deterministic runtime primitives for AI-assisted software development. It must remain usable by direct coding agents and by replaceable orchestrators.

## Invisible gate

The human should not have to remember MAU commands.

Before any durable edit in a target repository, a compatible worker must automatically obtain a valid MAU work context. In standalone mode this means invoking the MAU intake gate with the requested outcome and continuing writes only in the isolated workspace returned by the gate.

```text
NO VALID MAU WORK CONTEXT -> NO DURABLE WRITES
```

The returned execution contract is authoritative for the current work item. It defines the minimum workflow profile and minimum verification profile. A worker may strengthen them when repository evidence requires it, but must not silently downgrade them.

## Authority

- Repository code and Git history are authoritative for implementation.
- GitHub Issues identify independently deliverable work; Pull Requests carry reviewable delivery evidence.
- Project-local `AGENTS.md`, `.ai/project.json`, `PROJECT.md` and repository code override generic assumptions when they are more specific and do not violate safety constraints.
- Transient repository analysis is evidence, not a second durable knowledge database.
- Spec Kit artifacts structure non-trivial work; they do not replace the GitHub Issue, repository contract or executable verification as sources of truth.

## Before editing

- Run/obtain automatic intake before durable writes.
- Read the target repository contract and inspect the relevant code path.
- Reuse existing patterns before inventing new abstractions.
- Resolve implementation facts from repository evidence before asking a human.
- Use one canonical GitHub Issue for one independently deliverable outcome.
- Do not create duplicate Issues for internal worker or Spec Kit subtasks.
- Follow the workflow sequence returned by intake. When `engine=spec-kit`, initialize Spec Kit in the isolated workspace when needed and produce the required artifacts before completion.

## Repository analysis

- Unknown or invalid repositories are analyzed before onboarding.
- Deterministic analysis is read-only and evidence-first.
- Do not promote guesses into `PROJECT.md` or `.ai/project.json`.
- Refresh context when structural evidence has materially changed.

## Execution isolation

- Never allow concurrent workers to mutate the same working tree.
- Use an isolated branch/worktree/session for parallel implementation.
- One worker must not overwrite another worker's unreviewed changes.
- An orchestrator may own decomposition, dependency ordering and collision avoidance; Git remains the integration source of truth.

## Scope

- Make the smallest coherent change that satisfies the requested outcome.
- Do not perform unrelated refactoring, modernization or formatting churn.
- Treat unexpected blast-radius growth as a reason to re-inspect the approach.
- Preserve existing behavior and compatibility unless a change explicitly requires otherwise.

## Verification

- Run the strongest practical project-defined checks proportional to scope and risk, never below the verification profile returned by intake.
- MAU supplies the selected level to the project verifier through `MAU_VERIFICATION_PROFILE`.
- A missing or unavailable check is not a PASS.
- Inspect the final diff for unintended behavior, generated files, secrets, formatting regressions and unrelated edits.
- Never claim execution or verification that did not occur.
- Valid states are `PASS`, `FAIL`, `UNAVAILABLE`, `NOT_RUN`, and `NOT_APPLICABLE`.
- For Spec Kit-routed work, the MAU Spec Kit artifact gate must pass before completion. Unchecked implementation tasks block completion; critical work also requires completed checklist evidence.

## Safety

- Never commit, print, copy or infer secrets from production/runtime environments into Git.
- Do not use production systems as development workspaces.
- Persistent-data, auth, shared-core, destructive and externally visible changes require elevated scrutiny.
- Production deployment is outside ordinary implementation authority unless explicitly authorized.

## Delivery

```text
request -> intake -> analysis/onboarding -> Issue -> isolated implementation
        -> routed workflow -> proportional verification -> completion gate
        -> PR -> review/merge -> READY_TO_DEPLOY
```

Merge is not production authorization.

## Durable knowledge

Promote only stable information that materially reduces future rediscovery:

- `PROJECT.md`: durable project facts and architecture;
- `REPO_MAP.md`: compact navigation;
- `AGENTS.md`: operating invariants;
- `.ai/project.json`: machine-readable project and verification metadata.

Do not record transient task state as permanent repository knowledge.

## Orchestrators

A local orchestrator may dispatch workers and own ephemeral execution state, but it must not become a competing authority for source code, durable project knowledge, canonical work identity or verification truth.

Spec Kit is a workflow engine, not a second task tracker or durable authority layer. The default Codex path should execute its required skill/artifact sequence within the primary coding session rather than spawning redundant orchestration layers.
