# Negative results — recorded dead ends

## Standing

A negative result is evidence — it closes a layer so the next attempt doesn't
re-walk it. `knowledge/attempts/<challenge>.json` holds the kill map; this file
records the *class-level* negatives — the bounds that fail across the corpus.

## The falsifier → the negative

| Falsifier observed | It closes |
|---|---|
| `gcd(ni,nj)=1` for all pairs | `batch-gcd` |
| `gcd(e1,e2)>1` | `common-modulus` |
| `a` walked past budget, `a²-n` never square | `fermat` |
| `d ≥ n^0.25` | `wiener` |
| `d ≥ n^0.292` | `wiener` + `boneh-durfee` — small-d closed |
| unknown window `< n^0.25` | `coppersmith-*` |
| `m^e ≥ n` | `small-e-root`/`nth-root` |
| `<e` n's / a pad on `m` | `hastad` |
| `gcd(a^{B!}-1,n)=1` for `B` | `pollard-pm1` at `B` |
| `m2` not `a·m1+b` | `franklin-reiter` |
| `∏pi ≤ m` / no fault | `crt` |
| `d`/`phi` fails `pow` | `factor-from-d`/`rsa-decrypt` — wrong input |
| `gcd(e,phi)=1` | `eth-root` — normal `inverse` |

## The record shape

`knowledge/attempts/<challenge>.json`:
```json
{
  "challenge": "<name>",
  "class": "crypto-rsa",
  "attempts": [
    {"attack": "wiener", "bound": "d<n^0.25", "observed": "d~n^0.4", "verdict": "closed"},
    {"attack": "batch-gcd", "observed": "all gcd=1", "verdict": "closed"}
  ]
}
```

## The escalation

A recorded negative + a spent budget → `tools/decide.py` names the next rung:
`chain_match`, `reclassify`, `writeup_search`, `novel_plan`, `fanout_sweep`,
`solver_handoff`. The negative is *why* the rung is spent.
