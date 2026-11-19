# `hnp-ecdsa` — biased-nonce lattice recovery

## When it applies

Many ECDSA signatures with **distinct `r`** values, where every nonce `k` is
bounded: `0 ≤ k < B` for a known or inferable `B`. The bias shapes seen in
CTFs:

- **Short nonce** — "128-bit nonce" on a 256-bit curve → `B = 2^128`,
  `--nonce-bits 128`.
- **Timestamp-seeded `k`** — `k` derived from a unix timestamp →
  `B` covers the timestamp range, `--nonce-bound B`.
- **MSB/LSB bit leak** — the service returns (part of) `k` →
  `hnp`/`hnp-ecdsa` with the bound on the unknown part.

## Signature count

`hnp.required_signatures(order_bits, nonce_bits)`:

| order bits | nonce bits leaked | sigs needed (≈) |
|---|---|---|
| 256 | 128 | ~4 |
| 256 | 8 | ~64 |
| 160 | 8 | ~40 |

Rule of thumb: `sigs ≈ 2·order_bits / leaked_bits`. Too few → the lattice
finds a wrong short vector; too many → slow, no benefit.

## The command

```bash
python3 tools/crypto_attack.py hnp-ecdsa \
  --sigs sigs.json --order <n> \
  [--nonce-bits 128 | --nonce-bound 0x1000...] \
  [--curve secp256k1 --pubkey 04...]
```

- `--sigs` — JSON list of `[r, s, z]` or `{"r","s","z"}`, all `r` distinct.
- `--nonce-bits B` — `k < 2^B`.
- `--nonce-bound B` — `k < B` explicitly.
- `--curve` + `--pubkey` — verify the recovered `d` against `d·G == Q`.

## The math

Each signature: `k_i = s_i⁻¹(z_i + d·r_i) mod n`, `0 ≤ k_i < B`. Rewrite as
`k_i = t_i·d - u_i mod n` — a lattice of `n`-dim vectors whose shortest vector
reveals `d`. `hnp.py` builds the lattice, `lll.py` reduces it.

## Falsifier

- The recovered `d` fails `d·G == Q` → too few signatures, wrong bound, or
  the nonce wasn't actually biased (RNG was fine — the handout lied).
- LLL returns no plausible `d` → enlarge `--nonce-bound` by a factor,
  or gather more signatures.
- Any two `r` values repeat → you should be in `ecdsa-nonce-reuse`.

## Common mistakes

- Feeding `hnp-ecdsa` a signature set that includes a reuse pair — dedupe
  first, send the pair to `ecdsa-nonce-reuse`.
- Wrong `z` convention — lattice is unforgiving; verify one signature by
  hand: `s⁻¹z·G + s⁻¹r·Q` should have `x == r`.
- `nonce-bits` too tight — if the true `k` exceeds `B`, LLL can't find it.
