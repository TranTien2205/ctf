# Class boundary deep — what is and isn't crypto-prng

## The class

`crypto-prng` = a predictable pseudorandom generator whose STATE can be
recovered from outputs or whose SEED is enumerable. The whole class is
"the generator looks random but leaks its future".

## In scope

- **LCG** — `x_{i+1}=a·x_i+c mod m` → `lcg-*`.
- **LFSR** — linear feedback shift register → `berlekamp`/`lfsr-*`.
- **MT19937** — `mt19937-clone`.
- **xorshift128** — `xorshift128.py`.
- **weak seeds** — `seed(time())`/`pid`/`mt_srand` → seed-search.
- **platform variants** — `mt_rand`, `java.util.Random`, `rand()` — same
  families, different constants; fingerprint the variant.

## Out of scope — the boundaries

### `crypto-symmetric-oracle`

A **keyed** generator/cipher — the output is a function of a SECRET key,
not just the state. `AES-CTR(key)`, `HMAC(key)`, `ChaCha` — no short
output leaks the key. Confusable because both emit "random-looking"
bytes.

- **Boundary signal**: a secret key/seed you can't enumerate, `AES`/
  `ChaCha`/`HMAC`/`RC4` named, or `predict` falsified everywhere.
- **Rule**: if `G(state, key)` and `key` is unknown, it's not this class.

### `misc-encoding-carrier`

An **encoding**, not a generator — base64/hex/uuencode of a flag. The
"random-looking" bytes are a deterministic transform of the flag, not a
PRNG stream. Confusable because the carrier looks like noise.

- **Boundary signal**: a decode yields structure, no generator/seed in
  the mechanism.

### CSPRNG — genuinely secure

`os.urandom`, `secrets.token`, `/dev/urandom`, `crypto.getRandomValues`,
`SecureRandom`, `arc4random` — deliberately state-safe. Out of scope for
the whole class.

- **Boundary signal**: `os.urandom`/`secrets`/`SecureRandom`/`crypto.`/
  `arc4random` named, or `predict` falsified on every attack.
- **Rule**: name the generator FIRST. A CSPRNG named in source is the
  boundary.

### `crypto-ecc-dlog`/`crypto-rsa`

A nonce/parameter recovery problem — the "random" is a `k` in ECDSA or an
RSA nonce, not a PRNG stream. The recovery is a lattice/dlog attack, not
a state clone. Confusable because both "recover a secret number".

- **Boundary signal**: `k`/`r`/`s` signatures, `dlog`, `ECDSA`, `RSA`,
  `n=pq` — a different attack family.

## The reclassify signal

`predict != held` everywhere OR a CSPRNG/keyed generator confirmed →
`decide.py` → `reclassify` → the right class. The falsifier is the
boundary test.

## The catalogue honest note

`crypto-prng` is a **catalogue class** — nothing in this toolkit has
solved one yet (no chain card). The corpus is standard published
mechanism + field procedure, not locally-verified experience. Never
present it as experience.
