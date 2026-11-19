# Edge cases catalogue — the degenerate forms, the file

## `n` degenerate

- `n` prime → `phi=n-1`, `d=inverse(e,n-1)` — `edge-cases*.md`.
- `n`=p² → `phi=p(p-1)` — `edge-cases*.md`,`boundary-conditions*`.
- `n` smooth → `factorint` — `edge-cases*.md`.
- `n` multi-prime → `phi=∏(pi-1)` — `edge-cases*.md`.
- `n` small → a factor table — `edge-cases*.md`.

## `e` degenerate

- `e`=1 → `c=m` — `edge-cases*.md`.
- `gcd(e,phi)>1` → `eth-root` — `eth-root*.md`,`edge-cases*.md`.
- `e`≈`n` → `wiener`/`boneh-durfee` — `wiener*.md`,`boneh-durfee*.md`.

## `d`/`phi` degenerate

- `d` held → `factor-from-d`/`rsa-decrypt` — `factor-from-d*.md`.
- `phi` held → `factor-from-d`/`rsa-decrypt` — `factor-from-d*.md`.
- `dp`,`dq`,`qInv` → `crt` — `crt*.md`.
- `d` multi (λ/φ) → both decrypt — `edge-cases*.md`.

## `m` degenerate

- `m`=0/1/small → `c=pow(m,e,n)` — `edge-cases*.md`.
- `m` padded → strip `\x00\x02<pad>\x00`/OAEP — `verify*`,`edge-cases*.md`.
- `m` not the flag → a key/seed — `edge-cases*.md`.

## The verify

`pow(m,e,n)==c` / `p*q==n`.
