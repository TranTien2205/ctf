# Theory deep — why every PRNG recovery works

## The unifying fact

A PRNG is a deterministic finite-state machine:

```
state_{i+1} = F(state_i)
output_i    = G(state_i)
```

Attack the state. If `F` is linear (LCG, LFSR, xorshift) or `G` is
invertible (MT's temper), the state leaks through enough outputs — and the
future is deterministic. The whole family of attacks is "collect enough
`output_i` to pin `state_i`, then run `F` forward."

## The count floor — information theory

The state has `S` bits. Each output leaks at most `O` bits. The count
floor is roughly `ceil(S / O)`:

| Generator | State bits | Output bits | Floor |
|---|---|---|---|
| LCG (m known) | ~log2 m | ~log2 m | 3 (for a,c too) |
| LCG (m unknown) | ~log2 m | ~log2 m | 6 |
| LCG truncated | ~log2 m | high bits only | ~required |
| LFSR w | w | 1 per bit | 2w for BM |
| MT19937 | 19968 | 32 | 624 |
| xorshift128 | 128 | 32 | 4 |
| seed | ~log2 window | 32+ | window-size tries |

`624×32 = 19968` — exactly MT's state size. `4×32 = 128` — exactly
xorshift's. The count floor is information-theoretic, not arbitrary.

## Why linear generators are fatal

A linear `F` over GF(2) (LFSR, xorshift) or a modular-affine `F` (LCG)
means each output is a LINEAR FUNCTION of the state. `S` output bits give
`S` linear equations — a solvable system. The whole attack is linear
algebra.

- **LFSR/xorshift**: solve a GF(2) linear system.
- **LCG**: solve a modular-affine system (the telescope trick).

## Why MT19937 falls despite being "good"

MT's `F` (the twist) is linear GF(2) too, and `G` (temper) is a bijection.
The output isn't scrambled — it's a per-word bijection of a linear state.
`untemper` undoes `G`, the twist is known → the state leaks fully in 624
words. MT is statistically excellent and cryptographically dead.

## Why a CSPRNG resists

A CSPRNG's `F`/`G` are deliberately nonlinear / one-way — `G(state)` =
`AES(state, ctr)` or a hash. Inverting `G` is as hard as the primitive.
That's the class boundary: no short output leaks the state because `G`
isn't invertible and `F` isn't linear.

## The seed-search fact

`state_0 = f(seed)`. If `seed` has ~20-30 bits of entropy (`time()` sec in
a bounded window, `pid` 0..32k), enumerate `state_0` directly — no output
leak needed, just the seed space. The floor is the seed's bit-width, not
the state's.

## The truncation nuance

A truncated output (`x>>b`, `x mod n`) leaks PARTIAL state — the unknown
low bits make `G` non-invertible. The attack becomes a bounded-unknown
lattice problem (HNP-style) — `lcg-truncated`. The bound `l_i < 2^b` is
what makes the lattice close.

## The combiner nuance

A nonlinear combiner over `k` LFSRs has linear complexity ≈ product of
the widths — BM returns `L ≈ n/2`, the falsifier. The attack is then a
correlation attack (each LFSR correlated to the output) — out of this
module's plain-LFSR scope.

## The falsifier is the theory

Every attack's falsifier is "the model didn't fit": `gcd` didn't pin `m`,
BM's `L ≈ n/2`, `predict != held`. The theory says the structure is there;
the falsifier says it isn't — reclassify.
