# Project contract

The project contract is intentionally small and stack-neutral.

## Required

- `AGENTS.md` — operating invariants for workers;
- `.ai/project.json` — versioned machine-readable project metadata and verification entry point;
- `PROJECT.md` — durable project-specific knowledge;
- a repository-owned verification entry point declared by `.ai/project.json`.

## Optional

- `REPO_MAP.md` — compact navigation when repository structure is not obvious.

## Rules

- repository evidence overrides remembered session assumptions;
- durable facts belong in repository-owned artifacts, not an external agent memory database;
- secrets and temporary task state do not belong in the project contract;
- verification must report what actually ran;
- stack-specific checks belong behind the repository-owned verification entry point;
- a generated onboarding verifier may report `UNAVAILABLE`, but it must never fake `PASS`;
- manifest schema changes require an explicit `schema_version` change and compatible validator.

See `examples/repository/` for a complete minimal example.
