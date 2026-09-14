# T2 contracts

## Core
Treat the shared `crud/` engine as high-blast-radius framework core. Prefer project extension/action paths for application-specific behavior.

## Page
T2 uses the repository's declarative `$CRUD->Page(...)` page-builder conventions. Read a nearby working page before creating a new structure.

## Forms
Use the repository's established Form contract. `Rows` represents visual rows containing one or more field definitions. Copy real field/table names and options from code/schema evidence.

Existing record → update semantics.
New record → insert semantics.

Never route an update to a create handler just to preserve a legacy filename.

## AJAX
Determine the actual JS/bootstrap loaded by the target repository.

T2 may provide compatibility wrappers for legacy function-call shapes. If a legacy wrapper delegates to the T2 dispatcher, preserve it unless the task explicitly requires migration. Do not perform mechanical call-site rewrites without verifying the loaded client implementation and server endpoint.

## Compatibility
When T2 replaces a T1 bootstrap but many legacy pages read old session/global variables, prefer a narrow compatibility mapping derived from the new authoritative state rather than rewriting all readers at once.

Verify every mapping against the target repository.
