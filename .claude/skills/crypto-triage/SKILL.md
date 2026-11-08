---
name: crypto-triage
description: >
  Crypto recognition router. Use at the START of any crypto challenge. Maps one
  observable in the handout to one named attack, the falsifier that rules it out
  in seconds, one `tools/crypto_attack.py` invocation, and one depth file under
  `../ctf-crypto/`. Routes; never explains the mathematics.
tags: [crypto, jeopardy, triage, recognition, rsa, ecdsa, lattice, prng, ctf]
environment: [ctf, lab]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "three named attacks tried against the same observable with no recovered secret"
    - "a recovered value fails its tag, signature or decryption check twice"
    - "the primitive is non-standard (custom proof system, compiled oracle) — park and report"
evidence_level: catalogue
---

# Crypto — Recognition Router

**Catalogue classes.** The classes routed through this file — `crypto-rsa`,
`crypto-prng`, `crypto-ecc-dlog`, `crypto-symmetric-oracle` — each carry their
own depth card and `field-notes.md`, and all are `catalogue`: nothing here has
solved one. Standard published knowledge, not local experience — never say a
technique here worked here. Promotion to `verified` happens only through a
chain card and `tools/classify_solve.py`, never by editing the taxonomy.


Not: understand the cryptosystem. Instead: read the parameters, name the attack
they allow, run it, check the secret against something the handout verifies by
itself. This file routes — open **one** file from the index, never the directory.

## First probe

Write the parameter sheet before any attack. Every row below is keyed on these
numbers, so one guessed bit length routes to the wrong attack.

```bash
ls -la ./; file ./*; sed -n '1,60p' output*.txt   # supplied files, shape of the data
python3 tools/crypto_attack.py list              # attacks available and their args
```

Record exactly: **RSA** — modulus bits, `e`, ciphertext count, repeats.
**Block cipher** — mode, block size, IV/nonce, repeats, tag. **Signatures** —
group order, count, stated nonce bits, shared `r`. **Generator** — outputs
visible, modulus, truncation. **Hash/MAC** — construction, secret length stated.

**Falsifier** — closes the whole category: the data is an *encoding*, not a cipher.
If it decodes cleanly under base64, hex, a fixed table or single-byte XOR, go to
`../ctf-misc/` and stop.

**Blast radius** — local computation, no target writes. One exception: an
*oracle* challenge means thousands of remote queries — cap concurrency, count
them against any stated budget, cache every response.

## Observable to attack to command

Read the falsifier **before** running the command. Commands are `python3
tools/crypto_attack.py <id> ...`: every id accepts `--in file.json` with its
parameters as JSON, and `describe <id>` prints the applicability bound and exact
parameter names. A `—` means no tool covers it yet — go to the depth file.

