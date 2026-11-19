# Falsifier map — the falsifier → the file that defines it

## The bound falsifiers

| Falsifier | The file |
|---|---|
| `d ≥ n^0.25` | `wiener.md`, `lattice-bounds.md`, `per-bound.md` |
| `d ≥ n^0.292` | `boneh-durfee.md`, `lattice-bounds.md`, `boundary-cases-deep.md` |
| window `< n^0.25` | `coppersmith.md`, `lattice-bounds.md` |
| `m^e ≥ n` | `small-e-root.md`, `per-bound.md` |
| `<e` n's / `∏n<m^e` / pad | `hastad.md`, `per-bound.md` |
| `gcd(e1,e2)>1` | `common-modulus.md` |
| `|p-q|` large | `fermat.md` |
| `p-1` not `B`-smooth | `pollard-pm1.md` |
| `∏pi≤m` / no fault | `crt.md` |
| relation not linear | `franklin-reiter.md` |
| `gcd(e,phi)=1` | `crt.md`, `factor-from-d.md` |
| `d`/`phi` fails `pow` | `factor-from-d.md`, `evidence-rules.md` |

## The observation → the negative

| Observation | → |
|---|---|
| all `gcd=1` | `batch-gcd` dead |
| `a` budget out | `fermat` dead |
| lattice empty at bound | the lattice dead |
| `pow!=c` | a candidate, not a recovery |
| every bound met | the class falsifier — reclassify |

## The files

`falsifiers.md` — the list; `per-falsifier.md` — the kill map; `negative-map.md`
— observation → closed class; `negative-results.md` — the record shape;
`boundary-cases.md`/`-deep` — the bound at its edge.
