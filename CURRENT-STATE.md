# Spec Kit integration baseline

This branch keeps the public MAU ADS baseline stack-neutral while adding a deterministic workflow layer for non-trivial changes.

The **core operating model remains repository-first**:

- repository-first project contracts;
- work identity through GitHub Issues;
- isolated implementation workspaces;
- deterministic risk/complexity routing;
- mandatory pre-implementation clarification for Spec Kit-routed work;
- Spec Kit artifacts for standard/full/critical workflows;
- project-defined proportional testing and verification;
- reviewable delivery through Pull Requests;
- explicit deployment authorization boundaries;
- orchestrator/worker portability;
- generic onboarding validation and example repository contracts.

Current routing contract:

```text
trivial  -> direct workflow -> minimal verification
standard -> specify -> clarify -> clarification gate -> focused verification
full     -> specify -> clarify -> clarification gate -> full workflow -> full verification
critical -> full workflow + clarification + safety/checklist gates -> critical verification
```

An apparently small but under-specified request is deliberately promoted out of `trivial`. Non-trivial implementation remains blocked until the active Spec Kit feature contains a valid `clarification.json` and the clarification gate returns `PASS`.

The clarification contract separates what the agent may resolve itself from what must be asked:

- repository-backed implementation facts: resolve automatically;
- sourced non-substantive technical assumptions: allowed;
- missing functional behavior, risk acceptance or irreversible/destructive semantics: ask the user;
- unresolved questions: `NEEDS_CLARIFICATION`, `user_input_required=true`, `implementation_authorized=false`.

MAU owns intake, GitHub work identity, isolation, routing, clarification state, minimum verification profile and completion. Spec Kit owns specification/planning/task artifacts when selected. The target repository owns executable verification.

The default direct-agent design does not require an additional orchestrator or a separate agent process for every Spec Kit phase. Model routing is currently expressed as portable capability/cost tiers (`economy`, `balanced`, `strong`); mapping those tiers to concrete providers/models belongs to the executor/orchestrator and is not faked by MAU.

The repository also publishes an **optional reusable skill catalog** under `skills/`, including both generic workflow skills and Mauro-specific PHP/MySQL/JavaScript, CRUD, database-safety and AI-integration conventions.

These domain-specific skills are loaded only when repository evidence and task context make them relevant. They do not change the stack-neutral contract of the MAU ADS core and never override target-repository evidence or project-owned verification.
