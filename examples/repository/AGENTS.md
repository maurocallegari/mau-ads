# AGENTS.md

## Before editing

- Read `.ai/project.json`, `PROJECT.md` and `REPO_MAP.md` when present.
- Inspect the relevant source and tests before changing behavior.
- Use one canonical work item for one independently deliverable outcome.

## Scope

- Make the smallest coherent change that satisfies the requested outcome.
- Preserve existing behavior unless the task explicitly requires changing it.
- Avoid unrelated refactors and formatting churn.

## Verification

- Run the project-owned verification entry point.
- Report verification truthfully.
- Inspect the final diff for unintended edits.

## Safety

- Never commit secrets.
- Do not use production as a development workspace.
- Production deployment requires explicit authorization.
