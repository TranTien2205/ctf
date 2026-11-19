# batch-gcd — shared-prime recovery

`n_i`, `n_j` sharing a prime → `gcd(n_i,n_j)=p` splits both. Detection: ≥2
moduli from the same generator; a seeded/weak RNG. Bound: a collision must
exist — `gcd=1` everywhere is the falsifier. Chain: `p`→`q`→`phi`→`d`→`m`→`pow`.
Command: `crypto_attack.py batch-gcd --moduli n1 n2 ...`. See
`per-attack-batch-gcd.md` for the full module.
