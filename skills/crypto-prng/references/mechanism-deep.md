# Mechanism deep — the generators as machines

## The machine model

```
state_{i+1} = F(state_i)       # advance
output_i    = G(state_i)       # emit
```

`F` advances, `G` emits. The attack inverts `G` on enough outputs to pin
the state, then runs `F` forward. Every generator below is an `(F,G)` pair.

## LCG — `F` affine mod m, `G` identity-ish

```
F: x ← a·x + c mod m
G: x ↦ x            (raw)   or   x>>b (truncated)   or   x mod n
```

`F` affine → telescope differences kill `c`, gcd kills `m`. `G` identity →
direct solve; `G` truncated → lattice (HNP). `G` = `mod n` → reduced, not
invertible.

## LFSR — `F` linear GF(2), `G` = end bit

```
F: register shifts; new bit = XOR of tap bits
G: register ↦ the shifted-out bit (1 bit per clock)
```

`F` linear GF(2) → `w` outputs are `w` linear equations in `w` state bits.
`G` = 1 bit → `2w` bits for BM to pin the taps. A combiner `G` = `f(x_1,
..., x_k)` nonlinear → complexity ≈ product → the falsifier.

## MT19937 — `F` linear twist, `G` invertible temper

```
F: every 624 outputs, state ← twist(state)  (linear GF(2))
G: state[i] ↦ temper(state[i])  (invertible 32-bit)
```

`G` invertible → `untemper` each of 624 words → the state. `F` known →
roll forward. The output bits don't scramble the state — `G` is a
per-word bijection.

## xorshift128 — `F` linear GF(2), `G` = `w`

```
F: x,y,z,w ← y,z,w, w^(w>>19)^(x^(x<<11))^((x^(x<<11))>>8)
G: state ↦ w   (one word)
```

`F` linear GF(2), `G` = a whole word. 4 outputs = the state (the `w`s are
the register). `G` is identity on the emitted word — `untemper` isn't even
needed.

## The seed — `state_0 = f(seed)`

```
seed → state_0 (the init)
```

Not an `(F,G)` leak — the attack enumerates `state_0` from a bounded seed
space. `f` is the generator's init (`init_genrand` for MT, the LCG seed,
the LFSR load).

## The CSPRNG — `G` one-way

```
F: state ← stir(state, entropy)
G: state ↦ AES(state)/hash(state) — NOT invertible
```

`G` one-way → no short output leaks the state. `F` reseeds → the window
breaks. Out of scope — the class boundary.

## The post-processing wrapper

Real oracles wrap `G`: `randint = (G(state)·(b-a))/m + a`, `choice = seq[G
% len]`, `random() = G_pair/2^53`. The observation is `H(G(state))` —
normalize to `G(state)` before the attack, or the model is wrong.

## The reseed

`seed()` between outputs resets `state` and index — `output_i` no longer
share one `state_i` chain. Detect the discontinuity; collect within one
contiguous window.

## The alignment

"Consecutive" means `output_i` and `output_{i+1}` are adjacent in the
stream — no other caller consumed the generator between them. A shared
`random` module makes your outputs non-consecutive — the clone is off by
the gap.
