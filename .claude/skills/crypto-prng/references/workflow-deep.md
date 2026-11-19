# Workflow deep — the procedures annotated

## Why the count gate comes first

`decide.py` budgets the mechanism — running `mt19937-clone` on 623 outputs
wastes the whole budget on a shape that cannot work. Count first, attack
second.

## Why the rawness gate matters

An LCG's `x` seen through `mod n` or a float isn't `x` — the affine
structure you're solving for lives in the raw state. Normalize to the raw
int BEFORE the command, or the `a`,`c`,`m` you recover are wrong.

## The oracle procedure, annotated

```
collect consecutive outputs — gaps break "consecutive"
normalize to raw ints — hex→int, float→word, decode base64
fingerprint — LCG gcd? LFSR BM? MT? xorshift? seed shape?
count — meets the attack's floor?
run attack → predict → verify held-back → use → flag
```

## The fingerprint procedure, annotated

```
x_{i+1}-x_i diffs → gcd of telescoping → LCG if affine
berlekamp-massey → linear complexity small → LFSR
624 words? → mt19937-clone test
outputs change per-second → seed-search
none → CSPRNG/keyed → wrong class
```

## The verify-first procedure

```
recover state → hold back one output → predict it → match?
yes → the state is real → predict the flag/token
no  → wrong attack/params — do NOT record recovered
```

## The budget procedure

5 probes/15 min per mechanism — the controller (`decide.py`) counts. A
falsifier that fires ends the mechanism; record it in `attempts/`.
