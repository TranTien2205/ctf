# Per-family dlog deep — the dlog family, expanded

## The three components

| Component | Role | Files |
|---|---|---|
| `smoothness` | the gate — `ord` factor sizes | `per-attack-smoothness.md`,`smoothness-deep.md` |
| `pohlig-hellman` | `ord` smooth → CRT solve | `per-attack-pohlig-hellman.md`,`pohlig-hellman-deep.md` |
| `bsgs` | `x`/`ord` bounded → √n collision | `per-attack-bsgs.md`,`bsgs-deep.md` |

## The discriminator

```
smoothness --n ord →
  largest ≤ 2^40 → pohlig-hellman
  x bounded      → bsgs
  else           → safe-prime / not-dlog — re-read
```

`smoothness` is always first — it's the cheapest read and gates the family.

## The `--order` nuance

- `pohlig-hellman --order <ord(g)>` — the real subgroup order.
- `bsgs --order <bound>` — the bound on `x`, OR `ord(g)` when `x < ord`.

## The `h ∈ <g>` gate

`pow(h, ord, p) == 1` before either attack — `h` outside `<g>` has no `x`
in this formulation.

## The verify

`pow(g, x, p) == h` — the only accept.
