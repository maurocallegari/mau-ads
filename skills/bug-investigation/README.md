# Bug Investigation

## In una frase

Metodo evidence-first per trovare la causa reale di un bug prima di modificarne il codice.

## Mappa visuale

```text
                    BUG
                     |
                     v
             bug-investigation
                     |
                     v
                 REPRODUCE
                     |
                     v
              COLLECT EVIDENCE
                     |
                     v
               TRACE CAUSE
                     |
                     v
               MINIMAL FIX
                     |
                     v
             VERIFY REGRESSION
```

## Quando entra in gioco

Comportamento errato, regressione, errore intermittente o causa non immediatamente evidente.

## Come si compone

```text
bug-investigation
       +
context skill
(mauro-crud / mysql-change-safety / php-ai-integration)
```

## Possiede

Riproduzione, raccolta evidenze, isolamento della causa, fix minimo e verifica della regressione.

## Non possiede

Framework-specific knowledge, coding style o feature planning generale.

## Esempio

```text
Errore AJAX in CRUD T2
→ bug-investigation + mauro-coding-style + mauro-crud
```

## Runtime

Codex; riusabile come metodo condiviso quando disponibile.

## Versione

Versione definita dal `SKILL.md`/repository corrente.
