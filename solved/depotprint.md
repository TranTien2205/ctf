# DepotPrint — verified 2026-09-17

Chain: PHP last-value gate vs Flask first-value worker (duplicate-key parser
differential) → loopback chrome renders internal endpoints → format-string
`spool_line` in `app.py:59` leaks `app.config` through `/queue` → forged
supervisor JWT (leaked HS256 SIGNING_KEY) → `/console` shows the manifest
row the init script seeded with the flag.

## Evidence ancestry (live target http://192.168.223.1:9000, white-box mid-loop)
- Recon: "DepotPrint · waybill label service"; PHP/8.2.33 header; page
  comment names the architecture — gateway render.php on :9000, worker
  127.0.0.1:5000 loopback-only, spool queue.db.
- Black-box probes: internal targets 302 `rejected.html`; external target
  example.com 302 `/out/label-<md5(label)>.pdf` (PDF metadata: Creator
  HeadlessChrome 152, Producer Skia/PDF — the renderer is headless Chrome).
- chain_match 0/11; classify.py candidates: `web-ssrf` (a valid branch) —
  the format-string half came from the source read.
- Source (white-box once the handout landed):
  - `render.php:92`: `$upstream = "http://127.0.0.1:5000/render?" .
    $_SERVER['QUERY_STRING'] . "&job=" . $job` — raw forward, no re-encode.
  - `render.php:29-77` gate blocks `{}`, private IP literals, localhost, and
    resolves `gethostbyname` — but checks only `$_GET['target']`.
  - `app.py:173-174` takes `request.args.getlist("job")[-1]` and `args.get
    ("target")` = FIRST — duplicate-key differential.
  - `app.py:57-59`: `line.format(spool_line=spool_line)` on rows whose
    `target` is attacker text — format-string with a callable in scope.
- Exploit chain (all through hooks.py, ledger in state.json):
  1. `?target=http://127.0.0.1:5000/status?x={spool_line.__globals__[app].config[SIGNING_KEY]}&target=https://example.com&...`
     — the gate inspects the LAST target (example.com, public) and chrome
     fetches the FIRST. /status renders as a PDF → dup-key SSRF confirmed
     ("depotprint render worker online" read back from the PDF).
  2. `/queue` through the same trick rendered the spool report; the stored
     row contains `{spool_line.__globals__[app].config[SIGNING_KEY]}` —
     `.format()` substituted the real signing key into the report the PDF
     printed: SIGNING_KEY = dc7155da…a33b.
  3. Forged `{"supervisor": true}` HS256 with the leaked key →
     `?target=http://127.0.0.1:5000/console?ticket=<JWT>&target=https://example.com`
     → the manifest JSON rendered into a PDF read back from /out.
  4. Manifest seeded row: **depot-master-record** →
     `FLAG{REDACTED}`
- Flag read from a live PDF the worker produced.
- No cleanup needed: no writes beyond what the app stores itself.

## Traps
- Chrome normalizes and URL-encodes mixed braces in the displayed URL; for
  the concept check `same_document` handles it via unquote on both sides.
- `same_document` closes the redirect chain (a webhook.site 302 to the
  worker dies on the comparison, not on the gateway).
- httpbin.org 502'd from the target side; the dup-key parser split works
  without any external redirector at all.
- The gateway blocks `{}` only in the target edge value; keep the braced
  target as the FIRST occurrence and the clean external URL as the LAST.
- The PDF text layer is glyph-IDs mapped by an embedded ToUnicode — decode
  bfchar AND bfrange or the output reads as garbage.

Solver files: challenges/depotprint/state.json (hook ledger with all probes
and verdicts).