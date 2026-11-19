# Falsifiers deep — every kill, the meaning, the next action

## The shape falsifiers — the cheap kills

| Falsifier | Means | Action |
|---|---|---|
| `predict!=held` on floats | `random()`/`randint` not raw | normalize or variant |
| `predict!=held` on `x mod n` | reduced not raw `x` | the mod model, not `>>` |
| `predict!=held` on hex | undecoded | decode to int |
| `predict!=held` on gaps | non-consecutive | contiguous window |

## The count falsifiers — the free kills

| Falsifier | Means | Action |
|---|---|---|
| <3 lcg outs | can't solve | collect |
| <6 unknown-mod | gcd unpinned | collect |
| <2w lfsr bits | recurrence unpinned | collect |
| <624 mt words | no clone | seed-search/re-collect |
| <4 xorshift | underdetermined | collect |

## The mechanism falsifiers — the real kills

| Falsifier | Means | Action |
|---|---|---|
| `gcd→0/1` | not affine | not an LCG → re-fingerprint |
| `L≈n/2` | not plain LFSR | combiner → correlation |
| `predict!=held` everywhere | wrong model | re-fingerprint/reclassify |
| seed unbounded | CSPRNG | out of class |

## The param falsifiers

| Falsifier | Means | Action |
|---|---|---|
| `predict!=held` after `lcg-*` | wrong `m`/`a`/`c`/`low-bits` | recount/re-derive |
| `predict` diverges after `lfsr-*` | wrong taps/width/order | re-index/flip |
| `predict!=held` after `mt` | `mt_rand` variant | the PHP MT path |
| `predict!=held` after `xorshift` | `128+`/64* variant | the variant tool |

## The seed falsifiers

| Falsifier | Means | Action |
|---|---|---|
| no seed in window | window too narrow | widen bound |
| no seed in window | wrong call | reproduce the same call |
| window huge | not enumerable | CSPRNG → out |

## The class falsifier — the big kill

`predict != held-back` on every attack AND `os.urandom`/`secrets`/keyed
confirmed → the class is wrong → `crypto-symmetric-oracle` or reclassify.

## The record format

```json
{"mechanism":"mt19937-clone","measurement":"predict_next!=o624 on 624 raw words",
 "proves_dead":"not a clonable MT19937 in this window",
 "reopen_if":"a 624-word contiguous window with no reseed appears"}
```

Then `decide.py` — `chain_match→reclassify→writeup_search→novel_plan→
fanout_sweep→solver_handoff`.