| Observable in the handout | Named attack | Falsifier (seconds, not hours) | Command |
|---|---|---|---|
| `(n,e,c)`, `e` small (3, 5, 17), one modulus, short message | Low-exponent root | no small `k` makes the integer `e`-th root of `c + k*n` exact | `eth-root --c C --e 3` (exact-root check: `nth-root`) |
| `e` small and **several** moduli over the same message | Hastad broadcast (CRT then exact root) | fewer than `e` ciphertexts, or two moduli share a factor | `hastad --pairs n1:c1,n2:c2,n3:c3` |
| One `n`, two `e`, two `c`, `gcd(e1,e2)=1` | Common modulus (extended GCD, not CRT) | the exponents share a factor — that is the `gcd(e,phi)>1` shape | `common-modulus --in file.json` |
| `e` very large — same order of magnitude as `n` | Wiener (`d < n^0.25`) | convergents run out with no valid `d`; go to Boneh-Durfee | `wiener --n N --e E` |
| A stated bound on `d` above 0.25 (`d < n^0.27`), or Wiener failed | Boneh-Durfee (`d < n^0.292`) | LLL yields no small root — the real bound exceeds 0.292 | `boneh-durfee --n N --e E`, then `boneh-durfee-escalate` |
| Top or bottom `k` of a prime's `b` bits are given | Coppersmith small roots | `k/b < 0.5`; no lattice fixes too few known bits | `coppersmith-high-bits --in file.json` |
| `p` and `q` suspiciously close for the modulus size | Fermat factorisation | `isqrt(n)^2` still far from `n` after a few thousand steps | `fermat --n N` |
| Many public keys from one generator or service | Batch GCD | every pairwise GCD is 1 | `batch-gcd --moduli moduli.txt` |
| `p-1` smooth, or the text hints "weak prime" | Pollard p-1 | the smooth bound reaches 10^7 with no factor | `pollard-pm1 --n N` |
| A **discrete log** whose group order factors into small primes | Pohlig-Hellman | the largest prime factor of the order is still huge — check first with `smoothness`, then `bsgs` | `pohlig-hellman --in file.json` |
| A discrete log in a **small** group or with a bounded exponent | Baby-step giant-step | the order is huge and unfactored — out of reach above ~2**44 | `bsgs --g G --h H --p P` |
| Two signatures sharing the same `r` | Nonce reuse → direct `d` | all `r` values are distinct | `ecdsa-nonce-reuse --in file.json` |
| Many signatures, nonce stated or inferred **short** (128-bit `k`, 256-bit order) | Hidden Number Problem lattice | bias under ~4 bits, or fewer than about `2 * order_bits / bias_bits` signatures | `hnp-ecdsa --sigs sigs.json` |
| Consecutive outputs of a linear generator, possibly truncated | LCG recovery (lattice when truncated) | the outputs break the LCG relation on the stated modulus — try MT or LFSR | `lcg-recover --in file.json`, `lcg-unknown-modulus`, `lcg-truncated` |
| A raw bit keystream, a stated register width, or stated taps | LFSR reconstruction | `2*width` consecutive bits do not predict the next bit | `berlekamp-massey --in file.json`, then `lfsr-recover` / `lfsr-predict --bits ...` |
| >=624 consecutive 32-bit outputs, or Python `random` | MT19937 state clone | fewer than 624 full words and no float or GF(2) route | `mt19937-clone --in file.json` |
| A secret-prefix MAC, `sha256(secret + message)`, Merkle-Damgard, secret **length known** | Length extension | the MAC is HMAC, or the hash is a sponge (SHA-3, BLAKE2) | `length-extension --in file.json` |
| Two ciphertexts under one keystream (CTR, OFB, stream, OTP) | Many-time pad / crib drag | the XOR of the two is unprintable under every crib | `crib-drag --ct1 HEX --in file.json` |
| The **same nonce twice under AES-GCM** | Forbidden attack — recover `H`, forge tags | the nonces differ, or one ciphertext only per nonce | — → `../ctf-crypto/modern-ciphers.md` |
| A reused CTR counter or IV with one plaintext known | Keystream recovery by XOR | no offset where both ciphertexts are defined | `crib-drag --in file.json` |
| **Unauthenticated** CBC ciphertext you can resubmit | IV / previous-block bit flipping | a MAC or tag is verified before decryption | — → `../ctf-crypto/modern-ciphers-2.md` |
| The service distinguishes bad padding from bad content | CBC padding oracle (Bleichenbacher/Manger for RSA) | error text **and** timing identical for both cases | — → `../ctf-crypto/modern-ciphers.md` |
| Repeating 16-byte ciphertext blocks | ECB pattern leak, cut-and-paste, byte-at-a-time | no two blocks repeat and the length is not a clean multiple | — → `../ctf-crypto/modern-ciphers-2.md` |
| A modulus with no other handle — always try first | factordb and small-factor sweep | `n` is a clean two-prime product absent from factordb | `fermat --n N`, then `../ctf-crypto/triage-toolbox.md` |
| Letter-only ciphertext, no key material, a named classical cipher or none | Classical cipher (Caesar/Vigenere/substitution/transposition) | statistics show encoding, not cipher — route to misc-encoding-carrier | — → class `crypto-classical` (`../crypto-classical/`) |

## Route to depth — attack family to the one file

The attacks with a tool, and the one file that documents each. Full 16-family
index: `references/attack-to-reference.md`.

