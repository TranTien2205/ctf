# caesar catalogue — the shift, every variant

## The family

`c = p + k mod 26` — one `k` for all letters. ROT13 (`k=13`), ROT5 (digits),
ROT18, ROT47 (printable), Atbash (the reflection `c=25-p`).

## The detection

- IC ~0.066 — a monoalphabetic.
- `cipher_id` — a *single* chi² minimum at `k`.
- A name: "caesar"/"rot"/"shift"/"k=N".

## The solve

```bash
classical_solve caesar --text 'CT'     # the 25 ranked — the min is k
classical_solve atbash --text 'CT'     # the reflection
```

```python
# manual — the 25 shifts
for k in range(26):
    print(k, ''.join(chr((ord(c)-65-k)%26+65) for c in ct))
# rot13
import codecs; codecs.decode(ct, 'rot13')
```

## The polish

- A partial decode — letters shifted, digits/punct kept.
- A keyed-alphabet Caesar → `subst` after the offset.
- ROT5/18/47 → `codecs`/a script.

## The verify

The `k` shift produces language; re-shifting `pt` by `k` = `ct`.

## The falsifier

No `k` produces language → `subst` (a non-shift bijection).
