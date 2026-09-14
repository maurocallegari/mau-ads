# Start Here

MAU ADS is intended to run automatically behind a normal development request.

For a compatible direct coding worker:

```text
1. Receive the user's requested outcome.
2. Automatically obtain a MAU work context before durable edits.
3. If the repository is unknown/invalid, MAU analyzes and safely bootstraps it.
4. Resolve/create the canonical GitHub Issue.
5. Continue only in the isolated workspace returned by the gate.
6. Read the execution contract returned by intake.
7. Follow its workflow profile:
   - trivial -> direct narrow change
   - standard/full/critical -> required Spec Kit skill/artifact sequence
8. Implement the smallest coherent change.
9. Run repository-owned verification at or above the returned verification profile.
10. Pass the MAU completion gate and final diff review.
11. Deliver through PR/review.
12. Stop at READY_TO_DEPLOY unless production is explicitly authorized.
```

The user should not be asked to remember `mau analyze`, `mau onboard`, Spec Kit commands, or similar internal mechanics.

Internal machine-facing entry points:

```text
bin/mau-agent
bash bin/mau-spec-kit status <project>
bash bin/mau-spec-kit init <project> --integration codex
```

Architecture and profile rules: [`docs/SPEC-KIT.md`](docs/SPEC-KIT.md).
