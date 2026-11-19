# Evasion deep — the disguises, expanded

## The output-shape disguises, expanded

- **`random.random()`** — `getrandbits(53)/2^53` — a float pair, NOT a
  32-bit word; `mt19937-clone` on floats fails.
- **`randint(a,b)`/`choice(seq)`/`shuffle`** — the generator output is
  post-processed — the state isn't the observation.
- **`hex(v)`/`b64(v)`/`str(v)`** — decode to the int first.
- **`x mod n`/`x % N`** — the reduced state; the affine structure shifts.
- **`x >> b`/`x & ((1<<k)-1)`** — truncated (`lcg-truncated`/`low-bits`).

## The generator disguises, expanded

- **a `next()`/`rand()`/`secure_random()` wrapper** — usually LCG/LFSR
  inside; fingerprint the structure.
- **a combined generator** — `rand()^rand()`, LFSR+NLF — masked structure.
- **a reseeding oracle** — `srand(time())` per call → each output is a
  fresh seed — seed-search, not state-recovery.
- **`mt_rand`/`java.util.Random`/`Math.random`** — the platform variant;
  same family, different constants.

## The seed disguises, expanded

- `seed = int(time())` — bound `[issue_epoch - slack, now]`.
- `seed = pid`/`pid ^ time`/`time + pid` — two-factor; bound both.
- `seed = os.urandom`/`secrets.token` — NOT enumerable → wrong class.

## The verify disguises, expanded

- **one lucky match** — reproduce a SEQUENCE.
- **statistical uniformity** — not predictability.
- **the flag-shape string in the description** — not the recovered object.
