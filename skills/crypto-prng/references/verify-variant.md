# Verify variant — the accept protocol, the compact form

## The rule

`predict == held-back` — bit-for-bit, on data the attack never saw. The
only accept.

## The protocol

```
1. collect k+1 outputs
2. feed o0..o_{k-1} → recovered state
3. predict o_k
4. == o_k? yes → real → predict the flag-object
           no  → wrong → troubleshoot → falsifier
```

## Per attack

- **LCG**: `(a*o_last+c)%m == held`.
- **LFSR**: `lfsr-predict --count k == held_bits`.
- **MT**: `clone.getrandbits(32) == o624`.
- **xorshift**: `--predict 1 == o4`.
- **seed**: `Random(seed).call()==o0 and .call()==o1` — two outputs.

## The stronger check

Reproduce a SEQUENCE — `predict` for `k`,`k+1`,`k+2` — a single match is
a coincidence; a sequence is a recovery.

## The fails

`predict != held` → convention (`low-bits`/`taps`) → variant
(`mt_rand`/`128+`) → normalization (float/mod) → alignment (gap/reseed)
→ count → falsifier → `attempts` → `decide.py`.
