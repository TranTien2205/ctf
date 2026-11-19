# Werkzeug debugger — the Flask debug console

Flask's debugger serves an interactive Python console behind a PIN; the traceback page leaks enough to compute it.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /console with 'DEBUG MODE' banner | Werkzeug console | PIN exploit |
| traceback page with frame details | PIN material | compute or read |
| secret key in env/app.py | session signing | forge session |

## Steps

1. Probe /console; check whether the page loads.
2. The PIN is computed from machine ids (username, mac, machine-id, boot id, modname, app path) — leaks from the traceback and /proc reads.
3. If the PIN can't be computed, read the traceback's leaked locals anyway — they carry env and secrets.
4. A debugger on a production CTF is the intended path — look for the traceback page it came with.

## Falsifier

Falsifier — debugger off or the console requires a PIN with no leak path: the page alone isn't the exploit.

## Traps

- The PIN formula changed across Werkzeug versions — check the version.
- Sometimes the traceback alone leaks the flag without entering the console.
- app.py under debug serves source leaks too.

## Commands

```bash
curl -s '$BASE/console' | head -30
```

## Cross-references

`framework-debug.md` · `debug-endpoints.md`
