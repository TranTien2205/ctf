# Per-attack `smoothness` deep — the card, expanded

## The trigger — it's a gate, not an attack

`smoothness` never returns a flag — it returns the factor shape of `ord`
that decides `pohlig-hellman` vs `bsgs` vs not-dlog.

## The command

```bash
python3 tools/crypto_attack.py smoothness --n <ord>
```

`--n` is the order to factor-test; `--B` is the smoothness bound.

## The output read

- All factors ≤ `--B` → `ord` is `B`-smooth → `pohlig-hellman` viable.
- A factor > `--B` → not smooth at that bound → `bsgs` or defect.

## The boundary

- `--B` too low → false "not smooth"; raise it to ~2⁴⁰.
- `--B` too high → the factor test itself crawls.
- `ord` unknown → factor `p-1` for a generator, or `#E`/`ord(G)` on curves.

## The gate decisions

| Output | Route |
|---|---|
| smooth at ≤2⁴⁰ | `pohlig-hellman` |
| not smooth, `x` bounded | `bsgs` |
| not smooth, no bound | safe-prime / not-dlog — re-read |

## The verification

The gate isn't verified — the attack it gates is (`pow(g,x,p) == h`).
