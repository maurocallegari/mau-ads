# AGENTS.md — MAU ADS

## Purpose

This repository defines a repository-first operating contract and deterministic runtime primitives for AI-assisted software development. It must remain usable by direct coding agents and by replaceable orchestrators.

## Invisible gate

The human should not have to remember MAU commands.

Before any durable edit in a target repository, a compatible worker must automatically obtain a valid MAU work context.

```text
NO VALID MAU WORK CONTEXT -> NO DURABLE WRITES
```

The returned execution contract is authoritative for the current work item. It defines the minimum workflow profile and minimum verification profile. A worker may strengthen them when repository evidence requires it, but must not silently downgrade them.

`write_authorized=true` permits only the writes represented by the current gate state. When `implementation_authorized=false`, execute only the explicit gate-reconciliation actions, rerun intake, and do not edit application code until implementation becomes authorized.

## Onboarding gate

Repository onboarding is a blocking contract, not a documentation ceremony.

A repository is not implementation-ready until the MAU onboarding gate reports `READY`. Bootstrap may create the contract skeleton, but bootstrap alone never means the project is onboarded.

Onboarding must establish, with evidence:

- the project purpose;
- the canonical repository/source path;
- relevant durable constraints;
- a real repository-owned verification command;
- at least one successful `focused` verification baseline.

The machine-readable state lives in `.ai/onboarding.json`.

Onboarding policy:

- inspect repository evidence before asking the human;
- do not guess project purpose, canonical source ownership, environment boundaries or safety facts;
- when repository evidence is sufficient, record the fact and its source;
- when a required fact cannot be resolved, create an explicit `OPEN` onboarding question and surface `NEEDS_CLARIFICATION`;
- while onboarding is not `READY`, feature Issue/workspace creation and application-code implementation are blocked;
- allowed reconciliation scope is limited to project contract, onboarding state, project documentation and project verifier;
- the generated placeholder verifier intentionally reports `UNAVAILABLE` and can never make onboarding `READY`;
- onboarding finalization runs the repository verifier with `MAU_VERIFICATION_PROFILE=focused` and records the verifier hash; changing the verifier invalidates readiness until it is re-finalized.

## Task clarification gate

For Spec Kit-routed work, implementation is additionally blocked until the clarification gate passes. The worker must run specification/clarification, record `clarification.json` for the active feature, and resolve every substantive unknown before implementation.

Clarification policy:

- resolve implementation facts from repository evidence first;
- sourced, non-substantive technical assumptions are allowed;
- do not invent functional behavior, risk acceptance or irreversible/destructive semantics;
- unresolved functional, risk or irreversible decisions must become explicit user questions;
- while any such question is open, return `NEEDS_CLARIFICATION`, set `user_input_required=true`, and keep `implementation_authorized=false`;
- after answers are recorded, rerun intake before application-code changes.

## Authority

- Repository code and Git history are authoritative for implementation.
- GitHub Issues identify independently deliverable work; Pull Requests carry reviewable delivery evidence.
- Project-local `AGENTS.md`, `.ai/project.json`, `.ai/onboarding.json`, `PROJECT.md` and repository code override generic assumptions when they are more specific and do not violate safety constraints.
- Transient repository analysis is evidence, not a second durable knowledge database.
- Spec Kit artifacts structure non-trivial work; they do not replace the GitHub Issue, repository contract or executable verification as sources of truth.
- User answers recorded by onboarding/task clarification contracts are authoritative for unresolved decisions they answer.

## Before editing

- Run/obtain automatic intake before durable writes.
- Require onboarding `READY` before application-code changes.
- Read the target repository contract and inspect the relevant code path.
- Reuse existing patterns before inventing new abstractions.
- Resolve implementation facts from repository evidence before asking a human.
- Never infer a missing functional/risk/irreversible decision merely to avoid asking a question.
- Use one canonical GitHub Issue for one independently deliverable outcome.
- Do not create duplicate Issues for internal worker or Spec Kit subtasks.
- Follow the workflow sequence returned by intake. When `engine=spec-kit`, reconcile setup, run `specify -> clarify -> mau.clarification-gate`, and rerun intake before implementation.

## Repository analysis

- Unknown or invalid repositories are analyzed before onboarding.
- Deterministic analysis is read-only and evidence-first.
- Do not promote guesses into `PROJECT.md`, `.ai/project.json` or `.ai/onboarding.json`.
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
- Completion requires onboarding `READY`.
- For Spec Kit-routed work, the MAU Spec Kit artifact gate must also pass before completion. A missing/unresolved clarification contract blocks completion; unchecked implementation tasks also block completion; critical work additionally requires completed checklist evidence.

## Safety

- Never commit, print, copy or infer secrets from production/runtime environments into Git.
- Do not use production systems as development workspaces.
- Persistent-data, auth, shared-core, destructive and externally visible changes require elevated scrutiny.
- Production deployment is outside ordinary implementation authority unless explicitly authorized.

## Delivery

```text
request -> intake -> repository analysis
        -> onboarding gate
             -> inspect evidence
             -> ask only unresolved onboarding facts
             -> configure real verifier
             -> focused baseline PASS
             -> onboarding READY
        -> Issue -> isolated workspace
        -> Spec Kit setup if required
        -> specify/clarify -> task clarification gate
             -> repository resolves facts OR user answers substantive unknowns
        -> rerun intake -> implementation authorized
        -> routed implementation -> proportional verification -> completion gate
        -> PR -> review/merge -> READY_TO_DEPLOY
```

Merge is not production authorization.

## Durable knowledge

Promote only stable information that materially reduces future rediscovery:

- `PROJECT.md`: durable project facts and architecture;
- `REPO_MAP.md`: compact navigation;
- `AGENTS.md`: operating invariants;
- `.ai/project.json`: machine-readable project and verification metadata;
- `.ai/onboarding.json`: evidence that project identity/source/verification were actually resolved.

Do not record transient task state as permanent repository knowledge. `clarification.json` is work-item evidence inside the active Spec Kit feature, not global project knowledge.

## Orchestrators

A local orchestrator may dispatch workers and own ephemeral execution state, but it must not become a competing authority for source code, durable project knowledge, canonical work identity or verification truth.

Spec Kit is a workflow engine, not a second task tracker or durable authority layer. The default Codex path should execute its required skill/artifact sequence within the primary coding session rather than spawning redundant orchestration layers.
