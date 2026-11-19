# Detection playbook — the timed detection pass

## Minute 0-2 — the bundle

```bash
python3 tools/web/bundle_miner.py "$BASE" --out /tmp/bundle
grep -riE 'wss?://|new WebSocket|socket\.io|SockJS|stomp|pusher|ably|graphql-ws|mqtt' /tmp/bundle | head -10
```

Decide: the ws endpoint + the client library + the framing.

## Minute 2-4 — the schema + the auth

```bash
grep -riE '"(action|type|event|cmd|method|op|id|room|channel|user_id|role|from|to|token|q|filter|file|url|data|subscribe|join|destination|topic)"' /tmp/bundle | head -30
grep -riE '(cookie|authorization|bearer|token|jwt|\?token=|\?auth=|sec-websocket-protocol)' /tmp/bundle | head -15
curl -sI "$BASE/login" | grep -i 'set-cookie'
```

Decide: the action/field set + the auth mechanism + the SameSite.

## Minute 4-6 — the handshake cells

```bash
python3 tools/web/ws_probe.py "$WS/ws" --message '{}'                                    # baseline
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://evil.example' --message '{}'   # origin
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"me"}'  # binding
python3 tools/web/ws_probe.py "$WS/ws" --message '{"action":"me"}'                       # unauth
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Sec-WebSocket-Protocol: graphql-ws' --message '{}'  # subproto
```

Decide: the handshake verdicts — the `101`/`403`/`drop`/binding.

## Minute 6-9 — the message cells

```bash
# per mechanism — a fresh socket per mutation
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"read","id":"victim"}'   # idor
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"join","room":"admin"}'  # membership
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"admin"}'                # dispatch
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"from":"victim","action":"flag"}' # spoof
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"q":"{{7*7}}"}'                   # inject
```

Decide: the message verdicts — the `oracle`/`uniform`/`weak-neg`/`gap`.

## Minute 9-10 — the coverage + the route

```text
the matrix: every endpoint x check cell -> oracle/uniform/unmeasured
the route:  each oracle -> the flag-closing class
the record: the verbatim replies + the negative ledger
```

## The timed-budget decision

- 10 minutes buys the full detection pass — the endpoint + the handshake
  + the schema + the first message cells
- a `uniform` cell is closed in its probe — not re-probed
- a `weak-neg`/`gap` is a pending cell — the re-probe is named
- the budget's remainder goes to the `unmeasured` cells in cheapest-first
  order

## The playbook-record

`playbook: <minute>: <the step>: <the verdict>` — each minute's step +
the verdict it produced; the playbook is the timed pass.
