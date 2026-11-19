# Edge cases deep — the XS-leak variants, exhaustively

Every edge case that breaks the usual assumptions — the cause and the fix.

---

## 1. The airgapped bot — no external listener

```text
the bot can't reach attacker.com — the classic exfil (a listener)
fails. fix: a server-state channel (a counter/recency/token), a
write-back, or a DOM-writeback — not an external exfil.
```

## 2. The managed-policy bot — a forced sealed shape

```text
Chrome managed policy — URLBlocklist ['*'] + URLAllowlist — the bot
can ONLY visit the target's origin — NO attacker URL reaches it —
a declarative/server-state channel is the only one that works.
```

## 3. The same-site navigation — a SameSite bypass

```text
a meta-refresh issued BY THE TARGET is a same-site navigation — it
carries the Lax cookie a cross-site fetch wouldn't — the sealed
shape's whole design avoids the cross-site cookie question.
```

## 4. The 'unsafe-inline' style channel — a script-blocked case

```text
'script-src none' blocks JS; 'unsafe-inline' in default-src/style-src
still allows STYLES — the CSS oracle works. read the CSP for what
it does NOT block — a style/font hole is the channel.
```

## 5. The font-src wildcard — the exfil that survives

```text
'img-src self' blocks a bg-image exfil; 'font-src self *' allows an
external font — the @font-face unicode-range channel works. check
WHICH directive has the hole.
```

## 6. The secret in text, not an attribute — a selector mismatch

```text
a CSS attribute-selector needs the secret IN an attribute — a
secret in TEXT content doesn't match — a unicode-range @font-face
reads the rendered text.
```

## 7. The sorted secret — the char-set IS the answer

```text
'take N random chars, sort them' → the set IS the string — a char-set
oracle (unicode-range) returns the answer directly — no ordering
work needed.
```

## 8. The n-gram gap — a beam-search miss

```text
an n-gram marker set that doesn't cover the secret's transitions —
a gap the beam can't cross — widen the marker set (all 1/2/3-grams)
and the beam width.
```

## 9. The one-bit channel — the whole-secret question

```text
a channel that carries ONE bit can't read a multi-bit secret
directly — each query reads one bit — a 32-char secret needs ~N
queries — the feasibility arithmetic matters.
```

## 10. The destructive channel — a shared-store flood

```text
an LRU flood on a shared store evicts OTHER keys — including the
secret — only flood an instance that's yours alone.
```

## 11. The one-shot token — a spend-last oracle

```text
a GETDEL/single-use token's 'did it survive' burns the check — one
bit AND it's gone — spend it AFTER the cheaper channels narrow the
answer.
```

## 12. The bot's context — a non-flag session

```text
a plain-visitor bot reads a plain session, not the flag-holder's —
verify the bot's cookie — a flag cookie, an admin context.
```

## 13. The TTL window — a 60s secret

```text
a short-TTL secret — the leak+decode+submit must fit the window —
a slow sequential leak misses it — a high-bandwidth channel.
```

## 14. The rate-cap — a flood that won't fit

```text
thousands of markers need tens-hundreds rps — a flat throughput cap
makes the attack impossible — measure the rate first.
```

## 15. The noisy channel — a beam-search confidence

```text
a noisy channel's top candidate isn't always right — a beam search
over a noisy set needs a confidence check + a verify step.
```

## 16. The postMessage broadcast — a real read, not a leak

```text
a postMessage '*' broadcast transmits the data — a real read
primitive — the data is sent, not inferred.
```

## 17. The JSONP/XSSI serve — a real read, not a leak

```text
a JSONP endpoint serves data AS JavaScript — a script-tag read —
a real primitive, not a measure.
```

## 18. The stored-response — a cache-poison, not a leak

```text
a cache that stores a response for a future read is a cache-poison
question — not a side-channel measure.
```

## 19. The JSDOM bot — no render

```text
a JSDOM bot has no rendering engine — no CSS, no fonts, no :visited —
only the DOM/timing/count channels survive.
```

## 20. The partitioned :visited — a cross-site limit

```text
a partitioned :visited per top-frame site — a link to a URL visited
on another site doesn't style visited — a same-site or a render-
side-channel only.
```

## 21. The partitioned cache — a cross-site limit

```text
a partitioned cache per top-frame site — a resource cached on site
A isn't shared with site B — the cache-probe is a same-site read.
```

## 22. The SameSite=Strict cookie — the stricter gate

```text
a Strict cookie — even a top-level navigation doesn't carry it on
a first-party-only case — a sealed-shape same-site request still
works — the bot's request to the target itself is same-site.
```

## 23. The SameSite=None + Secure cookie — the credentialed read

```text
a None+Secure cookie — a cross-site fetch carries it — the classic
shape's whole channel carries the cookie.
```

## 24. The count oracle's length-first read — a narrowing

```text
a count oracle (frames.length) reads the result count — a length-
first read narrows the secret's length before the char-by-char.
```

## 25. The screenshotting bot — a DOM-writeback read

```text
a bot that screenshots the page — a DOM-writeback (the secret
rendered visibly) — the screenshot IS the exfil — no listener needed.
```

## 26. The incognito bot — a fresh-session case

```text
an incognito-context bot — a fresh session each visit — the flag
cookie is set per-visit — the leak reads under the flag-holder's
session.
```

## 27. The data: URL — a null-origin case

```text
a data: URL — an opaque/null origin — the channel is a same-origin
leak or a server-state read — the null origin's CORS Origin is the
literal 'null'.
```

## 28. The stored page — a same-origin case

```text
a stored page on the target's origin — a same-origin CSS/JS channel
— the Lax cookie rides on a same-site navigation.
```

## 29. The fragment — a same-origin navigation

```text
a URL fragment the bot's page reads — a same-origin navigation to
a specific element/state.
```

## 30. The COOP/COEP surface — an isolation gate

```text
a COOP same-origin window — a window.open returns a cross-origin-
isolated handle — a navigation check is still readable.
a COEP require-corp page — a cross-origin subresource needs a CORP
header — an unmarked resource fails — an onload/onerror oracle.
```
