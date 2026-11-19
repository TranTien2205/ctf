# Class boundary variant — the scope, compact

## In scope

- LCG → `lcg-*`
- LFSR → `berlekamp`/`lfsr-*`
- MT19937 → `mt19937-clone`
- xorshift128 → `xorshift128`
- weak seeds (`time()`/`pid`) → seed-search
- platform variants (`mt_rand`/`java`/`rand`) — same families

## Out of scope — the boundaries

- **CSPRNG** — `urandom`/`secrets`/`crypto.`/`SecureRandom`/`arc4random`
  → no recovery.
- **`crypto-symmetric-oracle`** — keyed (`AES`/`HMAC`/`ChaCha`) → the key
  is the secret.
- **`misc-encoding-carrier`** — a decode, not a generator.
- **`crypto-ecc-dlog`/`crypto-rsa`** — nonce/param recovery, not a stream.

## The reclassify signal

`predict != held` everywhere OR a CSPRNG/keyed generator named →
`decide.py` → `reclassify`.

## The honest note

`crypto-prng` is a `catalogue` class — no local chain cards. The corpus
is standard mechanism + field procedure, not locally-verified experience.
