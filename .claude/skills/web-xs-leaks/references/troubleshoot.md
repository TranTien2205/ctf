# Troubleshoot — when the XS-leak doesn't work

Each symptom, its cause, and the fix.

---

## 1. The oracle doesn't fire — nothing leaks

```text
cause: the control pair doesn't separate — the channel is broken
(the selector doesn't match, the font doesn't load, the counter
doesn't increment).
fix: verify the YES/NO pair — a YES hit proves the channel works;
a NO hit means the 'no leak' is a broken channel, not a negative.
```

## 2. The classic page's JS doesn't run — a CSP block

```text
cause: 'script-src none' or a managed policy — the sealed shape is
FORCED — no attacker JS anywhere.
fix: a declarative channel (CSS selector → font load) or a server-
state channel — not a client-side measure.
```

## 3. The credentialed fetch fails — a SameSite gate

```text
cause: a SameSite=Lax/Strict cookie — the bot's cross-site fetch
doesn't attach it — the read is non-credentialed.
fix: a meta-refresh issued BY THE TARGET (a same-site navigation)
or a sealed-shape channel that doesn't need the cookie cross-site.
```

## 4. The CSS oracle doesn't load — a CSP font/img gate

```text
cause: img-src 'self' blocks a bg-image exfil; font-src 'self'
(no wildcard) blocks an external font.
fix: use the FONT-SRC channel (a font load, not a bg-image) when
font-src has a host wildcard; check which directive has the hole.
```

## 5. The bot can't reach your listener — an airgapped exfil

```text
cause: the bot can't fetch attacker.com — the exfil fails even when
the leak works.
fix: a server-state channel, a write-back to the target, or a
DOM-writeback — not an external exfil.
```

## 6. The bot's session isn't the flag-holder's — wrong context

```text
cause: the bot is a plain visitor — reads a plain session, not the
flag-holder's.
fix: verify the bot's cookie — a flag cookie, an admin context.
```

## 7. The flood destroyed the secret — a destructive channel

```text
cause: an LRU flood that evicted the secret's own key — the thing
you're trying to read.
fix: check whether the secret lives in the same store; a flood
that destroys the flag is a failed channel, not a leak.
```

## 8. The one-shot token was spent early — a burned check

```text
cause: a GETDEL/single-use token's 'did it survive' is one bit AND
burns the check — spending it early wastes it.
fix: spend the one-shot token LAST — after the cheaper channels
narrow the answer.
```

## 9. The reconstruction is wrong — a noisy channel

```text
cause: a noisy channel's top candidate isn't always right — a beam
search over a noisy set needs a confidence check.
fix: verify the reconstruction — submit it, confirm acceptance, or
score it above a threshold.
```

## 10. The TTL window — the secret expired

```text
cause: a 60s TTL — the leak+decode+submit missed the window.
fix: measure the TTL; a high-bandwidth channel; the whole leak
must fit.
```

## 11. The rate-cap — the flood won't fit

```text
cause: thousands of markers need tens-hundreds rps — a flat
throughput cap makes the attack impossible.
fix: measure the rate; a smaller marker set or a different channel.
```

## 12. The managed-policy bot — a forced sealed shape

```text
cause: a Chrome managed policy (URLBlocklist ['*'] + URLAllowlist)
— the bot can ONLY visit the target's origin.
fix: a declarative/server-state channel — no attacker URL reaches
the bot.
```

## 13. The 'unsafe-inline' misread — styles still run

```text
cause: assuming 'script-src none' blocks everything — 'unsafe-inline'
in default-src still allows STYLES.
fix: read the CSP as a list of what's NOT allowed — styles/fonts
often survive a script block.
```

## 14. The reflected secret isn't in an attribute — no selector match

```text
cause: the CSS attribute-selector needs the secret IN an attribute
(data-secret, value, etc.) — a secret in text content doesn't match.
fix: find the attribute-carrier, or a different channel.
```

## 15. The n-gram set doesn't reassemble — a beam-search miss

```text
cause: the overlapping n-grams don't cover the secret — a gap in
the marker set, or a beam width too narrow.
fix: widen the marker set (all 1/2/3-grams) and the beam width.
```
