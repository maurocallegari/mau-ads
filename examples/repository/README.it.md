# Esempio di repository AI-ready

Questa cartella mostra il contratto minimo atteso da MAU ADS.

| File | Obbligatorio | Scopo |
|---|---:|---|
| `AGENTS.md` | sì | regole operative per i worker |
| `PROJECT.md` | sì | conoscenza durevole specifica del progetto |
| `.ai/project.json` | sì | metadati macchina e punto di ingresso della verifica |
| `REPO_MAP.md` | opzionale | mappa compatta quando la struttura non è ovvia |
| `dev/verify-local.sh` | sì | unico entry point di verifica posseduto dal progetto |

L'esempio è volutamente indipendente dallo stack. Questi file devono contenere conoscenza durevole e regole operative, non stato temporaneo dei task o segreti.
