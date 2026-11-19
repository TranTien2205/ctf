# Anti-patterns — the moves that cost time

## The wrong first move

- **Brute-forcing `n`** — factoring a proper `n` is hopeless by design. The bug
  is a precondition violation; brute force is not a strategy.
- **Trying `john`/`hashcat` on `c`** — RSA is not a hash; the ciphertext is not
  cracked, it is *attacked* via a structural weakness.
- **Reading `e` and stopping** — `e`=65537 deflects; the bug is in `p`,`q` or a
  leak. Read the keygen.

## The wrong discriminator

- **`e=3` → `small-e-root`** without checking `m³<n` — a wrapped `m` makes the
  root fail; `hastad`/`coppersmith` is the real route.
- **count → `batch-gcd`** without checking a collision — `gcd=1` everywhere is a
  negative, not a target.
- **"large n" → give up** — size is not the bound; the precondition is.

## The wrong bound handling

- **retrying a bound-exceeded attack** — `d≥n^0.292`, window `<n^0.25` are
  theorems. Record the negative; do not retry.
- **`fpylll` missing → give up** — `tools/crypto/` has a pure-python LLL; slower,
  same bound. `lll_backend` reports it.
- **guessing `B`/`m`/`t` without a reason** — the bound is a parameter; a small
  `B` misses, a large `m` is slow.

## The wrong recovery handling

- **`pow(m,e,n)!=c` → "it's the flag anyway"** — a decoy. The gate is the
  identity, not the shape.
- **a padded `m` = the flag** — `m` is the padded block; strip
  `\x00\x02<pad>\x00` / OAEP.
- **`eth-root` first candidate = the flag** — `g` candidates; `pow`+format picks.

## The wrong class

- **a socket printing numbers = an oracle** — it's transport; a computing
  socket is `crypto-symmetric-oracle`.
- **`g`,`h` present = RSA** — `crypto-ecc-dlog`.
- **a keystream = RSA** — `crypto-prng`.

## The wrong evidence

- **"the attack ran" = solved** — exit status is not evidence.
- **"looks like a flag" = solved** — `pow` is the gate.
- **recording nothing on a dead end** — a bound-exceeded is a result; record it.
