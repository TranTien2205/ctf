# Evasion and filter — working around XS-leak defenses

Each defense, what it blocks, and the channel that survives.

---

## 1. A script-src 'none' CSP — the JS block

```text
blocks: all attacker JS — the classic client-side oracles.
survives: a declarative channel (a CSS selector → a font/URL load —
the style engine, not JS) or a server-state channel (a counter/
recency/token — a mutation the GET caused).
```

## 2. A style-src 'self' — the external-stylesheet block

```text
blocks: an external stylesheet — your cross-origin CSS.
survives: a stored stylesheet on the target's origin (a custom-css
surface) — a same-origin carrier.
```

## 3. A font-src 'self' (no wildcard) — the external-font block

```text
blocks: an external font host — the @font-face unicode-range exfil.
survives: a CSS-selector oracle with a bg-image (if img-src has a
wildcard) or a same-origin font.
```

## 4. An img-src 'self' — the external-image block

```text
blocks: a bg-image exfil (a custom property → a url()).
survives: a font-face exfil (if font-src has a wildcard) or a
server-state channel.
```

## 5. A SameSite=Lax cookie — the cross-site-cookie gate

```text
blocks: a cross-site fetch's cookie — the classic shape's
credentialed read.
survives: a same-site navigation (a meta-refresh issued BY THE
TARGET) or a sealed-shape channel that doesn't need the cookie
cross-site.
```

## 6. A SameSite=Strict cookie — the stricter gate

```text
blocks: even a top-level navigation's cookie on a first-party-only
case.
survives: a sealed-shape channel — the bot's request to the target
itself is same-site — the Strict cookie rides on a same-site request.
```

## 7. A partitioned cache — the cache-probe limit

```text
blocks: a cross-site cache-probe — a resource cached on site A
isn't shared with site B.
survives: a same-site cache-probe or a different channel.
```

## 8. A partitioned :visited — the history read's limit

```text
blocks: a cross-site :visited read — a link to a URL visited on
another site doesn't style visited.
survives: a same-site :visited or a render-side-channel (a repaint
cost, a font-load trigger).
```

## 9. A managed policy — the URL-block

```text
blocks: ALL non-allowlisted URLs — the bot can't visit your page.
survives: a declarative/server-state channel — the only channel
that works under a forced sealed shape.
```

## 10. A COOP/COEP — the cross-origin-isolation gate

```text
a COOP same-origin window — a window.open returns a cross-origin-
isolated handle — a navigation check is still readable.
a COEP require-corp page — a cross-origin subresource needs a CORP
header — an unmarked resource fails — an onload/onerror oracle.
```

## 11. A rate-limit — the flood cap

```text
blocks: a flood that exceeds the rps — the LRU-eviction channel's
flood.
survives: a smaller marker set, a lower-rate channel, or a
different channel.
```

## 12. A TTL — the secret's expiry

```text
blocks: a slow sequential leak — the secret expires before the
leak completes.
survives: a high-bandwidth channel (a recency, a char-set) — a
single-visit leak.
```

## 13. A non-attribute secret — the selector's miss

```text
blocks: a CSS attribute-selector — the secret isn't in an attribute.
survives: a unicode-range @font-face — it reads the rendered text,
not an attribute.
```

## 14. A one-shot token — the burned check

```text
blocks: a repeated 'did it survive' query — a spent token is gone.
survives: spend it LAST — the cheaper channels (a counter, a recency)
narrow the answer first.
```

## 15. A noisy channel — the discrimination problem

```text
blocks: a clean read — the channel's noise floor.
survives: average over N samples (a timing oracle), a control pair
(to separate signal from noise), a higher-bandwidth channel.
```

## The per-defense channel-survival

```text
defense                  blocks              survives
script-src none          JS                  CSS/server-state
style-src self           external CSS        a stored stylesheet
font-src self            external fonts      a bg-image (if img-src *)
img-src self             external images     a font-face (if font-src *)
SameSite=Lax             cross-site cookie   a same-site navigation
SameSite=Strict          even top-level nav  a same-site request
partitioned cache        cross-site probe    a same-site probe
partitioned :visited     cross-site history  a same-site/render channel
managed policy           all attacker URLs   a declarative/server-state
COOP/COEP                isolation           an onload/onerror oracle
rate-limit               a flood             a smaller marker set
TTL                      a slow leak         a high-bandwidth channel
non-attribute secret     a CSS selector      a @font-face unicode-range
one-shot token           a repeated query    a spend-last ordering
a noisy channel          a clean read        an averaging/control pair
```
