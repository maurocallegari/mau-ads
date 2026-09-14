# Project contract

The project contract is intentionally small and stack-neutral, but implementation readiness is now gated by explicit onboarding evidence.

## Required

- `AGENTS.md` — operating invariants for workers;
- `.ai/project.json` — versioned machine-readable project metadata and verification entry point;
- `.ai/onboarding.json` — onboarding evidence, unresolved questions and verification baseline;
- `PROJECT.md` — durable project-specific knowledge;
- a repository-owned verification entry point declared by `.ai/project.json`.

## Optional

- `REPO_MAP.md` — compact navigation when repository structure is not obvious.
- `.specify/` and `specs/` — Spec Kit state/artifacts when a routed task requires Spec Kit.

## Verification entry point

The manifest continues to expose one repository-local verification command:

```json
{
  "schema_version": 1,
  "profile": "generic",
  "name": "example-project",
  "verification": {
    "command": "dev/verify-local.sh"
  }
}
```

MAU selects a minimum verification profile per task and passes it to that command as:

```text
MAU_VERIFICATION_PROFILE=minimal|focused|full|critical
```

Repositories may initially ignore the variable for backward compatibility, but they must not claim a stronger level of verification than actually ran. New/updated project verifiers should use it to avoid running expensive browser/integration checks for changes that only require `minimal`, while retaining broader checks for `full` or `critical` work.

## Onboarding readiness

A formally valid project contract is not enough to authorize implementation. `.ai/onboarding.json` must also resolve, with explicit evidence:

- project purpose;
- canonical source path;
- required durable constraints;
- a real project verifier;
- a successful `focused` baseline run.

If repository inspection cannot resolve a required fact safely, onboarding records an explicit open question and returns `NEEDS_CLARIFICATION`. The worker asks the user, records the answer/evidence and reruns onboarding.

The generated bootstrap verifier reports `UNAVAILABLE`; it is intentionally incapable of making onboarding `READY`.

On successful onboarding finalization, MAU records the verifier hash. Changing that verifier invalidates onboarding readiness until a new baseline is finalized.

## Markdown generation

Bootstrap does not let an LLM freely invent the project documentation. Initial Markdown is produced from fixed templates plus deterministic repository evidence:

- `AGENTS.md` is a stable operating-contract template;
- `PROJECT.md` starts with observed manifests/CI/tests/schema evidence and marks unknown purpose explicitly;
- `REPO_MAP.md` is generated from observed top-level paths.

The coding agent may enrich those files during onboarding, but only from repository evidence or explicit user answers. Unknown facts remain unknown rather than being fabricated.

## Rules

- repository evidence overrides remembered session assumptions;
- durable facts belong in repository-owned artifacts, not an external agent memory database;
- secrets and temporary task state do not belong in the project contract;
- verification must report what actually ran;
- stack-specific checks belong behind the repository-owned verification entry point;
- a generated onboarding verifier may report `UNAVAILABLE`, but it must never fake `PASS`;
- `implementation_authorized` remains false until onboarding is `READY`;
- Spec Kit artifacts describe/structure work but do not replace executable project verification;
- Spec Kit is required only when the MAU execution contract routes the task to it;
- manifest schema changes require an explicit `schema_version` change and compatible validator.

See `examples/repository/` for the minimal project shape, [`../onboarding/README.md`](../onboarding/README.md) for onboarding behavior and [`SPEC-KIT.md`](SPEC-KIT.md) for task-workflow ownership.
