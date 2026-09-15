# Current state — ADS 2.0

MAU ADS has one standalone request-to-ready control path.

Implemented core:

- repository-first project contract;
- GitHub Issue work identity;
- isolated worktrees;
- safe onboarding bootstrap inside the isolated workspace;
- portable local/production metadata;
- deterministic intake/completion preflight;
- replaceable local worker adapter, Codex by default;
- bounded implementation/verification/repair loop;
- repository-owned verifier with captured evidence;
- automatic verified commit and PR delivery;
- production authorization kept separate.

The core remains stack-neutral. `mauro-php` is an optional stronger project profile, not a global assumption.

Spec Kit, Harbor/eval-engineering, Orca and similar tools are external optional layers, not runtime dependencies or competing sources of truth.
