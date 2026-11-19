# Extended — the complete crypto-rsa field reference

This is the consolidated operating manual: the construction, the six violation
families, the decision procedure, the bounds, and the verify. Cross-references
live in `index.md` / `README.md`.

## The construction

`n = p·q`, `ed ≡ 1 mod φ(n)`, `φ=(p-1)(q-1)`. `c=m^e mod n`, `m=c^d mod n`.
Factoring `n` is the trapdoor. Every attack is a shortcut to `p`,`q`,`d`,`φ` —
a violation of a factoring precondition, not a break of RSA.

## The six violation families

1. **Wrap** — `m^e<n` → `c` is a plain power → `small-e-root`, `nth-root`,
   `hastad` (CRT+root across `e` moduli).
2. **Gap** — `|p-q|` small → `n=a²-b²` → `fermat`.
3. **Divisor** — shared prime / smooth `p-1` → `gcd` → `batch-gcd`, `pollard-pm1`.
4. **Exponent** — `d` small or `e` shared → `wiener` (`<n^0.25`), `boneh-durfee`
   (`<n^0.292`), `common-modulus` (`gcd=1`).
5. **Partial knowledge** — bits of `p`/`m` → Coppersmith small-root →
   `coppersmith-*`, partial-message.
6. **Leak** — `d`/`φ`/`dp`/`p`,`q` held → `factor-from-d`, `crt`, `rsa-decrypt`,
   `eth-root`; a Bellcore fault → `gcd(s'^e-m,n)`.

## The decision procedure

```
sheet (n,e,c,leaks,keygen) → discriminator → bound-check → attack → pow-verify
```

The discriminator table (`attack-table.md`) picks the id; the bound (`per-bound.md`,
`lattice-bounds.md`) is the falsifier — exceeded is a negative, not a retry.

## The bounds

- `d<n^0.25` wiener · `d<n^0.292` boneh-durfee
- window≥`n^0.25` coppersmith · `m^e<n` small-e · `≥e` n's hastad
- `gcd(e1,e2)=1` common-modulus · `|p-q|` small fermat · `p-1` smooth pollard
- `∏pi>m` / a fault / `dp` for crt · linear relation for franklin-reiter

## The verify

`pow(m,e,n)==c` for a plaintext; `p*q==n` for a factor. The whole proof standard.

## The toolchain

`tools/crypto_attack.py list` prints every id with its bound; `<id> --help` the
flags. `tools/crypto/` is stdlib-only — `fpylll` absent → pure-python LLL, slower
but same reach.

## The honest status

Catalogue class — no local solve. `verified-chains.md` records the standing.
The bounds and attack shapes are published-standard; nothing here is verified
experience. Record what happens in `../field-notes.md`.
