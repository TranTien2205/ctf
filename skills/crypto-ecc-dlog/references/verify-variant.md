# Verify variant — the proof checks, compact

## The scalar checks

```python
assert E.mul(G, d) == E.point(*Q)   # curve:  d·G == Q
assert pow(g, x, p) == h            # field:  g^x == h
assert pow(h, ord, p) == 1          # h ∈ <g>
```

## The sig checks (reuse)

```python
# same r already enforced by the dedupe; the real proof is d·G == Q
```

## The `hnp`/`hnp-ecdsa` check

- The lattice returns a `d` candidate — `d·G == Q` is the only accept.

## The `pohlig`/`bsgs` check

- `pow(g, x, p) == h` — the `x` is right only when it recomputes `h`.

## The defect check

- `smart`/`singular` → `x` → `x·G == Q` on the ORIGINAL curve.
- invalid curve → `d` → `d·G == Q` on the real curve.

## The flag check

`flag{...}`/`CTF{...}` in the decoded bytes — `class` evidence is the
scalar; `impact` evidence is the flag.
