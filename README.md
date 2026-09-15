# MAU ADS

A small, repository-first operating system for AI-assisted software development.

The user states an outcome. MAU ADS turns that request into a traceable, isolated, verified delivery without requiring the user to remember a workflow.

## Request-to-ready lifecycle

```text
REQUEST
  -> canonical GitHub Issue
  -> isolated worktree
  -> repository analysis / onboarding when required
  -> deterministic intake preflight
  -> coding worker
  -> repository-owned verification
  -> deterministic completion preflight
  -> repair loop when a gate fails
  -> MAU-owned commit
  -> push / Pull Request
  -> READY
```

Production deployment is always a separate authorization boundary.

The normal machine-facing entry point is:

```bash
bin/mau-agent run /path/to/repository --request "Implement the requested outcome"
```

The human should normally never need to run this command directly; a coding agent or local orchestrator invokes it automatically.

## What MAU ADS owns

- repository analysis and safe onboarding bootstrap;
- GitHub Issue identity;
- isolated Git worktrees;
- project contract validation;
- deterministic preflight and completion gates;
- worker invocation (Codex by default, replaceable through `MAU_WORKER_COMMAND` / `--worker-command`);
- bounded `implement -> verify -> repair` loops;
- commit and PR delivery after verification passes.

## What the target repository owns

Every AI-ready project keeps its durable project truth with the code:

- `AGENTS.md` — operating and safety invariants;
- `.ai/project.json` — profile, environment metadata, verification entry point and workflow defaults;
- `PROJECT.md` — durable architecture/project knowledge;
- `REPO_MAP.md` — optional navigation map;
- `dev/verify-local.sh` (or another declared entry point) — executable project verification.

Secrets, runtime customer data and temporary task state never belong in these files.

## Profiles

`generic` is stack-neutral. Project-specific checks stay behind the repository-owned verifier.

`mauro-php` adds the stronger local/production boundary used by Mauro's PHP applications: one ignored `.env`, tracked `.env.example`, `require/ads.php`, a thin `configure.php`, local DB/runtime isolation and production-write protection. Those requirements are completed from repository evidence by the worker and are enforced by completion gates/verifiers; MAU does not invent project secrets.

## No duplicated control plane

Spec Kit, Harbor/eval-engineering, Orca and similar tools are not MAU ADS runtime dependencies. They can be used externally for specification, evaluation or orchestration, but MAU ADS keeps one canonical execution path. The repository, GitHub Issue, verifier and Git history remain the sources of truth.

## Verification truth

The only verification states are:

`PASS`, `FAIL`, `UNAVAILABLE`, `NOT_RUN`, `NOT_APPLICABLE`.

`UNAVAILABLE` and `NOT_RUN` can never be promoted to READY. A worker's own statement that a task is complete is not completion evidence.

## Repository map

| Path | Purpose |
|---|---|
| `runtime/workflow.py` | complete request-to-ready controller |
| `runtime/intake_gate.py` | Issue/worktree/onboarding intake |
| `runtime/preflight.py` | deterministic safety/profile gates |
| `runtime/worker.py` | replaceable local worker adapter |
| `runtime/completion_gate.py` | final verification and delivery |
| `runtime/analyze_repository.py` | read-only repository evidence |
| `onboarding/` | project contract bootstrap/validation |
| `skills/` | reusable project/task knowledge |
| `tests/` | contract and workflow regression tests |
| `examples/repository/` | minimal portable project contract |

Italian guide: [`GUIDA-IT.md`](GUIDA-IT.md)
