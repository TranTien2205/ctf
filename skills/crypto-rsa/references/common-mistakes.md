# Common mistakes — the wrong moves

- `e=3` → `small-e-root` without checking `m³<n` — a wrapped `m` needs `hastad`/`coppersmith`.
- A large `n` is not safe — `|p-q|` small → `fermat` splits it.
- A large `e` is the *small-d* tell — `wiener`/`boneh-durfee`.
- ≥2 moduli ≠ `batch-gcd` — a *collision* is; `gcd=1` is a negative.
- A public PEM is `n`,`e` only — the rest is on the sheet.
- A bound exceeded is a theorem — record, don't retry.
- `pow(m,e,n)!=c` → a candidate, never a recovery.
- `phi=(p-1)(q-1)` fails for `n=p²`/prime/multi-prime.
- `inverse` failing → `eth-root`, not a bug.
- A socket printing numbers → transport, not an oracle.
See `common-mistakes-deep.md`.
