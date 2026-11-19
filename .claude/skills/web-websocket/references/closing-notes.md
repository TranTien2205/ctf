# Closing notes — the last-pass checklist before reporting

## The coverage check

- [ ] every `endpoint × check` cell is `oracle`/`uniform`/`unmeasured`-marked
- [ ] no `unmeasured` cell left that the budget could still buy
- [ ] each `uniform` cell's verbatim reply is recorded
- [ ] each `weak-negative` names the re-probe that reopens it
- [ ] each `gap` is recorded as a `gap`, not a `uniform`

## The finding check

- [ ] each `oracle` has the verbatim reply — the bytes the server sent
- [ ] the `post-probe` `--evidence` is a substring of `--response`
- [ ] each `oracle` names the flag-closing class/route
- [ ] a `101`/`pong`/`ok`/echo was not claimed as a finding
- [ ] a `SameSite`/binding leg was not inflated into full CSWSH
- [ ] a `uniform`-claim is a measured `uniform`, not a guessed one
- [ ] a `weak-negative` is reported as weak, not `uniform`

## The boundary check

- [ ] a frame-field injection routes to the PAYLOAD class
- [ ] an HTTP object-gap routes to `web-idor`, not this class
- [ ] a token's forge routes to `web-auth-session`
- [ ] a one-shot forged request routes to `web-csrf` (not CSWSH)
- [ ] a `graphql-ws` subscription routes the QUERY to `web-graphql`

## The catalogue-honesty check

- [ ] `web-websocket` is reported as a catalogue class — no local card
- [ ] a confirmed chain is filed via `classify_solve.py` — the FIRST
      local verification, not claimed as prior
- [ ] no writeup's claim was reported as a local finding

## The record check

- [ ] `../field-notes.md` has the endpoint, the framing, the auth, the
      oracle cells, the `uniform` cells
- [ ] the coverage matrix is recorded
- [ ] the budget ledger is within the 5/15 + 25/45 bounds
- [ ] each probe is one-field-per-connection
- [ ] a state-changing probe was kept low-volume and non-destructive

## The escalate check

- [ ] on `uniform`-all-cells: the escalation rungs — `chain_match`,
      `reclassify`, `writeup_search`, `novel_plan`, `fanout_sweep`,
      `solver_handoff` — are the next step, not "no bug"
- [ ] a spent budget → `tools/decide.py` answers `escalate`, not a
      guess at a sixth variant

## The report shape

```
endpoint:  <the ws path>
framing:   <raw|socket.io|sockjs|stomp|graphql-ws|mqtt|protobuf>
auth:      <cookie|token|bearer|none>
oracle:    [<the verbatim cross-boundary frames + the route>]
uniform:   [<the measured dead-end cells>]
weak-neg:  [<the re-probe named>]
gap:       [<the unresponsive cells>]
flag:      <the verbatim flag-bearing reply, if any>
```

## The last word

The socket is the transport; the finding is the frame. A `101` is never
the bug — the cross-boundary frame is. The corpus covers the four
mechanisms (CSWSH/unauth/IDOR/dispatch), the injection carriers, the
framing envelopes, and the evidence discipline — the depth is the
per-field per-mechanism pass, one mutation at a time.
