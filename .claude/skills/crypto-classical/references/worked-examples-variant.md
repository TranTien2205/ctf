# Worked examples variant — the solves, by family

## `caesar` — `k` from chi²

```bash
cipher_id --text 'WKHHDWHUHDWGVZQ'   # IC ~0.066, chi² min k=3
classical_solve caesar --text 'WKHHDWHUHDWGVZQ'   # → THEEATERATSW...
```

## `atbash` — the reflection

```bash
cipher_id --text 'GSVUFOGXZMTSRMGIVZMW'   # reversed ETAOIN
classical_solve atbash --text 'GSVUFOGXZMTSRMGIVZMW'   # → the flag
```

## `subst` — the anneal

```bash
cipher_id --text 'CT'   # IC ~0.066, flat chi²
classical_solve subst --text 'CT' --restarts 8
# → σ → 'gLAG{...}' → σ⁻¹(g)=f → 'flag{...}'
```

## `vigenere` — `L` from Kasiski

```bash
cipher_id --text 'LXFOPVEFRNHR'   # IC ~0.038, Kasiski L=5
classical_solve vigenere --text 'LXFOPVEFRNHR' --keylen 5
# → key LEMON → ATTACKATDAWN
```

## `railfence` — the depth

```bash
cipher_id --text 'CT'   # IC ~0.05, scrambled letters
classical_solve railfence --text 'CT'   # → depth 3 → THE...
```

## The layered — `enc → cipher → enc`

```python
import base64
l1 = base64.b64decode(ct)      # → caesar
l2 = caesar_decode(l1, 3)      # → morse
l3 = morse_decode(l2)          # → flag{...}
```

## The verify

`pt` language + `enc(pt)=ct`.
