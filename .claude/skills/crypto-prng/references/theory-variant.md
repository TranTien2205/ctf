# Theory variant — the attacks restated as information problems

## The state-recovery reframe

Each attack answers "how many output bits pin the state?"

- **LCG (m known)**: state `~log2 m`, output `~log2 m` per step — 3 steps
  pin `(state, a, c)` — three unknowns, three equations.
- **LCG (m unknown)**: add `m` to the unknowns — 6 steps for the gcd to
  pin all four.
- **LCG truncated**: the low `b` bits per output are unknown — the
  lattice trades more outputs for the missing low bits.
- **LFSR w**: `w` bits of state, 1 bit per output — `2w` outputs pin
  `(state, taps)`.
- **MT19937**: 19968 bits, 32 per output — exactly 624 outputs.
- **xorshift128**: 128 bits, 32 per output — exactly 4 outputs.
- **seed**: `log2 window` bits, the full output per try — window-size
  tries.

## Why the count floor is tight

The floor `S/O` is necessary and (for linear `F`) sufficient:

- **necessary** — fewer than `S` output bits can't pin `S` state bits.
- **sufficient** — for linear `F`/`G` the `S` equations are independent —
  the system has full rank — a unique state.

A nonlinear `G` (a combiner, a CSPRNG) breaks sufficiency — the outputs
aren't linear equations in the state.

## The linearity spectrum

| Generator | `F` linear? | `G` invertible? | Attack |
|---|---|---|---|
| LCG | affine mod m | yes (raw) | telescope gcd |
| LFSR | GF(2)-linear | 1-bit output | BM + state solve |
| MT | GF(2)-linear twist | `untemper` bijection | untemper 624 |
| xorshift | GF(2)-linear | `w` = whole word | 4-word solve |
| combiner-LFSR | GF(2)-linear | `f` NONlinear | correlation, not BM |
| CSPRNG | nonlinear stir | one-way | none |

The spectrum is the class: left side = this module's attacks; right side
= the boundary.

## The seed-search reframe

`state_0 = init(seed)` is a different entry — not an output leak but a
search over `seed`. The floor is `|seed space|` tries, not `S/O` outputs.
`time()`/`pid` collapse `|seed|` to enumerable size.

## The truncation reframe

`G = x>>b` drops `b` bits — `G` is no longer invertible. The unknown low
bits `l_i` are bounded `<2^b` — the bounded-unknown structure is exactly
Hidden-Number — the lattice. The tighter `b`, the fewer outputs the
lattice needs.

## The falsifier reframe

"The model didn't fit" is the theory running in reverse:

- `gcd → 0/1`: the outputs don't satisfy `t_{i+1}=a·t_i` — not affine.
- `L ≈ n/2`: no short recurrence — not a plain LFSR.
- `predict != held`: the recovered `(a,c,m)`/`state` doesn't extrapolate —
  wrong model.

## The boundary reframe

A CSPRNG's `G` is a one-way function (`AES`/`hash`) — `G` doesn't leak
`state` no matter how many outputs — the `S/O` floor is infinite. That's
the boundary: not a harder version of the same problem, a different
problem entirely.
