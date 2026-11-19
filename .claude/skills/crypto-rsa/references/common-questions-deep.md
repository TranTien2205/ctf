# Common questions deep — the RSA stalls, answered fully

## "The handout is just numbers — where do I start?"

Build the parameter sheet: count the `n`,`e`,`c`, find the leak, read the keygen.
Then walk `attack-table.md` — the first yes picks the attack id.
`crypto_attack.py list` shows every id with its applicability bound.

## "Wiener failed — is small-d dead?"

Not yet — Wiener's bound is `d<n^0.25`; Boneh-Durfee reaches `n^0.292`. If `e`
is still large (`e≈n`), escalate: `crypto_attack.py boneh-durfee-escalate`. Only
`d ≥ n^0.292` closes small-d — then look for a leak or another class.

## "e=3 but the cube root isn't the flag"

`e=3` needs `m^3<n`. A real flag usually wraps. Route: `hastad` if ≥3 moduli of
the same `m`; `coppersmith` partial-message if a pad/prefix is known; the flag
is `n^(1/3)`-sized at most for the plain root.

## "The lattice ran for minutes — is it working?"

`fpylll` is absent; `tools/crypto/` uses pure-python LLL — slow but correct.
`crypto_attack.py list` reports `lll_backend`. If the bound was exceeded it is
failing, not slow — check the applicability line before the run, not after.

## "pow(m,e,n)!=c but it looks like a flag"

A decoy or a wrong root. `pow` is the gate — a flag-shaped string that fails it
is a candidate. Check: the `eth-root` `gcd` candidates (try the others), a pad
to strip, or a bound-exceeded lattice.

## "Two moduli — batch-gcd gave nothing"

All `gcd=1` → the RNG produced distinct primes. The *count* is not the bug —
record the negative. Then per-`n` single attacks: `fermat`, `wiener`, etc.

## "I have d but inverse(e,phi) fails"

`gcd(e,φ)>1` — `e` and `φ` share a factor. `rsa-decrypt`/`eth-root` handle it —
multiple candidate roots, disambiguated by `pow` + flag format.

## "The PEM is partially redacted — which attack?"

If `p`'s high/low bytes leak → `coppersmith-high-bits`/`coppersmith-core`. If
`dp`,`dq`,`qInv` are present → `crt` reconstruction. If `d`/`phi` →
`factor-from-d`. Read which fields are *not* redacted.

## "Hastad needs e recipients — I have e-1"

`∏n < m^e` → the root isn't `m`. Route to `coppersmith` partial-message or
`franklin-reiter` — do not fabricate a fourth modulus.

## "The challenge gives a socket — is it a service?"

A socket that *prints* `n`,`e`,`c` is transport, not an oracle — treat as the
numbers. Only a socket that *computes* on your input (encrypt/decrypt/sign
queries) is `crypto-symmetric-oracle`.

## "Nothing in the table fires"

Proper RSA (random primes, `e=65537`, OAEP, no leak) → the bug is in the
protocol — a padding oracle, signature forgery, or side channel — not the key.
Reclassify; this class's falsifier is a properly-parameterised RSA.
