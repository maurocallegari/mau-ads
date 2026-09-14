# Deterministic onboarding gates

## Gate model

A gate is valid only when it has a stable name, observed value, current evidence, deterministic pass rule, and concrete recovery action.

`UNKNOWN`, `NOT_RUN`, missing, stale, unparsable and unverifiable do not become `PASS`.

## Core gates — every project

| Gate | Required proof |
|---|---|
| ISSUE_IDENTITY | canonical GitHub Issue when durable work occurs |
| WORKSPACE_AUTHORITY | exact repository root; no parent/competing Git authority |
| PROFILE_RESOLVED | tracked `.ai/project.json` or deterministic profile resolution |
| SECRETS_EXCLUDED | no real secrets/runtime customer data in tracked files |
| KNOWLEDGE_BASELINE | current `AGENTS.md`, `PROJECT.md`, and justified `REPO_MAP.md` |
| VERIFICATION_ENTRYPOINT | executable project verification declared in `.ai/project.json` |
| VERIFICATION_RESULT | current project verification passes with explicit evidence |
| GIT_BASELINE | clean HEAD, branch, origin, upstream and remote alignment |
| FINAL_AUDIT | canonical preflight/finalizer passes |

For the stack-neutral `generic` profile, these are the normative gates. Stack-specific proof belongs in `dev/verify-local.sh` rather than being invented by ADS.

## Additional Mauro PHP gates

Apply these only to the Mauro PHP profile when relevant to the application:

| Gate | Required proof |
|---|---|
| CONFIG_BOUNDARY | tracked `require/ads.php` + thin secret-free `configure.php` + ignored single `.env` + tracked `.env.example` |
| PHP_PARITY | production/local PHP major-minor and required extensions |
| DATABASE_ISOLATION | local database identity and proof it is not production, when DB-backed |
| DATABASE_SCHEMA | expected local schema/data baseline, when applicable |
| PRODUCTION_WRITE_ISOLATION | production mail/API/upload/payment/write integrations blocked or redirected locally |
| URL_PATH_BOUNDARY | redirects, assets, AJAX/API, exports and filesystem paths remain local |
| RUNTIME_SMOKE | stable local runtime responds through the expected entrypoints |
| FUNCTIONAL_MATRIX | representative behavior across applicable web mechanisms |

A gate that truly does not apply may be `NOT_APPLICABLE`, but only with observed evidence explaining why.

## Mauro PHP functional matrix

Use this only for a web application where the mechanisms exist:

```text
public_bootstrap
authentication_session
navigation
list_table
detail_form
ajax_api
assets_layout
print_report_export
upload_download
logout
```

A successful homepage alone is not certification.

## Generic verification examples

The generic profile can use any coherent repository-owned verifier, for example:

```text
Python:      pytest + lint/type checks
Node/TS:     npm test + npm run build
Go:          go test ./...
Rust:        cargo test
Java:        project build/test command
Static site: build + link/browser smoke checks
Library/CLI: unit/integration tests + package/build validation
```

ADS cares that the verifier is explicit, executable, current and truthful; it does not force one technology.

## Recovery

Classify failures before changing application code:

1. shared ADS/onboarding contract defect;
2. missing repository/runtime evidence;
3. project configuration defect;
4. pre-existing application defect;
5. genuine authority/destructive-choice blocker.

After a fix, invalidate stale evidence and rerun from the earliest affected gate.
