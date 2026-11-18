# Detection checklist — the rapid CSRF screen

The 90-second triage that decides whether a CSRF path exists —
before any depth skill opens.

---

## The six questions, in order

```text
1. is there a STATE-CHANGING endpoint?         → the write exists?
2. is there a VIEWER/delivery vehicle?         → a bot, a victim, a stored page?
3. which CREDENTIAL does the write need?       → a cookie, a position, a jar?
4. does the cookie attach cross-site?          → SameSite read
5. is a TOKEN required and verified?           → the strip test
6. can a form produce the required body?       → the content-type test
```

## The commands

```bash
# 1. the write inventory
grep -rnoE '(post|put|patch|delete|change|update|transfer|set|admin|role|grant|login|submit)' <src> | head -20

# 2. the viewer
grep -rnoE 'report|visit|bot|puppeteer|playwright|headless' <src> | head -10

# 3. the credential + 4. the SameSite read
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'

# 5. the token-strip
python3 tools/web/csrf_probe.py --url "$BASE/<ep>" --method POST \
  --body '<fields>' --token-field <f>

# 6. the content-type test
curl -i -X POST "$BASE/<ep>" -H 'Content-Type: text/plain' --data '{"a":1,"i":"="}' -b "$CJ"
```

## The go/no-go table

| Answer | Verdict |
|---|---|
| no write exists | not CSRF — wrong class |
| no viewer | no delivery — check stored-context or a social hook |
| credential won't attach (Strict, no vector) | dead for this credential |
| token required+verified+unreadable | dead — falsifier |
| content-type json-only+strict | dead via form — a sibling? |
| all open | build the delivery |

## The fast falsifiers — stop conditions

```text
- SameSite=Strict on the ONLY credential + no GET write + no stored
  page → dead
- a session-bound token the page can't read → dead
- an Origin check that can't be bypassed AND required → dead via
  this vector
- a json-only content-type + strict + no sibling → dead via form
- no viewer and no stored context → no delivery channel
```

## The routing check — is it CSRF or a confusable

```text
needs to READ a cross-origin response?  → web-cors
can run JS in the target's origin?      → web-xss (stronger)
the server fetches a URL?               → web-ssrf
a cross-origin side-channel measure?    → web-xs-leaks
a ws/wss channel?                       → web-websocket
```

## The chain_match before depth

```bash
python3 tools/chain_match.py --source <dir> --record <name>
# a literal match → the card to read; a family_leads → a hint.
# the TornadoService/SSOS cards carry the exact shapes.
```
