# MAU ADS

A repository-first operating layer for AI-assisted software development.

The human gives a normal development request. MAU ADS is used automatically by the coding agent or orchestrator to make that work traceable, isolated and verifiable without binding the workflow to one model, language, framework or orchestration product.

## The automatic lifecycle

```text
REQUEST
  -> automatic intake gate
  -> repository analysis / refresh
  -> automatic onboarding when required
  -> project contract validation
  -> canonical work item
  -> isolated workspace
  -> risk / complexity routing
     -> trivial: direct narrow workflow
     -> standard/full/critical: Spec Kit artifact workflow
  -> implementation
  -> proportional project-defined verification
  -> deterministic completion gate
  -> pull request / review
  -> merge
  -> READY_TO_DEPLOY
  -> production only with explicit authorization
```

**The user is not expected to remember MAU or Spec Kit commands.** Internal runtime entry points exist for agents and orchestrators.

## Project contract

An AI-ready repository exposes a small, explicit contract:

- `AGENTS.md` — operating rules for any worker;
- `.ai/project.json` — machine-readable metadata and verification entry point;
- `PROJECT.md` — durable project knowledge;
- `REPO_MAP.md` — optional compact navigation;
- repository-owned verification entry point declared by `.ai/project.json`.

See [`examples/repository/`](examples/repository/).

## Workflow routing

MAU separates workflow complexity from verification cost:

| Work profile | Execution | Verification |
|---|---|---|
| `trivial` | direct | `minimal` |
| `standard` | Spec Kit core path | `focused` |
| `full` | Spec Kit expanded path | `full` |
| `critical` | Spec Kit expanded path + checklist gate | `critical` |

The repository still owns the concrete executable checks. MAU passes the selected minimum through `MAU_VERIFICATION_PROFILE` and blocks completion if required workflow artifacts or verification evidence are missing.

See [`docs/SPEC-KIT.md`](docs/SPEC-KIT.md).

## Core invariants

1. Repository evidence beats remembered session state.
2. No valid MAU work context means no durable writes.
3. One independently deliverable outcome normally maps to one canonical GitHub Issue.
4. Parallel writers never mutate the same working tree.
5. Repository analysis is evidence-first and read-only.
6. Tests are executable checks; verification is evidence that the requested outcome is correct.
7. Verification states are truthful: `PASS`, `FAIL`, `UNAVAILABLE`, `NOT_RUN`, `NOT_APPLICABLE`.
8. Workflow and verification profiles may be strengthened by evidence, never silently downgraded.
9. Merge does not authorize production.
10. Models, agents, Spec Kit and orchestrators remain replaceable implementation layers around repository/Git truth.

## Repository map

| Path | Purpose |
|---|---|
| [`GUIDA-IT.md`](GUIDA-IT.md) | complete Italian guide |
| [`START-HERE.md`](START-HERE.md) | short machine/human entry point |
| [`AGENTS.md`](AGENTS.md) | executor-neutral operating contract |
| [`skills/`](skills/) | published reusable skill catalog and routing rules |
| [`docs/AUTOMATIC-LIFECYCLE.md`](docs/AUTOMATIC-LIFECYCLE.md) | invisible automatic lifecycle |
| [`docs/REPOSITORY-ANALYSIS.md`](docs/REPOSITORY-ANALYSIS.md) | evidence-first repository discovery |
| [`docs/STANDALONE.md`](docs/STANDALONE.md) | ownership in the standalone profile |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | ownership and system boundaries |
| [`docs/DEVELOPMENT-WORKFLOW.md`](docs/DEVELOPMENT-WORKFLOW.md) | request-to-delivery lifecycle |
| [`docs/PROJECT-CONTRACT.md`](docs/PROJECT-CONTRACT.md) | minimum AI-ready repository contract |
| [`docs/SPEC-KIT.md`](docs/SPEC-KIT.md) | Spec Kit ownership, workflow profiles and proportional verification |
| [`docs/ORCHESTRATION.md`](docs/ORCHESTRATION.md) | worker/orchestrator boundaries |
| [`docs/SAFETY.md`](docs/SAFETY.md) | safety boundaries |
| [`runtime/`](runtime/) | machine-facing intake, routing, Spec Kit and completion primitives |
| [`onboarding/`](onboarding/) | safe bootstrap and contract validation |
| [`examples/repository/`](examples/repository/) | minimal example repository |

Italian version: [`README.it.md`](README.it.md) · Complete Italian guide: [`GUIDA-IT.md`](GUIDA-IT.md)
