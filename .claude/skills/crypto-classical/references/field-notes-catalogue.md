# Field notes catalogue — the notes shape, indexed

## The solve record

```md
## <challenge> — <family>

- **the read**: `cipher_id` → IC X, chi² min k=Y / Kasiski L / flat
- **the family**: `caesar`/`subst`/`vigenere`/`railfence`/atbash
- **the solve**: `classical_solve <f> --text` → `k`/`L`/`σ`/depth
- **the verify**: `pt` = "..." → `enc(pt) == ct` → `flag{...}`
- **the trap**: <what cost time>
```

## The negative record

```md
## <challenge> — negative

- **the try**: `classical_solve caesar --text` → no `k` produces language
- **the close**: not a shift → `subst` re-route
- **the record**: `knowledge/attempts/<challenge>.json`
```

## The layered record

```md
## <challenge> — layered

- layer 1: `cipher_id` → "encoding" → `enc_detect` → a caesar `ct`
- layer 2: `cipher_id` → "caesar" → `classical_solve caesar` → a morse `ct`
- layer 3: `cipher_id` → "encoding" → `enc_detect` → `flag{...}`
```

## The field-notes file

`../field-notes.md` at the skill root — the per-challenge solve log.
