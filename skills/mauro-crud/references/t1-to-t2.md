# T1 to T2 migration

A T1→T2 upgrade changes framework generation and therefore requires explicit migration scope.

## Sequence
1. Detect and record the source stage.
2. Identify and inspect the authoritative T2 donor/reference implementation.
3. Map bootstrap, login/session roles, sidebar/navigation, page builder, form contract, lists and AJAX dispatch.
4. Preserve DB schema and business terminology unless separately requested.
5. Establish T2 bootstrap/core without mixing two competing framework implementations.
6. Recreate required legacy compatibility variables from T2 authoritative state.
7. Convert a simple representative module first.
8. Convert remaining modules in functional batches; complex/tabbed/custom pages last.
9. Compare original and converted actions/fields/links/filters.
10. Run syntax/structural checks for every batch and runtime smoke tests where available.

## No-invention
Do not add actions, fields, tabs, filters, modals or business logic that are absent from the original implementation or explicit task.

## Lists
Preserve behavior first. Move legacy list feeds to the repository's verified T2 list/table contract only when needed; do not force AJAX where a simple local/static table is the established T2 solution.

## Tabs
Use the actual T2 tab contract from the donor/reference repository. Distinguish lazy/async content from content rendered during the initial page load based on verified framework behavior.

## Runtime unavailable
Proceed with syntax and structural verification when DB/runtime is unavailable, but mark DB-backed behavior as pending. Never report a runtime PASS that was not executed.
