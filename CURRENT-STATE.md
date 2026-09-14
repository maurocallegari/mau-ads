# Public baseline

This repository is the public MAU ADS baseline.

The **core operating model remains stack-neutral**:

- repository-first project contracts;
- work identity through GitHub Issues;
- isolated implementation workspaces;
- project-defined testing and verification;
- reviewable delivery through Pull Requests;
- explicit deployment authorization boundaries;
- orchestrator/worker portability;
- generic onboarding validation and example repository contracts.

The repository also publishes an **optional reusable skill catalog** under `skills/`, including both generic workflow skills and Mauro-specific PHP/MySQL/JavaScript, CRUD, database-safety and AI-integration conventions.

These domain-specific skills are loaded only when repository evidence and task context make them relevant. They do not change the stack-neutral contract of the MAU ADS core and never override target-repository evidence or project-owned verification.
