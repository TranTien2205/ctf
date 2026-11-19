# Secrets in client JavaScript — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| apiKey/token/secret strings in bundle | possible live key | test or note |
| process.env refs in recovered source | build-time values leaked | read each |
| internal URL / admin route strings | route disclosure | probe them |
| firebaseConfig / supabase keys | backend-as-service creds | test scope |

## Falsifier

Falsifier — the bundle contains only public keys and self-references: no disclosure finding. Minified code still merits an endpoint scan.
