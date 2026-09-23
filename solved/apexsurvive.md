# ApexSurvive — SOLVED (assisted: writeups for direction, self-built execution)

- Platform: HTB Cyber Apocalypse 2024 [Insane] (~30 solves)
- Date: 2026-09-07
- Flag: `HTB{REDACTED}` (read from /root/flag via in-app SSTI)
- Artifacts: `~/ctf/challenges/apexsurvive/{race_run.py, xss.py, rce.py, race_profile*.py}`
- Writeups used: elmosalamy blog + official repo (direction); all payloads rebuilt/self-debugged.

## Chain

1. Register + normal email verify (through test@email.htb inbox).
2. **Race on `/profile`** (the INTENDED one — NOT sendVerification): `updateProfile`
   commits THEN `/profile` calls `sendEmail(userId, <request-param email>)` and
   `sendEmail` re-queries getToken → an interleaved update(B=.htb) commit lands
   between them → the email delivered to A (test@email.htb, inbox-visible)
   contains **B's token** → verify → `isInternal`.
   Winning burst: [B, A, B] × 15 over one HTTP/2 connection (~45 reqs, hit at
   round 1-6 with re-rolls).
3. **Stored XSS** via `product.note`: rendered inside `` let note = `{{note|safe}}` `` —
   a single `${...}` expression + trailing backtick+`//` = arbitrary JS at template
   literal evaluation (BEFORE DOMPurify). Payload (validated in local chromium):
   - JWT payload = `d.split('=')[1].split('.')[1]` + base64url→base64 + MANUAL padding
     (`atob` fails unpadded!) → `antiCSRFToken`
   - body via `new URLSearchParams({...})` — **bleach turns `&` into `&amp;` in
     stored notes; & must only exist at RUNTIME**
   - exfil = self-contained: the admin-bot XSS POSTs /api/addItem creating a
     product whose `note` = admin cookie; read it back as normal user.
   - Cookie staleness: the bot re-logins per visit — stolen cookies die fast;
     re-report and steal the FRESH one, verify with /settings == 200 immediately.
4. **Admin AFW**: `os.path.join(root, 'contracts', filename)` with
   filename=/app/uwsgi.ini etc. — checkPDF (PyPDF2 3.0.1 strict) forces valid PDF
   → hand-crafted PDFs with payload bytes inside the (unparsed) content stream.
5. **uwsgi RCE** (doyensec): overwrite /app/uwsgi.ini with FULL original config +
   `foo = @(exec://...)`; trigger reload via AFW on an imported .py — BUT the
   trigger file itself gets imported on reload → PDF there = brick (two instances
   died this way). Exfil via exec@curl→external tunnel failed (exec runs only on
   config parse; reload semantics + egress uncertain).
6. **FINAL RELIABLE RCE** (no exec, no brick): AFW
   `/app/application/templates/product.html` = PDF containing Jinja SSTI
   `{{ get_flashed_messages.__globals__['__builtins__']['open']('/root/flag').read() }}`
   + AFW a NEW `/app/application/zz_trigger.py` (never imported → reload without
   brick) → py-autoreload restarts workers → **jinja cache resets** → next
   /challenge/product/<id> renders MY template → flag printed in the page.

## Reusable lessons

- Read the OFFICIAL writeup's mechanism paragraph FIRST — I raced the wrong pair
  (sendVerification internal window — structurally void under REPEATABLE READ)
  for hours; the official writeup's "the application gets the confirmation token
  after updating the profile in a different function" sentence was the whole game.
- Dirty-AFW (content must pass a validator) kills naive overwrites: config-file
  RCE needs the FULL original config (partial = lost socket = permanent 502) and
  trigger files get IMPORTED on reload (PDF .py = permanent 502). Template AFW +
  fresh non-imported .py trigger avoids both.
- Jinja cache resets on worker restart: overwrite an ALREADY-CACHED template +
  force a worker reload via a fresh .py file.
