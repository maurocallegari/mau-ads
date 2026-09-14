# Architecture

MAU ADS is intentionally small. Durable truth stays in the target repository and GitHub; execution layers remain replaceable.

```text
request
  -> project contract
  -> canonical work item
  -> isolated worker/workspace
  -> implementation
  -> verification
  -> pull request
  -> review / merge
  -> READY_TO_DEPLOY
```

## Ownership

| Concern | Canonical owner |
|---|---|
| Source code | target repository |
| Durable project knowledge | `PROJECT.md` / repository docs |
| Operating rules | `AGENTS.md` |
| Machine-readable metadata | `.ai/project.json` |
| Work identity | GitHub Issue |
| Review/integration evidence | Pull Request |
| Verification entry point | target repository |
| Execution/coordination | replaceable agent/orchestrator |

The orchestrator may coordinate workers, but it must not become a second source of truth for code, project knowledge or task identity.
