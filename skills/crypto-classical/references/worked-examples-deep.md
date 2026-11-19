# Worked examples deep — the annotated solves

## Solve 1 — Caesar

```bash
python3 tools/cipher_id.py --text 'WKHHDWHUHDWGVZQ'
# IC ~0.066 — monoalphabetic. chi² min at k=3.
python3 tools/classical_solve.py caesar --text 'WKHHDWHUHDWGVZQ'
# k=3 → THEEATERATSW...  → the flag
```

## Solve 2 — Vigenere

```bash
python3 tools/cipher_id.py --text 'LXFOPVEFRNHR'
# IC ~0.038 — polyalphabetic. Kasiski → L=5.
python3 tools/classical_solve.py vigenere --text 'LXFOPVEFRNHR' --keylen 5
# → key LEMON → ATTACKATDAWN → the flag
```

## Solve 3 — substitution

```bash
python3 tools/classical_solve.py subst --text 'CT'
# → annealed σ → near-English → 'gLAG{...}' → σ(g)=f → flag{...}
```

## Solve 4 — rail-fence

```bash
python3 tools/classical_solve.py railfence --text 'CT'
# → depth 3 → THE... → the flag
```

## Solve 5 — the layered

```python
import base64, codecs
layer1 = base64.b64decode(ct)           # → a caesar-shifted string
layer2 = caesar_decode(layer1, 3)       # → morse
layer3 = morse_decode(layer2)           # → flag{...}
```

`cipher_id` on each layer — the charset tells the next decode.

## Solve 6 — the format-leak

`ct` starts `gsdh` — if `flag{` is at position 0 → `σ(g)=f`,`σ(s)=l`,`σ(d)=a`,
`σ(h)=g` → the `σ` anchored → `subst` polishes the rest.

## The verify

`pt` language + `enc(pt)=ct`.
