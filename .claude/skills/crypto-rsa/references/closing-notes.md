# Closing notes — crypto-rsa, the one-paragraph summary

RSA key/plaintext recovery: `n`,`e`,`c` + a leak → `p`,`q`,`d`,`φ`,`m`. Six
families — wrap (small `e`,`m^e<n`), gap (close `p,q`), divisor (shared/smooth
`p`), exponent (small/held `d`,`phi`), partial (bits), relation/leak
(`a·m1+b`,`sig` fault, `dp`,`qInv`). `crypto_attack.py list` → the bound → the
attack → `pow(m,e,n)==c`/`p*q==n`. **Catalogue** — no local solve.
