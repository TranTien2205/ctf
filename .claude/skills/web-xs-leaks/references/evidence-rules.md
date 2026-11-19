# Evidence rules — what counts as a confirmed XS-leak

The proof standard for the class — what a confirm actually requires.

---

## 1. The candidate-vs-confirm split — the whole distinction

```text
a CANDIDATE — a channel that fired, a reconstructed secret, a
classifier match, a chain-card match. a HYPOTHESIS, not a finding.

a CONFIRM — the reconstructed + VERIFIED secret: submit it, confirm
acceptance, or a confidence score above a threshold. the channel
is the means; the verified secret is the confirm.
```

## 2. The channel-fire is NOT the confirm

```text
'the oracle fired' (the font loaded, the counter incremented, the
background fetched) is a WORKING CHANNEL — not a leaked secret. the
channel must actually return the secret's data — the reconstructed
+ verified secret is the confirm.
```

## 3. The control-pair requirement — the channel-proof

```text
a side-channel is NOISY — a failed run and a negative answer look
identical without controls. the always-true control proves the
channel works; the never-true control proves 'no leak' isn't a
broken channel. a leak without a control pair is uninterpretable.
```

## 4. The verify-the-secret requirement — the confirm standard

```python
# the reconstructed secret is a CANDIDATE until verified:
# - submit it → confirm acceptance
# - check the confidence score clears a threshold
```

```text
a reconstructed token that doesn't verify is a candidate — the
confirm is the verified submission.
```

## 5. The sorted-secret shortcut — the char-set direct answer

```text
a sorted secret's character-set fully determines it — the set IS
the answer — a char-set oracle's output is the verified secret
(no ordering work needed). an unsorted secret's set needs a beam
reconstruction + a verify.
```

## 6. The negative-result discipline — a dead channel is a finding

```text
a control pair that doesn't separate → the channel is broken —
a proved negative, not a 'no leak'. record it — the broken channel
narrows the search as much as a working one.
```

## 7. The blast-radius record — a destructive channel

```text
an LRU flood that evicts the secret's own key is a FAILED channel —
record it — the flood's blast radius is a finding about the channel,
not just a failed attempt.
```

## 8. The feasibility record — a channel's bandwidth

```text
a channel's bits-per-visit × the visit count × the rate cap = the
feasibility arithmetic — record it — a channel that's infeasible
(too few bits, too slow, too short a TTL) is a finding.
```

## 9. The bot-context record — whose session the leak reads

```text
the leak reads under the BOT's session — record whose session the
bot carries — a flag-holder cookie, an admin context, or a plain
visitor. a leak that reads the wrong session is a candidate, not
the answer.
```

## 10. The confusable record — is it really a measure

```text
a channel that returns the DATA (JSONP, postMessage '*', a `*` ACAO)
is a real READ PRIMITIVE — not a measure. record which shape you
have — a real read is a CORS/JSONP question, not an XS-leak.
```

## 11. The flag gate — the final standard

```text
a flag counts ONLY when read from a live response or a supplied
artifact — a flag-shaped string that hasn't passed
`hooks.py pre-flag` is a candidate. the XS-leak's confirm is the
verified secret that reads the flag — not the channel's existence.
```

## 12. The falsifier record — when the surface is dead

```text
a sealed shape with no CSS oracle AND no server-state channel —
the oracle surface is dead → a different class. record the
measurement — the dead channel is a finding, not a failure.
```
