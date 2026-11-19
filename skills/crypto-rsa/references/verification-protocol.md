# Verification protocol — the proof procedure

1. **Recover** the value — `m`/`d`/`p`,`q`.
2. **Run the gate** — `pow(m,e,n)==c` / `p*q==n` / `pow(c,d,n)==m`+`pow(m,e,n)==c`.
3. **Sanity** — `1<p<n`, `p` prime, `n-phi+1==p+q`.
4. **Strip a pad** — `\x00\x02<pad>\x00` / OAEP if `m` is a padded block.
5. **`eth-root`** — try each `gcd` candidate; `pow`+format picks.
6. **Record** — `solved/` the evidence tuple `{sheet,attack,bound,recovered,pow}`;
   `hooks.py post-probe` with `--response` = the `pow` output.

The falsifier — the bound exceeded — is a negative: `negative-results.md` +
`knowledge/attempts/`. A `pow`-failing value is a candidate, never a recovery.
See `verify.md`, `evidence-*.md`.
