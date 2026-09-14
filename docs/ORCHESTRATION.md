# Orchestration

An orchestrator is an optional coordination layer, not a new source of truth.

## It may own

- queueing and task dispatch;
- worker/model selection;
- dependency ordering;
- parallel execution;
- collision avoidance;
- UI and progress visibility.

## It must not own

- a competing source-code history;
- a second durable task database that conflicts with GitHub;
- private project facts that never return to the repository;
- invented verification status.

## Parallel work

```text
Issue A -> Worker A -> isolated workspace A -> verify -> PR A
Issue B -> Worker B -> isolated workspace B -> verify -> PR B
```

If two tasks collide, serialize them, rebase explicitly or integrate through a dedicated step. Never allow blind concurrent writes to the same working tree.

Worker replacement should not require rewriting the project contract.
