# Negative results — recording a dead channel

What a failed XS-leak channel actually proves, and how to record it.

---

## 1. The broken-channel negative — a control pair that doesn't separate

```text
an always-true control that doesn't fire → the channel is broken —
the selector doesn't match, the font doesn't load, the counter
doesn't increment. a proved negative: THIS channel is dead.
record it: 'the CSS-selector channel on <surface> — the YES control
didn't fire — the secret isn't in an attribute'.
```

## 2. The noisy-channel negative — a false-positive channel

```text
a never-true control that fires → the channel is noisy or matches
ambient state — 'the CSS-selector channel fires on everything — the
attribute isn't the secret'. a proved negative: the channel's
discrimination is dead.
```

## 3. The CSP-blocked negative — a script/style/font gate

```text
'script-src none' → no JS → the sealed shape is forced.
'img-src self' → a bg-image exfil is blocked.
'font-src self' (no wildcard) → an external font is blocked.
record it: 'the <directive> CSP blocks the <channel> channel'.
```

## 4. The airgapped negative — no listener reach

```text
a bot that can't reach attacker.com — the classic exfil fails.
record it: 'the bot is airgapped — no external exfil — a server-
state channel or a write-back is required'.
```

## 5. The managed-policy negative — a forced sealed shape

```text
URLBlocklist ['*'] + URLAllowlist — the bot can ONLY visit the
target's origin — NO attacker URL reaches it.
record it: 'the managed-policy bot — a declarative/server-state
channel is the only one that works'.
```

## 6. The wrong-context negative — a non-flag session

```text
a plain-visitor bot reads a plain session, not the flag-holder's.
record it: 'the bot's session is a plain visitor — the leak reads
a plain session — the flag isn't in it'.
```

## 7. The destructive-channel negative — a shared-store flood

```text
an LRU flood that evicted the secret's own key — the thing you're
trying to read.
record it: 'the LRU flood on <store> evicted the secret — the
channel is destructive — a shared store'.
```

## 8. The one-shot-spend negative — a burned check

```text
a GETDEL/single-use token's 'did it survive' burned the check.
record it: 'the one-shot token was spent — the check is consumed —
a different channel is required'.
```

## 9. The TTL negative — a secret that expired

```text
a 60s TTL — the leak+decode+submit missed the window.
record it: 'the secret's TTL is 60s — the sequential leak misses
the window — a high-bandwidth channel is required'.
```

## 10. The rate-cap negative — a flood that won't fit

```text
thousands of markers need tens-hundreds rps — a flat throughput cap
makes the attack impossible.
record it: 'the rate cap is <N> rps — the <channel> channel needs
<M> markers — infeasible'.
```

## 11. The reconstruction negative — a beam-search miss

```text
an n-gram set that doesn't cover the secret's transitions — a gap
the beam can't cross.
record it: 'the n-gram set misses the <transition> — widen the
marker set'.
```

## 12. The confusable negative — a real read, not a measure

```text
a JSONP endpoint, a postMessage broadcast, a `*` ACAO — a real read
primitive, not a measure.
record it: 'the channel returns the DATA, not a bit — a real read
primitive — a CORS/JSONP question, not an XS-leak'.
```

## 13. The selector-mismatch negative — a text-node secret

```text
a CSS attribute-selector needs the secret IN an attribute — a
secret in TEXT content doesn't match.
record it: 'the secret is in text, not an attribute — a @font-face
unicode-range reads the rendered text instead'.
```

## 14. The dead-surface negative — no channel at all

```text
a sealed shape with NO CSS oracle (no attribute, no font wildcard)
AND NO server-state channel (no redis, no counter, no token, no
rate-limit) → the oracle surface is dead.
record it: 'the sealed surface is dead — no CSS oracle, no server-
state channel — a different class'.
```
