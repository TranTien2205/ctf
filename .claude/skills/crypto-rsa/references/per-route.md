# Per-route map — the recovery route → the chain

## The factor route

```
<factor attack> → p, q → factor-from-d / rsa-decrypt → m → pow verify
```

Factor attacks: `batch-gcd`, `fermat`, `pollard-pm1`, `coppersmith-*`,
`crt`-Bellcore, `factor-from-d` (from `d`/`phi`).

## The d route

```
<d attack> → d → rsa-decrypt → m → pow verify
```

`d` attacks: `wiener`, `boneh-durfee`, `factor-from-d`, `crt`-dp.

## The direct-m route

```
<m attack> → m → pow verify → flag
```

`m` attacks: `small-e-root`, `nth-root`, `hastad`, `common-modulus`,
`franklin-reiter`, `crt`-residues, `eth-root`, `rsa-decrypt`.

## The escalation route

```
<family A closed> → <family B> → ... → the solve
```

- `wiener` → `boneh-durfee` → `boneh-durfee-escalate` → closed.
- `coppersmith-high-bits` → `coppersmith-core` → closed.
- `batch-gcd` empty → per-`n` `fermat`/`wiener`.
- `small-e` fails → `hastad` / `coppersmith`.
- `fermat` slow → `pollard-pm1` / a leak.

## The terminal route

Every route ends at `pow(m,e,n)==c` or `p*q==n`. The route is the *chain*; the
verify is the *gate*.

## The route table

| You recovered | Next |
|---|---|
| `p`,`q` | `factor-from-d` → `d` → `rsa-decrypt` → `m` |
| `d`/`phi`/`dp` | `rsa-decrypt`/`crt`/`factor-from-d` → `m` |
| `m` | `pow` verify → flag |
| a negative | the next discriminator row |
| a bound met | the falsifier → the next row |
