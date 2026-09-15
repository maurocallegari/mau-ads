# Deterministic onboarding gates

A gate has a stable name, current evidence, deterministic rule and recovery action. `UNKNOWN`, `NOT_RUN`, missing, stale or unverifiable evidence never becomes PASS.

## Core gates

| Gate | Required proof |
|---|---|
| ISSUE_IDENTITY | canonical GitHub Issue for durable work |
| WORKSPACE_AUTHORITY | isolated non-base Git branch/worktree |
| CONTRACT | valid `AGENTS.md`, `PROJECT.md`, `.ai/project.json` |
| SECRETS_EXCLUDED | runtime env/private key candidates are not tracked |
| PRODUCTION_BOUNDARY | production deployment requires explicit authorization |
| VERIFICATION_ENTRYPOINT | repository-owned executable verifier |
| VERIFICATION_RESULT | current verifier result is PASS or justified NOT_APPLICABLE |
| DIFF_INTEGRITY | `git diff --check` succeeds and intended work produced a change |
| FINAL_AUDIT | completion preflight passes on the final workspace |

## Additional Mauro PHP gates

| Gate | Required proof |
|---|---|
| CONFIG_BOUNDARY | `require/ads.php`, thin `configure.php`, tracked `.env.example` |
| LOCAL_RUNTIME_ENV | local `.env` exists in the worktree and remains ignored/untracked |
| PHP_PARITY | project verifier proves required PHP version/extensions |
| DATABASE_ISOLATION | project verifier proves local DB identity is not production |
| DATABASE_SCHEMA | expected local schema/data baseline when applicable |
| PRODUCTION_WRITE_ISOLATION | external production writes are blocked/redirected locally |
| URL_PATH_BOUNDARY | local URLs/paths/assets/AJAX/exports stay local |
| RUNTIME_SMOKE | local runtime responds through expected entrypoints |
| FUNCTIONAL_MATRIX | representative behavior across mechanisms used by the app |

The generic MAU runtime enforces the first two Mauro-specific structural gates directly. Application/runtime-specific proof belongs in the repository verifier because only the project knows the correct commands and expected behavior.

## Recovery loop

On failure, MAU returns executable evidence to the worker. The worker may repair implementation/configuration/tests, but must not weaken a correct gate merely to obtain PASS. The loop is bounded by `workflow.max_fix_attempts`.
