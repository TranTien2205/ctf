# atbash deep — the reflection, annotated

## The transform

`c = 25 - p` — the alphabet reversed. `A↔Z`, `B↔Y`, ..., `M↔N`. Self-inverse:
`ct(ct(p)) = p`.

## The detection — the signal

- **IC ~0.066** — a bijection preserves it.
- **The freq is a *reversed* ETAOIN** — `σ(E)=V`, `σ(T)=G`, `σ(A)=Z` — the
  common `ct` letters are `Z,V,G,...` (the rares' images), not a rotation.
- **`flag{` → `uozt{`** — the format reads reversed — a dead giveaway.

## The solve

```bash
python3 tools/classical_solve.py atbash --text 'CT'   # the reflection
```

```python
''.join(chr(25 - (ord(c) - 65) + 65) for c in ct)
```

## The verify

`pt` language; `atbash(pt)` reproduces `ct`.

## The falsifier

The reflection produces garbage → a different `σ` → `subst`.

## The trap

`atbash` is a special `σ` — a `subst` anneal also solves it but slower. Try
`atbash` first when the freq is a *reversed* ETAOIN.
