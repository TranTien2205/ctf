# Preconditions — what must be true before each attack

## The universal precondition

`n = p·q` for the secret primes; `ed ≡ 1 mod φ`; the `c` is a real ciphertext.
Everything else is per-attack.

## Per-attack preconditions

### batch-gcd
- ≥2 moduli from the same generator.
- a prime collision — `gcd(ni,nj)>1` for some pair.
- the same `e` (or `e` per `n`); a `c` to recover.

### common-modulus
- one `n`, two `e` (`e1`,`e2`), `gcd(e1,e2)=1`.
- two ciphertexts of the **same** `m`: `c1`, `c2`.

### fermat
- `p`,`q` close: `next_prime`, `p+k`, `q=p+2`, a shared seed.
- `|p-q|` small — the `a` climb is `O(|p-q|)`.

### wiener
- `d < n^0.25` — shows as `e ≈ n` in size.

### boneh-durfee
- `d < n^0.292` — the small-`d` window beyond Wiener.

### coppersmith-high-bits / -core
- the top half of `p` known, or a centred guess `a` within `n^0.25`.
- the unknown window `< n^0.25`.

### small-e-root / nth-root
- `e` small, `m^e < n` — the wrap never happened.

### hastad
- the same `m` to `≥e` recipients under distinct coprime `n`.
- `∏ni > m^e`; no randomized pad.

### pollard-pm1
- `p-1` `B`-smooth; `B` ≥ the largest `p-1` factor.

### franklin-reiter
- `m2 = a·m1+b` linear, `a`,`b` known, same `n`,`e`.

### crt
- residues `∏pi>m`, OR a faulty+correct sig of the same `m`, OR consistent
  `dp`,`dq`,`qInv`.

### factor-from-d / rsa-decrypt / eth-root
- `d`,`φ`,`dp`,or the factors held.

## The class precondition

The handout is RSA *numbers* — not a service, not a group element. A service
that encrypts/decrypts is `crypto-symmetric-oracle`; a `g`,`h` is `crypto-ecc-dlog`.
