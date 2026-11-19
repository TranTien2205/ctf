# Edge cases — the shapes that break the happy path

## Signature-format edges

- `r`/`s` given as hex strings, DER-encoded signatures, or raw ints — normalize
  to ints before `--sigs`. DER: skip the `30`/`02` headers, take the two
  INTEGER fields.
- `z` given as the message, not the hash — hash it yourself (`sha256(m)`
  → int) unless the handout says otherwise.
- `s` in high-S vs low-S form — `s` and `n-s` are both valid; the attack
  works either way but verify catches it if you used the wrong one.

## Count edges

- N sigs where some pairs share `r` and others don't — extract the reuse
  pair(s) for `ecdsa-nonce-reuse`, run `hnp-ecdsa` on the distinct-`r` rest.
- `hnp-ecdsa` with too few sigs returns garbage that fails verify — the
  count formula is the signal to gather more.

## Curve edges

- `p` vs `n` swapped — `p` is the field, `n` the subgroup order. `order` in
  commands is always `n`.
- Compressed/uncompressed pubkeys — `04||x||y`, `02/03||x` — decompress
  before `ec.py` ops.
- `G` not the standard generator → every check must use the supplied `G`.

## Tooling edges

- `--sigs` JSON accepts hex strings (`"0x..."`) and ints — mixing is fine.
- `lll.py` is pure-python (no `fpylll` here) — lattice dimension over ~40
  gets slow; keep signature counts near the minimum.
- `--nonce-bound` vs `--nonce-bits` — bound is the integer `B`, bits is
  `log2(B)`.

## The verify edge

A `d` that verifies on the wrong curve means you derived on the wrong curve —
verify against the *supplied* `Q`, `G`, `p`, `a`, `b`.
