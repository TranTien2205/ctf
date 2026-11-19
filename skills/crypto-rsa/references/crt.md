# crt — residues / Bellcore fault / dp-dq-qInv

Three recoveries: residues `∏pi>m`→`m`; a fault `gcd(s'^e-m,n)=q`; `dp`,`dq`,
`qInv`→`p`,`q`. Commands: `crypto_attack.py crt --residues "r1,r2" --moduli "p1,p2"`,
`--n --e --sig --sig-faulty`, `--n --e --dp --dq --qInv`. Verify:
`pow(m,e,n)==c`/`gcd==q`/`p*q==n`. See `per-attack-crt.md`.