- bleach (stored XSS path): `&`→`&amp;` — build runtime strings (URLSearchParams).
- PEP 562 module `__getattr__` makes unknown-name imports survivable in stubs.
- Self-contained exfil (app-as-channel) is worth the extra payload work when the
  box has no trusted outbound; but keep browser-local validation (headless
  chromium + fetch stub) to debug JS payloads without burning bot cycles.

---

## Re-solved 2026-09-23 — self-solved from this card, and the destructive step turned out to be unnecessary

Second instance (`https://154.57.164.82:30612`, HTTP/2 + TLS — the port speaks HTTPS,
a plain `http://` request answers `400 The plain HTTP request was sent to HTTPS port`).
Same build. The chain card's `first_confirming_probe` was run first and held.

### What actually ran

1. **Race** — `race_run.py <base> s1` unchanged. `45/45` requests returned 200;
   round 1 produced 13 fresh tokens, **round 2 unlocked `isInternal`** via token
   `ee8927bd`. The account ends up as `s1int@apexsurvive.htb`, verified + Internal.
2. **Stored XSS** — `xss.py` unchanged. The admin bot created the `pwnX` product
   whose `note` carried its own cookie; read back as a normal user. JWT payload
   decoded to `{'id': 1, ...}` and `/challenge/settings` answered 200, so the
   cookie was live.
3. **AFW → SSTI** — this is where the recorded chain can be cut short.

### The step that is not needed: overwriting uwsgi.ini

The old `rce.py` overwrites `/app/uwsgi.ini` and drops a PDF on `/app/run.py`.
That is the path that bricked two instances the first time, and **none of it is
required**. Jinja caches a template per worker process, and `uwsgi.ini` runs
`processes = 4`, so a worker that has never served `/challenge/product/<id>`
still loads the file from disk. Simply writing the SSTI template and requesting
the page hit a cold worker **on the very first poll**:

```
[*] write /app/application/templates/product.html -> 200 {"message":"Contract Added"}
[+] FLAG: HTB{...}
```

No reload was forced, `uwsgi.ini` was never touched, and no `.py` was written.
`ssti_rce.py` in the challenge directory is that safe variant; it also restores
the original `product.html` from the supplied source on the way out.

Payload, unchanged from the first solve and still correct:
`{{ get_flashed_messages.__globals__['__builtins__']['open']('/root/flag').read() }}`
— `uwsgi.ini` sets `uid = root`, so the template reads the mode-600 flag directly
and the setuid `/readflag` helper is never needed.

### Why the write lands

- `api.py:160` — `os.path.join(current_app.root_path, 'contracts', uploadedFile.filename)`;
  an absolute `filename` discards the first two components.
- `middlewares.py:85` — `sanitizeInput()` cleans `request.args` and `request.form`
  only. `request.files` and therefore `.filename` are never touched.
- `api.py:156` — `checkPDF` runs `PdfReader(strict=True)`, which parses the xref
  and the object headers but never the content stream, so the payload rides there.

### Residual state to know about

Restoring the file on disk does **not** un-cache it. After the restore, 9 of 10
requests still rendered the SSTI template and 1 of 10 rendered the 6925-byte
original — the workers that had already cached the overwritten template keep
serving it, because `py-autoreload = 3` only watches `.py` files and no `.py`
changed. Restarting the instance clears it. Do not try to force the reload by
writing a PDF over an imported `.py`: that is exactly the brick.

### Reusable lessons (new)

- **Check whether the destructive step is load-bearing before taking it.** The
  recorded chain reached the flag through a config overwrite that had already
  cost two instances; the cache-miss across 4 workers made it unnecessary. A
  multi-process app means "the template is cached" is only true per worker.
- **Undoing a file write does not undo its effects.** Plan the cleanup around what
  the application caches, not around the bytes on disk, and say so plainly when
  the residue cannot be cleared without a restart.
- The port may be HTTPS even when the challenge is handed over as `host:port`;
  a `400 The plain HTTP request was sent to HTTPS port` is the tell.
