# hastad — the broadcast attack

Same `m` to `e` coprime `n` → CRT `x=m^e mod ∏ni` → `∏ni>m^e` → `x=m^e` →
`m=x^{1/e}`. Detection: `e` small, `≥e` ciphertexts of same `m`. Bound: `≥e` n's,
`∏n>m^e`, no pad. Verify: `pow(m,e)==x`. Command: `crypto_attack.py hastad
--pairs ... --moduli ... --e`. See `per-attack-hastad.md`.
