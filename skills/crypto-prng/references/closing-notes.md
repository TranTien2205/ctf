# Closing notes — the field summary

## The skill in one paragraph

A PRNG leaks its future through enough outputs or a bounded seed. Name
the generator (`mt19937`/`lfsr`/`lcg`/`xorshift`/seed — NOT
`urandom`/`secrets`), meet the count floor (3/6/required/2w/624/4),
normalize to raw ints (not float/`mod`/`randint`), pick the attack by
which params are known (`m`? → `lcg-recover`; `m`? → `unknown-modulus`;
`a,c,m`+`x>>b` → `truncated`; taps? → `lfsr-predict`; else → `BM`/`recover`;
624 → `clone`; 4 → `xorshift`; bounded seed → enumerate), run
`crypto_attack.py <id>`/`xorshift128.py`, verify `predict==held`, use the
predicted object, read `flag{` from the response.

## The five traps

1. `--low-bits` = DROPPED bits, not kept.
2. `--taps` = 1-indexed-LSB.
3. outputs must be RAW ints — float/`mod`/`randint` normalize first.
4. `Math.random` = `xorshift128+`, `mt_rand`/`java.util.Random`/`glibc
   rand` are variants.
5. 624/2w/3/6/4 are HARD floors — under them the attack can't run.

## The one rule

`predict == held-back` is the only proof a state is real. Never record a
recovery from a return value alone; never claim a flag from a
`flag{`-shaped string; a falsifier ends the mechanism — `attempts` +
`decide.py`.

## The honest status

`catalogue` class — no local chain cards. The corpus is standard
mechanism + field procedure.
