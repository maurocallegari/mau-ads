# Standalone profile

The `main` branch is the MAU ADS profile for direct coding agents without an external orchestrator.

## Ownership

MAU standalone owns the minimum lifecycle mechanics required to make repository rules real rather than advisory:

| Concern | Standalone owner |
|---|---|
| repository analysis | MAU |
| project contract bootstrap/validation | MAU |
| canonical GitHub Issue | MAU gate, when GitHub access is available |
| isolated worktree | MAU gate |
| implementation | selected coding worker |
| project verification | target repository |
| final diff review | worker/reviewer |
| PR/review | MAU completion gate + GitHub-capable worker |
| production authorization | human boundary |

If GitHub identity, authentication or a clean source baseline is unavailable, the gate returns a blocked/unavailable state instead of silently allowing writes.

## Human UX

The user gives the requested outcome. The worker invokes MAU automatically. Internal MAU commands are not part of the expected user workflow.
