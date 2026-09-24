# Bobby's Bistro — SOLVED (self-solved)

- Platform: HackTheBox. Target: `154.57.164.81:32209`. Source supplied.
- Stack: Flask + SQLAlchemy + SQLite, Chameleon (`.pt`) templates, RS256 JWT via PyJWKClient,
  a requests-based chat bot (not a browser).
- Flag: `/flag.txt` on disk; no route serves it, so it needs template-level file read.
- The name is the hint: Little Bobby Tables.

## Chain

1. **SQLi.** `/profile` POST builds its filter as
   `db.session.query(User).filter(text("token='{}'".format(token)))`. Using the ORM buys nothing
   once you format straight into `text()`. `' OR '1'='1` dumps the users table, and
   `profile.pt` renders `id`, `username` and `role` for each row — which hands over the admin's
   **user id**, and that id is the entire JWT claim (`{"user_id": ...}`).
2. **Arbitrary file write.** `/api/chat-messages` does
   `file.save(UPLOADS_DIR + "/" + file.filename)`. Werkzeug does **not** sanitise
   `FileStorage.filename` — `secure_filename()` has to be called explicitly and never is.
   Confirmed with a harmless probe: uploading as `../static/probe_<rand>.txt` and then fetching
   `/static/probe_<rand>.txt` returned the bytes.
3. **The JWT trust root is a writable file.** `verify_token()` constructs a **new
   `PyJWKClient` on every call** against `static/.well-known/jwks.json` with no caching, and
   takes the algorithm from the key itself. So the write primitive is a key-confusion primitive:
   append our own public key (new `kid`) to that JWKS and sign a token with the matching private
   key. `/admin/announcements` then returned 200.
   **Important:** the original key was kept alongside ours rather than replaced, so every other
   player's already-issued token still verified. Afterwards the file was restored byte-identically,
   which also revoked our own forged token (verified: it now 302s).
4. **Chameleon SSTI.** The admin announcement endpoint does `PageTemplate(content).render()` on
   markdown output, defended only by deleting the characters `` $ # { } " _ . ``. That kills
   `${...}` interpolation, dunder access and any dotted attribute access — but not TAL:
   single-quoted `tal:` attributes survive, `open` is present in the `python:` namespace, and a
   path can be built as `chr(47)+chr(102)+...` with no dots or quotes at all. `tal:repeat` over a
   file object iterates its lines, so the flag is read without ever calling `.read()`.

   `<div tal:repeat='l python:open(chr(47)+...+chr(116))' tal:content='l'>x</div>`

   The rendered result is stored as the announcement body and displayed on `/announcements`.

## Evidence ancestry

The SSTI payload was developed and proven in a local venv against the same Chameleon/Markdown
versions (full pipeline: `markdown()` -> character filter -> `PageTemplate().render()`) before
anything was posted, because each announcement is written to a row for *every* user and there is
no delete endpoint. The path traversal was proven with a throwaway file rather than by going
straight at the JWKS. The live chain then worked on the first attempt.

## Reusable lessons

- An ORM is not a defence. `filter(text("... '{}'".format(x)))` is a plain string-concatenation
  injection; look for `text()`, `.execute()` and f-strings rather than assuming the ORM parameterises.
- Werkzeug's `FileStorage.filename` is attacker-controlled and unsanitised. `dir + "/" + filename`
  is an arbitrary write every time.
- **Ask where a verifier's trust root lives.** Here the JWKS was a file inside the web root that
  the app re-read on every request, so "arbitrary file write" silently equals "forge any session".
  A key-set on disk plus any write primitive is a complete auth bypass.
- When injecting a key, *append* rather than replace: it keeps other sessions alive on a shared
  instance and is trivially reversible.
- A character blacklist is not a sandbox. Stripping `.` and `_` looks like it kills Python
  expression abuse, but `chr()` concatenation rebuilds any string, and choosing an *iterating*
  construct (`tal:repeat` over a file) sidesteps the method call the blacklist was aimed at.
- The filter ran on template *input*, so the flag's own braces passed through the output untouched.
