# Negative map — the observed-negative → the class it rules out

## The negatives, by observation

| You observed | It rules out |
|---|---|
| every `gcd(ni,nj)=1` | `batch-gcd` — no shared prime |
| `gcd(e1,e2)>1` | `common-modulus` — `m^gcd`, not `m` |
| `a` past budget, no `a²-n` square | `fermat` — `|p-q|` too large |
| `d ≥ n^0.25` | `wiener` — escalate to `boneh-durfee` |
| `d ≥ n^0.292` | `wiener`+`boneh-durfee` — small-d dead |
| known window `< n^0.25` | `coppersmith-*` — need a bigger leak |
| `m^e ≥ n` | `small-e-root`/`nth-root` — wrapped |
| `<e` ciphertexts / a pad | `hastad` — product too small / `m` differs |
| `gcd(a^M-1,n)=1` for `B` | `pollard-pm1` — `p-1` not smooth enough |
| relation not linear | `franklin_reiter` — needs `m2=a·m1+b` |
| `∏pi≤m` / no fault | `crt` — wraps / Bellcore impossible |
| `d`/`phi` fails `pow` | `factor-from-d`/`rsa-decrypt` — wrong input |

## The negatives → the fallback

| Closed | Try next |
|---|---|
| batch-gcd | per-`n` single attacks |
| wiener | boneh-durfee |
| boneh-durfee | a leak / another class |
| small-e-root | hastad (e n's) or coppersmith |
| hastad | coppersmith / franklin-reiter |
| fermat | pollard-pm1 / a leak |
| common-modulus | nth-root if `m^g<n` |
| coppersmith | a bigger leak / another attack |
| pollard-pm1 | a different precondition |
| franklin-reiter | a different relation |
| all bounds met | reclassify — protocol/oracle class |

## The kill-map

`knowledge/attempts/<challenge>.json` — each dead attack's id, the measured
bound, and the precondition that would reopen it.
