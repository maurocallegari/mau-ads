# Generic onboarding

MAU ADS onboarding is stack-neutral and normally runs automatically from intake when a repository does not yet expose a valid project contract.

```text
unknown repository
  -> read-only analysis
  -> safe bootstrap of missing contract files
  -> contract validation
  -> project-owned verification state
```

Bootstrap is conservative:

- existing contract files are preserved;
- deterministic evidence is promoted, guesses are not;
- no secrets are copied;
- if real verification cannot be inferred safely, the generated verifier reports `UNAVAILABLE` rather than `PASS`.

The machine-readable project manifest declares the verification entry point. The current schema version is `1`.

Verification exit-state convention:

```text
0 -> PASS
1 -> FAIL
2 -> UNAVAILABLE
3 -> NOT_RUN
4 -> NOT_APPLICABLE
```

The user is not expected to invoke onboarding commands manually. These scripts are runtime primitives for compatible agents/orchestrators and are also directly testable for development of MAU ADS itself.
