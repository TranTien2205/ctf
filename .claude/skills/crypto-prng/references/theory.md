# Theory — why the recoveries work

## The unifying fact

A PRNG is `state_{i+1}=F(state_i)`, `output_i=G(state_i)`. If `F` is
linear or `G` invertible, enough outputs pin the state — the future is
deterministic.

## The count floor

`S` state bits, `O` output bits/step → `ceil(S/O)` outputs. 624·32=19968
(MT), 4·32=128 (xorshift), 2w (LFSR: w state + w taps), 3/6 (LCG:
+a,+c,+m unknowns).

## Why linear is fatal

`F` linear → outputs are linear functions of the state → a solvable
system. LCG: modular-affine → telescope gcd. LFSR/xorshift: GF(2) →
linear solve. MT: `temper` invertible → `untemper` 624 words.

## The boundary

- **CSPRNG** — `G` one-way → no leak.
- **combiner** — `G` nonlinear → `L≈n/2` → correlation, not BM.
- **keyed** — `G(state,key)` → the key is the secret, not the state.

## The seed fact

`state_0=init(seed)`, `seed` bounded → enumerate `state_0` — no output
leak needed.

## The falsifier

`predict!=held`/`gcd→0`/`L≈n/2` — the model didn't fit → reclassify.
