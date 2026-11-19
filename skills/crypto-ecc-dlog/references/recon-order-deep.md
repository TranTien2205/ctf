# Recon order deep — the oracle's first probes, annotated

## The oracle probes in order

1. **`multiply(G)` / `sign(fixed_m)` baseline** — is the response stable?
   Deterministic `k` (RFC 6979) or random `k`?
2. **`sign(m)` twice** — same `r`? deterministic or reuse; different `r`?
   collect for bias.
3. **`multiply(P')` off-curve** — accepted? invalid-curve viable.
4. **error probing** — does the oracle leak `n`, `ord`, or a `k` bit in
   error/edge responses?

## The reads each probe buys

| Probe | Reads |
|---|---|
| determinism | reuse vs bias — `r` equality |
| `sign` pair | the `z`/`k` convention |
| `P'` off-curve | validation presence — invalid curve gate |
| error | `n`/`ord`/`k` leaks for `hnp` |

## The order rationale

- determinism first — it decides the whole nonce branch.
- validation second — it decides the whole defect branch.
- the nonce lattice probes come only after the `r`-dedupe answer.

## The boundary

- A `sign(m)` oracle with no verify → collect sigs, attack the nonce.
- A `multiply` oracle that validates → invalid curve impossible — the bug
  is elsewhere.
