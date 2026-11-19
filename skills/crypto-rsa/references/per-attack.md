# Per-attack map — the id → the file → the one-liner

| id | File | One-liner |
|---|---|---|
| `batch-gcd` | `batch-gcd.md` | `gcd(ni,nj)` for a shared `p` |
| `common-modulus` | `common-modulus.md` | `m=c1^a·c2^b`, `gcd(e1,e2)=1` |
| `fermat` | `fermat.md` | `n=a²-b²` for close `p,q` |
| `wiener` | `wiener.md` | `d<n^0.25` → CF convergent |
| `boneh-durfee` | `boneh-durfee.md` | `d<n^0.292` → LLL |
| `boneh-durfee-escalate` | `boneh-durfee-deep.md` | `m`,`t` up to the bound |
| `coppersmith-high-bits` | `coppersmith.md` | top `n/2` bits of `p` |
| `coppersmith-core` | `coppersmith.md` | `f(x)=a+x`, `x<n^0.25` |
| `small-e-root` | `small-e-root.md` | `m=c^{1/e}`, `m^e<n` |
| `nth-root` | `small-e-root.md` | the general `e`th root |
| `hastad` | `hastad.md` | CRT + root over `e` n's |
| `pollard-pm1` | `pollard-pm1.md` | `gcd(a^{B!}-1,n)` |
| `franklin-reiter` | `franklin-reiter.md` | `gcd` of related polys |
| `crt` | `crt.md` | residues / Bellcore / dp |
| `factor-from-d` | `factor-from-d.md` | `ed-1` splits `n` |
| `rsa-decrypt` | `factor-from-d.md` | `m=c^d mod n` |
| `eth-root` | `crt.md` | the `gcd(e,phi)` roots |

## The deep variants

`batch-gcd-deep`, `common-modulus-deep`, `fermat-deep`, `wiener-deep`,
`boneh-durfee-deep`, `coppersmith-deep`, `small-e-root-deep`, `hastad-deep`,
`pollard-pm1-deep`, `franklin-reiter-deep`, `crt-deep`, `factor-from-d-deep` —
the same attack with the bound maths and the failure modes.

## The index files

`attack-table.md` — the discriminator; `attack-table-deep.md` — the full table;
`attack-families.md` — the six primitives; `attack-shapes.md` — the geometric
signatures; `extended-corpus.md` — one paragraph each; `deep-dives.md` — the
long form.
