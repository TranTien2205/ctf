# When every stack route is closed — the handoff — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| canary blocks smash | no leak | closed |
| full RELRO | no GOT write | closed |
| PIE + no leak | addresses unknown | closed |
| no primitive survives the protection set | class correct, chain closed | hand back |

## Falsifier

Falsifier — a falsifier that doesn't hold (e.g., 'full RELRO' was actually partial): recheck the protection evidence.
