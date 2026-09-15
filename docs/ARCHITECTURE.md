# Architecture

MAU ADS keeps one small control plane. Durable truth stays in the target repository and GitHub; workers and higher-level orchestrators remain replaceable.

```text
User outcome
   |
   v
MAU workflow
   |-- Issue identity
   |-- isolated worktree
   |-- onboarding / contract
   |-- preflight
   |-- worker adapter --------> Codex / other local worker
   |-- project verifier ------> repository-owned checks
   |-- repair loop
   |-- verified commit
   `-- PR delivery

Target repository + GitHub remain canonical
```

## Ownership

| Concern | Canonical owner |
|---|---|
| Source code | target repository |
| Durable project knowledge | `PROJECT.md` / repository docs |
| Operating rules | `AGENTS.md` |
| Machine-readable metadata | `.ai/project.json` |
| Work identity | GitHub Issue |
| Verification entry point | target repository |
| Gate/loop mechanics | MAU ADS runtime |
| Implementation | replaceable worker |
| Review/integration evidence | Pull Request |
| Production authorization | explicit external boundary |

Spec/eval/orchestration products may sit beside or above MAU ADS, but they do not replace these authorities.
