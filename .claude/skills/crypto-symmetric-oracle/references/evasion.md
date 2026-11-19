# Evasion — when the service fights the oracle

Defenses you'll meet and how to work within (or around) them.

## Rate limiting

- Measure the accepted rate before starting; a loop that exceeds it gets
  blocked mid-byte.
- Space requests just under the limit; a 429 is a reset point, not noise.
- If parallel connections are allowed, bound them — a shared instance dies
  at ~50 concurrent.

## Response normalization

- The service collapses all errors to one page: the oracle channel may have
  moved to timing only — `timing-oracles.md`.
- Headers stripped of distinguishing fields: fall to body length.

## Request validation

- Schema-checked inputs (hex only, fixed length): match the schema — the
  oracle is inside it.
- Signed requests: find the signing path first; sometimes the signature
  itself is the oracle.

## Nonce/IV hygiene

- Nonce generated per-request: reuse attacks close; pivot to malleability
  or padding.
- Keyed nonces you can't predict: only observable reuse matters.

## Tag-before-decrypt hardening

- The classical countermeasure: nothing in this class survives it except
  nonce misuse. This is the honest exit, not a wall to batter.

## Key rotation

- If the key rotates per session, your captured oracle answers expire with
  it — run the whole loop in ONE session or the bytes don't compose.

## What is NOT evasion

- A different bug class pretending to be an oracle: a 500 from a missing
  template is not a crypto oracle.
