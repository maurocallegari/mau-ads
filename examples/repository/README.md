# Example AI-ready repository

This directory shows the minimum repository contract expected by MAU ADS.

| File | Required | Purpose |
|---|---:|---|
| `AGENTS.md` | yes | operating rules for workers |
| `PROJECT.md` | yes | durable project-specific knowledge |
| `.ai/project.json` | yes | machine-readable metadata and verification entry point |
| `REPO_MAP.md` | optional | compact navigation when structure is not obvious |
| `dev/verify-local.sh` | yes | one project-owned verification entry point |

The example is intentionally stack-neutral. These files should contain durable project knowledge and operating rules, not temporary task state or secrets.
