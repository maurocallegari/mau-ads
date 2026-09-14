# PHP AI Integration

## In una frase

Workflow condiviso per integrare AI/LLM nelle applicazioni PHP in modo portabile, validato e production-safe, usando Neuron AI come default quando compatibile.

## Mappa visuale

```text
                 PHP FEATURE AI/LLM
                         |
                         v
                php-ai-integration
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
    RUNTIME          ARCHITECTURE       SAFETY
   PHP >= 8.1?       Neuron AI         secrets
        |            abstraction       validation
     yes/no          provider/model    authorization
        |            configurable      logging
        +----------------+----------------+
                         |
                         v
                 STRUCTURED OUTPUT
                 / TOOLS / RAG / AGENT
                         |
                         v
                OFFICIAL NEURON SKILLS
```

## Quando entra in gioco

Nuova o modificata integrazione AI/LLM in un'applicazione PHP.

## Come si compone

```text
mauro-coding-style
        +
php-ai-integration
        |
        +→ neuron-agent-builder
        +→ neuron-structured-output
        +→ neuron-tool-creator
        +→ neuron-rag-specialist
        +→ altre skill ufficiali quando servono
```

## Possiede

- scelta dell'astrazione applicativa AI;
- compatibilità runtime PHP;
- provider/model portability;
- structured output validation;
- tool authorization e side-effect safety;
- timeout/retry/error handling;
- gestione sicura di secrets, prompt/context e logging.

## Non possiede

- API Neuron dettagliate già documentate upstream;
- stile PHP generale;
- business rules della singola app;
- schema DB non legato direttamente alla feature AI.

## Esempi

```text
Classificazione testo con output JSON
→ php-ai-integration + neuron-structured-output

Agent PHP con tool applicativi
→ php-ai-integration + neuron-agent-builder + neuron-tool-creator

App PHP 7.x
→ non installare Neuron incompatibile implicitamente
```

## Runtime

Supported coding agents.

## Versione

v1.0.0
