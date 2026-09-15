# MAU ADS

Un piccolo sistema operativo repository-first per lo sviluppo software assistito da AI.

L'utente descrive il risultato da ottenere. MAU ADS trasforma la richiesta in una consegna tracciata, isolata e verificata senza chiedere all'utente di ricordarsi il workflow.

## Ciclo richiesta -> READY

```text
RICHIESTA
  -> Issue GitHub canonica
  -> worktree isolata
  -> analisi / onboarding se necessario
  -> preflight deterministico
  -> coding worker
  -> verifica posseduta dal progetto
  -> completion gate deterministico
  -> loop di correzione se qualcosa fallisce
  -> commit eseguito da MAU
  -> push / Pull Request
  -> READY
```

La produzione resta sempre un'autorizzazione separata.

Entry point machine-facing:

```bash
bin/mau-agent run /percorso/repo --request "Implementa il risultato richiesto"
```

Normalmente non è un comando che deve lanciare Mauro: viene invocato automaticamente dal coding agent o da un orchestratore locale.

## Cosa governa MAU ADS

- analisi repository e bootstrap sicuro dell'onboarding;
- identità del lavoro tramite GitHub Issue;
- worktree Git isolate;
- validazione del contratto del progetto;
- preflight e completion gate deterministici;
- invocazione del worker (Codex di default, sostituibile);
- loop limitato `implementa -> verifica -> correggi`;
- commit e PR soltanto dopo il PASS.

## Cosa resta dentro ogni progetto

- `AGENTS.md` — invarianti operative e di sicurezza;
- `.ai/project.json` — profilo, ambienti, verifier e default workflow;
- `PROJECT.md` — conoscenza durevole del progetto;
- `REPO_MAP.md` — mappa opzionale;
- `dev/verify-local.sh` o equivalente — verifica eseguibile reale.

Segreti, dati runtime e stato temporaneo dei task non vanno versionati.

## Profili

`generic` resta neutro rispetto allo stack.

`mauro-php` aggiunge il confine locale/produzione usato nelle applicazioni PHP di Mauro: un solo `.env` ignorato, `.env.example` tracciato, `require/ads.php`, `configure.php` sottile, isolamento DB/runtime locale e protezione dalle scritture di produzione. ADS non inventa segreti: il worker completa la configurazione usando evidenza reale del repository e i gate impediscono READY finché i controlli richiesti non passano.

## Una sola pipeline

Spec Kit, Harbor/eval-engineering, Orca e strumenti simili non sono dipendenze runtime di MAU ADS. Possono essere usati esternamente per specifiche, eval o orchestrazione, ma non creano un secondo control plane.

## Verifica

Gli stati ammessi sono `PASS`, `FAIL`, `UNAVAILABLE`, `NOT_RUN`, `NOT_APPLICABLE`.

`UNAVAILABLE` e `NOT_RUN` non diventano mai READY. La frase del modello "ho finito" non è una prova.

Guida completa: [`GUIDA-IT.md`](GUIDA-IT.md)
