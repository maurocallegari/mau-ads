# MAU ADS — Guida completa in italiano

MAU ADS è un operating layer repository-first per lo sviluppo software assistito da AI.

L'obiettivo non è aggiungere un'altra interfaccia da imparare. L'utente continua a fare richieste normali, per esempio:

```text
"Correggi il bug nel salvataggio cliente."
"Aggiungi questa funzione."
"Lavora su questa repository."
```

Il worker o l'orchestratore usa MAU ADS automaticamente per rendere quel lavoro tracciabile, isolato e verificabile.

## 1. L'idea centrale

```text
UTENTE
  -> richiesta normale
  -> MAU ADS invisibile
  -> worker / orchestratore
  -> repository + GitHub
```

MAU ADS non vuole essere:

- una nuova dashboard;
- un task manager alternativo a GitHub;
- un database di memoria del progetto;
- un orchestratore obbligatorio;
- un framework legato a uno specifico linguaggio o stack;
- una CLI che l'utente deve imparare.

La fonte di verità durevole resta:

```text
codice + Git + documentazione del repository + GitHub
```

Agenti, modelli e orchestratori devono poter essere sostituiti.

## 2. Lifecycle automatico

Il lifecycle di riferimento è:

```text
RICHIESTA
  -> INTAKE GATE
  -> ANALISI / REFRESH REPOSITORY
  -> ONBOARDING AUTOMATICO se necessario
  -> VALIDAZIONE CONTRATTO
  -> WORK ITEM CANONICO
  -> WORKSPACE ISOLATO
  -> IMPLEMENTAZIONE
  -> VERIFICA DEL PROGETTO
  -> CONTROLLO FINALE DEL DIFF
  -> PULL REQUEST / REVIEW
  -> MERGE
  -> READY_TO_DEPLOY
  -> PRODUZIONE solo con autorizzazione esplicita
```

La regola fondamentale è:

```text
NO VALID MAU WORK CONTEXT
  =
NO DURABLE WRITES
```

Un worker compatibile non dovrebbe iniziare a modificare il repository finché il gate non ha stabilito che contesto, work item e workspace sono validi.

## 3. Cosa succede quando arriva una richiesta

### Repository già onboardata

MAU:

1. individua la root Git;
2. legge il contratto del progetto;
3. raccoglie evidenze strutturali aggiornate;
4. verifica che il contratto sia valido;
5. risolve o crea il work item canonico;
6. prepara un workspace isolato;
7. classifica il tipo/rischio del lavoro;
8. restituisce al worker un `mau.work_context` machine-readable;
9. autorizza le modifiche solo se i prerequisiti sono soddisfatti.

### Repository nuova o non onboardata

MAU prima esegue una discovery read-only, poi crea soltanto il contratto minimo necessario.

```text
REPOSITORY SCONOSCIUTA
  -> scanner deterministico read-only
  -> evidenze
  -> bootstrap contratto
  -> validazione
  -> normale lifecycle di lavoro
```

L'onboarding non deve inventare informazioni architetturali che il repository non dimostra.

## 4. Repository analysis

L'analisi della repository è una fase di prima classe, non un generico "leggi un po' di file" lasciato alla discrezione dell'LLM.

`runtime/analyze_repository.py` raccoglie evidenze come:

- root Git;
- branch corrente;
- commit HEAD;
- origin;
- stato dirty/clean;
- struttura top-level;
- fingerprint strutturale;
- manifest di build/dipendenze;
- configurazioni CI;
- documenti AI/developer già presenti;
- evidenze di test;
- migration/schema;
- esempi di configurazione;
- possibili entry point.

Lo scanner raccoglie fatti. Non deve trasformare automaticamente un indizio in una verità architetturale.

### Conoscenza transitoria e durevole

L'output completo dello scanner è transitorio. MAU non mantiene un grande dump di analisi continuamente aggiornato nel repository.

Solo le informazioni stabili e realmente utili vengono promosse in:

- `AGENTS.md`;
- `PROJECT.md`;
- `REPO_MAP.md`;
- `.ai/project.json`.

Questo evita di ricreare un Knowledge DB esterno che col tempo diverge dal codice.

## 5. Il contratto del progetto

Il contratto minimo è intenzionalmente piccolo e stack-neutral.

### Obbligatori

`AGENTS.md`
: regole operative che qualsiasi worker deve rispettare.

`.ai/project.json`
: metadati machine-readable, versione dello schema e entry point di verifica.

`PROJECT.md`
: conoscenza durevole specifica del progetto.

Entry point di verifica
: comando/file posseduto dal repository che esegue i controlli appropriati per quello specifico progetto.

### Opzionale

`REPO_MAP.md`
: mappa compatta del repository quando la struttura non è immediata.

### Regole

- l'evidenza del repository prevale su memoria o supposizioni della sessione;
- i segreti non appartengono al contratto;
- lo stato temporaneo di un task non appartiene al contratto;
- la verifica deve dichiarare ciò che è realmente successo;
- i controlli specifici dello stack restano dietro l'entry point di verifica del progetto;
- un verifier generato automaticamente può dichiarare `UNAVAILABLE`, ma non deve mai simulare `PASS`.

