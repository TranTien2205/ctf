# RSA attacks

Everything that starts from a modulus and a public exponent. Depth in
`rsa-attacks.md` and `rsa-attacks-2.md`.

Moved out of `SKILL.md` so the router stays thin. Content is unchanged.

---

## RSA Attacks

- **Small e with small message:** Take eth root
- **Common modulus:** Extended GCD attack
- **Wiener's attack:** Small d
- **Fermat factorization:** p and q close together
- **Pollard's p-1:** Smooth p-1
- **Hastad's broadcast:** Same message, multiple e=3 encryptions
- **Consecutive primes:** q = next_prime(p); find first prime below sqrt(N)
- **Multi-prime:** Factor N with sympy; compute phi from all factors
- **Restricted-digit primes:** Digit-by-digit factoring from LSB with modular pruning
- **Coppersmith structured primes:** Partially known prime; `f.small_roots()` in SageMath
- **Manger oracle (simplified):** Phase 1 doubling + phase 2 binary search; ~128 queries for 64-bit key
- **Manger on RSA-OAEP (timing):** Python `or` short-circuit skips expensive PBKDF2 when Y != 0, creating fast/slow timing oracle. Full 3-step attack (~1024 iterations for 1024-bit RSA). Calibrate timing bounds with known-fast/known-slow samples.
- **Polynomial hash (trivial root):** `g(0) = 0` for polynomial hash; craft suffix for `msg = 0 (mod P)`, signature = 0
- **Polynomial CRT in GF(2)[x]:** Collect ~20 remainders `r = flag mod f`, filter coprime, CRT combine
- **Affine over composite modulus:** CRT in each prime factor field; Gauss-Jordan per prime
- **RSA p=q validation bypass:** Set `p=q` so server computes wrong `phi=(p-1)^2` instead of `p*(p-1)`; test decryption fails, leaking ciphertext
- **RSA cube root CRT (gcd(e,phi)>1):** When all primes ≡ 1 mod e, compute eth roots per-prime via `nthroot_mod`, enumerate CRT combinations (3^k feasible for small k)
- **Factoring from phi(n) multiple:** Any multiple of `phi(n)` (e.g., `e*d-1`) enables factoring via Miller-Rabin square root technique; succeeds with prob ≥ 1/2 per attempt
- **Weak keygen via base representation:** Primes `p = kp*B + tp` with small kp create mixed-radix structure in n; brute-force kp*kq (2^24) to factor
- **RSA with gcd(e,phi)>1 (exponent reduction):** Reduce `e' = e/g`, compute `d' = e'^(-1) mod phi`, partial decrypt to `m^g`, then take g-th root over integers
- **RSA partial key recovery (dp/dq/qinv):** CRT exponents from partial PEM leak allow O(e) prime recovery: iterate k, check if `(dp*e-1)/k+1` is prime. See [rsa-attacks-2.md](rsa-attacks-2.md#rsa-partial-key-recovery-from-dp-dq-qinv-0ctf-2016).
- **RSA-CRT fault attack:** Single faulty CRT signature leaks factor via `gcd(s^e - m, n)` (Bellcore attack). See [rsa-attacks-2.md](rsa-attacks-2.md#rsa-crt-fault-attack--bit-flip-recovery-csaw-ctf-2016).
- **RSA homomorphic decryption bypass:** Multiplicative homomorphism lets you decrypt `c` by querying oracle with `c * r^e mod n`, then dividing result by `r`. See [rsa-attacks-2.md](rsa-attacks-2.md#rsa-homomorphic-decryption-oracle-bypass-ectf-2016).
- **RSA small prime CRT decomposition:** When `n` has many small prime factors, factor with trial division, solve `m mod p_i` per prime, CRT combine. See [rsa-attacks-2.md](rsa-attacks-2.md#rsa-with-small-prime-factors-and-crt-decomposition-hack-the-vote-2016).
- **Hastad broadcast with linear padding (Coppersmith):** When each of `e` recipients applies a known affine transform `a_i*m+b_i` before encryption, CRT + Coppersmith small_roots recovers `m`. See [rsa-attacks.md](rsa-attacks.md#hastad-broadcast-attack-with-linear-padding----coppersmith-plaidctf-2017).
- **RSA Montgomery reduction timing attack:** Leaked extra-subtraction counts in Montgomery multiplication reveal private key bits MSB-to-LSB via statistical correlation. See [rsa-attacks-2.md](rsa-attacks-2.md#rsa-timing-attack-on-montgomery-reduction-def-con-2017).
- **Bleichenbacher low-exponent signature forgery:** With e=3, forge PKCS#1 v1.5 signatures by computing cube root of a value with correct padding prefix; trailing garbage absorbs the remainder. See [rsa-attacks-2.md](rsa-attacks-2.md#bleichenbacher-low-exponent-rsa-signature-forgery-google-ctf-2017).
- **Franklin-Reiter related message attack (e=3):** Two ciphertexts of `m+pad1` and `m+pad2` with known padding difference; polynomial GCD in `Zmod(n)` recovers `m` directly. See [rsa-attacks.md](rsa-attacks.md#franklin-reiter-related-message-attack-on-rsa-e3-n1ctf-2018).
- **RSA signature bypass (e=1, crafted modulus):** Verifier accepts user-supplied `(n, e)`; set `e=1` and `n = sig - PKCS1_pad(msg)` so `pow(sig, 1, n)` equals expected padded hash. See [rsa-attacks-2.md](rsa-attacks-2.md#rsa-signature-bypass-with-e1-and-crafted-modulus-backdoorctf-2018).
- **Coppersmith on linearly-related primes:** When `q ~ k*p` for known `k`, approximate `q ~ sqrt(k*n)` and use Coppersmith `small_roots` on the error term. Generalizes Fermat factorization to non-consecutive primes. See [rsa-attacks.md](rsa-attacks.md#coppersmith-attack-on-linearly-related-rsa-primes-asis-ctf-2018).

See [rsa-attacks.md](rsa-attacks.md) and [advanced-math.md](advanced-math.md) for full code examples.


## Bleichenbacher RSA Padding Oracle (ROBOT)

RSA PKCS#1 v1.5 padding validation oracle → adaptive chosen-ciphertext plaintext recovery. ~10K queries for RSA-2048. Affects TLS implementations via timing. See [modern-ciphers.md](modern-ciphers.md#bleichenbacher--pkcs1-v15-rsa-padding-oracle).


## RSA Multiplicative Homomorphism Signature Forgery

Unpadded RSA: `S(a) * S(b) mod n = S(a*b) mod n`. If oracle blacklists target message, sign its factors and multiply. See [rsa-attacks-2.md](rsa-attacks-2.md#rsa-signature-forgery-via-multiplicative-homomorphism-mma-ctf-2015).


## Blum-Goldwasser Bit-Extension Oracle (PlaidCTF 2013)

Extend ciphertext by one bit per oracle query to leak plaintext via parity. Manipulate BBS squaring sequence to produce valid extended ciphertexts. See [modern-ciphers-2.md](modern-ciphers-2.md#blum-goldwasser-bit-extension-oracle-plaidctf-2013).


