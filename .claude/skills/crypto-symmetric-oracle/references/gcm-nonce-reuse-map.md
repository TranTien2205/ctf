# GCM nonce reuse — the forbidden attack — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| Two records, same nonce, same key, different AAD/CT | H recoverable | tools/gcm_nonce.py |
| You can submit (ct, tag) pairs for verification | forgery oracle available | forge after H recovered |
| 96-bit nonce built from a counter that wraps or a fixed field | reuse inevitable | collect the pair |

## Falsifier

Falsifier — no nonce ever repeats (checked across all captured records) or the tag check precedes every decrypt attempt uniformly: the forbidden attack has no input. Reclassify toward tag truncation or a different class.
