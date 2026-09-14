# MySQL Change Safety

## In una frase

Workflow di sicurezza per modifiche persistenti MySQL: capire impatto e compatibilità prima di cambiare schema o dati.

## Mappa visuale

```text
                  MYSQL CHANGE
                       |
                       v
              mysql-change-safety
                       |
                       v
              INSPECT READERS/WRITERS
                       |
                       v
                CLASSIFY RISK
                       |
          +------------+------------+
          |                         |
          v                         v
      ADDITIVE                  DESTRUCTIVE
          |                         |
          v                         v
       EXPAND               explicit approval/
          |                 migration strategy
          v
       MIGRATE
          |
          v
       CONTRACT
          |
          v
 VERIFY + RECOVERY AWARENESS
```

## Quando entra in gioco

Schema, indici, trigger, stored routine, bulk data migration o altra modifica persistente MySQL con possibile blast radius.

## Come si compone

```text
mauro-coding-style
        +
mysql-change-safety
        +
[feature-planning se il cambiamento è ampio]
```

## Possiede

- analisi readers/writers;
- classificazione rischio;
- compatibility strategy;
- expand → migrate → contract;
- locking/performance awareness;
- verifica pre/post;
- rollback/recovery awareness.

## Non possiede

- naming DB generale Mauro;
- business rules della singola app;
- deployment completo;
- backup/recovery infrastructure.

## Esempi

```text
Aggiunta colonna nullable
→ inspect → additive change → verify

Rename colonna usata da PHP legacy
→ expand → migrate consumers → contract successivo

Bulk UPDATE
→ scope rows → transaction/locking analysis → execute → verify
```

## Runtime

Supported coding agents.

## Versione

v1.0.0
