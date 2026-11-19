# Negative results variant — the record, the compact form

## The record

```json
{"mechanism":"<id>","measurement":"<the failed predict>",
 "proves_dead":"<what it kills>","reopen_if":"<what would reopen>"}
```

## The per-attack kills

- `lcg-recover`: `gcd(x1-x0,m)!=1` everywhere / `predict!=held`.
- `lcg-unknown-modulus`: `gcd→0/1` / `gcd`=stubborn multiple.
- `lcg-truncated`: no short vector / `predict!=held`.
- `berlekamp-massey`/`lfsr-*`: `L≈n/2` / `predict` diverges.
- `mt19937-clone`: <624 / `predict!=held`.
- `xorshift128`: `predict!=held` / wrong variant.
- seed: no match in window / unbounded.

## The reopen keys

- "reopen if a 624 contiguous window appears".
- "reopen if `m`/`a`/`c`/taps get leaked".
- "reopen if the seed window shrinks".
- "reopen if the `128+`/`mt_rand`/`java` variant tool exists".

## The class kill

`predict!=held` everywhere + `urandom`/`secrets`/keyed → wrong class →
`decide.py` → `reclassify`.
