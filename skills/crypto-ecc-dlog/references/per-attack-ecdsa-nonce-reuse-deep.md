# Per-attack `ecdsa-nonce-reuse` deep — the card, expanded

## The trigger

`r_i == r_j` for two signatures on different `z`s. Exact equality —
`r` is `k·G`'s x-coordinate, so equal `r` ⟹ equal `k` (with overwhelming
probability).

## The command

```bash
python3 tools/crypto_attack.py ecdsa-nonce-reuse --sigs sigs.json --order <n>
```

`--sigs` is a JSON file: `[{"r","s","z"}, …]`. `--order` is `n`.

## The algebra

```
k = (z1 - z2)/(s1 - s2)  mod n
d = (s1·k - z1)/r        mod n
```

## The verification

`d·G == Q`. A `d` that doesn't reproduce `Q` means `z`/`order` was wrong —
not the attack.

## The falsifiers

- No dup `r` → dead; `hnp-ecdsa`/`hnp` next.
- `d·G ≠ Q` → `z`/`order`/`n`-vs-`p` wrong.

## The boundary

- Same `r` on same `m` → `z` identical → the equations degenerate; you get
  `d` only if a second distinct `m` reuses `k`.
- RFC 6979 → same `m` reuses `k` trivially; cross-`m` never.

## The boundary notes

- `r` must match **as an integer** — normalize hex/DER first.
- `z` per sig — `int(H(m_i))` truncated or `mod n`; the convention matters.
