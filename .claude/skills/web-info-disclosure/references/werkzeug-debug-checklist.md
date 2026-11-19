# Werkzeug debugger — the Flask debug console — checklist

Flask's debugger serves an interactive Python console behind a PIN; the traceback page leaks enough to compute it.

## Checklist

- [ ] Probe /console; check whether the page loads.
- [ ] The PIN is computed from machine ids (username, mac, machine-id, boot id, modname, app path) — leaks from the traceback and /proc reads.
- [ ] If the PIN can't be computed, read the traceback's leaked locals anyway — they carry env and secrets.
- [ ] A debugger on a production CTF is the intended path — look for the traceback page it came with.

## Abort conditions

- The PIN formula changed across Werkzeug versions — check the version.
- Sometimes the traceback alone leaks the flag without entering the console.
- app.py under debug serves source leaks too.

## Falsifier

Falsifier — debugger off or the console requires a PIN with no leak path: the page alone isn't the exploit.
