# Automatic lifecycle

MAU ADS is not a command interface for the human. It is an invisible operating layer used by a coding agent or orchestrator.

The human interaction stays ordinary:

```text
"Fix this bug in repository X."
```

A compatible executor automatically performs:

```text
REQUEST
  -> INTAKE GATE
  -> REPOSITORY ANALYSIS / REFRESH
  -> AUTOMATIC ONBOARDING when required
  -> CONTRACT VALIDATION
  -> CANONICAL WORK ITEM
  -> ISOLATED WORKSPACE
  -> WORKER
  -> PROJECT VERIFICATION
  -> FINAL DIFF REVIEW
  -> PR / REVIEW
  -> READY_TO_DEPLOY
```

## Core invariant

```text
NO VALID MAU WORK CONTEXT
  =
NO DURABLE WRITES
```

The internal `bin/mau-agent` and runtime modules are machine-facing primitives. They exist so workers can execute the contract consistently; the human should not need to remember their syntax.

## Standalone mode

`main` is the standalone reference profile.

When no external orchestrator is present, the intake gate is responsible for:

- validating or safely bootstrapping the project contract;
- resolving/creating the canonical GitHub Issue when GitHub CLI access is available;
- refusing readiness when the work item cannot be established;
- creating an isolated Git worktree for the writer;
- returning a machine-readable work context.

The completion gate runs repository-owned verification, checks the final Git state, pushes the isolated branch and creates/reuses a Pull Request when GitHub delivery is available.

## Orchestrated mode

An external orchestrator may own task dispatch, GitHub integration and workspace creation. MAU then validates repository-specific conditions and authorizes writes only after the orchestrator supplies durable work-item identity and isolated workspace evidence.
