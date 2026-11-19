# First hour — the ordered playbook for a fresh challenge

## Minute 0-5 — the fingerprint

```
1. read the source / observe one output
2. name the generator — mt19937? lfsr? lcg? xorshift? seed? urandom?
3. urandom/secrets → STOP, wrong class → crypto-symmetric-oracle
4. otherwise → pick the family
```

The fingerprint is the cheapest discriminator — the generator's name or
the gcd/BM/clone test.

## Minute 5-10 — the gate

```
5. collect the oracle's outputs — consecutive, raw
6. normalize — hex→int, float→word, mod→raw problem
7. count against the floor — 3/6/req/2w/624/4
8. confirm alignment — no gaps, no reseed
```

Under the floor → collect more or pick a different attack. The count
gates everything.

## Minute 10-15 — the attack

```
9. compose the command — real flags from payload-dictionary*
10. run it — crypto_attack.py <id> or xorshift128.py
11. hold back the verification output
```

## Minute 15+ — the close

```
12. predict == held-back? → yes → use → flag
                         → no  → troubleshoot* → falsifier → attempts
```

## The one-decision summary

- `m` known + 3 raw outs → `lcg-recover`.
- `m` unknown + 6 raw outs → `lcg-unknown-modulus`.
- `a`,`c`,`m` known + `x>>b` → `lcg-truncated --low-bits b`.
- bitstream + taps? → `berlekamp-massey` → `lfsr-*`.
- 624 raw words → `mt19937-clone`.
- 4 raw words → `xorshift128`.
- `seed(time())` + bounded window → enumerate.

## What to never do in hour 1

- run `mt19937-clone` on <624.
- feed `x mod n`/floats to `lcg-recover`.
- run `xorshift128` on `Math.random` (`128+`).
- guess `--low-bits`/`--taps` — recount the dropped bits / run BM.
- record a state without `predict==held`.
- keep re-running the same model after `predict != held` — it's falsified.
