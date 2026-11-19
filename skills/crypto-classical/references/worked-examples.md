# Worked examples — the annotated solves

## Example 1 — Caesar

```bash
python3 tools/cipher_id.py --text 'WKHHDWHUHDWGVZQ'
# IC ~0.066 — monoalphabetic. chi² min at k=3.
python3 tools/classical_solve.py caesar --text 'WKHHDWHUHDWGVZQ'
# k=3 → 'THEEATERATSW...' — the flag
```

## Example 2 — Vigenere

```bash
python3 tools/cipher_id.py --text 'LXFOPVEFRNHR'
# IC ~0.038 — polyalphabetic. Kasiski → L=5.
python3 tools/classical_solve.py vigenere --text 'LXFOPVEFRNHR' --keylen 5
# → key LEMON → 'ATTACKATDAWN' — the flag
```

## Example 3 — substitution

```bash
python3 tools/classical_solve.py subst --text 'CT'
# → annealed σ → 'gLAG{...}' — σ⁻¹(g) should be f → 'flag{...}'
```

## Example 4 — rail-fence

```bash
python3 tools/classical_solve.py railfence --text 'CT'
# → depth 3 → 'THE...' — the flag
```

## Example 5 — the layered

```python
import base64, codecs
layer1 = base64.b64decode(ct)     # → a caesar-shifted string
layer2 = caesar_decode(layer1, 3) # → morse
layer3 = morse_decode(layer2)     # → flag{...}
```

`cipher_id` on each layer — the charset tells the next decode.

## Example 6 — the format-leak

`ct` starts `gsdh` — `flag{` at position 0 → `σ⁻¹(g)=f`,`σ⁻¹(s)=l`,
`σ⁻¹(d)=a`,`σ⁻¹(h)=g` → the `σ` anchored → `subst` polishes the rest.
