# Start Here

MAU ADS is intended to run automatically behind a normal development request.

For a compatible direct coding worker:

```text
1. Receive the user's requested outcome.
2. Automatically obtain a MAU work context before durable edits.
3. If the repository is unknown/invalid, MAU analyzes and safely bootstraps it.
4. Resolve/create the canonical GitHub Issue.
5. Continue only in the isolated workspace returned by the gate.
6. Read project context and relevant source/tests.
7. Implement the smallest coherent change.
8. Run project-owned verification and final diff review.
9. Deliver through PR/review.
10. Stop at READY_TO_DEPLOY unless production is explicitly authorized.
```

The user should not be asked to remember `mau analyze`, `mau onboard`, or similar commands.

Internal machine-facing entry point:

```text
bin/mau-agent
```

