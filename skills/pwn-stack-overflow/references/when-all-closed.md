# When every stack route is closed — the handoff

Full RELRO + canary + PIE + NX + no leak primitive: every stack-corruption route is falsified. The honest move is to record the dead routes and hand back to the router.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| canary blocks smash | no leak | closed |
| full RELRO | no GOT write | closed |
| PIE + no leak | addresses unknown | closed |
| no primitive survives the protection set | class correct, chain closed | hand back |

## Steps

1. Run each route's falsifier — if ALL fire, the stack route is closed.
2. Record each dead route with its closing falsifier in field-notes.
3. Hand back to the router with the dead-route list — the next class may own a different primitive.
4. A 'no' is a measurement: it saves the next attempt from re-walking the same ground.

## Falsifier

Falsifier — a falsifier that doesn't hold (e.g., 'full RELRO' was actually partial): recheck the protection evidence.

## Traps

- The honest output is the falsifier that closes each route — not 'it didn't work'.
- A closed stack route can coexist with an open heap/format/logic route.
- The kill map in knowledge/attempts/ records this for the next attempt.

## Cross-references

`negative-results.md` · `class-boundary.md`
