# Summary — crypto-rsa

RSA key or plaintext recovery. `n`,`e`,`c` + a leak → `p`,`q`,`d`,`φ`,`m`. Six
violation families: wrap, gap, divisor, exponent, partial, relation/leak.

`crypto_attack.py list` → `attack-table.md` discriminator → bound-check → attack
→ `pow(m,e,n)==c`/`p*q==n` verify.

Catalogue class — no local solve. `../field-notes.md` (skill root) records real
solves.
