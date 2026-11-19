# Per-attack invalid-curve deep — the card, expanded

## The trigger

An oracle `multiply(P)`/`sign(P)`/`DH(P)` that accepts `P` without checking
`P ∈ E` — off-curve points land on a different curve `E'` sharing `p` and
`a` but with `b' = y² - x³ - ax`.

## The command

```bash
python3 -c "from tools.crypto import ec"   # library module — no __main__   # offline check
# the attack is a procedure, not a single command:
#  for each fake curve E'_i with smooth ord:
#    submit P'_i → oracle → d·P'_i
#    bsgs/pohlig-hellman → d mod ord_i
#  CRT → d
```

## The mechanism

Pick `P'` on `E'_i` with small smooth `ord_i` → oracle returns `d·P'_i` →
`bsgs`/`pohlig` → `d mod ord_i` → CRT over several `E'_i` → `d`.

## The verification

`d·G == Q` on the REAL curve.

## The falsifiers

- `P'` rejected → validation present → attack impossible.
- `ord_i` too big per fake curve → no `d mod ord_i`.

## The boundary

- Only works where validation is absent — `on_curve(P)` is the kill.
- `ord_i` must be small enough for `bsgs` — large `ord_i` gives nothing.
- The `b'` computation: `b' = (y'² - x'³ - a·x') mod p` for the fake `P'`.

## The CRT step

`d ≡ d_i (mod ord_i)` across `i` → CRT → `d` when `∏ord_i ≥ ord(G)`.
