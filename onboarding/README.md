# Generic onboarding

MAU ADS onboarding is stack-neutral and evidence-first. It is a blocking readiness gate, not just generation of a few Markdown files.

```text
unknown repository
  -> read-only analysis
  -> safe bootstrap of missing contract files
  -> onboarding assessment
       -> resolve facts from repository evidence
       -> ask the user only for unresolved required facts
  -> configure real project verifier
  -> run focused verification baseline
  -> onboarding READY
```

Until onboarding is `READY`, application-code implementation is not authorized.

## Bootstrap output

Bootstrap creates only missing files and preserves existing ones:

- `AGENTS.md` — worker invariants and MAU gate rules;
- `PROJECT.md` — conservative project skeleton plus observed evidence;
- `REPO_MAP.md` — top-level repository map from deterministic file scanning;
- `.ai/project.json` — machine-readable verification entry point;
- `.ai/onboarding.json` — machine-readable onboarding state/evidence/questions;
- `dev/verify-local.sh` — safe placeholder verifier that reports `UNAVAILABLE`.

The Markdown files are initially generated from deterministic templates and repository evidence collected by `runtime/analyze_repository.py`; bootstrap does not ask an LLM to invent project facts. During onboarding, the primary coding agent inspects source/docs/tests and enriches durable documentation only with evidence-backed facts. If a required fact cannot be established from the repository, it becomes an explicit onboarding question rather than a guess.

## Onboarding state

`.ai/onboarding.json` tracks:

- project purpose plus evidence;
- canonical source path plus evidence;
- durable constraints;
- verification command and baseline evidence;
- open/resolved onboarding questions.

Typical gate states:

```text
NEEDS_ASSESSMENT
NEEDS_CLARIFICATION
NEEDS_VERIFICATION_SETUP
READY
BLOCKED
```

`NEEDS_CLARIFICATION` sets `user_input_required=true`. The worker should surface only the unresolved questions, record the answers, then rerun the gate.

## Verification baseline

A repository cannot become `READY` with the generated placeholder verifier. Finalization executes the repository-owned verifier with:

```text
MAU_VERIFICATION_PROFILE=focused
```

The baseline must return `PASS`. MAU records the verifier SHA-256; if that verifier changes later, onboarding returns to `NEEDS_VERIFICATION_SETUP` until a new baseline is finalized.

Verification exit-state convention:

```text
0 -> PASS
1 -> FAIL
2 -> UNAVAILABLE
3 -> NOT_RUN
4 -> NOT_APPLICABLE
```

## Runtime primitives

Compatible agents/orchestrators normally call these invisibly, but the primitives are directly testable:

```bash
python onboarding/onboarding_gate.py status /path/to/project
python onboarding/onboarding_gate.py seed /path/to/project
python onboarding/onboarding_gate.py finalize /path/to/project
```

The user should not need to remember these commands during normal development.
