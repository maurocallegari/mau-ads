# Mauro Coding Style

## In una frase

Il DNA tecnico comune delle applicazioni Mauro: convenzioni PHP/MySQL/JavaScript, naming, compatibilità e semplicità, indipendentemente dal framework CRUD.

## Mappa visuale

```text
                    MAURO-CODING-STYLE
                    "come scriviamo software"
                              |
        +---------------------+---------------------+
        |                     |                     |
        v                     v                     v
   PHILOSOPHY                PHP                 DATABASE
   - semplice            - [] per array           - ID
   - esplicito           - helper discovery       - ID<Entita>
   - pragmatico          - HTML leggibile         - IS_*
   - legacy-safe         - bootstrap verificato   - Tab_*
   - low abstraction     - minimal diff           - tab_*
        |                                             |
        +----------------------+----------------------+
                               |
                               v
                         COMPATIBILITY
                    comportamento esistente
                         prima del cleanup
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
            JS/UI            NAMING          SECURITY
        stack esistente    dominio italiano   prevale
```

## Regole PHP forward-style

```text
nuovo / codice sostanzialmente riscritto
                |
                v
        usa [] per gli array
                |
                +--> niente conversioni massive fuori scope

nuovo helper
    |
    v
cerca equivalenti nella repo
    |
    +--> esiste? riusa
    |
    +--> manca? nome generico + collocazione canonica se davvero condiviso
```

L'HTML multilinea costruito in PHP resta markup mantenibile: deve essere semanticamente indentato e leggibile nel sorgente.

## Quando entra in gioco

```text
repo/app Mauro PHP/MySQL/JS
            |
            v
   mauro-coding-style
```

Non richiede che la repo usi Mauro CRUD.

## Come si compone

```text
                 mauro-coding-style
                         |
          +--------------+---------------+
          |              |               |
          v              v               v
    mauro-crud   mysql-change-    php-ai-integration
                     safety                |
                                           v
                                       Neuron AI
```

## Possiede

- convenzioni generali PHP/MySQL/JavaScript Mauro;
- `[]` come sintassi PHP standard per array nuovi o sostanzialmente riscritti;
- discovery e riuso degli helper prima di crearne di nuovi;
- naming/collocazione coerente degli helper condivisi;
- leggibilità dell'HTML multilinea generato da PHP;
- naming e convenzioni database ricorrenti;
- terminologia di dominio italiana;
- filosofia compatibility-first e legacy-safe;
- preferenza per soluzioni semplici, esplicite e proporzionate;
- routing verso skill specialistiche per DB e AI.

## Non possiede

- contratti T0/T1/T2/T3 del framework CRUD;
- procedure dettagliate per modifiche MySQL ad alto rischio;
- implementazione tecnica delle feature AI/LLM;
- fatti specifici di una singola applicazione;
- regole universali dell'agente.

## Esempi

```text
Repo Mauro non CRUD
→ mauro-coding-style

Repo Mauro CRUD
→ mauro-coding-style + mauro-crud

ALTER TABLE / migrazione dati
→ mauro-coding-style + mysql-change-safety

Nuova feature AI PHP
→ mauro-coding-style + php-ai-integration
```

## Runtime

Supported coding agents.

## Versione

v1.2.0
