# Probe map — the question → the probe → the attack

## "How many moduli?"

`len(set of n)` → `≥2` → `batch-gcd` or `hastad`; `=1` → single-modulus.

## "How many exponents on one n?"

`len(e on the same n)` → `2` → `common-modulus`; `1` → single-exponent.

## "How many ciphertexts of the same m?"

`len(c of same m)` → `≥e` → `hastad`.

## "What is e?"

`e` → `3/5/17` → `small-e`/`hastad`/`franklin-reiter`; `65537` → default;
`~n` → `wiener`/`boneh-durfee`; `gcd(e,phi)>1` → `eth-root`.

## "Are p,q close?"

keygen `next_prime`/`p+k`/`q=p+2`, or `a=isqrt(n)+1` quickly finds `a²-n` square
→ `fermat`.

## "Is d small?"

`e≈n` → `d<n`^0.292 likely → `wiener` then `boneh-durfee`.

## "Is p-1 smooth?"

keygen hints / `pollard-pm1` `gcd` fires → `pollard-pm1`.

## "Is there a leak?"

`d`/`phi`/`dp`/`dq`/`qInv`/`p`-bits/`m`-partial/`p`,`q` present →
`factor-from-d`/`crt`/`coppersmith`/`rsa-decrypt`/`eth-root`.

## "Is there a relation?"

`m2=a·m1+b` linear → `franklin-reiter`.

## "Is there a fault?"

correct + faulty `sig` of same `m` → `crt` Bellcore.

## "Is there a partial?"

`p` high/low → `coppersmith-*`; `m` partial → `coppersmith` partial-message.

## "Is m wrapped?"

`m^e<n` → `small-e-root`/`nth-root`; `m^e≥n` → `hastad`/`coppersmith`.

## The falsifier probes

| Probe | If it fails → rules out |
|---|---|
| all `gcd(ni,nj)=1` | `batch-gcd` |
| `gcd(e1,e2)>1` | `common-modulus` |
| `a` past budget | `fermat` |
| `d≥n^0.292` | `wiener`+`boneh-durfee` |
| window `<n^0.25` | `coppersmith-*` |
| `m^e≥n` | `small-e-root` |
| `<e` n's / pad | `hastad` |
| `gcd(a^{B!}-1,n)=1` | `pollard-pm1` |
| not linear | `franklin-reiter` |
| `∏pi≤m` / no fault | `crt` |