## 6. Onboarding automatico

Se il contratto manca, MAU può bootstrapparlo automaticamente.

Il bootstrap deve essere conservativo:

- non sovrascrive deliberatamente informazioni già presenti senza motivo;
- crea il contratto minimo;
- non pretende di conoscere ciò che non è dimostrato;
- prepara un verifier iniziale che resta `UNAVAILABLE` finché non esistono controlli reali adatti al progetto.

Questo è importante: repository "onboardata" non significa automaticamente repository "verificata".

## 7. Work item canonico e GitHub Issue

Per un outcome consegnabile indipendentemente MAU usa normalmente una sola GitHub Issue canonica.

```text
1 outcome consegnabile
  =
1 Issue canonica
```

I sottotask interni del planner o dell'orchestratore non devono generare automaticamente altre Issue.

In modalità standalone, se l'origin è GitHub e `gh` è disponibile/autenticato, il gate:

1. cerca una Issue aperta con titolo compatibile;
2. la riusa se esiste;
3. altrimenti ne crea una nuova.

Se non riesce a stabilire un'identità di lavoro canonica, non deve fingere che il requisito sia soddisfatto.

## 8. Workspace isolato

Ogni writer concorrente deve avere il proprio workspace.

In standalone MAU usa un Git worktree separato e una branch dedicata al work item.

Schema:

```text
Issue #123
  -> branch dedicata
  -> worktree isolato
  -> worker
```

Se il working tree sorgente è dirty, la preparazione del nuovo workspace viene bloccata anziché rischiare di perdere o mescolare modifiche.

La regola resta:

```text
mai due writer sullo stesso working tree mutabile
```

## 9. Routing e rischio

Il work context contiene anche il routing derivato dalla richiesta.

Lo scopo non è sostituire il ragionamento del worker, ma fornire un primo livello coerente per:

- tipo di lavoro;
- capacità/skill necessarie;
- livello di attenzione richiesto.

Cambiamenti come autenticazione, dati persistenti, core condiviso, operazioni distruttive o side effect esterni richiedono maggiore scrutinio rispetto a una modifica locale a basso impatto.

## 10. Implementazione

Una volta autorizzato il workspace, il worker deve:

- leggere il contratto del progetto;
- ispezionare il percorso di codice rilevante;
- riusare pattern già presenti;
- fare la modifica coerente più piccola che soddisfa l'outcome;
- evitare refactor, modernizzazioni e churn non richiesti;
- evitare di allargare il blast radius senza una ragione concreta.

## 11. Test e verification non sono la stessa cosa

MAU distingue esplicitamente:

```text
TEST
  = controllo eseguibile

VERIFICATION
  = evidenza che l'outcome richiesto sia corretto
```

Gli stati ammessi sono:

```text
PASS            verifica richiesta eseguita e superata
FAIL            verifica eseguita e fallita
UNAVAILABLE     verifica pertinente ma non eseguibile
NOT_RUN         verifica non eseguita
NOT_APPLICABLE  controllo realmente non applicabile
```

`UNAVAILABLE` e `NOT_RUN` non possono essere trasformati in `PASS`.

## 12. Completion gate

Il lavoro non dovrebbe essere dichiarato completato solo perché il worker ha smesso di modificare file.

`runtime/completion_gate.py` controlla almeno:

1. contratto del progetto valido;
2. verifica repository-owned eseguita;
3. stato finale della verifica compatibile con la completion;
4. `git diff --check`;
5. branch isolata diversa dalla base;
6. working tree senza modifiche non committate;
7. delivery GitHub, se disponibile.

Se tutto è corretto, lo stato diventa:

```text
READY_FOR_REVIEW
```

Non `DEPLOYED`.

## 13. Pull Request

In standalone, quando GitHub e `gh` sono disponibili, il completion gate:

- push-a la branch;
- riusa una PR aperta per quella branch se esiste;
- altrimenti crea una nuova PR;
- collega la Issue quando il numero è disponibile.

La PR è l'evidenza di review/integrazione, non l'autorizzazione alla produzione.

## 14. Confine della produzione

MAU mantiene una separazione esplicita:

```text
MERGED
  -> READY_TO_DEPLOY
  -> autorizzazione esplicita?
       -> sì: deployment secondo il processo del progetto
       -> no: stop
```

Il merge non autorizza automaticamente la produzione.

Il normale worker di implementazione non deve assumere di poter fare deploy solo perché la modifica è stata approvata.

## 15. Orchestratori esterni

Un orchestratore è opzionale.

Può possedere:

- queue e dispatch;
- scelta worker/modello;
- dipendenze;
- parallelismo;
- collision avoidance;
- UI e visibilità dello stato;
- eventualmente creazione workspace e integrazione GitHub.

Non deve diventare:

