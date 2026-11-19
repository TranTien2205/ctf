# When every stack route is closed — the handoff — case catalogue

Full RELRO + canary + PIE + NX + no leak primitive: every stack-corruption route is falsified. The honest move is to record the dead routes and hand back to the router.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | canary blocks smash | no leak | closed |
| 2 | full RELRO | no GOT write | closed |
| 3 | PIE + no leak | addresses unknown | closed |
| 4 | no primitive survives the protection set | class correct, chain closed | hand back |

## Falsifier

Falsifier — a falsifier that doesn't hold (e.g., 'full RELRO' was actually partial): recheck the protection evidence.
