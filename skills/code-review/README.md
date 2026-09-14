# Code Review

## In una frase

Revisione risk-first delle modifiche: cerca regressioni, bug e violazioni dei contratti prima di discutere stile cosmetico.

## Mappa visuale

```text
                 CODE CHANGE
                     |
                     v
                 code-review
                     |
          +----------+----------+
          |                     |
          v                     v
      UNDERSTAND DIFF       UNDERSTAND CONTEXT
          |                     |
          +----------+----------+
                     |
                     v
                FIND RISKS
                     |
          +----------+----------+
          |          |          |
          v          v          v
       BUGS      REGRESSIONS   CONTRACTS
          \          |          /
           +---------+---------+
                     |
                     v
              ACTIONABLE FINDINGS
```

## Quando entra in gioco

Review di diff, commit, PR o implementazione completata.

## Come si compone

Usa le skill di dominio pertinenti per capire i contratti che il codice deve rispettare.

## Possiede

Review risk-first, severity, evidenza concreta e finding azionabili.

## Non possiede

Implementazione della feature, framework knowledge o project knowledge.

## Esempio

```text
Review feature AI in CRUD
→ code-review + mauro-coding-style + mauro-crud + php-ai-integration
```

## Runtime

Codex; riusabile come metodo condiviso quando disponibile.

## Versione

Versione definita dal `SKILL.md`/repository corrente.
