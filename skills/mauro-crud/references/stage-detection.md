# Mauro CRUD stage detection

Use observable repository evidence; never classify from a project name alone.

## T0
No operative Mauro CRUD engine. No meaningful `$CRUD->Page(...)` usage and no established T1 form/CRUD micro-framework on the live request path. The application may still follow `mauro-coding-style`.

## T1
Typical evidence:
- no authoritative shared top-level T2 `crud/` engine;
- legacy `Form` / `CrudUtility` / `layout_crud.php` style helpers may exist;
- CRUD/list/AJAX machinery is scattered across `view/`, `action/`, `require/` or similar;
- little or no declarative `$CRUD->Page(...)` usage.

T1 variants can differ significantly. Record observed capabilities rather than forcing a subtype.

## T2
Strong evidence:
- shared top-level `crud/` engine on the live bootstrap path;
- declarative `$CRUD->Page(...)` used by operative views/modules;
- shared page/form/table/AJAX machinery;
- project-specific actions/extensions separated from framework core.

## T3
Separate OOP-oriented generation/framework. Treat as provisional/outside the normal T1/T2 path unless the task explicitly targets it. Presence of classes or a `crud/` directory alone is insufficient; verify the OOP layer executes on the request path.

## Mixed / unknown
Use when evidence conflicts, migration is partial, or confidence is insufficient.

## Reporting
When stage matters, report:
- stage;
- confidence: high / medium / low;
- decisive evidence;
- contradictory evidence;
- what remains unverified.

Do not use arbitrary file-count gates. Escalation is based on architectural ambiguity and blast radius.
