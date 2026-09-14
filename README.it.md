# MAU ADS

Un operating layer repository-first per lo sviluppo software assistito da AI.

La persona fa una normale richiesta di sviluppo. MAU ADS viene usato automaticamente dall'agente di coding o dall'orchestratore per rendere il lavoro tracciabile, isolato e verificabile, senza legare il workflow a un modello, linguaggio, framework o prodotto di orchestrazione specifico.

**L'utente non deve ricordarsi comandi MAU.** Gli entry point runtime esistono per agenti e orchestratori.

Per una spiegazione completa e operativa in italiano: [`GUIDA-IT.md`](GUIDA-IT.md).

## Lifecycle automatico

```text
RICHIESTA
  -> intake gate automatico
  -> analisi / refresh repository
  -> onboarding automatico se necessario
  -> validazione del contratto del progetto
  -> work item canonico
  -> workspace isolato
  -> implementazione
  -> verifica definita dal progetto
  -> pull request / review
  -> merge
  -> READY_TO_DEPLOY
  -> produzione solo con autorizzazione esplicita
```

## Contratto del progetto

Un repository AI-ready espone un contratto piccolo ed esplicito:

- `AGENTS.md` — regole operative per qualsiasi worker;
- `.ai/project.json` — metadati machine-readable e punto di ingresso della verifica;
- `PROJECT.md` — conoscenza durevole specifica del progetto;
- `REPO_MAP.md` — navigazione compatta opzionale quando la struttura non è ovvia;
- un entry point di verifica posseduto dal repository e dichiarato in `.ai/project.json`.

Vedi [`examples/repository/`](examples/repository/) per un esempio minimo completo.

## Invarianti fondamentali

1. L'evidenza del repository prevale sulla memoria della sessione.
2. Senza un MAU work context valido non sono consentite modifiche durevoli.
3. Un outcome consegnabile indipendentemente corrisponde normalmente a una sola Issue GitHub canonica.
4. Writer paralleli non modificano mai lo stesso working tree.
5. L'analisi del repository è evidence-first e read-only.
6. I test sono controlli eseguibili; la verifica è l'evidenza che l'outcome richiesto sia corretto.
7. Gli stati di verifica devono essere veritieri: `PASS`, `FAIL`, `UNAVAILABLE`, `NOT_RUN`, `NOT_APPLICABLE`.
8. Il merge non autorizza la produzione.
9. Modelli, agenti e orchestratori sono sostituibili.

## Mappa del repository

| Percorso | Scopo |
|---|---|
| [`GUIDA-IT.md`](GUIDA-IT.md) | guida completa in italiano |
| [`START-HERE.md`](START-HERE.md) | ingresso operativo breve per umano/worker |
| [`AGENTS.md`](AGENTS.md) | contratto operativo executor-neutral |
| [`skills/`](skills/) | catalogo pubblico delle skill riusabili e regole di routing |
| [`docs/AUTOMATIC-LIFECYCLE.md`](docs/AUTOMATIC-LIFECYCLE.md) | lifecycle automatico invisibile |
| [`docs/REPOSITORY-ANALYSIS.md`](docs/REPOSITORY-ANALYSIS.md) | discovery evidence-first del repository |
| [`docs/STANDALONE.md`](docs/STANDALONE.md) | ownership nel profilo standalone |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | ownership e confini del sistema |
| [`docs/DEVELOPMENT-WORKFLOW.md`](docs/DEVELOPMENT-WORKFLOW.md) | lifecycle richiesta-consegna |
| [`docs/PROJECT-CONTRACT.md`](docs/PROJECT-CONTRACT.md) | contratto minimo di un repository AI-ready |
| [`docs/ORCHESTRATION.md`](docs/ORCHESTRATION.md) | confini tra worker e orchestratore |
| [`docs/SAFETY.md`](docs/SAFETY.md) | confini di sicurezza |
| [`runtime/`](runtime/) | primitive machine-facing di intake, analisi e completion |
| [`onboarding/`](onboarding/) | bootstrap sicuro e validazione del contratto |
| [`examples/repository/`](examples/repository/) | repository minimo di esempio |

Versione inglese: [`README.md`](README.md)
