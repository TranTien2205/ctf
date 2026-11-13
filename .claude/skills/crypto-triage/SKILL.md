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
| One `(n,e)`, **two** ciphertexts of linearly-related plaintexts (`m2 = a*m1 + b`, counter/prefix padding) | Franklin-Reiter — polynomial GCD over Z/n | gcd is not linear, meaning the relation is not what was claimed — or a non-invertible coefficient splits `n` (tool reports the factor) | `python3 tools/crypto/franklin_reiter.py --n N --e 3 --a 1 --b B --c1 C1 --c2 C2` |
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
| An EC discrete log (Q = k·P) where **#E(F_p) == p** ("anomalous", or count is stated) | Smart / Semaev-Araki-Satoh — p-adic lift, dlog in seconds | `#E != p` — route to pohlig-hellman/bsgs instead | `python3 tools/crypto/smart_attack.py --p P --a A --b B --gx X --gy Y --qx X --qy Y --order N` |
| An EC discrete log where the cubic's **discriminant is 0** (singular curve, `4a^3+27b^2 == 0`, "not really an EC") | Singular-curve collapse — cusp maps to F_p additive, node to F_p\* multiplicative dlog | discriminant nonzero — real curve, back to pohlig-hellman/bsgs/smart_attack | `python3 tools/crypto/singular_ec.py --p P --a1 A --a0 B --gx X --gy Y --qx X --qy Y` |
| `java.util.Random` output (`nextInt`), or a 48-bit LCG leaking only its top 32 bits | Truncated LCG (modulus `2^48`, `a=0x5DEECE66D`, `c=0xB`, `low_bits=16`) | outputs are bounded `nextInt(n)` — rejection-sampled, not a clean truncation | `lcg-truncated --in file.json` with those constants; needs 3+ full `nextInt()` outputs |
| Consecutive outputs of a linear generator, possibly truncated | LCG recovery (lattice when truncated) | the outputs break the LCG relation on the stated modulus — try MT or LFSR | `lcg-recover --in file.json`, `lcg-unknown-modulus`, `lcg-truncated` |
| A raw bit keystream, a stated register width, or stated taps | LFSR reconstruction | `2*width` consecutive bits do not predict the next bit | `berlekamp-massey --in file.json`, then `lfsr-recover` / `lfsr-predict --bits ...` |
| >=624 consecutive 32-bit outputs, or Python `random` | MT19937 state clone | fewer than 624 full words and no float or GF(2) route | `mt19937-clone --in file.json` |
| >=4 consecutive 32-bit outputs of a stated xorshift128 (XOR+shift only) | GF(2) linear state recovery — every output bit is an XOR-subset of the 128 state bits | outputs fail the regeneration check — wrong variant; xorshift128+/xoroshiro128+ (V8 `Math.random`) add words with INTEGER addition, carry makes it nonlinear, needs SAT | `python3 tools/crypto/xorshift128.py --outs o1,o2,o3,o4` |
| A secret-prefix MAC, `sha256(secret + message)`, Merkle-Damgard, secret **length known** | Length extension | the MAC is HMAC, or the hash is a sponge (SHA-3, BLAKE2) | `length-extension --in file.json` |
| Two ciphertexts under one keystream (CTR, OFB, stream, OTP) | Many-time pad / crib drag | the XOR of the two is unprintable under every crib | `crib-drag --ct1 HEX --in file.json` |
| The **same nonce twice under AES-GCM** | Forbidden attack — recover `H`, forge tags | the nonces differ, or one ciphertext only per nonce | `python3 tools/gcm_nonce.py recover --ct1 HEX --tag1 HEX --ct2 HEX --tag2 HEX` then `forge --ct HEX --tag HEX --h HEX --new-ct HEX` |
| A reused CTR counter or IV with one plaintext known | Keystream recovery by XOR | no offset where both ciphertexts are defined | `crib-drag --in file.json` |
| **Unauthenticated** CBC ciphertext you can resubmit | IV / previous-block bit flipping | a MAC or tag is verified before decryption | `python3 tools/cbc_bitflip.py --ct HEX --known ORIG --want NEW --at OFF` (offset <16 lands in the IV — `--iv` + `--inject` instead) → `../ctf-crypto/modern-ciphers-2.md` |
| The service distinguishes bad padding from bad content | CBC padding oracle (Bleichenbacher/Manger for RSA) | error text **and** timing identical for both cases | `python3 tools/pad_oracle.py --ct HEX --url 'http://t/dec?ct={CT}' --ok-status 200` |
| Repeating 16-byte ciphertext blocks | ECB pattern leak, cut-and-paste, byte-at-a-time | no two blocks repeat and the length is not a clean multiple | `python3 tools/ecb_oracle.py --url 'http://t/e?d={PT}' shape` then `crack` for an appended secret |
| A modulus with no other handle — always try first | factordb and small-factor sweep | `n` is a clean two-prime product absent from factordb | `fermat --n N`, then `../ctf-crypto/triage-toolbox.md` |
| Letter-only ciphertext, no key material, a named classical cipher or none | Classical cipher (Caesar/Vigenere/substitution/transposition) | statistics show encoding, not cipher — route to misc-encoding-carrier | — → class `crypto-classical` (`../crypto-classical/`) |
| A bare hash string to crack ("find the password/preimage") | format identification first — salted formats change everything | `tools/hash_id.py` names family + hashcat mode + first move; an unrecognised result routes to enc_detect | `python3 tools/hash_id.py <hash>` |
| An encrypted `.zip` ("extract the flag", password unknown) | ZipCrypto dictionary attack — flag bit 0 set, 12-byte check header | flag bit 3 check byte or AES entries | `python3 tools/zip_crack.py secret.zip words.txt` (12-byte check rejects a wrong password before any decompress) |
| A `.crt`/`.pem` certificate or public-key file | field mining first (flag in subject/SAN/serial), then key analysis | all fields ordinary AND the key is strong — the file is a carrier, not the puzzle | `python3 tools/cert_info.py cert.pem` — names, SANs, validity, key kind/bits, sig algorithm, weak-key notes; an RSA key under 1024 bits routes to `fermat`/`batch-gcd` rows |
|| A binary ciphertext blob, no key, XOR-looking (high-byte or key-period hints) | Repeating-key XOR crack (hamming key-length, per-column single-byte) | no key length decodes to language — it is a cipher, not XOR | `python3 tools/xor_solve.py crack --hex HEX` (`single` for one-byte pads; `cipher_id` if it is letters) |
|| A `.pgp`/`.gpg`/`.asc` blob (OpenPGP packet data, `gpg --list-packets` absent) | packet inventory first — public key? signature? encrypted message? | packets all encrypted AND no weak-alg or short-key named | `python3 tools/pgp_parse.py file.pgp` (`--armor` for ASCII armor) — packet types, key alg/bits, user IDs, issuer keyids; an RSA key under 1024 bits routes to `fermat`, a known keyid to `search_facts`/writeup |
| The service decrypts your RSA ciphertext and leaks one bit (parity, `< n/2`, last byte) | Parity oracle — interval halving, ~log2(n) queries | one probe returns identical output for a known-even and known-odd plaintext | `python3 tools/parity_oracle.py --n HEX --e 65537 --ct HEX --url 'http://t/d?ct={CT}' --ok-regex 'odd|1'` |
| The service says only "PKCS#1 padding **valid**/invalid" (`00 02` prefix, verbose error or status split) | Bleichenbacher '98 — interval-set narrowing over the PKCS conformance oracle | one probe where a definitely-nonconforming ciphertext (e.g. `1`) answers the same as a conforming one — the signal is not padding | `python3 tools/bleichenbacher.py --n HEX --e 65537 --ct HEX --url 'http://t/d?ct={CT}' --ok-regex 'valid|ok' --neg-regex 'invalid|bad'` |
| `k` of `n` shares `(x, y)` plus a stated prime, "reconstruct the secret" | Shamir combine — mod-p Lagrange at 0 | shares come in different moduli or one share is corrupt (combine twice with a different subset and compare) | `python3 tools/crypto/shamir.py --p P --shares '1:y1,2:y2,3:y3'` |
| A weight list + target sum ("subset", "knapsack", "pick items") | Lagarias-Odlyzko lattice | density n/log2(max) >= 0.64 — tool reports it rather than trying | `python3 tools/crypto/subsetsum.py --weights '...' --sum S` |

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
| `gcm_nonce.py` recover/forge, `pad_oracle.py`, `ecb_oracle.py`, `cbc_bitflip.py` | `../ctf-crypto/modern-ciphers.md`, `../ctf-crypto/modern-ciphers-2.md` | `Forbidden attack`, `Padding oracle`, `Byte-at-a-time` sections |

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
