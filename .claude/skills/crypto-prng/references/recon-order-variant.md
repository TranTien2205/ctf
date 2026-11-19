# Recon order variant — the oracle probes, compact

## The probes

1. **baseline** — one call → the shape (int/float/bit/hex).
2. **repeat** — two calls → stream vs fixed.
3. **collect** — k+1 calls → consecutive stream + held-back.
4. **error** — bad request → `m`/seed/gen-name leak.
5. **count** — the ceiling → which attack.
6. **params** — source `MOD`/`a`/`c`/taps/`seed`/`srand`.

## The buys

| Probe | Buys |
|---|---|
| baseline | family hint |
| repeat | stream vs fixed |
| collect | the count + held-back |
| error | the cheapest params leak |
| count | the attack floor |
| params | `m`/`a,c`/taps/`low-bits`/window |

## The boundary reads

- `seed()`/`srand()` in handler → reseeding → seed-search.
- `mod n`/`>>b`/`&mask` → not raw → normalize/truncated.
- `urandom`/`secrets` → out.

## The order rationale

shape→stream→count→params→attack — each probe buys the next gate.
