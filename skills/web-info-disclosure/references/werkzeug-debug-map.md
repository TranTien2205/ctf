# Werkzeug debugger — the Flask debug console — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /console with 'DEBUG MODE' banner | Werkzeug console | PIN exploit |
| traceback page with frame details | PIN material | compute or read |
| secret key in env/app.py | session signing | forge session |

## Falsifier

Falsifier — debugger off or the console requires a PIN with no leak path: the page alone isn't the exploit.
