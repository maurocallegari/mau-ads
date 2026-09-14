# Feature Planning

## In una frase

Trasforma una richiesta di feature in un piano implementabile, proporzionato al rischio e basato sul codice reale.

## Mappa visuale

```text
               FEATURE REQUEST
                     |
                     v
              feature-planning
                     |
          +----------+----------+
          |                     |
          v                     v
      INSPECT REPO          DEFINE GOAL
          |                     |
          +----------+----------+
                     |
                     v
             SCOPE + CONSTRAINTS
                     |
                     v
             IMPLEMENTATION PLAN
                     |
                     v
             VERIFY / ACCEPTANCE
```

## Quando entra in gioco

Feature non banale, cambiamento multi-step o task con scelte architetturali/ambiguità significative.

## Come si compone

Può precedere qualsiasi skill specialistica: `mauro-crud`, `mysql-change-safety`, `php-ai-integration`.

## Possiede

Planning proporzionato, scope, dipendenze, rischi, sequenza implementativa e acceptance criteria.

## Non possiede

Framework knowledge, coding style, implementazione o project facts durevoli.

## Esempio

```text
Feature CRUD con modifica DB
→ feature-planning
→ mauro-coding-style + mauro-crud + mysql-change-safety
```

## Runtime

Codex; riusabile come metodo condiviso quando disponibile.

## Versione

Versione definita dal `SKILL.md`/repository corrente.
