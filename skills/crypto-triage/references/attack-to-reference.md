# Attack family to the one depth file

Full index for `../SKILL.md`. Every file path and every `##` section name below was
verified to exist in `../../ctf-crypto/` (24 files, 448 KB) — not guessed. Paths are
written in full, relative to this file.

Open **one** file and jump straight to the named section. If the section name has
drifted, re-derive the index with:

```bash
for f in skills/ctf-crypto/*.md; do echo "## $f"; grep -n '^## ' "$f"; done
```

| Attack you named | The one file | Section to jump to |
|---|---|---|
| Low-exponent root, Hastad broadcast, common modulus, Wiener, Pollard p-1, Fermat, multi-prime | `../../ctf-crypto/rsa-attacks.md` | `Small Public Exponent`, `Hastad's Broadcast Attack` (padded: `...with Linear Padding`), `Common Modulus Attack`, `Wiener's Attack`, `Pollard's p-1 Factorization`, `RSA with Consecutive Primes` |
| Batch GCD, CRT faults, `gcd(e,phi)>1`, dp/dq leaks, ROCA, RSA oracles | `../../ctf-crypto/rsa-attacks-2.md` | `Batch GCD for Shared Prime Factoring`, `RSA-CRT Fault Attack`, `ROCA Attack` |
| Coppersmith small roots, partially known primes, small private exponent by lattice | `../../ctf-crypto/advanced-math.md` | `Coppersmith's Method (Structured Primes, LACTF 2026)`; small-`d`: `Coppersmith's Method (Close Private Keys)` — **see Known gaps** |
| Pohlig-Hellman, BSGS, Hensel lifting, GF(2)[x] | `../../ctf-crypto/advanced-math.md` | `Pohlig-Hellman Attack`, `Baby-Step Giant-Step for General DLP`, `Hensel's Lemma` |
| HNP, LWE, truncated LCG as a lattice, knapsack, and the LLL/BKZ/Babai recipes | `../../ctf-crypto/lattice-and-lwe.md` | `Hidden Number Problem (HNP)`, `LCG and Truncated Output as a Lattice Problem`, `Core Tools: LLL, BKZ, Babai, CVP, SVP`; read `Quick Triage` and `Common Failure Modes` first |
| ECDSA/DSA nonce reuse, small subgroup, invalid curve, singular, Smart | `../../ctf-crypto/ecc-attacks.md` | `ECDSA Nonce Reuse`, `Small Subgroup Attacks`, `Smart's Attack` |
| AES-GCM nonce reuse, CBC padding oracle, CTR keystream reuse, Bleichenbacher | `../../ctf-crypto/modern-ciphers.md` | `AES-GCM Nonce Reuse / Forbidden Attack`, `CBC Padding Oracle Attack`, `AES-CTR Constant Counter`, `Bleichenbacher / PKCS#1 v1.5` |
| Hash length extension, ECB byte-at-a-time, ECB cut-and-paste, CBC bit flip | `../../ctf-crypto/modern-ciphers-2.md` | `Hash Length Extension Attack`, `AES-ECB Byte-at-a-Time Chosen Plaintext`, `AES-CBC IV Bit-Flip Authentication Bypass` |
| Custom hash state reversal, CBC cookie flipping, sponge collisions, SPN | `../../ctf-crypto/modern-ciphers-3.md` | `Custom Hash State Reversal`, `CBC Previous-Block Byte Flipping` |
| LFSR, Berlekamp-Massey, Galois tap recovery, RC4, custom keystreams | `../../ctf-crypto/stream-ciphers.md` | `LFSR Stream Cipher Attacks` (both BM and Galois tap recovery live in it) |
| MT19937, LCG parameter recovery, V8 XorShift, time seeds, chaotic maps | `../../ctf-crypto/prng.md` | `Mersenne Twister (MT19937) State Recovery`, `LCG Parameter Recovery Attack` |
| One-contest PRNG variants (Java LCG, Z3, cellular automata) | `../../ctf-crypto/prng-attacks.md` | pick by contest name from its Table of Contents |
| Many-time pad, Vigenere, substitution, Polybius, XOR key recovery | `../../ctf-crypto/classic-ciphers.md` | `OTP Key Reuse / Many-Time Pad XOR`, `XOR Variants` |
| ZKP, Groth16, KZG, PLONK, Shamir, garbled circuits, Z3 modelling | `../../ctf-crypto/zkp-and-advanced.md` | `Z3 SMT Solver Guide`, then the named scheme |
| Paillier, Rabin, ElGamal, braid groups, homomorphic, quantum | `../../ctf-crypto/exotic-crypto.md` | then `../../ctf-crypto/exotic-crypto-2.md` |
| Nothing named yet; you need the sweep or a tool choice | `../../ctf-crypto/triage-toolbox.md` | `Quick Start Commands` |

## Cheaper per-area triage cards

Each is a short recognition card rather than a full family file, so try one first when
the family is obvious but the variant is not:

- `../../ctf-crypto/triage-rsa.md`, `../../ctf-crypto/triage-block-stream.md`
- `../../ctf-crypto/triage-ecc-lattice-zkp.md`, `../../ctf-crypto/triage-prng.md`
- `../../ctf-crypto/triage-hash-crc.md`, `../../ctf-crypto/triage-classical.md`

## Need a variant, not a family

```bash
grep -rn "^## .*<keyword>" skills/ctf-crypto/ | head
```

## Known coverage gap

**Boneh-Durfee** appears nowhere in `../../ctf-crypto/`. The nearest coverage is
`../../ctf-crypto/advanced-math.md` section `Coppersmith's Method (Close Private Keys)`,
the same small-`d` lattice family but not the Boneh-Durfee construction. Treat
`crypto_attack.py boneh_durfee --help` as the primary reference and record what
actually worked in `../field-notes.md`.
