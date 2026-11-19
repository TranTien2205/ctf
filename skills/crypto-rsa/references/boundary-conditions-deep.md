# Boundary conditions deep — the edge cases that change everything

## The `e` boundaries

- **`e`=1** — `c=m`, no attack needed.
- **`e`=3** — `m³<n` → `small-e`; `≥e` n's → `hastad`.
- **`e`=65537** — the default; the bug is elsewhere.
- **`e`≈`n`** — small `d` → `wiener`/`boneh-durfee`.
- **`gcd(e,phi)>1`** — no inverse → `eth-root`, the `g` candidates.

## The `n` boundaries

- **`n` prime** — `phi=n-1`, `d=inverse(e,n-1)` directly.
- **`n`=p²** — `phi=p(p-1)` not `(p-1)²`.
- **`n` smooth** — `factorint` splits it directly.
- **`n` multi-prime** — `phi=∏(pi-1)`; `eth-root` for `gcd(e,phi)>1`.
- **`n` ≥2** — `batch-gcd`/`hastad`, not a single-modulus attack.
- **`n` very small** (128/256-bit) — `factorint`/a table lookup may split it.

## The `d`/`phi` boundaries

- **`d` held** → `factor-from-d`, `rsa-decrypt`, or `phi=(e·d-1)//k`.
- **`phi` held** → `factor-from-d`, `rsa-decrypt` directly.
- **`dp`,`dq`,`qInv`** → `crt` manual.
- **`d` small** — the `n^0.25`/`n^0.292` bounds.

## The `m` boundaries

- **`m³<n`** → `small-e`; `m³≥n` → wrapped → `hastad`/`coppersmith`.
- **`m2=a·m1+b`** → `franklin-reiter`.
- **`m` partial** → `coppersmith` partial-message.
- **`m` padded** — strip the pad; `pow` held on the block.
- **`m`=0,1,small** → trivial; check `c=pow(m,e,n)` directly.

## The `p`,`q` boundaries

- **`|p-q|` small** → `fermat`.
- **`p` shared** → `batch-gcd`.
- **`p-1` smooth** → `pollard-pm1`.
- **`p` bits** → `coppersmith`.
- **`p`,`q` held** → `rsa-decrypt`/`eth-root`.

## The verify

`pow(m,e,n)==c` / `p*q==n` — the gate on every boundary case.
