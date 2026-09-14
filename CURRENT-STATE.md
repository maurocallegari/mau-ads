# Spec Kit integration baseline

This branch keeps the public MAU ADS baseline stack-neutral while adding deterministic repository-readiness and task-workflow gates.

The **core operating model remains repository-first**:

- repository-first project contracts;
- blocking onboarding readiness through `.ai/onboarding.json`;
- evidence-first onboarding clarification instead of guessed project facts;
- successful `focused` verifier baseline before implementation can start;
- work identity through GitHub Issues only after onboarding is `READY`;
- isolated implementation workspaces;
- deterministic risk/complexity routing;
- mandatory pre-implementation clarification for Spec Kit-routed work;
- Spec Kit artifacts for standard/full/critical workflows;
- project-defined proportional testing and verification;
- reviewable delivery through Pull Requests;
- explicit deployment authorization boundaries;
- orchestrator/worker portability.

Repository readiness now follows:

```text
analyze -> bootstrap missing contract -> assess onboarding
        -> repository evidence resolves facts OR explicit user questions
        -> configure real verifier -> focused baseline PASS
        -> onboarding READY
        -> feature Issue/workspace may be created
```

Bootstrap alone never means `ONBOARDED`. The generated verifier reports `UNAVAILABLE`; it must be replaced before readiness. Finalization records the verifier hash, so changing that verifier invalidates readiness until a new baseline is established.

Current task routing contract:

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

MAU owns repository readiness, intake, GitHub work identity, isolation, routing, clarification state, minimum verification profile and completion. Spec Kit owns specification/planning/task artifacts when selected. The target repository owns executable verification.

The default direct-agent design does not require an additional orchestrator or a separate agent process for every Spec Kit phase. Model routing is currently expressed as portable capability/cost tiers (`economy`, `balanced`, `strong`); mapping those tiers to concrete providers/models belongs to the executor/orchestrator and is not faked by MAU.

The repository also publishes an **optional reusable skill catalog** under `skills/`, including both generic workflow skills and Mauro-specific PHP/MySQL/JavaScript, CRUD, database-safety and AI-integration conventions.

These domain-specific skills are loaded only when repository evidence and task context make them relevant. They do not change the stack-neutral contract of the MAU ADS core and never override target-repository evidence or project-owned verification.