| Attack you ran | The one file | Section to jump to |
|---|---|---|
| `eth-root`, `hastad`, `wiener`, `fermat`, `common-modulus`, `pollard-pm1` | `../ctf-crypto/rsa-attacks.md` | `Small Public Exponent`, `Hastad's Broadcast Attack`, `Wiener's Attack`, `RSA with Consecutive Primes`, `Common Modulus Attack`, `Pollard's p-1 Factorization` |
| `batch-gcd`, plus CRT faults, `gcd(e,phi)>1`, dp/dq leaks, ROCA | `../ctf-crypto/rsa-attacks-2.md` | `Batch GCD for Shared Prime Factoring`, `RSA-CRT Fault Attack`, `ROCA Attack` |
| `coppersmith-high-bits`, `boneh-durfee` | `../ctf-crypto/advanced-math.md` | `Coppersmith's Method (Structured Primes, LACTF 2026)`; small-`d`: `Coppersmith's Method (Close Private Keys)` — **see Known gaps** |
| `pohlig-hellman`, plus `bsgs` and Hensel lifting | `../ctf-crypto/advanced-math.md` | `Pohlig-Hellman Attack`, `Baby-Step Giant-Step for General DLP`, `Hensel's Lemma` |
| `hnp-ecdsa`, `hnp`, `lcg-truncated` | `../ctf-crypto/lattice-and-lwe.md` | `Hidden Number Problem (HNP)`, `LCG and Truncated Output as a Lattice Problem`, `Core Tools: LLL, BKZ, Babai, CVP, SVP`; read `Quick Triage` and `Common Failure Modes` first |
| `berlekamp-massey`, `lfsr-recover`, `lfsr-predict` | `../ctf-crypto/stream-ciphers.md` | `LFSR Stream Cipher Attacks` (both BM and Galois tap recovery live in it) |
| `length-extension` | `../ctf-crypto/modern-ciphers-2.md` | `Hash Length Extension Attack` |
| `ecdsa-nonce-reuse`, `mt19937-clone`, `crib-drag`, `lcg-*`, `smoothness`, `crt`, `factor-from-d`, `rsa-decrypt` | file named in the command column above | full index: `references/attack-to-reference.md` |
| No tool yet (GCM nonce reuse, CBC padding oracle, ECB cut-and-paste) | `../ctf-crypto/modern-ciphers.md`, `../ctf-crypto/modern-ciphers-2.md` | hand-roll from the depth file |

## Multi-stage ladder

Some challenges are not one attack but a **ladder**: stage *k*'s plaintext is
stage *k+1*'s key, every stage with its own authenticator. Never attack a
ladder as one monolith.

1. **Enumerate the stages before attacking any** — each one's key name,
   nonce/ciphertext/tag triple, and what derives its key. Ten small named
   attacks is a two-hour job; one opaque blob is a lost day.
2. **Expect only the first stage to show cleartext parameters** — later ones
   sit inside the blobs, so enumerate the *skeleton* (stage count and shape);
   each decryption hands you the next parameter sheet.
3. **Build the derivation graph and mark the decoys** — a blob no recovered key
   decrypts, and from which no later key derives, is padding.
4. **Classify each stage independently** — in isolation almost every stage is a
   textbook attack.
5. **Use the authenticator as the per-stage oracle** — a verified tag *is* the
   proof the key is right; call a stage solved only once its tag verifies.
6. **Take the free stages first, park the expensive one in the background** —
   lattice stages run for minutes and escalate a parameter.
7. **Expect two attacks inside one stage** — read the final derivation rather
   than guessing it; the order and the *subset* of secrets come from the
   generator.

CSCV2026's `TYPHON`: twelve Greek-keyed stages, only the first exposing
parameters, chaining truncated LCG → Hastad → Wiener → GCM nonce reuse → LFSR →
Pohlig-Hellman → SHA-256 length extension → ECDSA-HNP → Boneh-Durfee →
Coppersmith. Nothing novel; slow only because every attack was written from
scratch mid-contest.

## Probe rules

- Parameter sheet first. A named attack on a guessed bit length is wasted budget.
- One attack per observable, cheapest first, falsifier read before the run. If
  the falsifier holds, cross the row out — do not tune its parameters.
- A recovered value is a **hypothesis** until it decrypts, verifies a tag or
  matches a supplied artifact. Only then is it evidence.
- Three named attacks and nothing recovered means the observable was misread:
  return to the parameter sheet, not a fourth attack (`../LOOP_DISCIPLINE.md`).
- A missing optional dependency (`fpylll`, `sympy`, `mpmath`) is a *tool*
  failure, not a failed attack — take the fallback, never reclassify.
- Record every solve in the class's own `field-notes.md` (`proposed` until
  reviewed). See `../../LEARNING_LOOP.md`.

## Known gaps

- **Boneh-Durfee has no depth file.** Nearest is `../ctf-crypto/advanced-math.md`
  `Coppersmith's Method (Close Private Keys)` — the same small-`d` lattice
  family. Use `boneh-durfee --help` and record what worked in `field-notes.md`.
- **A custom proof system or compiled oracle** — PLONK/KZG verifier, Poseidon
  behind a shipped `.so`, query-budgeted HSM — is not a standard shape. Say so,
  then route to `../ctf-crypto/zkp-and-advanced.md` plus `../rev-triage/`.
