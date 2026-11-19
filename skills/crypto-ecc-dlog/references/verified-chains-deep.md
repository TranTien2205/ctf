# Verified chains deep — what a real card would carry

## The card anatomy

A `knowledge/chains/` card for a `crypto-ecc-dlog` solve:

```json
{
  "id": "ecc-<slug>",
  "class": "crypto-ecc-dlog",
  "signals": ["ecdsa", "nonce", "secp256k1"],
  "chain": ["sigs", "r-dedupe", "ecdsa-nonce-reuse", "d·G == Q", "flag"],
  "first_confirming_probe": "crypto_attack.py ecdsa-nonce-reuse --sigs sigs.json --order n",
  "falsifier": "no duplicate r in sigs",
  "blast_radius": "read-only — offline math"
}
```

## The traps a card records

- The `z` convention that worked (truncation vs `mod n`).
- The `--order` value — `n` vs `p` mistake to avoid.
- The sig count/bound that made the lattice converge.
- The `--sigs` format detail that tripped the first attempt.

## The patterns a card captures

| Pattern | Attack |
|---|---|
| `r` dup | `ecdsa-nonce-reuse` |
| `k < B` sigs | `hnp-ecdsa` |
| `(t,u)` leak | `hnp` |
| smooth `ord` | `pohlig-hellman` |
| bounded `x` | `bsgs` |
| `#E == p` | `smart_attack` |
| `Δ == 0` | `singular_ec` |
| unvalidated `P` | invalid curve |

## The honest status

Zero cards today — the corpus is the field procedure; the first solve
writes the first confirmed card.
