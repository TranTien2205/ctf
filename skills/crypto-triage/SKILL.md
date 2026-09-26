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

Not: understand the cryptosystem. Instead: read the parameters, name the attack they allow,
run it, check the recovered secret against something the handout verifies by itself. This
file routes — open **one** file from the index, never the directory.

## First probe

Write the parameter sheet before any attack. Every row below is keyed on these
numbers, so one guessed bit length routes to the wrong attack.

```bash
ls -la ./; file ./*; sed -n '1,60p' output*.txt   # supplied files, shape of the data
python3 tools/crypto_attack.py --list            # attacks available and their args
```

Record exactly: **RSA** — modulus bits, `e`, ciphertext count, repeated modulus or
message. **Block cipher** — mode, block size, IV/nonce, repeated blocks or nonces, tag
present. **Signatures** — group order, count, stated nonce bits, shared `r`.
**Generator** — outputs visible, modulus, truncated. **Hash/MAC** — construction, and
whether the secret length is stated.

**Falsifier** — closes the whole category: the data is an *encoding*, not a cipher.
If it decodes cleanly under base64, hex, a fixed table or single-byte XOR, go to
`../ctf-misc/` and stop.

**Blast radius** — local computation, no target writes. One exception: an *oracle*
challenge (padding, LSB, chosen-ciphertext service) means thousands of remote queries
— cap concurrency, count them against any stated budget, cache every response.

## Observable to attack to command

Read the falsifier **before** running the command. Commands are short for `python3
tools/crypto_attack.py <name> ...` (`--help` for arg shapes); a `—` means no tool covers
it yet, so go to the depth file and hand-roll.

| Observable in the handout | Named attack | Falsifier (seconds, not hours) | Command |
|---|---|---|---|
| `(n,e,c)`, `e` small (3, 5, 17), one modulus, short message | Low-exponent root | no small `k` makes the integer `e`-th root of `c + k*n` exact | `integer_nth_root --value C --n 3 --modulus N` |
| `e` small and **several** moduli over the same message | Hastad broadcast (CRT then exact root) | fewer than `e` ciphertexts, or two moduli share a factor | `hastad_broadcast --pairs n1:c1,n2:c2,n3:c3 --e 3` |
| One `n`, two `e`, two `c`, `gcd(e1,e2)=1` | Common modulus (extended GCD, not CRT) | the exponents share a factor — that is the `gcd(e,phi)>1` shape | — → `../ctf-crypto/rsa-attacks.md` |
| `e` very large — same order of magnitude as `n` | Wiener (`d < n^0.25`) | convergents run out with no valid `d`; go to Boneh-Durfee | `wiener --n N --e E` |
| A stated bound on `d` above 0.25 (`d < n^0.27`), or Wiener failed | Boneh-Durfee (`d < n^0.292`) | LLL at `m=6..8` yields no small root — the real bound exceeds 0.292 | `boneh_durfee --n N --e E --delta 0.27 --m 6` |
| Top or bottom `k` of a prime's `b` bits are given | Coppersmith small roots | `k/b < 0.5`; no lattice fixes too few known bits | `coppersmith_known_high_bits --n N --known A --known-bits 128 --p-bits 256` |
| `p` and `q` suspiciously close for the modulus size | Fermat factorisation | `isqrt(n)^2` still far from `n` after a few thousand steps | `fermat_factor --n N` |
| Many public keys from one generator or service | Batch GCD | every pairwise GCD is 1 | `batch_gcd --file moduli.txt` |
| `p-1` smooth, or the text hints "weak prime" | Pollard p-1 | the smooth bound reaches 10^7 with no factor | — → `../ctf-crypto/rsa-attacks.md` |
| A **discrete log** whose group order factors into small primes | Pohlig-Hellman | the largest prime factor of the order is still huge — use BSGS instead | `pohlig_hellman --p P --g G --h H` |
| Two signatures sharing the same `r` | Nonce reuse → direct `d` | all `r` values are distinct | — → `../ctf-crypto/ecc-attacks.md` |
| Many signatures, nonce stated or inferred **short** (128-bit `k`, 256-bit order) | Hidden Number Problem lattice | bias under ~4 bits, or fewer than about `2 * order_bits / bias_bits` signatures | `hnp_ecdsa_biased_nonce --sigs sigs.json --order N --nonce-bits 128` |
| Consecutive outputs of a linear generator, possibly truncated | LCG recovery (lattice when truncated) | the outputs break the LCG relation on the stated modulus — try MT or LFSR | `lcg_recover --outputs o1,o2,... --modulus M` |
| A raw bit keystream, a stated register width, or stated taps | LFSR reconstruction | `2*width` consecutive bits do not predict the next bit | `berlekamp_massey --bits 0101...`, then `lfsr_reconstruct --bits ... --width 32 --taps 32,30,26,24` |
| >=624 consecutive 32-bit outputs, or Python `random` | MT19937 state clone | fewer than 624 full words and no float or GF(2) route | — → `../ctf-crypto/prng.md` |
| A secret-prefix MAC, `sha256(secret + message)`, Merkle-Damgard, secret **length known** | Length extension | the MAC is HMAC, or the hash is a sponge (SHA-3, BLAKE2) | `length_extension --hash sha256 --mac HEX --secret-len 32 --orig MSG --append SUFFIX` |
| Two ciphertexts under one keystream (CTR, OFB, stream, OTP) | Many-time pad / crib drag | the XOR of the two is unprintable under every crib | — → `../ctf-crypto/classic-ciphers.md` |
| The **same nonce twice under AES-GCM** | Forbidden attack — recover `H`, forge tags | the nonces differ, or one ciphertext only per nonce | — → `../ctf-crypto/modern-ciphers.md` |
| A reused CTR counter or IV with one plaintext known | Keystream recovery by XOR | no offset where both ciphertexts are defined | — → `../ctf-crypto/modern-ciphers.md` |
| **Unauthenticated** CBC ciphertext you can resubmit | IV / previous-block bit flipping | a MAC or tag is verified before decryption | — → `../ctf-crypto/modern-ciphers-2.md` |
| The service distinguishes bad padding from bad content | CBC padding oracle (Bleichenbacher/Manger for RSA) | error text **and** timing identical for both cases | — → `../ctf-crypto/modern-ciphers.md` |
| Repeating 16-byte ciphertext blocks | ECB pattern leak, cut-and-paste, byte-at-a-time | no two blocks repeat and the length is not a clean multiple | — → `../ctf-crypto/modern-ciphers-2.md` |
| A modulus with no other handle — always try first | factordb and small-factor sweep | `n` is a clean two-prime product absent from factordb | `fermat_factor`, then `../ctf-crypto/triage-toolbox.md` |

