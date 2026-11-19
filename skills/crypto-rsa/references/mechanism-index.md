# Mechanism index — the six primitives → their files

## The primitives and the files

| Primitive | The files |
|---|---|
| wrap | `mechanism.md`,`mechanism-deep.md`,`small-e-root*.md`,`nth-root*.md`,`hastad*.md` |
| gap | `mechanism.md`,`fermat*.md`,`theory*.md` |
| divisor | `mechanism.md`,`batch-gcd*.md`,`pollard-pm1*.md` |
| exponent | `mechanism.md`,`wiener*.md`,`boneh-durfee*.md`,`common-modulus*.md`,`factor-from-d*.md`,`lattice-bounds.md` |
| partial | `mechanism.md`,`coppersmith*.md`,`lattice-bounds.md` |
| relation/leak | `mechanism.md`,`franklin-reiter*.md`,`crt*.md`,`eth-root*.md`,`rsa-decrypt*.md`,`factor-from-d*.md` |

## The bound index

| The bound | The file |
|---|---|
| `d<n^0.25` | `wiener.md`,`wiener-deep.md`,`lattice-bounds.md` |
| `d<n^0.292` | `boneh-durfee.md`,`boneh-durfee-deep.md`,`lattice-bounds.md` |
| window`n^0.25`/`n^(1/e)` | `coppersmith.md`,`coppersmith-deep2.md`,`lattice-bounds.md` |
| `m^e<n` | `small-e-root*.md`,`nth-root*.md` |
| `≥e` n's | `hastad*.md` |
| `gcd=1` | `common-modulus*.md` |
| `|p-q|` small | `fermat*.md` |
| `B`≥factor | `pollard-pm1*.md` |
| linear/`∏pi>m`/fault/`dp` | `franklin-reiter*.md`,`crt*.md` |
| `gcd(e,phi)>1` | `eth-root*.md` |
| `d`/`phi`/`p`,`q` held | `factor-from-d*.md`,`rsa-decrypt*.md` |

## The maps

`mechanism-map.md` — primitive → bug files; `per-mechanism.md` — primitive →
falsifier; `mechanism-catalogue.md` — primitive → the bound/verify table.
