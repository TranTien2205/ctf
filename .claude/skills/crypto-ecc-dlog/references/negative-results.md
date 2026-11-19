# Negative results — the no's that still count

## The no's and what they rule out

| Result | Rules out | Reopen if |
|---|---|---|
| no duplicate `r` in N sigs | `ecdsa-nonce-reuse` | new sigs arrive |
| `hnp-ecdsa` verify fails with correct count/bound | biased-nonce | better `B`/more sigs |
| `smoothness` says largest factor > 2⁴⁰ | `pohlig-hellman` | smaller bound, different group |
| `bsgs` no collision inside `ord(g)` | bounded-`x` | `x` estimate wrong |
| `#E ≠ p` | `smart_attack` | — |
| `Δ ≠ 0 mod p` | `singular_ec` | — |
| server validates points | invalid-curve | — |
| `x·G ≠ Q` everywhere | this class | re-route |

## The format

`knowledge/attempts/<challenge>.json`:

```json
{
  "challenge": "name",
  "attempts": [
    {"attack": "hnp-ecdsa", "result": "verify-failed",
     "falsifier": "d·G != Q with 8 sigs, B=2^128",
     "reopen_if": "challenge supplies a nonce bound"}
  ]
}
```

## The record

`tools/state.py <challenge> --hypothesis … --verdict falsified` + the JSON
entry. The next attempt skips the dead ends — the budget resets on the
remaining strategies, not the challenge.
