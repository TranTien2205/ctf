# Werkzeug debugger — the Flask debug console — case catalogue

Flask's debugger serves an interactive Python console behind a PIN; the traceback page leaks enough to compute it.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /console with 'DEBUG MODE' banner | Werkzeug console | PIN exploit |
| 2 | traceback page with frame details | PIN material | compute or read |
| 3 | secret key in env/app.py | session signing | forge session |

## Falsifier

Falsifier — debugger off or the console requires a PIN with no leak path: the page alone isn't the exploit.
