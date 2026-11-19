# Negative results deep — what to record when it fails

## The record shape

A falsifier isn't a failure to hide — it's a measured kill. Record in
`attempts/`:

```json
{
  "mechanism": "mt19937-clone",
  "measurement": "predict_next != held_back_word on 624 consecutive raw words",
  "proves_dead": "the stream is not a clonable MT19937 in this window",
  "reopen_if": "a contiguous 624-word window with no reseed becomes available"
}
```

## The per-attack falsifiers to record

### `lcg-recover` dead

- `gcd(x1-x0, m) != 1` for every available triple AND `m` can't be
  factored → `a` isn't invertible → the plain closed-form is dead.
  Record: "no invertible difference in N outputs; m composite".
- `predict != held` → wrong `m` or non-raw inputs.
  Record: "predict_next diverged on held-back o_k".

### `lcg-unknown-modulus` dead

- `gcd` collapses to 0/1 → not affine → not an LCG.
  Record: "u_i gcd = 0/1 over k outputs — not an affine recurrence".
- `gcd` = a stubborn multiple of `m` → `lcg-recover` fails on it.
  Record: "gcd = a multiple; recovered m rejected by predict".

### `lcg-truncated` dead

- lattice returns no consistent state → `low-bits`/`a`/`c`/`m`/shape
  wrong. Record: "lattice under-determined or wrong bound".

### `berlekamp-massey` / `lfsr-*` dead

- linear complexity `≈ n/2` → not a plain LFSR.
  Record: "linear complexity ~ n/2 — combiner or non-LFSR".
- `predict` diverges on every convention → wrong model.
  Record: "lfsr-predict diverges for all tap conventions".

### `mt19937-clone` dead

- <624 → can't run. Record: "only k<624 consecutive raw words available".
- `predict != held` on 624 → non-raw / gap / reseed / wrong variant.
  Record: "clone rejected by held-back word — likely non-raw or reseed".

### `xorshift128` dead

- `predict != held` → wrong variant (`128+`/64*) or non-consecutive.
  Record: "xorshift128 rejected — variant or alignment".

### seed-search dead

- no seed in the window reproduces the output → wider window or CSPRNG.
  Record: "no seed in [lo,hi] reproduced o0 — widen or wrong class".

## The class falsifier — the big kill

`predict != held-back` everywhere, OR `os.urandom`/`secrets`/keyed
output confirmed → the class is wrong → `crypto-symmetric-oracle` or a
different class. Record the class kill and the reclassify signal.

## The reopen conditions

Each falsifier records what would reopen it:

- "reopen if a 624-word contiguous window appears" — a different endpoint
  or a private generator.
- "reopen if `m`/`a`/`c` get leaked" — a source read.
- "reopen if the seed window shrinks" — a tighter epoch bound.
- "reopen if the variant is `128+` and a `+` tool exists" — a capability
  addition.

## The `decide.py` handoff

After the falsifier, `decide.py` names the next rung:
`chain_match → reclassify → writeup_search → novel_plan → fanout_sweep →
solver_handoff`. Record the falsifier BEFORE the handoff — the next rung
builds on what was proven dead.
