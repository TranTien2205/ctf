# Werkzeug debugger — the Flask debug console — deep

Flask's debugger serves an interactive Python console behind a PIN; the traceback page leaks enough to compute it.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — debugger off or the console requires a PIN with no leak path: the page alone isn't the exploit.

## Highest-cost traps

- The PIN formula changed across Werkzeug versions — check the version.
- Sometimes the traceback alone leaks the flag without entering the console.
- app.py under debug serves source leaks too.

## Commands

```bash
curl -s '$BASE/console' | head -30
```

## Cross-references

`framework-debug.md` · `debug-endpoints.md`
