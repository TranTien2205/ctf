# Negative results variant — recording the no's, restated

## The `attempts` JSON shape

```json
{
  "attack": "<id>",
  "result": "<falsified|verify-failed|out-of-reach>",
  "falsifier": "<what killed it>",
  "reopen_if": "<what would change the no>"
}
```

## The `falsified` entries

- `ecdsa-nonce-reuse` + `no-duplicate-r` → reopen on a dup `r`.
- `smart_attack` + `#E != p` → reopen on anomalous params.

## The `verify-failed` entries

- `hnp-ecdsa` + `d·G != Q` → reopen on corrected `z`/`ord`/bound.
- `pohlig-hellman` + `g^x != h` → reopen on corrected `ord`/`h∈<g>`.

## The `out-of-reach` entries

- `bsgs` + `ord > 2^44` → reopen on a bounded-`x` hint.
- `pohlig-hellman` + `factor > 2^40` → reopen on a smooth-order variant.

## Why record

`knowledge/attempts/` is the kill map — the next attempt reads the no
instead of re-walking the dead layer.
