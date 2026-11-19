# Per-probe map — the canonical probes and what each proves — deep

| Probe | Request(s) | Proves |
|---|---|---|
| Replay | same input ×2 | deterministic vs per-request IV |
| Length-step | input k vs k+1 | block vs stream, block size |
| Repetition | 'A'*48 | ECB fingerprint |
| Corruption-A | flip byte in C_{i-1} | does a pad-ish error appear |
| Corruption-B | keep pad valid, break MAC | the second answer → oracle exists |
| Tag-tamper | corrupt the tag field | tag verified? before decrypt? |
| Nonce-diff | collect two records | nonce reuse present |
| Prefix-map | vary each input field | which ct block holds which field |
| Alignment-pad | 'A'*k sweep | fixed prefix length mod block |
| Secret-length | grow input, watch plateaus | hidden suffix length |
| Rate measure | N requests timed | loop feasibility |
| Timing-pair | 50+ samples ×2 conditions | timing channel exists |
| Truncation | tag prefixes len 1..16 | minimum accepted tag |
| Encoding-peel | decode ct hex→b64→raw | what's actually encrypted |
| Verify-shape | valid vs invalid tag | verify oracle exists |

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Probe | Request(s) | Proves |
|---|---|---|
| Replay | same input ×2 | deterministic vs per-request IV |
| Length-step | input k vs k+1 | block vs stream, block size |
| Repetition | 'A'*48 | ECB fingerprint |
| Corruption-A | flip byte in C_{i-1} | does a pad-ish error appear |
| Corruption-B | keep pad valid, break MAC | the second answer → oracle exists |
| Tag-tamper | corrupt the tag field | tag verified? before decrypt? |
| Nonce-diff | collect two records | nonce reuse present |
| Prefix-map | vary each input field | which ct block holds which field |
| Alignment-pad | 'A'*k sweep | fixed prefix length mod block |
| Secret-length | grow input, watch plateaus | hidden suffix length |
| Rate measure | N requests timed | loop feasibility |
| Timing-pair | 50+ samples ×2 conditions | timing channel exists |
| Truncation | tag prefixes len 1..16 | minimum accepted tag |
| Encoding-peel | decode ct hex→b64→raw | what's actually encrypted |
| Verify-shape | valid vs invalid tag | verify oracle exists |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`
