# Error analysis — what the XS-leak's failures mean

Each failure mode, what it tells you, and the next move.

---

## 1. The YES control doesn't fire — the channel is broken

```text
an always-true condition that doesn't fire → the channel itself is
dead (the selector doesn't match, the font doesn't load, the
counter doesn't increment). fix the channel before the secret.
```

## 2. The NO control fires — a false-positive channel

```text
a never-true condition that fires → the channel is noisy or matches
ambient state — the 'leak' is a false positive. fix the channel's
discrimination before the secret.
```

## 3. The classic page's JS doesn't run — a CSP block

```text
'script-src none' or a managed policy → the sealed shape is forced.
a declarative channel (CSS → font load) or a server-state channel.
```

## 4. The credentialed fetch fails — a SameSite gate

```text
a Lax/Strict cookie doesn't ride a cross-site fetch — the read is
non-credentialed. a same-site navigation (a meta-refresh issued by
the target) or a sealed-shape channel.
```

## 5. The CSS oracle doesn't load — a CSP font/img gate

```text
img-src 'self' blocks a bg-image exfil; font-src 'self' (no wildcard)
blocks an external font. check WHICH directive has the hole — a
font-src 'self' * is the @font-face channel.
```

## 6. The bot can't reach your listener — an airgapped exfil

```text
a bot that can't fetch attacker.com — a server-state channel, a
write-back, or a DOM-writeback — not an external exfil.
```

## 7. The bot's session isn't the flag-holder's — wrong context

```text
a plain-visitor bot reads a plain session, not the flag-holder's.
verify the bot's cookie — a flag cookie, an admin context.
```

## 8. The flood destroyed the secret — a destructive channel

```text
an LRU flood evicted the secret's own key — the thing you're trying
to read. only flood an instance that's yours alone.
```

## 9. The one-shot token was spent early — a burned check

```text
a GETDEL/single-use token's 'did it survive' burns the check — one
bit AND it's gone. spend it LAST.
```

## 10. The reconstruction is wrong — a noisy channel

```text
a noisy channel's top candidate isn't always right — a beam search
over a noisy set needs a confidence check + a verify step.
```

## 11. The TTL window — the secret expired

```text
a 60s TTL — the leak+decode+submit missed the window. a high-
bandwidth channel; the whole leak must fit.
```

## 12. The rate-cap — a flood that won't fit

```text
thousands of markers need tens-hundreds rps — a flat throughput cap
makes the attack impossible. a smaller marker set or a different
channel.
```

## 13. The managed-policy bot — a forced sealed shape

```text
URLBlocklist ['*'] + URLAllowlist — the bot can ONLY visit the
target's origin. a declarative/server-state channel — the only
channel that works.
```

## 14. The reflected secret isn't in an attribute — a selector mismatch

```text
a CSS attribute-selector needs the secret IN an attribute — a
secret in TEXT content doesn't match. a unicode-range @font-face
reads the rendered text instead.
```

## 15. The n-gram set doesn't reassemble — a beam-search miss

```text
a gap in the n-gram coverage — a transition the markers don't
cover. widen the marker set (all 1/2/3-grams) and the beam width.
```

## 16. The 'the oracle fired' over-claim — a channel, not a read

```text
a channel that fired isn't a leaked secret — the channel must
actually return the secret's data. the confirm is the reconstructed
+ verified secret.
```

## 17. The 'one bit per visit' assumption — a bandwidth misread

```text
assuming a channel carries one bit — a recency channel carries
thousands; a CSS oracle's one load carries a whole char-set.
measure the bandwidth.
```

## 18. The sorted-secret misread — an ordering assumption

```text
assuming a char-set gives the secret — only true for a SORTED
secret. an unsorted secret needs an n-gram/beam reconstruction.
```
