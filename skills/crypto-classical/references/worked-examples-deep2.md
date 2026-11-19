# Worked examples deep 2 — more annotated solves

## The ROT13 flag

```python
import codecs
codecs.decode('synt{ebg13_vf_gnfgl}', 'rot13')  # → 'flag{rot13_is_tasty}'
```

## The format-anchored subst

```python
# ct = 'gsdh{abc...}' — flag{ at pos 0-4
# σ⁻¹(g)=f, σ⁻¹(s)=l, σ⁻¹(d)=a, σ⁻¹(h)=g, σ⁻¹('{')='{'
# → σ anchored → the rest of the decode follows
```

## The Beaufort

```bash
# the Vigenere decode gives garbage — try the reciprocal
# c = k - p → p = k - c → decode with 'key' subtracted
```

## The columnar

```python
# n=24, w=4, key 'ZEBR' → columns 3,1,0,2
# fill 6×4 row-major; read cols in ZEbra order → the ct
# decode: read the cols in key order, write row-major
```

## The layered chain

```python
import base64
l1 = base64.b64decode(ct)          # → caesar
l2 = caesar(l1, k=3)               # → morse
l3 = morse(l2)                     # → flag{...}
# cipher_id on l1 → 'encoding'; on l2 → 'caesar'; on l3 → 'flag'
```

## The verify

`pt` language + `enc(pt)=ct`.
