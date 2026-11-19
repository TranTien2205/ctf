# Evasion — the hide-the-attack shapes

## Disguised nonce reuse

- `r` values differ but `k_i` differs by a known offset — not reuse, but a
  structured nonce → `hnp-ecdsa` with `--nonce-bound`.
- Signatures on the *same message* with different `r` — deterministic `k`
  would give same `r`; differing `r` means random `k` — still `hnp-ecdsa`
  if bounded.

## Disguised smooth order

- `ord(g)` looks prime-ish but the challenge gives `ord` factors indirectly
  (a list of small subgroup orders). `smoothness` on `ord(g)` finds them.
- `g` of small order inside a big `p` — `bsgs`/`pohlig` on `ord(g)`, not `p-1`.

## Disguised defect curve

- Params given as `y² = x³ + c` (`a = 0`, `b = c`) — `Δ` check still applies.
- `#E` not given — count it (`ec.py` on small `p`), or the challenge wants
  a protocol flaw, not a math attack.

## Disguised `z`

- `z` given as raw message → hash first (`sha256`).
- `z` as hex string vs int — `--sigs` accepts both, but the *value* must be
  the truncated hash.

## Disguised verify

- `d` recovers but `d·G` is on a *different* curve → you solved for a fake
  curve; check which `G`/`p`/`a`/`b` the supplied `Q` uses.