## Route to depth — attack family to the one file

The attacks with a tool, and the one file that documents each. Full 16-family index,
with every `##` section name verified against the corpus:
`references/attack-to-reference.md`.

| Attack you ran | The one file | Section to jump to |
|---|---|---|
| `integer_nth_root`, `hastad_broadcast`, `wiener`, `fermat_factor`, common modulus, Pollard p-1 | `../ctf-crypto/rsa-attacks.md` | `Small Public Exponent`, `Hastad's Broadcast Attack`, `Wiener's Attack`, `RSA with Consecutive Primes`, `Common Modulus Attack`, `Pollard's p-1 Factorization` |
| `batch_gcd`, plus CRT faults, `gcd(e,phi)>1`, dp/dq leaks, ROCA | `../ctf-crypto/rsa-attacks-2.md` | `Batch GCD for Shared Prime Factoring`, `RSA-CRT Fault Attack`, `ROCA Attack` |
| `coppersmith_known_high_bits`, `boneh_durfee` | `../ctf-crypto/advanced-math.md` | `Coppersmith's Method (Structured Primes, LACTF 2026)`; small-`d`: `Coppersmith's Method (Close Private Keys)` — **see Known gaps** |
| `pohlig_hellman`, plus BSGS and Hensel lifting | `../ctf-crypto/advanced-math.md` | `Pohlig-Hellman Attack`, `Baby-Step Giant-Step for General DLP`, `Hensel's Lemma` |
| `hnp_ecdsa_biased_nonce`, `lcg_recover` when truncated | `../ctf-crypto/lattice-and-lwe.md` | `Hidden Number Problem (HNP)`, `LCG and Truncated Output as a Lattice Problem`, `Core Tools: LLL, BKZ, Babai, CVP, SVP`; read `Quick Triage` and `Common Failure Modes` first |
| `berlekamp_massey`, `lfsr_reconstruct` | `../ctf-crypto/stream-ciphers.md` | `LFSR Stream Cipher Attacks` (both BM and Galois tap recovery live in it) |
| `length_extension` | `../ctf-crypto/modern-ciphers-2.md` | `Hash Length Extension Attack` |
| No tool yet (GCM/CTR nonce reuse, padding oracle, ECB, MT19937, many-time pad, ECDSA `r` reuse) | file named in the command column above | full index: `references/attack-to-reference.md` |

