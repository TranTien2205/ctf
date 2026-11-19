# Error-message taxonomy — what the reject actually tells you

Every oracle is built from an error channel. Naming WHICH error layer
answered is the first read.

## The layers

| Layer | Typical answer | Distinguishes |
|---|---|---|
| Transport/framework | 400 bad request, 500 stack trace | malformed input vs processed input |
| Encoding layer | 'invalid hex', 'bad base64' | encoding vs crypto failure |
| Padding check | 'bad padding', silent reject | pad-valid vs pad-invalid |
| MAC/tag check | 'authentication failed' | MAC pass vs fail |
| Application | 'invalid user', 200-with-error | plaintext-level checks |

## The useful reads

- 500-stack-trace naming a crypto function: the crypto layer executed —
  corruption reached it.
- Different status for 'bad pad' vs 'good pad, bad MAC': the canonical
  padding oracle.
- Timing difference between pad-check (fast) and MAC-check (slower crypto):
  a timing oracle when statuses match.

## Reading order

1. Baseline the valid response.
2. Corrupt → which layer answers? (framework? crypto? app?)
3. The layer that answers with DISTINCT text for DISTINCT corruption types
   is the oracle channel.

## Traps

- Framework errors echo the INPUT — sanitize before assuming signal.
- A catch-all handler that returns identical 500s hides a still-useful
  timing channel underneath.
