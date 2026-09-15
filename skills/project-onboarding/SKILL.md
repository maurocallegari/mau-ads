---
name: project-onboarding
description: Execute or resume deterministic MAU ADS onboarding for any software project. Use for onboarding, repository contract creation, local verification, legacy/production/Git reconciliation, or deciding whether a repository is ready for normal ADS work.
---

# Project onboarding

Use the current MAU ADS runtime in this repository. Do not refer to the former `ai-development-system/04-project-onboarding` tree and do not invent a parallel checklist.

## Authority

1. target repository/workspace evidence;
2. `.ai/project.json`, `AGENTS.md`, `PROJECT.md`, `REPO_MAP.md`;
3. repository-owned verifier;
4. current MAU deterministic gates;
5. relevant shared skills;
6. assumptions, marked and never used to pass a gate.

Production/FTP/SFTP may provide evidence or deployment transport. They are never the development workspace.

## Entry points

The complete path is normally invoked through:

```bash
bin/mau-agent run /absolute/project/root --request "<outcome>"
```

Lower-level onboarding primitives are:

```bash
bin/mau-agent onboard /absolute/project/root --profile auto
bin/mau-agent validate /absolute/project/root --run-verification
bin/mau-agent preflight /absolute/project/root --phase completion
```

The user should not have to remember these commands.

## Profiles

### Generic

Use `generic` for projects that do not follow Mauro's application-specific PHP configuration boundary. The contract is stack-neutral and the repository verifier owns the actual test/build/smoke commands.

### Mauro PHP

Use `mauro-php` for Mauro applications whose runtime configuration follows or is being migrated to:

```text
.env                  runtime-only, ignored; local + production values
  -> require/ads.php  reusable environment/config loader
  -> configure.php    thin project-specific adapter
  -> application bootstrap
```

Requirements:

- one root `.env`, never tracked;
- tracked `.env.example` without real secrets;
- `require/ads.php` owns environment parsing/detection and safety;
- `configure.php` remains a thin adapter preserving project-specific constants and behavior;
- local database/runtime identity must not resolve to production;
- production mail/API/upload/payment/write effects must be blocked or safely redirected locally;
- runtime verification must cover the mechanisms actually used by the application.

An isolated Git worktree does not naturally contain ignored files. The MAU manifest can declare local `runtime_files` such as `.env`; intake copies them from the source workspace into the isolated worktree without tracking them.

## Onboarding behavior

When a project lacks the contract, bootstrap occurs inside the Issue worktree, not in the source working copy. The generated `PROJECT.md` and verifier are intentionally conservative. The implementation worker must inspect repository evidence, complete project knowledge/configuration, and replace the generated `UNAVAILABLE` verifier with real checks.

Do not declare onboarding complete from narrative judgment. Completion requires the project verifier plus MAU completion preflight to pass.

## Skill composition

Load only skills required by evidence/task, such as Mauro coding conventions, CRUD, persistent-data safety, bug investigation, frontend verification, AI integration or code review. Generic onboarding must not inherit Mauro-specific requirements just because MAU ADS is maintained by Mauro.

## Verification truth

Allowed states are exactly `PASS`, `FAIL`, `UNAVAILABLE`, `NOT_RUN`, `NOT_APPLICABLE`.

Missing evidence is never PASS. `UNAVAILABLE` cannot become READY.
