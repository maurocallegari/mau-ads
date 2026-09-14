---
name: feature-planning
description: Plan non-trivial software changes before implementation. Use when a task is cross-cutting, ambiguous, high-risk, architectural, affects shared code or database behavior, or explicitly asks for a plan. Do not use for trivial localized edits.
---

# Feature Planning

Plan only when planning adds value.

## Goal

Produce an implementation plan grounded in the actual repository, not a generic design proposal.

## Workflow

1. Read repository instructions and relevant documentation.
2. Inspect the current implementation and execution path.
3. Identify affected components, dependencies, contracts, and blast radius.
4. Separate:
   - observed facts;
   - assumptions;
   - unresolved decisions.
5. Define the smallest implementation that satisfies the requested behavior.
6. Identify verification required after implementation.
7. Identify risks only when they materially affect the plan.

## Planning depth

### Small but non-trivial task

Return:
- intended change;
- affected areas/files;
- verification.

### Complex task

Return:
- current behavior;
- target behavior;
- implementation steps;
- affected components/files;
- data or schema impact;
- compatibility concerns;
- verification strategy;
- unresolved decisions.

## Constraints

- Do not redesign unrelated architecture.
- Do not propose modernization unless required by the task.
- Do not fabricate repository behavior.
- Prefer concrete file paths and existing abstractions over generic recommendations.
- Do not turn a simple task into a large project.
- Do not implement while the user has requested planning only.

## Human gate

Require explicit approval before implementation only when:
- the proposed solution materially expands the requested scope;
- an irreversible or destructive operation is involved;
- production or external systems would be changed;
- a major architectural or compatibility decision remains unresolved.

Otherwise, if the user requested both planning and implementation, continue after planning without an unnecessary approval stop.

## Proportionality refinements

- When unresolved product or domain decisions can materially change the implementation, identify them before committing to a preferred technical design. A provisional recommendation is allowed, but label it explicitly as provisional.
- Keep verification proportional to the change. Do not prescribe broad regression testing for trivial presentation-only edits unless the affected execution path justifies it.
