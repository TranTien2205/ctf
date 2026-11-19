# Glossary — terms in the corpus

| Term | Meaning |
|---|---|
| `d` | ECDSA private scalar |
| `k` | ECDSA ephemeral nonce — the attack surface |
| `r`, `s` | signature components — `r` is `x(k·G) mod n`, `s` the equation |
| `z` | message hash as integer (`order_bits` truncation or `mod n`) |
| `n` | group order (`ord(G)` for curves, `p-1`/`ord(g)` for fields) |
| `p` | field prime |
| `Q` | public point `d·G` |
| `G` | generator point |
| `h`, `g` | DLP statement `h = g^x mod p` |
| `E(Fp)` | elliptic curve over `Fp` |
| `#E` | point count `p + 1 - t` |
| `t` (trace) | `p + 1 - #E` |
| `Δ` | discriminant `-16(4a³ + 27b²)` |
| anomalous | `#E == p` — smart_attack territory |
| singular | `Δ == 0` — singular_ec territory |
| HNP | Hidden Number Problem — `k_i = t_i·d - u_i mod n`, `k_i < B` |
| LLL | lattice basis reduction (`tools/crypto/lll.py`, pure-python) |
| BSGS | baby-step giant-step, `O(√B)` |
| PH | Pohlig-Hellman — per-factor dlog + CRT |
| smooth | all prime factors small |
| twist | the curve `E'` sharing coefficients — invalid-curve tool |
| `--sigs` | JSON file `[r,s,z]` triples / `{"r","s","z"}` objects |
| `--order` | always `n` (subgroup order), never `p` |
| `--nonce-bits`/`--nonce-bound` | bound on `k` — bits vs integer `B` |
| RFC 6979 | deterministic `k` — identical input → identical `(r,s)` |
| MOV/Frey-Rück | pairing transfer to `F_{p^k}` — small embedding degree |
| verify | `x·G == Q` or `g^x == h` — the only finish line |
