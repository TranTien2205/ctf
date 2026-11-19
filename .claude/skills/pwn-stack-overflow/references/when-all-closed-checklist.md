# When every stack route is closed — the handoff — checklist

Full RELRO + canary + PIE + NX + no leak primitive: every stack-corruption route is falsified. The honest move is to record the dead routes and hand back to the router.

## Checklist

- [ ] Run each route's falsifier — if ALL fire, the stack route is closed.
- [ ] Record each dead route with its closing falsifier in field-notes.
- [ ] Hand back to the router with the dead-route list — the next class may own a different primitive.
- [ ] A 'no' is a measurement: it saves the next attempt from re-walking the same ground.

## Abort conditions

- The honest output is the falsifier that closes each route — not 'it didn't work'.
- A closed stack route can coexist with an open heap/format/logic route.
- The kill map in knowledge/attempts/ records this for the next attempt.

## Falsifier

Falsifier — a falsifier that doesn't hold (e.g., 'full RELRO' was actually partial): recheck the protection evidence.
