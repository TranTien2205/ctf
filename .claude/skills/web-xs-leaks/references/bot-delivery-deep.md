# Bot delivery deep — every path an attacker page takes to the bot

The complete delivery taxonomy — each shape, its constraint, and the
channel it forces.

---

## 1. The /report endpoint — the canonical delivery

```bash
curl -X POST "$BASE/report" -d 'url=https://attacker/page'
# or a JSON body
curl -X POST "$BASE/report" -H 'Content-Type: application/json' \
  -d '{"url":"https://attacker/page"}'
# or a form-encoded
curl -X POST "$BASE/report" --data-urlencode 'url=https://attacker/page'
```

```text
the bot opens the submitted URL — your page's JS runs on YOUR
origin (the classic shape) or doesn't run (the sealed shape). the
deciding question: does the bot's context allow YOUR JS?
```

## 2. The data: URL — a null-origin case

```bash
curl -X POST "$BASE/report" --data-urlencode \
  'url=data:text/html,<html><script>...</script></html>'
# a base64 data: URL
curl -X POST "$BASE/report" --data-urlencode \
  'url=data:text/html;base64,PGh0bWw+...'
```

```text
a data: URL — an opaque/null origin — the channel is a same-origin
leak or a server-state read. a null origin's CORS Origin is the
literal 'null' — a CORS-null-reflect reads the data.
```

## 3. The stored page — a same-origin case

```text
a stored page on the target's origin (a comment, a note, a profile
field) — the bot visits it — the stored content's JS/CSS runs on
the TARGET's origin — a same-origin channel. the Lax cookie rides.
```

## 4. The fragment — a #id the bot's page reads

```bash
curl -X POST "$BASE/report" -d 'url=https://target/page#' + fragment
# a fragment the page's JS reads — a same-origin navigation to a state
```

```text
a URL fragment the bot's page reads — a same-origin navigation to
a specific element/state — the fragment carries the delivery.
```

## 5. The managed-policy bot — a forced sealed shape

```text
Chrome managed policy — URLBlocklist ['*'] + URLAllowlist — the bot
can ONLY visit the target's origin — NO attacker URL reaches it.
the ONLY channels are:
- a DECLARATIVE channel (a CSS selector → a font/URL load — the
  style engine does the work)
- a SERVER-STATE channel (a mutation the GET caused — a counter,
  a recency, a token)
```

## 6. The airgapped bot — a server-state exfil

```text
a bot that can't reach attacker.com — the classic exfil (a listener)
fails — the ONLY exfil is:
- a server-state channel (a counter/recency/token you read on the
  target)
- a write-back (the data lands on the target — a comment, a field)
- a DOM-writeback (a screenshotting bot reads the rendered secret)
```

## 7. The meta-refresh — a same-site navigation

```text
a meta-refresh issued BY THE TARGET is a same-site navigation — it
carries the Lax cookie a cross-site fetch wouldn't. the sealed
shape's whole design avoids the cross-site cookie question — the
bot's request to the target itself is same-site.
```

## 8. The same-origin CSS + privileged URL — the verified card

```text
a unicode-range leak recovers a token's char-set → a second
stylesheet's @font-face src is the SAME-ORIGIN privileged URL → the
bot's font load is the privileged GET that no external client could
fire. the channel that read the token becomes the channel that
spends it.
```

## 9. The multiple-visits case — a per-visit delivery

```text
a channel that carries N bits per visit needs the bot to visit N
times — each /report is a separate visit. the delivery's feasibility
is the visit-count × the bits-per-visit.
```

## 10. The single-visit case — a high-bandwidth channel

```text
a recency/LRU channel carries thousands of bits per visit — a single
/report suffices — the whole char-set leaks in one visit. the
channel's bandwidth determines the visit count.
```

## 11. The incognito bot — a fresh-session case

```text
an incognito-context bot — a fresh session each visit — the bot's
session is set per-visit (a setCookie with the flag) — the leak
reads under the flag-holder's session.
```

## 12. The headed-vs-headless bot — the render surface

```text
a headless browser — still renders — the CSS/font/render channels
work. a JSDOM — no render — only the DOM/timing/count channels
survive — no CSS, no fonts, no :visited.
```

## 13. The screenshotting bot — a DOM-writeback read

```text
a bot that screenshots the page — a DOM-writeback (the secret
rendered visibly in a large font) is the read-back — the screenshot
IS the exfil — no listener needed.
```

## 14. The per-shape delivery-selection

```text
a /report + a URL + JS runs          → the classic shape
a /report + a URL + JS blocked       → a declarative/server-state
a data: URL                          → a null-origin/same-origin case
a stored page                        → a same-origin case
a managed-policy bot                 → a declarative channel only
an airgapped bot                     → a server-state/write-back
a meta-refresh                       → a same-site navigation
a high-bandwidth channel             → a single visit
a low-bandwidth channel              → multiple visits
a screenshotting bot                 → a DOM-writeback read
an incognito bot                     → a fresh-session case
a JSDOM                              → a DOM/timing channel only
```

## 15. The delivery-check — the bot's reachability

```bash
# can the bot reach your listener
curl -sI "https://attacker/listener" || echo "airgapped — a server-state channel"
# does the bot carry the flag session
grep -rnoE 'setCookie|cookie.*flag|flag.*cookie' <src> | head -5
# is the bot's URL attacker-controlled
grep -rnoE 'goto|visit|url.*submit' <src> | head -5
# does the bot render
grep -rnoiE 'puppeteer|playwright|selenium|headless|JSDOM' <src> | head -5
```
