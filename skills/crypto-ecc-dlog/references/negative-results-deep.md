# Negative results deep — the no's with their reopeners

## `ecdsa-nonce-reuse` no's

| No | Meaning | Reopen if |
|---|---|---|
| no dup `r` in N sigs | no reuse | new sigs, or `k` biased → hnp |
| `d·G ≠ Q` after solve | `r`/`z`/`n` wrong | recompute `z` other convention |

## `hnp-ecdsa` no's

| No | Meaning | Reopen if |
|---|---|---|
| verify fails at count | biased nonce wrong | more sigs / wider `B` |
| lattice junk | `B` too tight / outlier | prune sigs, widen `B` |

## `pohlig-hellman` no's

| No | Meaning | Reopen if |
|---|---|---|
| largest factor > 2⁴⁰ | not PH-able | `x` bounded → `bsgs` |
| `g^x ≠ h` | `ord`/`h` wrong | subgroup check `pow(h,ord,p)` |

## `bsgs` no's

| No | Meaning | Reopen if |
|---|---|---|
| no collision | `x` outside bound | bigger bound, `ord` recheck |
| `ord` > 2⁴⁴ | ceiling | PH or defect |

## `smart_attack`/`singular_ec` no's

| No | Meaning | Reopen if |
|---|---|---|
| `#E ≠ p` / `Δ ≠ 0` | not that defect | other defect / protocol bug |

## Invalid curve no's

| No | Meaning |
|---|---|
| validation error | impossible — server checks points |

## The record

Every no goes to `knowledge/attempts/<challenge>.json` with the falsifier
and its reopener — the next attempt skips them.
