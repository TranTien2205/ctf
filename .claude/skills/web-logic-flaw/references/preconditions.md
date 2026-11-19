# Preconditions — what must be true for each mechanism to fire

Every mechanism has a precondition list — the conditions that must hold
for the shape to be exploitable at all. Check them before probing;
their absence is the falsifier.

## Mass assignment

- [ ] model carries privileged fields (`role`, `balance`, `verified`)
- [ ] binder merges extra request fields (merge-all, not allowlist)
- [ ] the field's write path isn't separately gated

Falsifier: stored-default on read-back → allowlist proven.

## Workflow skip

- [ ] a multi-step flow exists (cart→pay→confirm, register→verify→active)
- [ ] at least one transition checks a weaker precondition than the
      flow requires (existence vs state predicate)

Falsifier: every transition checks the full precondition — `302/400`.

## State replay

- [ ] a one-time action exists
- [ ] no consumed-marker, or a marker scoped so a replay escapes it

Falsifier: `409` on the serial replay — endpoint-level marker.

## Numeric boundary

- [ ] arithmetic on a user-supplied value (`qty*price`, `balance - amt`)
- [ ] the value's sign/zero/NaN/width isn't fully validated at the field

Falsifier: `400`/clamp on every boundary row — but only for THAT field.

## Scaling-after-check (Pachinko)

- [ ] an index is bounds-checked, then transformed before use
- [ ] the transform's reachable range exceeds the checker's intent —
      including regions the check never meant to protect

Falsifier: out-of-limit ID rejected identically to a malformed ID —
transform checked or absent.

## Unit confusion

- [ ] a value has implicit units and both representations reach the sink

Falsifier: canonical normalization — `100` means one thing everywhere.

## Idempotency

- [ ] a should-be-once action exists
- [ ] dedup absent, scoped wrong, or non-atomic

Falsifier: `409` on exact replay at the right scope.

## Trust-in-earlier-step

- [ ] a value travels server→client→server (hidden field, echo, cookie,
      token, header, callback)
- [ ] the downstream handler trusts it without recomputing

Falsifier: `400 mismatch` — the server recomputes.

## Time

- [ ] a time field reaches the check from client-controlled data
- [ ] the comparison uses the client's value, not server state

Falsifier: `400` on past/future values — server-side validation.

## Sequence

- [ ] IDs assumed monotonic
- [ ] no server-side ordering/uniqueness tracking

Falsifier: `409`/`400` on stale IDs.

## Ownership (logic-shaped)

- [ ] a transition references an object by ID
- [ ] the transition path skips the owner check (the read path's `403`
      doesn't decide — probe the transition)

Falsifier: `403` on the transition path too — route to IDOR for reads.

## Singleton

- [ ] a "the" object exists (admin, config, flag-holder)
- [ ] uniqueness assumed, not constrained

Falsifier: `409` on second create — uniqueness enforced.
