# Two-validator gap deep — the check/check mismatch internals

`two-validator-gap.md` covers the shape. This module is the internals —
where the second validator lives, what makes them disagree, and the
full mismatch taxonomy.

## The shape

Two components both validate "the same" value — a WAF and an app, a
schema and a binder, a checker and a sink — holding different models of
what "valid" means. The gap is the set-difference: values one accepts
that the other rejects, or representations one normalizes that the
other doesn't.

```
validator A:  id < LIMIT          — reads the raw index
sink B:       mem[off + id*S]     — uses the transformed index
```

Pachinko: A's range `[0, LIMIT)` maps under `off + id*S mod 2^w` to
addresses B was never told to exclude.

## Where the two validators live

| Validator A | Validator B | The gap |
|---|---|---|
| WAF | app binder | encodings/spellings WAF misses |
| JSON schema | form binder | a second content-type path |
| create binder | update binder | per-method allowlists |
| transport parser | app parser | duplicate keys — first vs last wins |
| UI bounds | server checker | UI bound is client-side fiction |
| checker | sink | checked value ≠ used value (Pachinko) |
| endpoint dedup | ledger dedup | `200` twice, effect once |
| proxy normalizer | app normalizer | `web-parser-differential` ground |

## The disagreement taxonomy

### Domain disagreement

A accepts `[0, 65535]`; B uses `off + id*4` reaching `[off, off+262140]`
— B's reach exceeds A's intent. Probe: `id` values past the documented
bound, diff the rejection layer.

### Representation disagreement

A inspects `role` (literal); B binds `%72ole` (decoded) — different
normalization stages. Probe: encoded/cased/decorated keys.

### Cardinality disagreement

A validates `params["role"]` (first); B binds `params.get_all("role")`
(last or array) — duplicate-key semantics. Probe both orders:
`role=user&role=admin` AND `role=admin&role=user` — the winner names
which element B takes.

### Time disagreement

A checks `expiry` at request entry; B evaluates it later — a TOCTOU on
time itself. Or A's clock vs B's clock drifting — `expiry == now`
inclusive/exclusive probes.

### Scope disagreement

A dedups `(user, code)`; B applies `(code)` globally — or the reverse.
The key-coverage probes enumerate which.

### Layer disagreement

A rejects at transport (schema); B would accept at binder. The
contrast probe — malformed vs out-of-limit — names which layer each
rejection came from; a value passing A and failing at B with a
different error is the different-layer signal.

## The detection protocol

1. Map validator A's range: binary-search the `200`→`400` boundary.
2. Submit values just past A's documented bound; bucket rejections by
   shape (status + text + timing).
3. A DIFFERENT-shaped rejection = value passed A, died at B — the gap
   is live and the layer is located.
4. The same-shaped rejection = B shares A's bound — falsifier.

## The exploitation pattern

Once the gap is live, the question is what B's unchecked range
reaches:

- transform output → memory outside the checked region (Pachinko's
  instruction-memory write);
- decode output → fields the schema never saw (the `role` that was
  `%72ole` at inspection time);
- coerce output → types the validator assumed impossible (`"0x10"` →
  `16` where `0x10` wasn't a "number" to check);
- concatenate output → split keys rejoining downstream.

The general sentence, one more time: **the value the checker bounds is
not the value the sink uses**. Every two-validator gap is that sentence
with different nouns.
