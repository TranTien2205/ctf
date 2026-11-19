# Per-boundary map — each boundary and its owning module — deep

| Boundary | Module | The one-line rule |
|---|---|---|
| Compression before encryption | `boundary-cases.md` | length oracle, not byte-at-a-time |
| Random per-request prefix | `block-alignment.md` | attack a fixed suffix backwards |
| CTR block-level counters | `ctr-nonce-reuse.md` | align by absolute counter |
| Truncated digests | `length-extension.md` | state-width retention decides |
| Multi-block secrets | `ecb-byte-at-a-time.md` | synthetic window per block N |
| Pad \\x01 false positive | `cbc-padding-oracle.md` | re-probe with byte[14] changed |
| Rate limits | `response-distinguishers.md` | measure rate, bound requests |
| Padding-free modes | `authenticated-boundary.md` | tag is the check, not the pad |
| Authenticated before decrypt | `authenticated-boundary.md` | class closed — route out |
| Random 96-bit GCM nonce | `gcm-nonce-reuse.md` | birthday bound, usually unreachable |
| HMAC/sponge MAC | `hmac-vs-raw-mac.md` | no MD state to extend |
| Constant-time verify | `verify-oracle.md` | no timing channel exists |
| Base64/hex layering | `edge-cases.md` | decode before any XOR |
| DES 8-byte blocks | `edge-cases.md` | recipe scales to block size |
| Key-boundary mid-blob | `ecb-prefix-suffix.md` | secrets may use different keys |

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Boundary | Module | The one-line rule |
|---|---|---|
| Compression before encryption | `boundary-cases.md` | length oracle, not byte-at-a-time |
| Random per-request prefix | `block-alignment.md` | attack a fixed suffix backwards |
| CTR block-level counters | `ctr-nonce-reuse.md` | align by absolute counter |
| Truncated digests | `length-extension.md` | state-width retention decides |
| Multi-block secrets | `ecb-byte-at-a-time.md` | synthetic window per block N |
| Pad \\x01 false positive | `cbc-padding-oracle.md` | re-probe with byte[14] changed |
| Rate limits | `response-distinguishers.md` | measure rate, bound requests |
| Padding-free modes | `authenticated-boundary.md` | tag is the check, not the pad |
| Authenticated before decrypt | `authenticated-boundary.md` | class closed — route out |
| Random 96-bit GCM nonce | `gcm-nonce-reuse.md` | birthday bound, usually unreachable |
| HMAC/sponge MAC | `hmac-vs-raw-mac.md` | no MD state to extend |
| Constant-time verify | `verify-oracle.md` | no timing channel exists |
| Base64/hex layering | `edge-cases.md` | decode before any XOR |
| DES 8-byte blocks | `edge-cases.md` | recipe scales to block size |
| Key-boundary mid-blob | `ecb-prefix-suffix.md` | secrets may use different keys |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`
