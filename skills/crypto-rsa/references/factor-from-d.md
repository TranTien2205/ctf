# factor-from-d / rsa-decrypt / eth-root — the leak terminals

`d`/`phi`/`dp`/`p`,`q` held → `factor-from-d` (splits `n` via `ed-1`), `rsa-
decrypt` (`m=c^d`), `eth-root` (`gcd(e,phi)>1` → the `g` candidates). Commands:
`crypto_attack.py factor-from-d --n --e --d`, `rsa-decrypt --n --e --d --c`,
`eth-root --c --e --factors`. Verify: `pow(m,e,n)==c`/`p*q==n`. See
`per-attack-factor-from-d.md`.
