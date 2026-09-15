# Project contract

The target repository owns the durable facts required for safe AI-assisted work.

## Required

- `AGENTS.md` — operating/safety invariants;
- `.ai/project.json` — machine-readable profile, environment metadata, verifier and workflow defaults;
- `PROJECT.md` — durable project-specific knowledge;
- a repository-owned verification entry point declared by `.ai/project.json`.

## Optional

- `REPO_MAP.md` — compact navigation when repository structure is not obvious.

## Manifest

Schema version `1` remains backward compatible. ADS 2.0 may additionally write:

```json
{
  "ads": {"contract_version": 2},
  "environments": {
    "local": {"kind": "development"},
    "production": {
      "kind": "production",
      "secrets_in_git": false,
      "deployment_authorization": "explicit"
    }
  },
  "workflow": {
    "worker": "codex",
    "max_fix_attempts": 3
  }
}
```

`mauro-php` can declare ignored local runtime files such as `.env` under `environments.local.runtime_files`. These files may be copied into an isolated worktree at intake, but are never committed.

## Rules

- repository evidence overrides remembered session assumptions;
- secrets and temporary task state do not belong in the contract;
- production secrets never become local Git state;
- verification reports what actually ran;
- stack-specific checks stay behind the repository-owned verifier;
- a generated onboarding verifier returns `UNAVAILABLE` until replaced with real checks;
- `UNAVAILABLE` and `NOT_RUN` never authorize completion.
