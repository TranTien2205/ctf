---
name: ctf-crypto
description: Deep cryptography reference. Open only after the thin router `crypto-triage` is not enough. RSA, AES, ECC, lattice/LWE, PRNG, padding oracle, ZKP, classical ciphers.
license: MIT
compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  user-invocable: "false"
---

# Cryptography - Router

Understand the primitive before naming an attack. A named attack run on guessed
parameters burns the budget and produces a result that cannot be checked.

This file routes. Open one file from the table, never the directory.

## First probe

Collect every parameter and size, and write them down, before choosing anything.

```bash
file ./handout*                      # what was actually supplied
python3 -c "print(open('out.txt').read()[:400])"   # the shape of the data
openssl rsa -pubin -in key.pub -text -noout        # modulus, exponent, bit length
```

What to record: for RSA the modulus, the public exponent, and whether a modulus
or a message is shared across ciphertexts; for a block cipher the mode, the block
size, the IV, and whether any two ciphertext blocks repeat; for a hash the digest
length and whether the server distinguishes a padding error from a content error;
for anything with randomness, the generator and how many consecutive outputs you
can see.

**Falsifier** - the observation that closes this class: the data is an encoding
rather than a cipher. If it decodes cleanly with base64, hex or a fixed table,
this is `../ctf-misc/encoding-and-cipher.md`.

## Route to depth

Open one. The `triage-*` files hold what used to sit in this router; the rest are
the full corpus.

| Signal | File |
|---|---|
| Nothing named yet; need the sweep or a tool choice | `triage-toolbox.md` |
| Shift, substitution, transposition, a hand cipher | `triage-classical.md`, then `classic-ciphers.md` |
| Historical machine or codebook cipher | `historical.md` |
| A mode-level weakness: ECB structure, CBC padding, CTR nonce reuse | `triage-block-stream.md` |
| Full block and stream depth | `modern-ciphers.md`, `modern-ciphers-2.md`, `modern-ciphers-3.md`, `stream-ciphers.md` |
| A modulus and a public exponent | `triage-rsa.md`, then `rsa-attacks.md`, `rsa-attacks-2.md` |
| A curve, a lattice, or a proof system | `triage-ecc-lattice-zkp.md`, then `ecc-attacks.md`, `lattice-and-lwe.md`, `zkp-and-advanced.md` |
| A digest, a MAC, or a checksum used as one | `triage-hash-crc.md` |
| Output of a generator you must predict | `triage-prng.md`, then `prng.md`, `prng-attacks.md` |
| Number theory the attack depends on | `advanced-math.md` |
| Nothing above fits | `exotic-crypto.md`, `exotic-crypto-2.md` |

## When to Pivot

- If the real blocker is understanding a binary, obfuscated client, or weird VM, switch to `/ctf-reverse`.
- If the challenge is mostly packet carving, disk recovery, or stego extraction before any decryption starts, switch to `/ctf-forensics`.
- If the task is just implementing an exploit against a vulnerable network service after the crypto part is solved, switch to `/ctf-pwn` or `/ctf-web`.
- If the crypto challenge involves adversarial ML, model extraction, or neural-network-based ciphers, switch to `/ctf-ai-ml`.
- If the challenge is really an encoding puzzle, esoteric cipher, or polyglot trick rather than true cryptanalysis, switch to `/ctf-misc`.


## Additional Resources

