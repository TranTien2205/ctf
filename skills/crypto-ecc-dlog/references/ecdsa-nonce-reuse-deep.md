# `ecdsa-nonce-reuse` — the closed-form key recovery

## When it applies

Two ECDSA signatures with the **same `r` value** — identical nonce `k`. The
most common CTF shape and the cheapest check: scan all `r` values for a
duplicate before reaching for any lattice.

## The math

```
s₁ = k⁻¹(z₁ + d·r)   s₂ = k⁻¹(z₂ + d·r)   (mod n)

k = (z₁ - z₂) / (s₁ - s₂)        mod n
d = (s₁·k - z₁) / r              mod n
```

One division each — no lattice, no heuristics.

## The command

```bash
python3 tools/crypto_attack.py ecdsa-nonce-reuse --sigs sigs.json --order <n>
```

`sigs.json` is a list of `[r, s, z]` triples or `{"r","s","z"}` objects;
the first two entries are used. `order` is the curve order `n`
(secp256k1: `0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141`).

In code:

```python
from tools.crypto import hnp
d = hnp.ecdsa_recover_nonce_reuse(
    {"r": r, "s": s1, "z": z1},
    {"r": r, "s": s2, "z": z2},
    order,
)
```

## Preconditions

- Exactly the same `r` — byte-identical, not "similar". Similar nonces are
  the biased case → `hnp-ecdsa`.
- Correct `z` — hash of each message as integer (FIPS truncation first,
  `mod n` second if the result fails verify).
- Correct `order` — the curve's subgroup order, not the field prime `p`.

## Falsifier

The recovered `d` must satisfy `d·G == Q`. If it doesn't:

- `z` computed wrong → recompute with the other convention.
- The two `r`s weren't actually equal → re-check bytes.
- Wrong `order` → for named curves use the published `n`.

## Finding reuse at scale

With N signatures sort by `r`; a duplicate `r` means reuse across *any*
pair of messages — not necessarily consecutive. A signing oracle that returns
identical `(r, s)` for identical input uses deterministic `k` (RFC 6979);
for reuse across *different* messages you need a broken RNG or a reset.

## Common mistakes

- Using `s` instead of `r` to detect reuse — coincidence on `s` means nothing.
- Mixing up `z` order — `sig[0]` and `sig[1]` are the first two entries of
  the JSON; put the pair with the shared `r` first.
- Treating `r` as the nonce — `r = x(k·G)`, the `k` inside is what repeats.
