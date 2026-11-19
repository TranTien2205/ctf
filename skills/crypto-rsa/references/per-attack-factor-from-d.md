# factor-from-d / rsa-decrypt / eth-root — the leak terminals, complete

## What it is

`d`/`phi`/`dp`/`p`,`q` held → recover the rest arithmetically.

## factor-from-d

`ed-1 = k·φ`, `k` small → write `k·2^t·r`; random `g`, `g^r` chains → a
non-trivial `x` with `x²≡1 mod n` → `gcd(x-1,n)=p`. `crypto_attack.py
factor-from-d --n --e --d` (or `--phi`).

## rsa-decrypt

`m = c^d mod n` — `crypto_attack.py rsa-decrypt --n --e --d --c` or
`--n --p --q --e --c`.

## eth-root

`gcd(e,phi)=g>1` → `e` not invertible → the `g` `e`th-root candidates →
`pow(m_i,e,n)==c` + flag format picks. `crypto_attack.py eth-root --c --e --n
--p --q`.

## Detection

- `d`/`phi`/`dp`/`dq`/`qInv`/`p`/`q` in the handout.
- `inverse(e,phi)` failing → `gcd(e,phi)>1` → `eth-root`.

## The verify

`pow(m,e,n)==c` / `p*q==n`.
