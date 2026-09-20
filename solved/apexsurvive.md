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