- [classic-ciphers.md](classic-ciphers.md) - Classic ciphers: Vigenere (+ Kasiski examination), Atbash, substitution wheels, XOR variants (+ multi-byte frequency analysis), deterministic OTP, cascade XOR, book cipher, OTP key reuse / many-time pad, variable-length homophonic substitution, grid permutation cipher keyspace reduction, image-based Caesar shift ciphers, XOR key recovery via file format headers
- [modern-ciphers.md](modern-ciphers.md) - Modern cipher attacks: AES (CFB-8, ECB leakage), CBC-MAC/OFB-MAC, padding oracle, S-box collisions, GF(2) elimination, LCG partial output recovery, affine cipher over composite modulus, AES-GCM with derived keys, AES-GCM nonce reuse (forbidden attack), Ascon-like reduced-round differential cryptanalysis, custom linear MAC forgery, CBC padding oracle (full block decryption), Bleichenbacher RSA PKCS#1 v1.5 padding oracle (ROBOT), birthday attack / meet-in-the-middle, CRC32 collision signature forgery, AES key recovery via byte-by-byte zeroing oracle, AES-CBC ciphertext forging via error-message decryption oracle
- [modern-ciphers-2.md](modern-ciphers-2.md) - Modern cipher attacks (Part 2): Blum-Goldwasser bit-extension oracle, hash length extension, compression oracle (CRIME-style), hash function time reversal via cycle detection, OFB mode invertible RNG backward decryption, weak key derivation via public key hash XOR, HMAC-CRC linearity attack, DES weak keys in OFB mode, SRP protocol bypass, modified AES S-Box brute-force, square attack on reduced-round AES, AES-ECB byte-at-a-time chosen plaintext, AES-ECB cut-and-paste block manipulation, AES-CBC IV bit-flip auth bypass, Rabin LSB parity oracle, PBKDF2 pre-hash bypass, MD5 multi-collision via fastcol
- [modern-ciphers-3.md](modern-ciphers-3.md) - Modern cipher attacks (Part 3): custom hash state reversal, CRC32 brute-force for small payloads, noisy RSA LSB oracle error correction, sponge hash MITM collision, CBC IV forgery + block truncation, padding oracle to CBC bitflip RCE, SPN S-box intersection attack, AES-CFB IV recovery from timestamp-seeded PRNG, three-round XOR protocol key cancellation, AES-CBC UnicodeDecodeError side-channel oracle, SHA-256 basis attack for XOR-aggregate hash bypass, custom MAC forgery via XOR block cancellation, HMAC key recovery via XOR+addition arithmetic
- [stream-ciphers.md](stream-ciphers.md) - Stream cipher attacks: LFSR (Berlekamp-Massey, correlation attack, known-plaintext, Galois vs Fibonacci, Galois tap recovery via autocorrelation), RC4 second-byte bias, XOR consecutive byte correlation
- [rsa-attacks.md](rsa-attacks.md) - RSA attacks: small e (cube root), common modulus, Wiener's, Pollard's p-1, Hastad's broadcast, Hastad with linear padding (Coppersmith), Franklin-Reiter related message (e=3), Coppersmith linearly-related primes, Fermat/consecutive primes, multi-prime, restricted-digit, Coppersmith structured primes, Manger oracle, polynomial hash
- [rsa-attacks-2.md](rsa-attacks-2.md) - RSA attacks (specialized): RSA p=q validation bypass, cube root CRT gcd(e,phi)>1, factoring from phi(n) multiple, multiplicative homomorphism signature forgery, weak keygen via base representation, RSA with gcd(e,phi)>1 exponent reduction, batch GCD shared prime factoring, partial key recovery from dp/dq/qinv, RSA-CRT fault attack, homomorphic decryption oracle bypass, small prime CRT decomposition, Montgomery reduction timing attack, Bleichenbacher low-exponent signature forgery, RSA signature bypass with e=1 and crafted modulus
- [ecc-attacks.md](ecc-attacks.md) - ECC attacks: small subgroup, invalid curve, Smart's attack (anomalous, with Sage code), fault injection, clock group DLP, Pohlig-Hellman, ECDSA nonce reuse, Ed25519 torsion side channel, DSA nonce reuse, DSA key recovery via MD5 collision on k-generation
- [zkp-and-advanced.md](zkp-and-advanced.md) - ZKP/graph 3-coloring, Z3 solver guide, garbled circuits, Shamir SSS, bigram constraint solving, race conditions, Groth16 broken setup, DV-SNARG forgery, KZG pairing oracle for permutation recovery, Shamir SSS reused polynomial coefficients
- [prng.md](prng.md) - PRNG attacks (foundational): MT19937, MT float recovery via GF(2) magic matrix for token prediction, LCG, GF(2) matrix PRNG, V8 XorShift128+ Math.random state recovery via Z3, middle-square, deterministic RNG hill climbing, random-mode oracle, time-based seeds, C srand/rand synchronization via ctypes, password cracking, logistic map chaotic PRNG
- [prng-attacks.md](prng-attacks.md) - PRNG attacks (CTF-era, 2017+): MT subset-sum seed recovery, MT19937 constraint propagation, Rule 86 cellular automaton reversal via Z3, Java LCG meet-in-the-middle partial modulo, LCG backward stepping via modular inverse, LFSR bit-fold ASCII parity, Z3 solve-time timing oracle, randcrack DSA k prediction, format-string PRNG seed offset, NTP-poisoned PRNG UUID XOR
- [historical.md](historical.md) - Historical ciphers (Lorenz SZ40/42, book cipher implementation)
- [advanced-math.md](advanced-math.md) - Advanced mathematical attacks (isogenies, Pohlig-Hellman, baby-step giant-step (BSGS) for general DLP, LLL, Merkle-Hellman knapsack via LLL, Coppersmith, quaternion RSA, GF(2)[x] CRT, S-box collision code, LWE lattice CVP attack, affine cipher over non-prime modulus, introspective CRC via GF(2) linear algebra)
- [lattice-and-lwe.md](lattice-and-lwe.md) - Lattice attack triage and workflow: LLL/BKZ/Babai, HNP from partial or biased nonces, truncated LCG state recovery, LWE embedding and CVP, Ring-LWE / Module-LWE recognition, orthogonal lattices, subset sum / knapsack, and common failure modes
- [exotic-crypto.md](exotic-crypto.md) - Exotic algebraic structures (braid group DH / Alexander polynomial, monotone function inversion, tropical semiring residuation, Paillier cryptosystem, Hamming code helical interleaving, ElGamal universal re-encryption, FPE Feistel brute-force, icosahedral symmetry group cipher, Goldwasser-Micali replication oracle)
- [exotic-crypto-2.md](exotic-crypto-2.md) - Exotic algebraic structures (Part 2, 2017+): BB-84 QKD MITM, ElGamal trivial DLP (B=p-1), Paillier LSB oracle via homomorphic doubling, differential privacy noise cancellation, homomorphic encryption bit-extraction, ElGamal over matrices via Jordan normal form, OSS signature forgery via Pollard, Cayley-Purser decryption without private key, BIP39 partial mnemonic checksum brute force, Asmuth-Bloom CRT threshold recovery, Rabin with polynomial primes, LCG period detection, Vandermonde polynomial coefficient recovery

---


## Prerequisites

**Python packages (all platforms):**
```bash
pip install pycryptodome z3-solver sympy gmpy2 hashpumpy fpylll py_ecc
```

**Linux (apt):**
```bash
apt install hashcat sagemath
```

**macOS (Homebrew):**
```bash
brew install hashcat
```

**Manual install:**
- SageMath — Linux: `apt install sagemath`, macOS: `brew install --cask sage`
- RsaCtfTool — `git clone https://github.com/RsaCtfTool/RsaCtfTool` (automated RSA attacks)

> **Note:** `gmpy2` requires libgmp — Linux: `apt install libgmp-dev`, macOS: `brew install gmp`.

