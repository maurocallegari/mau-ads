# Project contract

The project contract is intentionally small and stack-neutral.

## Required

- `AGENTS.md` — operating invariants for workers;
- `.ai/project.json` — versioned machine-readable project metadata and verification entry point;
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

## Rules

- repository evidence overrides remembered session assumptions;
- durable facts belong in repository-owned artifacts, not an external agent memory database;
- secrets and temporary task state do not belong in the project contract;
- verification must report what actually ran;
- stack-specific checks belong behind the repository-owned verification entry point;
- a generated onboarding verifier may report `UNAVAILABLE`, but it must never fake `PASS`;
- Spec Kit artifacts describe/structure work but do not replace executable project verification;
- Spec Kit is required only when the MAU execution contract routes the task to it;
- manifest schema changes require an explicit `schema_version` change and compatible validator.

See `examples/repository/` for a complete minimal example and [`SPEC-KIT.md`](SPEC-KIT.md) for workflow ownership.
