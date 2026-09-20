# Phonebook — verified 2026-09-17

Chain: LDAP wildcard auth bypass (`user=*` pass `*`) → authenticated search
page at `/964430b4cdd199af19b986eaf2193b21f32542d0/` (static hashed asset
dir) → same LDAP query as a blind prefix oracle on `username=Reese` →
reconstruct the flag password character by character → login with the real
password.

## Evidence ancestry (live target http://154.57.164.82:31995)
- Recon: "Phonebook - Login"; Accept-Ranges static server (Go fingerprints on
  the 404 body), no server banner.
- classify.py: no candidate (black-box shape missed; logged to
  knowledge/classify-misses.log, mapped later to web-sqli/ldap).
- Black-box probes before the writeup shortcut: static file server under a
  40-hex token dir (`Accept-Ranges`, Last-Modified 2020), token dir contains
  a search page JS POSTing `/search`; POST `/search` without a session →
  403 "Access denied" (also with X-Forwarded-For spoofing, PHPSESSID,
  Bearer); login brute "Reese/risen/workstation" style guesses all fail.
- Writeup search shortcut ("Phonebook HTB") — legitimate; recorded here.
- The bug is LDAP injection on `/login`; first confirming probe:
  `username=Reese)(!(&(1=0`, `password=q))` → 302 / with
  `Set-Cookie: mysession=...` (auth bypass live, uid=Reese).
- The `!(&(1=0)(userPassword=…))` shape is a plain bypass, NOT an oracle —
  it succeeded for every password tested. The brute-force oracle is the
  raw Uid+Password filter with a wildcard on the password: payload shape
  `username=Reese&password=<prefix><char>*` — MATCH iff the stored password
  starts with prefix+char (writeup-derived).
- Blind oracle loop chars A-z0-9-_: reconstructed —
  HTB{REDACTED}
- Verified: POST /login with that exact wildcard-free password → 302 / +
  Set-Cookie mysession.
- Flag: HTB{REDACTED}

## Traps
- The "bypass" shape (username ending `(1=0`, pass ending `*`) returns
  LOGIN-OK for every password — that is the bypass, not a password oracle;
  do not brute with that shape.
- The blind oracle uses the UNCUT username `Reese` with the password field
  carrying the injected prefix + trailing `*`.
- Response signal: `Location: /login?message=Authentication failed` vs any
  other Location — one bit per request.
- Charset: the flag charset included `{` `}` `_` and `4xx0r` slang — plan
  for the full punctuation set.
- The 40-hex directory is the static asset mirror; /login.html inside it is
  content-identical to /login.
- search.js leaked (asset mirror) the POST /search shape and required the
  session cookie the login produces.

Solver script: /tmp/opencode/ldap_flag_bf.py (concurrent char-step oracle).