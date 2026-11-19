# Glossary — business-logic vocabulary

- **allowlist binding**: the handler copies only named fields from the
  request into the model. The mass-assignment falsifier.
- **baseline**: the same request without the manipulation, run and saved
  first. Logic evidence is a diff; the baseline is half of it.
- **boundary alphabet**: the canonical set of numeric edge values (`-1`,
  `0`, `-0`, `NaN`, `Infinity`, `1e309`, int/uint wraps, hex, strings).
- **chain card**: a `knowledge/chains/*.json` record of a verified solve —
  a candidate shape with its own `first_confirming_probe`, never a proof.
- **checker bound**: the limit the validator actually enforces (measured
  from rejection behavior), vs the **documented bound** (what the
  description says) and the **effective bound** (what the transform
  permits).
- **echo**: the response to a write reflecting the sent fields. Proves
  parsing, not storage — confirm with a separate read-back.
- **family_leads**: chain-card matches reached through `chain[]` prose
  vocabulary — always weak, read-only leads, never recordable probes.
- **falsifier**: a probe result that closes a hypothesis. `role: user`
  after `role=admin` falsifies mass assignment on that endpoint.
- **idempotency**: the property that replaying an action has the same
  effect as running it once. Its absence is the replay shape.
- **layer**: where in the pipeline a value is rejected — transport/schema,
  binder, state machine, ledger, transform. Different layers reject with
  different shapes; identical rejections across probes name one layer.
- **mass assignment**: the binder copying unrequested fields into the
  model — `role=admin` at register.
- **mechanism alphabet**: this skill's enumeration of logic-flaw
  mechanisms — field-binding, ordering, replay, boundaries, transforms,
  trust. Each has a probe and a falsifier.
- **negative result**: a probe with no distinguishing signal — bounds the
  mechanism's location without closing it.
- **read-back**: confirming a write's effect through a separate GET.
  The echo is not the store.
- **replay**: re-sending a completed transition — the serial form tests
  idempotency (logic-flaw); the parallel form tests TOCTOU
  (race-condition).
- **scaling-after-check**: the value is bounds-checked raw, then
  transformed (offset, scale) before use — the Pachinko shape.
- **singleton assumption**: code that assumes one privileged object exists
  and doesn't enforce uniqueness on creating a second.
- **state machine**: the graph of permitted transitions the handlers
  implement — vs the line the developer imagined. The flaw is an extra
  edge.
- **transform**: any arithmetic or encoding between check and use —
  offset+scale, unit conversion, decode, coercion. The check covers the
  input; the sink consumes the output.
- **trust-in-earlier-step**: a downstream handler trusting a value an
  upstream step produced — hidden-field prices, step-1 tokens at step 3,
  boundary headers.
- **validator gap**: two validators (or a validator and a sink) holding
  different models of the same value — the generalized Pachinko lesson.