- una seconda history del codice;
- un task database durevole in conflitto con GitHub;
- il posto esclusivo in cui vivono fatti del progetto;
- la fonte di uno stato di verifica inventato.

In modalità orchestrata MAU può delegare alcune meccaniche, ma continua a validare le condizioni repository-specifiche.

Per autorizzare le scritture l'orchestratore deve fornire almeno:

- identità del work item;
- workspace isolato.

## 16. Cosa vede l'utente

Idealmente soltanto questo:

```text
UTENTE:
"Correggi il bug X."

SISTEMA:
- intake automatico
- eventuale onboarding
- Issue canonica
- workspace isolato
- worker
- verifica
- PR
```

L'utente non dovrebbe dover scrivere:

```text
mau analyze
mau onboard
mau doctor
mau work start
```

Le primitive interne esistono perché il worker possa eseguire il protocollo in modo consistente.

## 17. Entry point machine-facing

L'entry point standalone attuale è:

```text
bin/mau-agent
```

Internamente inoltra al gate Python di intake.

Un worker compatibile deve invocarlo automaticamente con l'outcome richiesto prima delle modifiche durevoli.

La sintassi è documentata per integratori e agenti, non perché l'utente debba memorizzarla.

## 18. Quando MAU blocca il lavoro

Il blocco è intenzionale quando mancano condizioni necessarie.

Esempi:

- repository non riconoscibile come Git;
- contratto invalido e bootstrap non possibile;
- origin GitHub non disponibile quando serve una Issue canonica;
- GitHub CLI assente o non autenticata in standalone;
- working tree sorgente dirty prima della creazione del worktree;
- workspace isolato non disponibile;
- verifica `FAIL`, `UNAVAILABLE` o `NOT_RUN` quando la completion la richiede;
- `git diff --check` fallisce;
- modifiche non committate al momento della completion;
- push o PR non riusciti quando richiesti.

Il principio è:

```text
mancanza di evidenza != successo
```

## 19. Safety

Le regole valgono indipendentemente da modello, agente, linguaggio o orchestratore.

- mai committare, stampare o copiare segreti in Git;
- non usare la produzione come workspace di sviluppo;
- operazioni distruttive richiedono maggiore scrutinio;
- modifiche auth/authorization richiedono maggiore scrutinio;
- modifiche a dati persistenti richiedono maggiore scrutinio;
- modifiche al core condiviso richiedono maggiore scrutinio;
- side effect esterni richiedono maggiore scrutinio;
- il deployment richiede autorizzazione esplicita;
- non dichiarare una verifica mai eseguita;
- preservare dati utente e comportamento esistente salvo richiesta contraria;
- controllare il diff finale per scope accidentale, file generati e modifiche estranee.

## 20. Mappa dei file principali

```text
mau-ads/
├── README.md
├── README.it.md
├── GUIDA-IT.md
├── START-HERE.md
├── AGENTS.md
├── CURRENT-STATE.md
├── bin/
│   └── mau-agent
├── runtime/
│   ├── analyze_repository.py
│   ├── intake_gate.py
│   ├── routing.py
│   └── completion_gate.py
├── onboarding/
│   ├── bootstrap_project.py
│   └── validate_project.py
├── docs/
├── examples/repository/
└── tests/
```

## 21. Repository di esempio

`examples/repository/` mostra il contratto minimo di una repository MAU-ready:

- `AGENTS.md`;
- `PROJECT.md`;
- `REPO_MAP.md`;
- `.ai/project.json`;
- `dev/verify-local.sh`.

L'esempio serve a mostrare la forma del contratto, non a imporre uno stack specifico.

## 22. Limiti attuali della versione standalone

La baseline corrente è già eseguibile, ma ha limiti intenzionali:

- per automatizzare Issue e PR in standalone dipende da GitHub CLI `gh` disponibile e autenticata;
- il bootstrap non può inventare una vera strategia di test per un progetto sconosciuto: il verifier iniziale resta prudente;
- il routing è un supporto deterministico iniziale, non un sostituto del reasoning del worker;
- l'analisi semantica profonda resta responsabilità del worker, ma deve essere grounded nelle evidenze raccolte;
- l'esecuzione automatica del gate richiede che il coding agent/orchestratore venga integrato con MAU: avere i file nel repository da solo non obbliga magicamente ogni client esistente a chiamare il runtime.

Quest'ultimo punto è importante: MAU ADS definisce il protocollo e fornisce le primitive, ma il client che esegue il codice deve rispettare il gate.

## 23. Risultato desiderato

MAU ADS vuole rendere possibile questo modello:

```text
Mauro
  -> "fammi questa modifica"

MAU ADS
  -> capisce lo stato della repo
  -> crea/valida il contesto
  -> rende il lavoro tracciabile
  -> isola il writer
  -> impone verifica e completion rules

Worker / orchestratore
  -> esegue

GitHub + repository
  -> conservano la verità durevole
```

L'utente resta concentrato sull'outcome. La disciplina operativa viene applicata automaticamente sotto il livello della conversazione.
