# Field notes deep — what a real solve records

## The record, complete

After a solve, `post-probe` gets:

- `hypothesis-id` — the attack id (`ecdsa-nonce-reuse`, `hnp-ecdsa`, ...).
- `class` — `crypto-ecc-dlog`.
- `evidence-kind` — `class` (the scalar + verify) or `impact` (the flag).
- `evidence` — the verbatim output: `d=0x…`, `d·G == Q`, `x=…`, `pow==h`.
- `response` — the bytes the evidence was read from (tool output, the
  decoded flag bytes).

## The falsifier record

A falsified attack goes to `knowledge/attempts/<challenge>.json`:

```json
{
  "attack": "hnp-ecdsa",
  "result": "verify-failed",
  "falsifier": "d·G != Q with 8 sigs, B=2^128",
  "reopen_if": "challenge supplies a nonce bound"
}
```

## The chain-card record

A real solve → `knowledge/chains/` card via `classify_solve.py`:

- params (`p a b G n` or curve name),
- attack id + flags,
- the falsifier that would have saved time,
- the verify transcript.

## The `../field-notes.md` shape

```
## <date> — <challenge>
- hypothesis: ecdsa-nonce-reuse
- result: confirmed — d recovered, d·G == Q
- evidence: <verbatim output>
- falsifier-noted: none / <if any>
```

`proposed` → `confirmed` after review (`../../../LEARNING_LOOP.md`).
