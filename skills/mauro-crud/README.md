# Mauro CRUD

## In una frase

Knowledge layer del framework Mauro CRUD: riconosce T0/T1/T2/T3 e guida manutenzione e migrazioni preservando il comportamento reale.

## Mappa visuale

```text
              mauro-coding-style
                       |
                       v
                 MAURO-CRUD
                       |
       +---------------+---------------+
       |               |               |
       v               v               v
  STAGE DETECTION   MAINTENANCE     MIGRATION
  T0 T1 T2 T3       legacy-safe      T1 → T2
       |               |               |
       +---------------+---------------+
                       |
                       v
                  NO-INVENTION
             codice reale = priorità
                       |
          +------------+------------+
          |                         |
          v                         v
     T2 CONTRACTS              COMPATIBILITY
     $CRUD->Page              preserve behavior
     Form/Rows/AJAX           narrow adapters
```

## Quando entra in gioco

```text
repo appartiene alla famiglia Mauro CRUD
                    |
                    v
               mauro-crud
```

Non si attiva solo perché una repo usa PHP/MySQL.

## Come si compone

```text
mauro-coding-style
        +
mauro-crud
        +
[skill task-specifica se necessaria]
```

## Possiede

- stage T0/T1/T2/T3;
- framework detection;
- contratti T2;
- no-invention durante manutenzione/migrazione;
- compatibilità T1/T2;
- metodologia T1 → T2.

## Non possiede

- stile PHP/MySQL/JS generale;
- onboarding completo della repo;
- deployment;
- project-specific knowledge;
- regole generali di planning/review.

## Esempi

```text
Bug in pagina CRUD T2
→ mauro-coding-style + mauro-crud + bug-investigation

Conversione T1 → T2
→ feature-planning + mauro-coding-style + mauro-crud
```

## Runtime

Supported coding agents.

## Versione

v4.1.0
