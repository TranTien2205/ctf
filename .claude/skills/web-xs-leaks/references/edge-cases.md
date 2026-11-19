# Edge cases — the XS-leak variants that break the usual assumptions

## The airgapped bot — no external listener

```text
the bot can't reach attacker.com — the classic shape's exfil fails.
fix: a server-state channel (counter/recency/token), a write-back,
a DOM-writeback, or a same-origin leak page.
```

## The managed-policy bot — a forced sealed shape

```text
Chrome managed policy — URLBlocklist ['*'] + URLAllowlist — the bot
can ONLY visit the target's origin. no attacker URL reaches it.
fix: a declarative/server-state channel — the only channel that
works under a forced sealed shape.
```

## The same-site navigation — a SameSite bypass

```text
a meta-refresh issued BY THE TARGET is a same-site navigation — it
carries the Lax cookie a cross-site fetch wouldn't. the sealed
shape's whole design avoids the cross-site cookie question.
```

## The 'unsafe-inline' style channel — a script-blocked case

```text
'script-src none' blocks JS; 'unsafe-inline' in default-src/style-src
still allows STYLES — the CSS oracle works. read the CSP for what
it does NOT block — a style/font hole is the channel.
```

## The font-src wildcard — the exfil that survives

```text
'img-src self' blocks a bg-image exfil; 'font-src self *' allows
an external font — the @font-face unicode-range channel works.
check WHICH directive has the hole.
```

## The secret in text, not an attribute — a selector mismatch

```text
a CSS attribute-selector needs the secret IN an attribute
(data-secret, value, etc.). a secret in TEXT content doesn't
match — but a unicode-range @font-face reads the rendered text.
```

## The sorted secret — the char-set IS the answer

```text
'take N random chars, sort them' → the character set fully
determines the string — a char-set oracle (unicode-range) returns
the answer directly. no ordering work needed.
```

## The n-gram gap — a beam-search miss

```text
an n-gram marker set that doesn't cover the secret's transitions —
a gap the beam can't cross. widen the marker set (all 1/2/3-grams)
and the beam width.
```

## The one-bit channel — the whole-secret question

```text
a channel that carries ONE bit can't read a multi-bit secret
directly — each query reads one bit. a 32-char secret needs ~N
queries — the feasibility arithmetic matters.
```

## The destructive channel — a shared-store flood

```text
an LRU flood on a shared store evicts OTHER keys — including the
secret. check whether the secret lives in the same store; only
flood an instance that's yours.
```

## The one-shot token — a spend-last oracle

```text
a GETDEL/single-use token's 'did it survive' burns the check —
one bit AND it's gone. spend it AFTER the cheaper channels narrow
the answer.
```

## The bot's context — a non-flag session

```text
a plain-visitor bot reads a plain session, not the flag-holder's.
verify the bot's cookie/context — a flag cookie, an admin context.
```

## The TTL window — a 60s secret

```text
a short-TTL secret: the leak+decode+submit must fit the window —
a slow sequential leak misses it. use a high-bandwidth channel.
```

## The rate-cap — a flood that won't fit

```text
thousands of markers need tens-hundreds rps — a flat throughput cap
makes the attack impossible however correct. measure the rate first.
```

## The noisy channel — a beam-search confidence

```text
a noisy channel's top candidate isn't always right — a beam search
over a noisy set needs a confidence check + a verify step (submit
the reconstruction, confirm acceptance).
```

## The postMessage broadcast — a real read, not a leak

```text
a postMessage that broadcasts data to '*' is a REAL read primitive —
not a side-channel measure. it returns the data, not a bit about it.
the boundary: a channel that returns the DATA is a read; a channel
that returns a BIT is a measure.
```

## The JSONP/XSSI serve — a real read, not a leak

```text
a JSONP endpoint serves data AS JavaScript — a script-tag read —
a real primitive. an XS-leak is only when the response is OPAQUE
and you infer it.
```

## The stored-response — a cache-poison, not a leak

```text
a cache that stores a response for a future read is a cache-poison
question — not a side-channel measure. the XS-leak is a MEASURE of
the current response's shape.
```
