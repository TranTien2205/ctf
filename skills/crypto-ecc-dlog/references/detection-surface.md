# Detection surface — the minimal read path

## One read, one route

| Observation | Route |
|---|---|
| two `r` equal | `ecdsa-nonce-reuse` |
| `k` bounded, many sigs | `hnp-ecdsa` |
| `(t,u)` pairs | `hnp` |
| `ord` smooth | `pohlig-hellman` |
| `x` bounded | `bsgs` |
| `ord` ? | `smoothness` |
| `#E == p` | `smart_attack` |
| `Δ == 0` | `singular_ec` |
| unvalidated point | invalid curve |

## The three gates

1. `r` scan.
2. `smoothness --n <ord>`.
3. `Δ`/`#E` check.

## The two verifies

`x·G == Q` · `g^x == h`.

## The one record

`post-probe` → `../field-notes.md`.

## The one escalate

`decide.py` — rungs until `stop_report`.
