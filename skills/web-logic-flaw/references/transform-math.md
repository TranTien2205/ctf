# Transform math — the wrap arithmetic for the Pachinko shape

The verified card's core: `addr = off + id·S mod 2^w`. This module is
the computation — how to find the `id` that lands the transform on the
target.

## The parameters

- `off` — the base offset: where `id=0` writes. Source: the loader's
  array base + header size + alignment.
- `S` — the stride/scale: bytes per index unit. Source: the element
  size in source (`id*4`, `id*8`, `id*recordSize`) or measured from two
  known `id → address` observations.
- `w` — the word width: the modulus — index width, pointer width, or
  the memory-space width (WASM linear memory addressing).
- `T` — the target address: instruction memory, an adjacent object, a
  privileged field.
- `LIMIT` — the checker's bound on `id`.

## Solving for id

Case 1 — `S` odd (invertible mod `2^w`):

```
id ≡ (T - off) · S⁻¹     (mod 2^w)
S⁻¹ = S^(2^(w-1) - 1) mod 2^w          — or extended Euclid
```

Case 2 — `S` even:

```
g = gcd(S, 2^w)
solvable iff g | (T - off)
id ≡ ((T - off)/g) · (S/g)⁻¹     (mod 2^w/g)
solutions: id + k·(2^w/g),  k = 0..g-1
```

Then pick the solution in `[0, LIMIT)` — or in whatever range the
CHECKER accepts (which may exceed `LIMIT` when the check itself is
flawed — a different-layer rejection measures the real bound).

## Worked example (the card's shape, parameterized)

Suppose `off = 0x1000`, `S = 4`, `w = 16` (16-bit index space), target
instruction at `T = 0x0020`:

```
g = gcd(4, 65536) = 4
T - off = 0x0020 - 0x1000 = -0xFE0 ≡ 0xF020 (mod 0x10000)
0xF020 / 4 = 0x3C08
id ≡ 0x3C08 · 1⁻¹ = 0x3C08 (mod 0x4000)    — 4 solutions spaced 0x4000
id ∈ {0x3C08, 0x7C08, 0xBC08, 0xFC08}
```

Pick the `id` inside the checker's accepted range — the one whose
transformed address lands on `T` is a checked-index write into
instruction space.

## The measurement path when `off`/`S`/`w` are unknown

- `S`: two accepted `id` values + their write addresses →
  `S = (a2 - a1)/(id2 - id1)`.
- `off`: `a1 - id1·S`.
- `w`: the width where observed addresses wrap — binary-search `id`
  values that wrap the address space.
- the reachable class: enumerate `off + id·S mod 2^w` for accepted `id`s
  and pick the target INSIDE it — don't force an unreachable `T`.

## Signedness and negative strides

- `S < 0`: `id` grows, address shrinks — reaches BELOW `off`.
- `id` checked unsigned, arithmetic signed: `id ∈ [INT_MAX+1, UINT_MAX]`
  reads negative on the signed side — `off + (-k)·S`.
- `id` checked signed `id >= 0`, stored unsigned: `-1` → `UINT_MAX` →
  `off + UINT_MAX·S mod 2^w` — near-`off-S` target.

## The write width

The card's write was 2 bytes — the write's width decides what `T` can
be: a 2-byte instruction patch, a 4-byte pointer overwrite, a single
byte flag flip. The exploitable `T` set is `{targets writable in the
write's width at a reachable address}`.

## The shared-memory question

The last Pachinko link: the transformed address landed where the
interpreter executes — data and code shared one space. For a new
target ask the same question: what does the sink's memory region ALSO
contain? Program bytes (execute-on-write), privileged objects
(corrupt-on-write), or flag fields (read-on-write)? The target type
decides the payload.
