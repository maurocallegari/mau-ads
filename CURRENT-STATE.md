# Spec Kit integration baseline

This branch keeps the public MAU ADS baseline stack-neutral while adding a deterministic workflow layer for non-trivial changes.

The **core operating model remains repository-first**:

- repository-first project contracts;
- work identity through GitHub Issues;
- isolated implementation workspaces;
- deterministic risk/complexity routing;
- Spec Kit artifacts for standard/full/critical workflows;
- project-defined proportional testing and verification;
- reviewable delivery through Pull Requests;
- explicit deployment authorization boundaries;
- orchestrator/worker portability;
- generic onboarding validation and example repository contracts.

Current routing contract:

```text
trivial  -> direct workflow -> minimal verification
standard -> Spec Kit core   -> focused verification
full     -> Spec Kit full   -> full verification
critical -> Spec Kit + safety/checklist gates -> critical verification
```

MAU owns intake, GitHub work identity, isolation, routing, minimum verification profile and completion. Spec Kit owns specification/planning/task artifacts when selected. The target repository owns executable verification.

The default direct-agent design does not require an additional orchestrator or a separate agent process for every Spec Kit phase. Model routing is currently expressed as portable capability/cost tiers (`economy`, `balanced`, `strong`); mapping those tiers to concrete providers/models belongs to the executor/orchestrator and is not faked by MAU.

The repository also publishes an **optional reusable skill catalog** under `skills/`, including both generic workflow skills and Mauro-specific PHP/MySQL/JavaScript, CRUD, database-safety and AI-integration conventions.

These domain-specific skills are loaded only when repository evidence and task context make them relevant. They do not change the stack-neutral contract of the MAU ADS core and never override target-repository evidence or project-owned verification.
