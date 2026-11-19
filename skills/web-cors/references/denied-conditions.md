# Denied conditions — when the CORS read is closed, definitively

The conditions under which NO CORS read is possible — the hard
falsifiers that end the class.

---

## 1. A `*` on a sensitive endpoint — the structural falsifier

```text
a `*` endpoint can NEVER be a credentialed read — the browser
rejects `*`+credentials universally, in every engine, by spec.
a `*` on /api/me reads public data only — the flag isn't reachable
through a credentialed CORS read on a `*` endpoint. FALSIFIED.
```

## 2. ACAC absent — the credential gate held

```text
no Access-Control-Allow-Credentials → the read is non-credentialed
even with a reflected/allowed ACAO — the session cookie doesn't
reach the JS. a public read of public data. FALSIFIED for a
credentialed read.
```

## 3. A SameSite=Strict cookie — the credential can't attach

```text
a SameSite=Strict session cookie NEVER attaches to a cross-site
fetch — a credentialed CORS read is impossible regardless of ACAO.
a SameSite=Lax cookie attaches only on same-SITE fetches — a
cross-SITE read is non-credentialed. FALSIFIED for the cross-site
credentialed read.
```

## 4. A strict allowlist with no bypass — the origin gate held

```text
an exact-match allowlist — no reflect, no null, no lookalike, no
subdomain, no url-parse confusion — the foreign origin is rejected.
FALSIFIED — unless an alternate-read channel exists.
```

## 5. A strict preflight + no simple path — the request gate held

```text
the read NEEDS a non-simple request (a custom header, a non-simple
method) AND the preflight's ACAM/ACAH denies it AND no simple
request reaches the data. FALSIFIED for that read shape.
```

## 6. No sensitive endpoint — the read target is public

```text
every readable endpoint returns public/nonsensitive data — the CORS
read works but carries nothing worth exfiltrating. FALSIFIED —
a different endpoint or a different class.
```

## 7. No session — the credential source is absent

```text
no cookie, no Bearer, no client cert — the read has no credential
to carry — a public read. FALSIFIED for a credentialed read.
```

## 8. No delivery path — the page can't reach the victim

```text
no /report bot, no stored context, no subdomain, no phishing surface
— the exploit page can't reach the victim's session. FALSIFIED
for a bot-driven read.
```

## 9. No exfil channel — the data can't leave

```text
the read works but the bot can't reach any exfil endpoint AND no
write-back/DOM-writeback/postMessage channel exists — the data is
trapped. FALSIFIED for an exfil-dependent solve (but a page-side
readback may still work).
```

## 10. No alternate-read — the whole surface is closed

```text
CORS closed AND no JSONP endpoint AND no ws channel AND no
postMessage broadcast AND no XSS surface AND no XS-leak — the
entire cross-origin read surface is dead. FALSIFIED — reclassify.
```

## The denied-conditions ledger — the closure recorded

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-closed: <the held gate> — <the evidence> — pivot=<class>"
python3 tools/hooks.py post-probe <c> --verdict refutes \
  --hypothesis-id <H> --class web-cors --evidence-kind class \
  --evidence '<the held gate>' --response '<the bytes>'
```

## The kill-map — the closed layers with their reopen conditions

```json
{"layer":"cors-aco","status":"closed","evidence":"strict allowlist","reopen":"a lookalike/null/sub passes"}
{"layer":"cors-acac","status":"closed","evidence":"ACAC absent","reopen":"ACAC appears"}
{"layer":"cors-cookie","status":"closed","evidence":"SameSite=Strict","reopen":"a non-cookie credential"}
{"layer":"cors-endpoint","status":"closed","evidence":"public data","reopen":"a sensitive endpoint found"}
{"layer":"cors-delivery","status":"closed","evidence":"no bot/stored/sub","reopen":"a delivery surface found"}
{"layer":"jsonp","status":"closed","evidence":"no callback","reopen":"a JSONP endpoint found"}
{"layer":"ws","status":"closed","evidence":"no ws","reopen":"a ws endpoint found"}
```
