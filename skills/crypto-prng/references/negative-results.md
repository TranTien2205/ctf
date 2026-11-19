# Negative results — recording the no's

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

- `mt19937-clone` + `623 outputs` → reopen on a 624th consecutive word.
- `lfsr-recover` + `linear complexity ~ stream` → reopen on a plain LFSR.
- `lcg-recover` + `x1-x0 not invertible` → reopen on more outputs/`m`.

## The `verify-failed` entries

- `lcg-truncated` + `predict != held-back` → reopen on corrected
  `--low-bits`/`m`/`a`/`c`.
- `mt19937-clone` + `predict != held-back` → reopen on raw `getrandbits(32)`
  instead of `random()` floats.

## The `out-of-reach` entries

- `mt19937-clone` + `outputs < 624` → reopen on a full window.
- `xorshift128` + `<4 outputs` → reopen on the 4th.
- seed-search + `unbounded window` → reopen on a stated epoch.
- any + `os.urandom`/`secrets`/`keyed` → reopen on a real PRNG.

## Why record

`knowledge/attempts/` is the kill map — the next attempt reads the no
instead of re-walking the dead generator hypothesis.
