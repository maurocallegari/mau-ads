# Repository analysis

Repository analysis is a first-class phase before onboarding or implementation.

## Goal

Turn an unknown repository into grounded evidence without asking an LLM to invent facts.

```text
UNKNOWN REPOSITORY
  -> deterministic read-only scan
  -> evidence
  -> project contract / worker interpretation
```

## Deterministic scanner

`runtime/analyze_repository.py` collects evidence such as:

- Git root, branch, head, origin and dirty state;
- top-level structure and a structural fingerprint;
- build/dependency manifests;
- CI configuration;
- existing AI/developer context files;
- test evidence;
- migration/schema evidence;
- configuration examples;
- likely entrypoint candidates.

It does not claim architectural meaning that repository evidence does not support.

## Durable vs transient knowledge

Scanner output is transient. Do not commit a continuously stale repository-analysis dump.

Only stable facts that materially reduce future rediscovery are promoted into:

- `AGENTS.md`;
- `PROJECT.md`;
- `REPO_MAP.md`;
- `.ai/project.json`.

## Refresh

A structural fingerprint lets an executor decide whether the repository has changed enough to justify a targeted refresh. Normal task execution should not repeat expensive semantic rediscovery when the durable contract is still valid.
