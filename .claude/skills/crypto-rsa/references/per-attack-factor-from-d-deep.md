# per-attack factor-from-d / rsa-decrypt / eth-root deep — the terminal, the full treatment

## `factor-from-d` — `d`/`phi` → the factors

`ed-1 = k·φ` → `ed-1 = 2^t·r`; `g^r, g^{2r}, ... mod n` → a non-trivial `x²≡1`
→ `gcd(x-1,n)=p`.

```bash
crypto_attack.py factor-from-d --n <n> --e <e> --d <d>
crypto_attack.py factor-from-d --n <n> --e <e> --phi <phi>
```

`p*q==n` for the factors.

## `rsa-decrypt` — `p`,`q`/`d` → `m`

```bash
crypto_attack.py rsa-decrypt --n <n> --e <e> --c <c> --p <p> --q <q>
```

`p`,`q` → `phi` → `d` → `m` → `pow(m,e,n)==c`. If `d` is held directly,
`m=pow(c,d,n)` manually.

## `eth-root` — `gcd(e,phi)>1` → the `g` roots

`e` not invertible mod `φ` → `m^e` has `g` `e`th roots mod `n`. With `p`,`q`:
the `g_p`/`g_q` roots, CRT-combined → `g` candidates → `pow`+format.

```bash
crypto_attack.py eth-root --c <c> --e <e> --factors "<p>,<q>"
```

`pow(m_i,e,n)==c` + the flag format picks the true `m`.

## The bounds

- `factor-from-d` — the `d`/`phi` held, real.
- `rsa-decrypt` — `p`,`q`/`d` held.
- `eth-root` — `gcd(e,phi)>1`, `p`,`q` held.

## The chain

`d`/`phi` → `factor-from-d` → `p`,`q` → `rsa-decrypt` → `m` → `pow` → flag.

## The verify

`pow(m,e,n)==c` / `p*q==n` — the terminal gate.

## The honest status

Standard — catalogue.
