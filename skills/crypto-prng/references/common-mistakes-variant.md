# Common mistakes variant — the operator errors, compact

## The count errors

- `mt19937-clone` on 623 — the hard gate; collect one more.
- `lcg-unknown-modulus` on 5 — no gcd; collect a 6th.
- `berlekamp` on `2w-1` — wrong taps; collect one more bit.
- `xorshift128` on 3 — underdetermined.
- any attack before the count check — wasted run.

## The rawness errors

- `x mod n` to `lcg-recover` — wrong `a`,`c`.
- floats to `mt19937-clone` — garbage.
- hex/base64 undecoded — decode to int.
- `randint`/`choice`/`shuffle` as raw — post-processed.

## The convention errors

- `--low-bits` = kept — it's DROPPED `b`.
- `--taps` wrong convention — 1-indexed-LSB.
- `--outputs` sorted/dedup — breaks consecutive.

## The variant errors

- `xorshift128` on `Math.random` — it's `128+`.
- `random` clone on `mt_rand` — PHP differs.
- `java.util.Random` as unknown LCG — `a,c,m` known → `lcg-truncated`.
- `glibc rand` as plain LCG — additive.

## The param errors

- `--modulus` on `lcg-unknown-modulus` — it takes none.
- `m=2^32` assumed — `rand`=2^31, `java`=2^48.

## The verification errors

- record `a,c`/`state` without `predict==held`.
- verify on a training output.
- one lucky match = recovery.
- `flag{` from the description.

## The class errors

- `lcg-*`/`lfsr-*`/`mt-*` on `urandom`/`secrets` — wrong class.
- `mt19937-clone` on `seed=time()` — seed-search.
- "looks random" = unattackable — the whole class is that.
