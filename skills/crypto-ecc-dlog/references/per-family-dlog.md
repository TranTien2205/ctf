# Dlog family — `h = g^x mod p` and `Q = x·P`

## The two generic attacks

| Shape | Attack | Command |
|---|---|---|
| `ord(g)`/`#E` smooth | `pohlig-hellman` | `--g g --h h --p p --order n` |
| `x` bounded / small `n` | `bsgs` | `--g g --h h --p p --order n` |
| order unknown | `smoothness` | `--n n` |

## The order decision

- `ord(g)` = `p-1` when `g` generates `Fp*`; a proper subgroup otherwise.
- `#E` for curves — the challenge supplies it or you compute it.
- `smoothness --n <order>` is the gate — largest factor decides PH feasibility.

## The bounded `x` read

If the challenge says `x < 2^40` → that's `bsgs` with `order` = the bound.
If `x` unstated → `bsgs` needs `ord(g) ≤ 2^44`.

## On curves

`dlog.bsgs`/`dlog.pohlig_hellman` are written for multiplicative groups;
on `Q = x·P` use the same math with `ec.py` point arithmetic — the order
logic is identical.

## The boundary

Generic `√n` is the ceiling — above ~2⁴⁴ you need a *defect* (anomalous,
singular, smooth, invalid) or the attack isn't dlog-shaped at all.
