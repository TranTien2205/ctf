# Verify deep — the accept gate, annotated

## The rule

**Never trust a recovery you haven't reproduced.** `predict == held-back`
is the only accept signal — everything else is a candidate.

## The held-back protocol

```
1. collect k+1 outputs (k for recovery, 1 held back)
2. feed o0..o_{k-1} to the attack → recovered state
3. predict output k
4. predict == o_k?  yes → state real → predict the flag-object
                    no  → wrong attack/params → troubleshoot
```

For MT: `o0..o622` recover, `o623` held back, `predict_next == o623`.
For LFSR: hold back `k` bits, `lfsr-predict --count k`, compare.
For seed-search: the seed must reproduce `o0` AND predict `o1`.

## Why held-back, not in-training

A recovery fit on `o0..o_{k-1}` that predicts `o_k` is verified on data it
never saw — the standard test. Predicting an output it was fit on proves
nothing (a wrong `a,c` can be forced to interpolate).

## The reproduction check — stronger still

After `predict == held`, reproduce a SEQUENCE: `predict_next` for outputs
k, k+1, k+2 — all match. A single lucky match is not a recovery.

## The `lcg-recover` verification

```python
# after the command returns a, c:
x_next = (a*o_last + c) % m
assert x_next == held_back
```

## The `lfsr-predict` verification

```python
predicted = lfsr_predict(bits, taps, width, count=k)
assert predicted == held_back_bits[:k]
```

## The `mt19937-clone` verification

```python
clone = mt19937_clone(o[:624])
assert clone.getrandbits(32) == o_held  # the 625th
```

## The seed verification

```python
r = random.Random(seed); assert r.getrandbits(32)==o0 and r.getrandbits(32)==o1
```

## The failure ladder

`predict != held` → check the convention (`--low-bits`/`--taps`/`modulus`)
→ the variant (`mt_rand`/`xorshift+`) → the normalization (float/mod) →
record the falsifier → `attempts` → `decide.py`.
