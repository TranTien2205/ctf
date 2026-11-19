# Troubleshoot variant — the fixes, restated

## `ecdsa-nonce-reuse` fails

- `d·G ≠ Q` → recompute `z` (truncation vs mod), `--order` = `n` not `p`.
- No `k` recovered → the `r`s weren't actually equal.

## `hnp-ecdsa` fails

- Junk lattice → `m < required`, gather more sigs.
- `d·G ≠ Q` → `z`/`order`/`B` wrong, or a `k` outlier.

## `hnp` fails

- `t`/`u` mismatch → recompute `t = s⁻¹r`, `u = -s⁻¹z` mod `n`.
- No `d` → bound too tight or the leak isn't `k`.

## `pohlig-hellman` fails

- Stall → `ord` factor > 2⁴⁰ → `bsgs` or defect.
- `g^x ≠ h` → `ord` wrong or `h ∉ <g>`.

## `bsgs` fails

- No match → `h ∉ <g>` or `x > B`.
- OOM → `ord`/`B` > 2⁴⁴.

## `smart`/`singular` fails

- `#E ≠ p`/`Δ ≠ 0` → wrong attack — `#E` smooth → PH, bounded → bsgs.

## Invalid curve fails

- `P` rejected → validation present → not this attack.
- CRT wrong → the `ord_i` or `d mod ord_i` recomputed badly.