## Multi-stage ladder

Some challenges are not one attack but a **ladder**: stage *k*'s recovered plaintext is
stage *k+1*'s key, and every stage carries its own authenticator (a GCM tag, an HMAC, a
signature). Never attack a ladder as one monolith.

1. **Enumerate the stages before attacking any.** List each one: key name, its
   nonce/ciphertext/tag triple, what derives its key. Ten small named attacks is a
   two-hour job; one opaque blob is a lost day.
2. **Expect only the first stage to show cleartext parameters.** Later ones sit inside
   the blobs, so you enumerate the *skeleton* — stage count and shape — not the
   numbers; each decryption hands you the next parameter sheet.
3. **Build the derivation graph and mark the decoys.** A blob no recovered key
   decrypts, and from which no later key derives, is padding — decide that from the
   graph, not from how hard the blob looks.
4. **Classify each stage independently** against the table above; in isolation almost
   every stage is a textbook attack.
5. **Use the authenticator as the per-stage oracle.** A verified tag *is* the proof the
   key is right, so a mismatch localises to one stage instead of poisoning everything
   below it — call a stage solved only once its tag verifies.
6. **Take the free stages first** (one that only parses a log or config proves the
   harness works) and **park the expensive one in the background**: lattice stages run
   for minutes and escalate a parameter.
7. **Expect two attacks inside one stage**, and read the final derivation rather than
   guessing it: usually a concatenation and a hash, but the order and the *subset* of
   secrets come from the generator.

CSCV2026's `TYPHON`: twelve Greek-keyed stages, only the first exposing parameters,
chaining truncated LCG → Hastad → Wiener → GCM nonce reuse → LFSR → Pohlig-Hellman →
SHA-256 length extension → log parse → config parse → ECDSA-HNP → Boneh-Durfee →
Coppersmith, master key hashing seven of the recovered secrets, not all. Nothing novel;
slow only because every attack was written from scratch mid-contest.

## Probe rules

- Parameter sheet first. A named attack on a guessed bit length is wasted budget.
- One attack per observable, cheapest first, falsifier read before the run. If the
  falsifier holds, cross the row out — do not tune its parameters.
- A recovered value is a **hypothesis** until it decrypts something, verifies a tag or
  matches a supplied artifact. Only then is it evidence.
- Three named attacks and nothing recovered means the observable was misread: return to
  the parameter sheet, not a fourth attack (`../LOOP_DISCIPLINE.md`).
- A missing optional dependency (`fpylll`, `sympy`, `pycryptodome`, `mpmath`) is a
  *tool* failure, not a failed attack — take the fallback, never reclassify.
- Record every solve in `field-notes.md` here (`proposed` until reviewed against a
  chain card). See `../../LEARNING_LOOP.md`.

## Known gaps

- **Boneh-Durfee has no depth file.** The string appears nowhere in `../ctf-crypto/`.
  Nearest is `../ctf-crypto/advanced-math.md` `Coppersmith's Method (Close Private Keys)` — the same
  small-`d` lattice family, not the Boneh-Durfee construction. Use
  `boneh_durfee --help` and record what worked in `field-notes.md`.
- **A custom proof system or compiled oracle** — a PLONK/KZG verifier with circuit
  selectors, a Poseidon permutation behind a shipped `.so`, a query-budgeted HSM — is
  not a standard shape and this router does not cover it. Say so, then route to
  `../ctf-crypto/zkp-and-advanced.md` plus `../rev-triage/`. CSCV2026's
  `baby_circuit` was this shape and is still unsolved here.
