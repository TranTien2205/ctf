# Detection deep — reading the signals that name CSRF

The class signal is "a browser can send a request the victim didn't
intend". The observable signals that point here — and the ones that
point elsewhere.

---

## 1. The positive signals

```text
- a state-changing endpoint that takes no CSRF token
- a Set-Cookie with missing/None/Lax SameSite
- a bot/report/visit endpoint — a privileged viewer exists
- a localhost/remote_ip/private-network gate — the bot IS local
- an Origin/Referer check that looks incomplete or absent
- a login/SSO endpoint — a credential-plant candidate
- a JSON endpoint that might accept text/plain
- a GET route that mutates state
- a persistent cookie jar across bot visits
```

## 2. The classify.py signal mapping

```text
tools/classify.py names web-csrf from the mechanism vocabulary in
source or observation:
- 'csrf', 'xsrf', 'cross-site', 'forgery'
- 'SameSite', 'samesite' — the cookie attribute in play
- 'Origin', 'referer' — the header checks
- a bot/visit/report surface — the delivery vehicle
- 'remote_ip', 'localhost', '127.0.0.1' — a position-gate the bot
  passes
the candidate is a hypothesis — confirm by measuring the gates.
```

## 3. The chain_match first — the card-shaped recall

```bash
python3 tools/chain_match.py --source <dir> --record <name>
# a literal signal match → a graded candidate + the card to read
# a family_leads match → a weak-graded card to READ, not a probe
```

Run the matcher before inventing — the TornadoService/SSOS cards
carry the exact shapes.

## 4. The black-box signals — no source

```text
- a cookie with no SameSite attribute → the bot's browser may attach
- a form endpoint that accepts a foreign-Origin replay → no Origin check
- a token field ABSENT from a state-changing form → maybe unprotected
- a /report or 'contact admin' feature → the viewer exists
- a SameSite=Lax cookie + a GET link that changes state → the open case
```

## 5. The "which credential attaches" read — the first measurement

```bash
# the auth cookie's attribute decides the whole class
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
#   SameSite=Strict → not via this cookie
#   SameSite=Lax    → GET-nav only
#   SameSite=None;Secure → open
#   missing         → modern=Lax, old-bot=None
#   Partitioned     → third-party dead
```

This ONE response answers the central question — read it first.

## 6. The "is there a viewer" read — the bot surface

```bash
# the delivery vehicle exists?
grep -rnoE 'report|visit|admin-bot|preview|review|contact|check.*url|puppeteer|playwright|headless' <src> | head -20
# or black-box: a 'report this' / 'contact admin' UI feature
```

No viewer = no delivery vehicle → the CSRF needs a different reader
(a stored page's viewer, a social hook) or a different class.

## 7. The "does the write exist" read — the state-change question

```text
CSRF needs a WRITE — an endpoint that changes state. a read-only
API isn't CSRF material; a state-changing one is. grep the write-
verb routes; check the GET routes for side-effects.
```

## 8. The "the credential is a position not a cookie" read

```text
a localhost/remote_ip/PNA gate — the 'credential' is the bot's
network position, not a cookie. SameSite is irrelevant — the bot's
browser IS the privileged client. the TornadoService card's read.
```

## 9. The "the jar persists" read — the SSOS signal

```text
does the bot's cookie jar persist across visits? a fresh-context
bot loses cookies between cycles; a persistent-profile bot keeps
them. the login-CSRF needs the jar to persist.
```

## 10. The signal→skill routing

```text
a cross-origin WRITE under ambient credentials      → web-csrf
a cross-origin READ (the response matters)          → web-cors
JS running in the target's origin                   → web-xss
the SERVER fetching a URL                           → web-ssrf
a cross-origin SIDE-CHANNEL measure                 → web-xs-leaks
a ws/wss channel cross-origin                       → web-websocket
the classify.py answer is a candidate — confirm the delivery model
before opening the depth skill.
```

## 11. The negative signals — when it isn't CSRF

```text
- the 'state change' needs a token the attacker can't read → not CSRF
- the 'delivery' is actually a server-side fetch → SSRF
- the 'response' is what you need → CORS
- there's no viewer/delivery vehicle → no CSRF channel
- the write is already reachable by a direct request (no ambient
  credential needed) → an access-control bug, not CSRF
```

## 12. The first-probe decision

```text
the class signal is present → the first probe is the cookie-
attribute read + a token-strip replay:
  curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
  python3 tools/web/csrf_probe.py --url <ep> --method POST \
    --body '<fields>' --token-field <f>
the cookie attribute names the delivery surface; the token-strip
names the enforcement gap. both together scope the attack.
```
