# Standalone profile

The standalone profile is a complete local software-development loop, not a set of advisory markdown instructions.

| Concern | Owner |
|---|---|
| repository analysis | MAU |
| contract bootstrap/validation | MAU + target repo evidence |
| canonical GitHub Issue | MAU intake |
| isolated worktree | MAU intake |
| implementation | selected coding worker |
| project verification | target repository |
| deterministic gates | MAU |
| repair retries | MAU workflow |
| verified commit | MAU workflow |
| PR delivery | MAU completion gate |
| production authorization | explicit human boundary |

The default worker is local Codex CLI. `MAU_WORKER_COMMAND` or `--worker-command` can replace it without changing project contracts.

If Issue identity, Git state, verifier evidence or required profile gates are unavailable, the workflow stops with `BLOCKED` instead of silently continuing.
