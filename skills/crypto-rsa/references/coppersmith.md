# coppersmith — the small-root lattice attacks

`f(x)=a+x≡0 mod p`, `|x|<n^0.25` → recover `p`. Variants: `coppersmith-high-bits`
(top bits of `p`), `coppersmith-core` (centred guess / general `f`),
partial-message (`|x|<n^(1/e)`). Detection: a redacted/leaked `p`, a centred
guess, a pad. Bound: the unknown `<n^0.25` (factor) / `<n^(1/e)` (message).
Commands: `crypto_attack.py coppersmith-high-bits --n --known --bits`,
`coppersmith-core --n --a`. See `per-attack-coppersmith.md`.
