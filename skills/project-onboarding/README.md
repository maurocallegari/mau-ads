# Project Onboarding

The skill delegates execution to the canonical ADS coordinator
`04-project-onboarding/scripts/ads_onboard.py`, which resolves `ADS_ROOT`,
reconciles safe runtime drift, runs certification gates and persists evidence.

```text
Onboard <project>
        |
        v
resolve authority and acquire evidence
        |
        v
normalize config + isolated local runtime
        |
        v
current-HEAD behavioral certification
        |
        v
knowledge + GitHub baseline
        |
        v
ADS final executable gate
        |
        +--> ONBOARDED
        |
        +--> STOP: gate + evidence + resume action
```

This skill orchestrates ADS chapter 04. It does not duplicate framework, coding-style, database, frontend, debugging or review knowledge.

The final state is produced by executable gates, not by an agent's narrative assessment.
