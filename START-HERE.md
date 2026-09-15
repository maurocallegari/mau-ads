# Start Here

MAU ADS runs behind a normal development request.

A compatible worker/orchestrator uses one canonical path:

```text
request
  -> bin/mau-agent run
  -> Issue
  -> isolated worktree
  -> onboarding/contract when needed
  -> preflight
  -> worker
  -> verify
  -> repair loop
  -> commit
  -> PR
  -> READY
```

The user should not be asked to remember internal MAU commands.

`run` is the complete lifecycle. `intake`, `preflight`, `finish`, `analyze`, `validate` and `onboard` exist as lower-level machine-facing primitives.
