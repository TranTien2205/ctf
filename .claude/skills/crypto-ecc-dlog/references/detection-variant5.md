# Detection variant 5 — the reads by what is attacker-controlled

## The supplied-vs-derived split

- **Supplied** — `p a b G n Q`/`g h`, the sigs, the bound, the oracle.
- **Derived** — `z` from `m`, `t`/`u` from the sigs, `ord(g)` from `p`,
  `#E`/`Δ` from `p a b`, `x`/`d` from the attack.

## The honest reads

- A supplied `Q` is a verify target; a derived `d` must reproduce it.
- A supplied bound is trusted only if it covers every `k_i`.
- A supplied `ord` that is `p` (not `n`) is the classic swap.

## The trap reads

- `p` given but `n` needed → `--order` wants `n`.
- `ord` given but `x` bounded → `bsgs --order <bound>` not `--order ord`.
- `sigs` inline → `--sigs` wants a file, not the JSON.
- `k` "random" → RFC 6979 deterministic on some curves — cross-`m` reuse
  impossible, same-`m` reuse trivial.
