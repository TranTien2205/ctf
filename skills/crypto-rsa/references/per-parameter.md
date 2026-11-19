# Per-parameter map — the value → what it leaks

## `n` — the modulus

- **bit-length** — 512/1024/2048/4096; not a bound, just context.
- **`isqrt(n)**2==n`** → `n=p²`, `phi=p(p-1)`.
- **`isPrime(n)`** → `phi=n-1`.
- **`factorint(n)`** → a smooth `n` splits directly.
- **`e≈n`** → `d` small → `wiener`/`boneh-durfee`.

## `e` — the public exponent

- **`3,5,17,257`** → small-e → `small-e-root`, `hastad`, `franklin-reiter`.
- **`65537`** → default — the bug is elsewhere.
- **`~n` bits** → `d` small → `wiener`/`boneh-durfee`.
- **`gcd(e,phi)>1`** → `eth-root`.
- **two `e` on one `n`, `gcd=1`** → `common-modulus`.

## `c` — the ciphertext

- **`c` count ≥ `e`, same `m`** → `hastad`.
- **`c < n`** → `m^e` wrapped → not a plain root.
- **`c`/`m` relation `m2=a·m1+b`** → `franklin-reiter`.
- **`c` small / a perfect power** → `small-e-root`.

## `d` — the private exponent

- **leaked** → `factor-from-d`/`rsa-decrypt`.
- **small** → `wiener`/`boneh-durfee`.
- **`d mod (p-1)` (`dp`)** → `crt` → `p`.

## `phi` — the group order

- **leaked** → `factor-from-d`/`rsa-decrypt`.
- **`gcd(e,phi)>1`** → `eth-root`.
- **`n-phi+1==p+q`** — the consistency check.

## `p`, `q` — the factors

- **held** → `rsa-decrypt`/`eth-root`.
- **partial** → `coppersmith-*`.
- **`dp`,`dq`,`qInv`** → `crt`.
- **a fault on `q`** → `crt` Bellcore.

## `m` — the plaintext

- **`m^e<n`** → `small-e-root`.
- **partial `m`** → `coppersmith` partial-message.
- **`m2=a·m1+b`** → `franklin-reiter`.
- **`m` residues mod `pi`** → `crt`.

## `B`, `m`, `t` — the tuning parameters

- **`B`** — `pollard-pm1` bound; raise it.
- **`m`,`t`** — the lattice dimensions; raise to approach the bound.
