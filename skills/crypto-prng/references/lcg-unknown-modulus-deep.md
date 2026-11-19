# lcg-unknown-modulus deep — `m`,`a`,`c` all unknown

## The attack id

```bash
python3 tools/crypto_attack.py lcg-unknown-modulus --outputs o0,o1,o2,o3,o4,o5
```

`--outputs` = ≥6 comma-separated consecutive raw outputs. No modulus — it
is recovered.

## The math — the telescope trick

Differences kill the increment `c`:

```
t_i = x_{i+1} - x_i          (mod m)
t_{i+1} = a·t_i              (mod m)      # c cancels
```

So consecutive `t` satisfy `t_{i+1}·t_{i-1} - t_i^2 ≡ 0 (mod m)`. Each
`u_i = t_{i+1}·t_{i-1} - t_i^2` is a multiple of `m`:

```
m divides gcd(u_1, u_2, ..., u_{k-2})
```

Take the gcd over all windows — `m` falls out (usually exactly, up to a
small multiple). Then `lcg-recover` for `a`,`c`.

## Why ≥6 outputs

`u_i` needs three `t`s = four `x`s for one `u`. Two `u`s for a gcd → six
`x`s minimum. More outputs → a cleaner gcd (the spurious factors shrink).

## The failure modes

- **gcd → 0 or 1** — the outputs are not an LCG (or `m` is huge / the
  stream has a gap). Falsifier.
- **gcd = a multiple of `m`** — `u_i` are all `≡0 mod m` but share a
  common factor — try dividing by small factors / gather more outputs.
- **gcd = a factor of `m`** — `m` itself is composite and the gcd caught a
  factor — factor the gcd, test each candidate.
- **`m` is huge / nonstandard** — the gcd gives a multiple; the
  `lcg-recover` step fails → suspect a non-LCG generator.

## The known-`m` shortcut

If a writeup/source hints `m` (`2^32`, `2^48`, a named modulus), skip the
gcd — feed `--modulus` straight into `lcg-recover`. The gcd trick is for
when `m` is genuinely unknown.

## The output-shape trap — the same

`--outputs` wants raw states. `x mod n` / `x>>b` / floats break the
telescope (`t_i` no longer equal `a·t_{i-1}`). This attack is the MOST
shape-sensitive — one non-raw output poisons every `u`.

## The verification

Recovered `m` → `lcg-recover` → `a`,`c` → `predict_next == held-back`.
The whole chain is verified on a held-back output — never on the inputs
the gcd was built from.

## Expected signal / falsifier

- **Expected signal**: a plausible `m` (power of two / product), then
  `a`,`c`, then `next == held`.
- **Falsifier**: gcd collapse / no invertible `a` / `predict != held`.

## When to stop

- <6 outputs → cannot run. Collect more.
- gcd gives garbage after 8+ outputs → probably not an LCG. Re-fingerprint.
