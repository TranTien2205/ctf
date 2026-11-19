# Edge cases deep — the degenerate forms, annotated

## `n` degenerate

- **`n` prime** — `phi=n-1`, `d=inverse(e,n-1)` — no factorisation.
- **`n`=`p²`** — `phi=p(p-1)` — `isqrt(n)**2==n`.
- **`n` smooth** — `factorint(n)` splits → `phi` directly.
- **`n` multi-prime** — `phi=∏(pi-1)` — a multi-prime challenge.
- **`n` small** (≤512-bit) — `factorint` or a factor DB (factordb) may split it.
- **`n` shared across keys** — `batch-gcd`.

## `e` degenerate

- **`e`=1** — `c=m`, no attack.
- **`e` even/`gcd(e,phi)>1`** — no inverse → `eth-root`, the `g` candidates.
- **`e`≈`n`** — small `d` → `wiener`/`boneh-durfee`.
- **`e` coprime but `phi` shared** — two `e` → `common-modulus`.

## `d`/`phi` degenerate

- **`d` held** → `factor-from-d`, `rsa-decrypt`.
- **`phi` held** → `factor-from-d`/`rsa-decrypt`/`d=inverse(e,phi)`.
- **`dp`,`dq`,`qInv`** → `crt` manual.
- **`d` multi** — `d` may differ by `λ`/`φ` — both decrypt.

## `m` degenerate

- **`m`=0/1/small** — `c=pow(m,e,n)` trivially — check first.
- **`m` padded** — strip `\x00\x02<pad>\x00`/OAEP.
- **`m` not the flag** — `m` is a key/seed; the flag is `m`-derived.

## The verify

`pow(m,e,n)==c` / `p*q==n`.
