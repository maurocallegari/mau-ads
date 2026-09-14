# Skills and reusable capabilities

MAU ADS includes the reusable skill catalog directly in this repository.

A compatible worker should load only the smallest set of skills required by the task. Repository evidence and project-owned verification remain authoritative: a skill guides method and conventions, but never overrides the actual project contract.

## Published skills

| Skill | Purpose |
|---|---|
| [`project-onboarding`](project-onboarding/) | deterministic project onboarding and certification gates |
| [`feature-planning`](feature-planning/) | planning for non-trivial, cross-cutting or high-risk changes |
| [`bug-investigation`](bug-investigation/) | evidence-first defect investigation and minimal fixes |
| [`code-review`](code-review/) | risk-first review of diffs, regressions and verification gaps |
| [`frontend-change`](frontend-change/) | HTML/CSS/JS/UI/responsive changes with native-pattern reuse |
| [`mauro-coding-style`](mauro-coding-style/) | shared Mauro PHP/MySQL/JavaScript conventions |
| [`mauro-crud`](mauro-crud/) | Mauro CRUD T0/T1/T2/T3 contracts, maintenance and migration knowledge |
| [`mysql-change-safety`](mysql-change-safety/) | safety workflow for persistent MySQL schema/data changes |
| [`php-ai-integration`](php-ai-integration/) | production-safe PHP AI/LLM integration policy |

## Routing

See [`ROUTING.md`](ROUTING.md) for the catalog routing rules.

The routing principle is:

```text
TASK
  -> classify work
  -> inspect repository evidence
  -> select only relevant skills
  -> implement
  -> minimum sufficient verification
```

Skills compose when needed. Examples:

```text
bug in Mauro CRUD
→ bug-investigation + mauro-coding-style + mauro-crud + code-review

persistent MySQL change
→ mysql-change-safety + relevant project/domain skill + code-review

PHP AI feature
→ feature-planning when non-trivial + mauro-coding-style + php-ai-integration + code-review

frontend change
→ frontend-change + project-specific style/framework skill when applicable
```

## Lock file

[`skills.lock`](skills.lock) records the source tree SHA of the catalog snapshot imported into this public baseline.

## Authority

For a concrete task, use this order:

1. current target repository code and runtime evidence;
2. target repository `AGENTS.md`, `.ai/project.json`, `PROJECT.md` and verification entry point;
3. relevant MAU ADS skills;
4. assumptions.

A reusable skill never turns missing evidence into `PASS` and never authorizes production by itself.
