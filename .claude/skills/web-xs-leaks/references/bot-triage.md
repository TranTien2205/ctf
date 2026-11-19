# Bot triage — which bot, which channel

The bot's configuration decides the whole attack's shape.

---

## The bot's render surface — does it render

```text
a REAL browser (Chrome/Firefox/Safari, headless or headed) — the
CSS/font/render channels work — the full oracle surface.
a JSDOM — no render — only the DOM/timing/count channels survive —
no CSS, no fonts, no :visited.
the deciding question: does the bot render?
```

## The bot's URL control — whose page it visits

```text
a /report that takes a URL → the bot visits YOUR page → the classic
shape (if JS runs) or a declarative channel (if JS is blocked).
a fixed-URL bot → the bot only visits the target → the sealed shape.
a managed-policy bot → a forced sealed shape — URLBlocklist ['*'].
```

## The bot's session — whose context it reads under

```text
a flag-holder session — a flag cookie, an admin context → the leak
reads under the flag-holder's session.
a plain-visitor session → the leak reads a plain session — the flag
isn't in it — a wrong-context case.
verify the bot's cookie: grep 'setCookie|cookie.*flag|flag.*cookie'.
```

## The bot's network reach — can it reach your listener

```text
a bot that reaches attacker.com → the classic exfil (a listener).
an airgapped bot → a server-state channel, a write-back, or a
DOM-writeback — not an external exfil.
```

## The bot's isolation — an incognito context

```text
an incognito-context bot — a fresh session each visit — the flag
cookie is set per-visit (a setCookie with the flag) — the leak reads
under the flag-holder's session.
```

## The bot's screenshot — a DOM-writeback read

```text
a bot that screenshots the page — a DOM-writeback (the secret
rendered visibly in a large font) — the screenshot IS the exfil —
no listener, no server-state read needed.
```

## The bot's managed policy — a forced sealed shape

```text
Chrome managed policy — URLBlocklist ['*'] + URLAllowlist — the bot
can ONLY visit the target's origin — NO attacker URL reaches it —
a declarative/server-state channel is the only one that works.
```

## The per-bot channel-map — which channel for which bot

```text
bot                              channel
a real browser + a URL-submit    the classic shape (JS) or CSS/server-state
a real browser + a fixed URL     the sealed shape — CSS/server-state
a real browser + a managed policy a declarative/server-state only
a JSDOM + a URL-submit           DOM/timing/count only
a JSDOM + a fixed URL            a server-state channel only
a screenshotting bot             a DOM-writeback read
an airgapped bot                 a server-state/write-back/DOM-writeback
an incognito bot                 a fresh-session case — verify the cookie
```

## The bot's per-config grep — the launch args

```bash
# the bot's launch args — the context
grep -rnoiE 'puppeteer\.launch|playwright|selenium|headless|incognito|args:|URLBlocklist|URLAllowlist|JSDOM' <src> | head -20
# the bot's session — the flag-holder context
grep -rnoE 'setCookie|cookie.*flag|flag.*cookie|admin.*cookie' <src> | head -10
# the bot's URL — attacker-controlled or fixed
grep -rnoE 'goto|visit|url.*submit|report' <src> | head -10
```

## The bot-triage decision — which shape the bot forces

```text
a real browser + a URL-submit + JS runs      → the classic shape
a real browser + a URL-submit + JS blocked   → a declarative/server-state
a real browser + a fixed URL                 → the sealed shape
a managed-policy bot                         → a declarative/server-state only
a JSDOM                                      → DOM/timing/count only
an airgapped bot                             → a server-state/write-back
a screenshotting bot                         → a DOM-writeback read
```

## The bot's reachability check — the exfil's feasibility

```bash
# can the bot reach your listener
curl -sI "https://attacker.com/listener" || echo "airgapped — a server-state channel"
# does the bot carry the flag session
grep -rnoE 'setCookie|cookie.*flag|flag.*cookie' <src> | head -5
# does the bot render
grep -rnoiE 'puppeteer|playwright|selenium|headless|JSDOM' <src> | head -5
```
