# Neuron AI reference policy

This reference keeps only stable integration facts and discovery rules. Do not copy the full upstream API surface into this repository.

## Canonical upstream

- Project: `neuron-core/neuron-ai`
- Package: `neuron-core/neuron-ai`
- Documentation: use the official Neuron documentation linked by the upstream repository.
- Current upstream branch/release documentation must win over memorized examples.

As verified during creation of this Skill (2026-08-20), upstream declares PHP `^8.1` and provides native concepts for providers, tools/toolkits, structured output, RAG, workflows, monitoring/debugging and AI-assisted-development skills.

Runtime compatibility must always be checked again in the target project and against current upstream requirements before installation or upgrade.

## Use upstream skills instead of duplicating APIs

Neuron currently publishes specialized skills including:
- `neuron-agent-builder` — agent construction;
- `neuron-tool-creator` — tools/toolkits;
- `neuron-structured-output` — typed/structured model output;
- `neuron-rag-specialist` — RAG;
- `neuron-workflow-architect` — workflows;
- `neuron-debugger` — debugging;
- `neuron-test-engineer` — testing;
- `neuron-evaluation-engineer` — evaluation.

When available in the agent runtime, use the relevant upstream skill together with `php-ai-integration`.

Responsibility split:

```text
php-ai-integration
= application architecture, provider portability, validation, auth, failure and persistence boundaries

official neuron-* skills/docs
= current Neuron classes, APIs, configuration and framework-specific implementation
```

## Version drift rule

Neuron evolves quickly. Never encode a current constructor signature, namespace, model option or provider list into durable project architecture unless the project actually depends on it.

Before implementing or upgrading Neuron:
1. inspect the project's `composer.json` / lock state;
2. identify installed Neuron version if present;
3. consult documentation/source matching that version;
4. preserve existing integration unless migration is part of the task;
5. run Composer/runtime checks before claiming compatibility.
