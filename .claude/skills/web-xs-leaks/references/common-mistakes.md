# Common mistakes — the ways XS-leak analysis goes wrong

Each a real failure mode: what it looks like, why it fails, the fix.

---

## 1. "the oracle exists" ≠ "the secret is read"

```text
a working channel (the control pair separates) doesn't mean the
secret is leaked — the oracle must actually return the secret's
data. a channel that fires but reads nothing is a candidate, not
a confirm.
```

Fix: the confirms is the reconstructed+verified secret, not the
oracle's existence.

## 2. Skipping the control pair — the silent failure

```text
an oracle without an always-true and never-true control — a failed
run and a wrong answer look identical. 'no leak' could mean 'the
secret doesn't match' OR 'the channel is broken'.
```

Fix: always build the YES/NO control pair — it separates 'no leak'
from 'broken channel'.

## 3. The "one bit per visit" assumption — the bandwidth trap

```text
assuming the channel carries one bit per bot visit — it's only true
for a one-shot-token channel. a recency/LRU channel carries
thousands of bits; a CSS oracle's one load carries a whole char-set.
```

Fix: measure the channel's bandwidth — a high-bandwidth channel
needs far fewer visits than a one-bit one.

## 4. The SameSite=Lax cookie trap — the credentialed fetch fails

```text
the classic shape's fetch to YOUR page's cross-site request doesn't
attach a Lax cookie — the read is non-credentialed. a 'the channel
works but the data is public' failure.
```

Fix: a meta-refresh issued BY THE TARGET bypasses it — a same-site
navigation; or a sealed-shape channel that doesn't need the cookie.

## 5. The destructive-flood — an unrecorded blast radius

```text
an LRU flood that forces eviction destroys every other key in the
store — including possibly the secret you're trying to read. a
'my flood deleted the flag' failure.
```

Fix: only flood an instance that's yours alone; read the
blast_radius; check whether the secret lives in the same store.

## 6. The unverified reconstruction — a noisy-channel wrong answer

```text
a noisy channel's top candidate isn't always right — a beam-search
reconstruction over a noisy n-gram set needs a confidence check.
'I reconstructed a token' ≠ 'the token is correct'.
```

Fix: verify the reconstruction — submit it and confirm acceptance,
or check the confidence score clears a threshold.

## 7. The sealed-shape misread — assuming JS runs

```text
a bot that takes a URL but a CSP blocks all script — 'my page's JS
doesn't run' — the sealed shape is FORCED. a 'the channel works in
my browser but not the bot's' failure.
```

Fix: check the CSP + the managed policy BEFORE building — a
script-blocking CSP forces a declarative/server-state channel.

## 8. The bot's session isn't the flag-holder's — wrong context

```text
the leak reads under the BOT's session — a plain-visitor bot reads
a plain session, not the flag-holder's. 'the channel works but the
data isn't the flag' failure.
```

Fix: verify the bot carries the flag session — a flag cookie, an
admin context.

## 9. The TTL window — the leak outlives the secret

```text
a secret with a 60s TTL — the leak + reconstruction + submission
must fit in the window — a slow sequential leak misses it.
```

Fix: measure the TTL; use a high-bandwidth channel; the whole
leak+decode+submit must fit.

## 10. The rate-cap failure — the flood won't fit

```text
thousands of markers need tens-hundreds rps — a flat throughput cap
makes the attack impossible however correct it is.
```

Fix: measure the request rate first — a capped rate means a smaller
marker set or a different channel.

## 11. The 'unsafe-inline' misread — styles still run

```text
assuming 'script-src none' blocks EVERYTHING — 'unsafe-inline' in
default-src still allows STYLES — the CSS oracle works even when
script is dead.
```

Fix: read the CSP as a list of what's NOT allowed — styles and
fonts often survive a script block.

## 12. The one-shot-token spend — a burned check

```text
a GETDEL/single-use token's 'did it survive' is one bit AND burns
the check — spending it early wastes the channel.
```

Fix: spend the one-shot token LAST — after the cheaper channels
narrow the answer.

## 13. The 'the oracle fired' over-claim — a channel, not a read

```text
a channel that fired (the font loaded, the counter incremented)
isn't a leaked secret — the channel must actually return the
secret's data.
```

Fix: the confirm is the reconstructed+verified secret — the channel
is the means, not the end.

## 14. The bot-reachability — an airgapped exfil

```text
the classic shape's read-back is your listener — an airgapped bot
can't reach it. a 'the leak works but the exfil fails' failure.
```

Fix: a server-state channel, a write-back, or a DOM-writeback —
not an external exfil.

## 15. The 'the page's JS reads the oracle' confusion — the sealed case

```text
in the sealed shape, YOUR page's JS can't run — the oracle is a
declarative channel or a server-state read — not a client-side
measure.
```

Fix: name the sub-shape FIRST — classic (JS runs) vs sealed (no JS).
