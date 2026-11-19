# Probe order — cheapest first, always

## The gates in cost order

1. **Inventory scan** — `r` values deduped. Cost: free.
2. **`smoothness --n <ord>`** — factoring gate. Cost: seconds.
3. **`Δ mod p` check** — `4a³+27b² mod p`. Cost: free.
4. **`#E == p` check** — point count comparison. Cost: free (if `#E` given).
5. **`required_signatures`** — do you have enough sigs? Cost: free.
6. **`ecdsa-nonce-reuse`** — closed form, instant.
7. **`bsgs`** — `O(√n)` — only if `n` small/bounded.
8. **`pohlig-hellman`** — per-factor — only if smooth.
9. **`hnp-ecdsa`/`hnp`** — lattice — last resort for nonce bias.
10. **`smart_attack`/`singular_ec`** — defect — when the gates said so.
11. **invalid curve** — oracle — when the server exists.

## The two non-starters (don't probe)

- One signature, no bound → nothing to do.
- Safe-prime `p-1 = 2q` → PH useless.

## The "stop and re-read" moments

- `bsgs` no match → don't retry with bigger `B` — check `h ∈ <g>` and
  `ord(g)` instead.
- `hnp-ecdsa` wrong `d` → don't raise `--nonce-bits` blindly — the bound
  must come from the challenge's actual `k` construction.

## The verify moment

After *any* solve — `x·G == Q`/`g^x == h` — before recording anything.
