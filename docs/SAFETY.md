# Safety

These boundaries apply regardless of agent, model, language or orchestrator.

- Never commit, print or copy secrets into Git.
- Do not use production systems as development workspaces.
- Destructive operations, authentication/authorization changes, persistent-data changes, shared-core changes and externally visible side effects require higher scrutiny.
- Production deployment requires explicit authorization for that operation.
- Never report a verification result that did not actually occur.
- If a relevant check cannot run, report `UNAVAILABLE` or `NOT_RUN`; never convert missing evidence into `PASS`.
- Preserve user data and existing behavior unless the requested change explicitly requires otherwise.
- Inspect the final diff for accidental scope growth, generated files and unrelated edits.
