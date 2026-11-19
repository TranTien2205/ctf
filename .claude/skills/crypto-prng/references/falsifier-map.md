# Falsifier map — observation → kill → action

## The output-shape kills

| Observation | Kill | Action |
|---|---|---|
| floats `x.xx` | not a raw word | convert `×2**53` pair or re-collect as ints |
| `x mod n` | reduced state | this is `lcg-truncated`-like or not-cloneable |
| hex/base64 | not raw | decode to int |
| gaps in stream | not consecutive | re-collect contiguous window |

## The count kills

| Count | Kill | Action |
|---|---|---|
| <3 lcg outs | can't solve | collect more |
| <6 unknown-mod | gcd unpinned | collect more |
| <2w lfsr bits | recurrence unpinned | collect more |
| <624 mt words | NO clone | seed-search/re-collect |
| <4 xorshift | underdetermined | collect more |

## The mechanism kills

| Signal | Kill | Action |
|---|---|---|
| gcd collapses to 0/1 | not affine | reclassify |
| linear complexity ≈ n | not plain LFSR | combiner → correlation attack |
| `predict != held` | wrong params/variant | troubleshoot |
| seed unbounded | CSPRNG | wrong class |
| `predict != held` everywhere | keyed/CSPRNG | reclassify |

## The action ladder

```
predict != held → troubleshoot* → still fail → record falsifier → attempts
→ decide.py next rung → stop when rungs spent
```
