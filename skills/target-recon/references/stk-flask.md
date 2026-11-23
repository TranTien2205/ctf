# Stack playbook: flask

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Flask fingerprints: session cookie (itsdangerous
signed Base64), Werkzeug Server header, /static/ convention.

Recon checks:
- session cookie decode -> session_dissect: itsdangerous shape
  means forgeable with the secret
- GET /console -> Werkzeug debugger: PIN-protected RCE console
  = the CTF classic; debugger in traceback = DEBUG mode
- /static/ path style + template echoes in errors
- Jinja {{ }} in error messages -> ssti weight
- Default 404 JSON vs HTML -> API vs page style

Predicts: session forge (weak secret), ssti (Jinja2), sqli on
raw SQL, idor.
## Pivot

Signal harvested -> out-*; route named -> that skill.
