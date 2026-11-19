# Per-attack `pohlig-hellman` deep — the card, expanded

## The trigger

`h = g^x mod p` where `ord(g)` is smooth — `smoothness --n ord` shows all
prime factors ≤ ~2⁴⁰.

## The command

```bash
python3 tools/crypto_attack.py pohlig-hellman --g <g> --h <h> --p <p> --order <ord>
```

`--order` is `ord(g)` — often `p-1` for a generator, a subgroup `q` otherwise.

## The mechanism

`ord = ∏ qᵢ^eᵢ` → `x mod qᵢ^eᵢ` from a `qᵢ`-sized dlog each → CRT → `x`.

## The verification

`pow(g, x, p) == h`.

## The falsifiers

- `smoothness` shows a factor > 2⁴⁰ → out of reach.
- `g^x ≠ h` → `ord` wrong or `h ∉ <g>`.

## The boundary

- `h ∉ <g>` (`pow(h, ord, p) ≠ 1`) → the statement is malformed; solve in
  the subgroup `h` actually lives in.
- `x` could be ≥ `ord` → PH returns `x mod ord`; the full `x` may need the
  bound.
- safe-prime `ord = 2q` → `2` and `q` — `q` large → dead.

## The curve variant

Same algorithm on `E` via `ec.py` — `ord = #E` or `ord(G)` smooth → PH
with curve ops.
