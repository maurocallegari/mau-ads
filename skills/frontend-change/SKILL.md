---
name: frontend-change
version: 1.1.0
description: Use for HTML, CSS, JavaScript, UI action, layout, responsive, Bootstrap, Tailwind, jQuery or other frontend presentation/interaction changes. Discover and reuse native repository UI patterns before creating anything new, minimize blast radius, and verify the rendered result proportionally.
---

# Frontend Change

## Goal

Make the smallest UI change that satisfies the requested behavior and looks/behaves as if it already belonged to the application.

## Activate when

Use for changes involving:
- HTML/markup;
- CSS/layout/responsive behavior;
- Bootstrap/Tailwind classes;
- jQuery/JavaScript interaction;
- buttons, actions, menus, modals, forms and visual controls;
- user-visible labels when rendered placement/behavior matters.

Do not activate for backend-only changes.

## Native-first workflow

Before editing, follow this order:

```text
DISCOVER → REUSE → ADAPT → CREATE
```

1. Identify the exact target UI and behavior.
2. Search the same page/module for an equivalent pattern.
3. If needed, search the same repository for 1–3 analogous examples.
4. Extract the native pattern: markup, classes, spacing, iconography, action placement, tooltip conventions, JS/event handling, permission handling and responsive behavior.
5. Reuse an existing component/helper/pattern when semantics match.
6. Adapt the closest native pattern when exact reuse is not possible.
7. Create a new pattern only when repository evidence shows no suitable existing one.
8. Make the minimum coherent change.
9. Verify both functional correctness and native consistency.

## Style precedence

When multiple approaches are valid, prefer:

```text
same page/module
→ same repository
→ same Mauro/framework family
→ shared skill convention
→ new pattern
```

Repository-native consistency takes precedence over generic framework or design best practice unless the local pattern is defective, unsafe, inaccessible, or explicitly being redesigned.

## Rules

- Preserve the repository's frontend stack; do not introduce a new framework/build system for a local change.
- Prefer additive changes over replacing existing controls.
- Do not invent a new component/helper when an equivalent pattern already exists.
- Do not create a second visual language for a behavior already represented elsewhere in the repository.
- Reuse existing icon family, button hierarchy, tooltip style, spacing conventions and action ordering when applicable.
- Keep responsive behavior intact when the touched area is responsive.
- Preserve neighboring controls and permissions unless replacement/removal is explicitly requested.
- Do not turn a copy/spacing/button change into unrelated redesign.
- For Mauro repositories, compose with `mauro-coding-style`.
- For CRUD-generated UI, compose with `mauro-crud` when framework contracts are involved.

## Native consistency check

After the change, ask both:

```text
Does it work?
Does it look and behave native to this application?
```

Check only what is relevant:
- same component/action pattern;
- same spacing and visual hierarchy;
- same iconography and labels/terminology;
- same interaction/tooltip conventions;
- same permission/visibility behavior;
- no new UI pattern introduced without a concrete need.

This is a consistency check, not a requirement for broad visual regression testing.

## Verification

Follow ADS chapter 06: minimum sufficient verification proportional to risk.

Typical levels:

```text
text/label only
→ inspect diff + verify rendered text when practical

localized visual change
→ inspect affected view + native consistency check

interactive control
→ verify trigger + expected result + neighboring controls

cross-page/responsive change
→ verify affected representative pages/viewports
```

Do not require broad E2E, staging or unrelated regression suites for a trivial localized presentation change.

Never claim visual/runtime verification when only static code inspection was possible.
