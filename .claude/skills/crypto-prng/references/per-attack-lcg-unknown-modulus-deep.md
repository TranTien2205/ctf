# per-attack lcg-unknown-modulus deep — the gcd-trick modulus recovery

## The command

```bash
python3 tools/crypto_attack.py lcg-unknown-modulus --outputs o0,...,o5
```

NO `--modulus` — `m` is the unknown being recovered. ≥6 outputs.

## The derivation

Kill `c` with differences:

```
t_i = x_{i+1} - x_i  (mod m)
t_{i+1} = a·t_i      (mod m)
t_{i+1}·t_{i-1} - t_i^2 ≡ 0  (mod m)
```

Each `u_i = t_{i+1}·t_{i-1} - t_i^2` is a multiple of `m`. The gcd over
windows gives `m` (usually exactly). Then `lcg-recover` for `a`,`c`.

## The ≥6 floor

One `u` needs three `t`s = four `x`s. Two `u`s for a gcd → six `x`s.
More outputs → the spurious common factors shrink → a cleaner `m`.

## The failure modes

- **`gcd → 0`** — degenerate/deterministic — not a real stream.
- **`gcd → 1`** — the `u_i` share no factor — NOT an affine recurrence —
  the falsifier → re-fingerprint.
- **`gcd` = a multiple of `m`** — the `u_i` are `≡0 mod m` but share a
  larger factor — try dividing by small factors (2,3,5,...) or gather
  more outputs.
- **`gcd` = a proper factor of `m`** — `m` composite and the gcd caught a
  factor — factor the gcd, test each candidate against `predict==held`.

## The rawness trap — the most shape-sensitive

Every `u_i` depends on `t_i` — one `x mod n`/`x>>b`/float/gap poisons
THREE `u` values. This attack is the most normalization-sensitive —
normalize ALL outputs before running.

## The verification

`m` → `lcg-recover --outputs o0,o1,o2 --modulus m` → `a`,`c` →
`predict_next == held`. The recovered `m` is only real if the resulting
`a`,`c` extrapolate.

## The shortcut

If source names `m` (`MOD`, `2^31`, `2^48`, a known modulus) → skip the
gcd → `lcg-recover --modulus m` directly.

## Expected signal / falsifier

- **Expected**: a plausible `m` (power-of-2/product), then `a`,`c`, then
  `next == held`.
- **Falsifier**: `gcd→0/1` / no invertible `a` / `predict != held`.
