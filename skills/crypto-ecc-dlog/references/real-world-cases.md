# Real-world cases — where these attacks showed up outside CTF

## PlayStation 3 (2010)

Sony's ECDSA used a **static nonce `k`** — the textbook `ecdsa-nonce-reuse`:
two signatures, same `r`, `d` recovered in closed form, master key leaked,
custom firmware possible. The canonical example the CTF shape mirrors.

## Android `SecureRandom` (2013)

Broken RNG produced **repeated `k`** in Bitcoin ECDSA signatures — same
attack, mass key theft from wallets.

## Nonce-bias in TLS/SSH implementations

`hnp-ecdsa`-style biased nonces (e.g. short `k`, MSB-leaked `k`) recovered
private keys across real deployments — the "Minerva" and "LadderLeak"
lines of research. The lattice count math `2·order_bits/leaked_bits` is what
made small leaks sufficient.

## Safe-prime vs smooth-prime choices

DH groups with `p-1` smooth (early `modp` mistakes) fell to `pohlig-hellman`;
the `p-1 = 2q` safe-prime convention exists precisely to kill it.

## The moral

These are not exotic bugs — they're the same 6 shapes on repeat: nonce
reuse, biased nonce, smooth order, bounded exponent, anomalous/singular
curve, invalid point. A CTF challenge is almost always one of them.
