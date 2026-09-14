# Spec Kit integration

MAU ADS uses GitHub Spec Kit as a replaceable workflow engine for non-trivial implementation work. MAU remains the outer policy and evidence layer.

## Ownership

```text
USER REQUEST
  -> MAU intake
     -> repository contract
     -> canonical GitHub Issue
     -> isolated workspace
     -> deterministic risk/complexity routing
        -> TRIVIAL: direct implementation path
        -> STANDARD/FULL/CRITICAL: Spec Kit artifact path
     -> repository-owned verification profile
     -> MAU completion gate
     -> Pull Request
```

MAU owns:

- work identity through the canonical GitHub Issue;
- isolated workspaces;
- risk and complexity classification;
- minimum workflow profile;
- minimum verification profile;
- truthful verification states;
- final completion/delivery gate;
- production authorization boundary.

Spec Kit owns, when routed to it:

- specification artifacts;
- planning artifacts;
- implementation task decomposition;
- artifact consistency/convergence workflow.

The target repository owns executable project verification.

## Profiles

| MAU profile | Workflow | Minimum verification | Intended use |
|---|---|---|---|
| `trivial` | direct `inspect -> implement -> verify` | `minimal` | local deterministic changes such as labels/copy/typos |
| `standard` | `specify -> plan -> tasks -> implement -> converge` | `focused` | ordinary bounded changes |
| `full` | `specify -> clarify -> plan -> tasks -> analyze -> implement -> converge` | `full` | new sections/modules, integrations, cross-cutting work |
| `critical` | full path plus checklist gate | `critical` | production/destructive/credential/irreversible work |

Routing is a minimum. Repository evidence may justify stronger checks. A worker must never silently downgrade the profile returned by intake.

## Model policy

MAU emits capability/cost tiers rather than vendor model names:

- `economy`
- `balanced`
- `strong`

This keeps routing portable across Codex, other workers and future orchestrators. The executor maps a tier to an available model. Model choice must not weaken the required workflow or verification profile.

## Verification profiles

MAU keeps one repository-owned verification entry point in `.ai/project.json` and supplies the selected profile through:

```text
MAU_VERIFICATION_PROFILE=minimal|focused|full|critical
```

A project verifier may use that value to select proportional checks. Example:

```text
minimal
  -> targeted syntax/output/diff checks only

focused
  -> normal project checks + targeted acceptance evidence

full
  -> broader runtime/integration/browser checks relevant to the change

critical
  -> full relevant verification plus safety/rollback evidence required by the project
```

The exact checks remain project-owned. `UNAVAILABLE` and `NOT_RUN` are never converted into `PASS`.

## Spec Kit setup

The adapter is:

```bash
bash bin/mau-spec-kit status /path/to/project
bash bin/mau-spec-kit init /path/to/project --integration codex
```

Initialization uses the official Spec Kit CLI in-place, non-interactively, with the Codex integration and Python scripts. The bundled `lean` preset is installed by default.

The Codex integration is skills-based. MAU does not require a second orchestrator or a separate agent session for each Spec Kit phase. The normal path is one primary coding-agent session following the required Spec Kit skill/artifact sequence, then MAU gates the resulting artifacts deterministically.

## Deterministic completion

For `standard`, `full` and `critical` profiles, MAU completion requires an active Spec Kit feature and these artifacts:

```text
spec.md
plan.md
tasks.md
```

Unchecked implementation tasks block completion. For `critical`, unchecked checklist items also block completion.

After the artifact gate, MAU executes the repository verification entry point with the selected verification profile, checks the final Git state/diff, and only then permits reviewable delivery.

## Onboarding boundary

Spec Kit does not replace repository onboarding. MAU still validates or bootstraps the minimum project contract:

```text
AGENTS.md
.ai/project.json
PROJECT.md
repository-owned verification command
```

Spec Kit is initialized only when a routed workflow needs it. This keeps trivial work cheap and avoids turning every edit into a specification ceremony.
