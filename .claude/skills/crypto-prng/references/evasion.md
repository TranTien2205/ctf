# Evasion — the disguises that hide the generator

## The naming disguises

- `token`/`nonce`/`ticket`/`key`/`session_id`/`uid`/`salt` — a "random"
  value that's a PRNG output in disguise.
- `random`/`rand`/`secure_random` mislabeled — `secure_random` calling
  `rand()` is still `rand()`.

## The output disguises

- **hex/base64** — decode to the raw int.
- **floats** — `random.random()`/`mt_rand`/`Math.random` — the raw word is
  a `getrandbits` pair or a scaled int.
- **`mod n`/`% N`** — the state is reduced — the observation isn't `x`.
- **post-processing** — `randint`/`choice`/`shuffle`/`hash()` — the output
  is a function of the state, not the state.

## The seed disguises

- `seed = time()`/`int(time())`/`time()*1000`/`pid`/`pid+time` — bound the
  window from the issue epoch.
- `seed = os.urandom`/`secrets` — NOT enumerable → wrong class.
- `srand(time(0))`/`mt_srand`/`new Random(System.currentTimeMillis())` —
  the platform variant of timestamp seeding.

## The generator disguises

- **a custom `next()`** — usually an LCG/LFSR in disguise; fingerprint.
- **a combined generator** — `rand()+rand()` or an LFSR with a nonlinear
  filter — the structure is masked.
- **a reseeding generator** — `srand` per-request → each output is a fresh
  seed, not a stream.

## The verification disguises

- **a coincidence on one output** — not a recovery; reproduce a sequence.
- **"close" outputs** — bit-for-bit only; `predict != held-back` is the kill.
