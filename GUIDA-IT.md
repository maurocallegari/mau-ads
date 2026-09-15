# MAU ADS 2.0 — guida operativa

## Obiettivo

MAU ADS deve permettere questo uso:

```text
"Implementa X"
        ↓
Issue -> workspace isolato -> implementazione -> test -> correzioni -> PR -> READY
```

L'utente non deve trasformarsi nel supervisore dell'agente. Il sistema deve bloccare automaticamente ciò che non è verificato.

## Architettura minima

MAU ADS centrale vive in una repository propria. Ogni progetto conserva solo il proprio contratto e la propria conoscenza. GitHub conserva l'identità del lavoro e la review. Il coding worker è sostituibile.

```text
MAU ADS centrale
  runtime/workflow.py
  runtime/intake_gate.py
  runtime/preflight.py
  runtime/worker.py
  runtime/completion_gate.py
  onboarding/
  skills/

TARGET REPOSITORY
  AGENTS.md
  PROJECT.md
  REPO_MAP.md
  .ai/project.json
  dev/verify-local.sh
  source code / tests
```

## Onboarding

Quando il contratto manca, ADS non modifica la working copy principale. Prima crea/risolve la Issue e la worktree isolata, poi esegue il bootstrap nella worktree.

Il bootstrap crea soltanto struttura e fatti deterministici. Non inventa scopo, architettura, credenziali o comandi di test. Il worker deve leggere il progetto e completare `PROJECT.md`, `REPO_MAP.md`, configurazione e verifier con evidenza reale.

### Generic

Il profilo `generic` richiede un verifier reale adatto allo stack: test, build, lint, smoke, browser check o altra combinazione coerente.

### Mauro PHP

Il profilo `mauro-php` usa come target:

```text
.env                  locale/runtime, ignorato da Git
.env.example          placeholder tracciato
require/ads.php       loader ambiente/configurazione
configure.php         adapter sottile dell'applicazione
```

Il worker deve preservare costanti e bootstrap specifici del progetto e migrare la configurazione senza copiare ciecamente quella di un'altra applicazione. Quando la worktree viene creata, i runtime file dichiarati nel manifest (per esempio `.env`) possono essere copiati dalla working copy sorgente alla worktree senza essere tracciati.

Le verifiche del progetto devono coprire, dove applicabile: parità PHP, DB locale separato, schema/dati necessari, blocco scritture verso produzione, URL/path locali, runtime smoke e funzioni rappresentative.

## Task normale

`runtime/workflow.py` governa l'intero ciclo:

1. `intake()` crea/riusa la Issue e prepara la worktree.
2. Il contratto viene validato o bootstrappato.
3. `preflight(..., phase="intake")` verifica sicurezza, branch isolato, segreti e confine produzione.
4. Il worker viene eseguito nella worktree.
5. Il verifier del progetto viene eseguito fuori dal giudizio narrativo del worker.
6. `preflight(..., phase="completion")` applica i gate finali.
7. `git diff --check` e presenza di modifiche vengono verificati.
8. Se qualcosa fallisce, l'evidenza viene rimandata al worker e il ciclo riparte, fino al limite configurato.
9. Solo dopo PASS ADS esegue il commit.
10. Il completion gate ripete la verifica sul commit pulito e crea/riusa la PR.

## Worker

Codex CLI è il default locale. Il runtime usa `codex exec` nella worktree e mantiene il worker sostituibile.

Per usare un altro worker locale che legge il prompt da stdin:

```bash
MAU_WORKER_COMMAND="my-agent --non-interactive" bin/mau-agent run ...
```

Lo stesso può essere passato con `--worker-command`.

Il modello non è il proprietario della verità di completamento. Può implementare e correggere; i gate decidono READY.

## `.ai/project.json`

Esempio:

```json
{
  "schema_version": 1,
  "profile": "generic",
  "name": "my-project",
  "ads": {"contract_version": 2},
  "environments": {
    "local": {"kind": "development"},
    "production": {
      "kind": "production",
      "secrets_in_git": false,
      "deployment_authorization": "explicit"
    }
  },
  "verification": {"command": "dev/verify-local.sh"},
  "workflow": {"worker": "codex", "max_fix_attempts": 3}
}
```

Nel profilo `mauro-php`, `environments.local.runtime_files` può dichiarare file runtime ignorati come `.env` da rendere disponibili nella worktree.

## Stati

Il verifier può produrre soltanto:

- `PASS`;
- `FAIL`;
- `UNAVAILABLE`;
- `NOT_RUN`;
- `NOT_APPLICABLE`.

Solo `PASS` e, quando semanticamente corretto, `NOT_APPLICABLE` consentono di avanzare. Un test non eseguibile è un blocco, non un successo implicito.

## GitHub

Una Issue rappresenta un outcome consegnabile. I subtasks interni non generano nuove Issue. La PR contiene la consegna verificata e chiude la Issue. Il merge non autorizza il deploy.

## Portabilità

ADS non viene copiato interamente in ogni progetto. La repository ADS contiene runtime e skill condivise. Il progetto contiene il proprio contratto. Clonando entrambi si ricostruisce il sistema; segreti e path macchina restano locali.

## Cosa non entra nel runtime

Spec Kit non è necessario come secondo workflow engine: il runtime ADS possiede già Issue, worktree, worker, loop e gate. Può essere usato come fonte di pattern o, in futuro, per task che richiedono specifiche formali, ma non deve diventare una dipendenza obbligatoria.

Harbor/eval-engineering serve a valutare ADS e confrontare harness/modelli; non è parte del task quotidiano.

Orca o altri orchestratori possono stare sopra ADS per visualizzare e dispatchare task, ma non devono sostituire Issue, repository contract o verifier come fonti di verità.

## Comandi interni

```bash
bin/mau-agent run ...        # ciclo completo
bin/mau-agent intake ...     # solo intake
bin/mau-agent preflight ...  # gate deterministici
bin/mau-agent finish ...     # completion/delivery
bin/mau-agent analyze ...    # analisi read-only
bin/mau-agent validate ...   # validazione contratto
bin/mau-agent onboard ...    # solo bootstrap contratto
```

Sono primitive per agenti/orchestratori, non una checklist che Mauro deve ricordare.
