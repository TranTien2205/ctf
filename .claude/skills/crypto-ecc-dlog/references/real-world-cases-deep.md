# Real-world cases deep — the attacks that left the lab

## PlayStation 3 ECDSA (2010) — the canonical reuse

Sony signed firmware with a **constant `k`**. Two signatures, same `r`,
closed-form `d` — the master key leaked and custom firmware became
possible. The exact shape `ecdsa-nonce-reuse` automates.

## Android `SecureRandom` (2013) — reuse at scale

A broken RNG produced the **same `k`** across independent Bitcoin
transactions. Attackers scraped the blockchain for duplicate `r`s and
drained wallets — the `r`-dedupe check, industrialized.

## Minerva (2019) — the biased-nonce research

Timing side-channels leaked a few bits of `k` per ECDSA signature on
smartcards/crypto libraries. `hnp-ecdsa`-style lattice recovery with
~dozens of signatures and a small bound — the `required_signatures` math
is exactly what made a tiny leak sufficient.

## LadderLeak (2019) — 1-bit leaks

A single bit of `k` per signature, many signatures — `hnp` with `B = 2`
on the leaked part. The theoretical edge of the same attack.

## Safe-prime groups — the designed resistance

TLS `modp` groups (`p-1 = 2q`) exist precisely to kill `pohlig-hellman`.
Early DH mistakes (smooth `p-1`) are why. If a CTF challenge gives a
safe-prime order, the bug is *not* the math.

## The pattern

The same 6 shapes repeat: reuse, bias, leak, smooth order, bounded
exponent, defect curve. CTF challenges are these stories compressed.
