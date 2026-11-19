# Workflow (deep) — the complete timed pass

## Phase 0 — recon (bounded, ~3 commands)

```bash
python3 tools/web/bundle_miner.py "$BASE" --out /tmp/bundle
grep -riE 'wss?://|socket\.io|SockJS|stomp|pusher|ably|graphql-ws|new WebSocket' /tmp/bundle
grep -riE '(action|type|event|cmd|method|op|id|room|channel|token|jwt|auth)":"?' /tmp/bundle | head -40
```

Outputs: the ws endpoint, the client library (the framing), the action
set, the field names, the auth mechanism.

## Phase 1 — handshake-side

```bash
# 1a. the baseline handshake
python3 tools/web/ws_probe.py "$WS/ws" --message '{}'
# 1b. the foreign Origin
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://evil.example' --message '{}'
# 1c. the cookie-binding
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=victim' --message '{"action":"me"}'
# 1d. the no-auth open
python3 tools/web/ws_probe.py "$WS/ws" --message '{"action":"me"}'
# 1e. the sub-protocols
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Sec-WebSocket-Protocol: graphql-ws' --message '{}'
# 1f. the SameSite read
curl -sI "$BASE/login" | grep -i 'set-cookie'
```

## Phase 2 — the schema + the framing

- the bundle's `ws.send`/`socket.emit` → the first-frame shape + the
  action set
- the `Sec-WebSocket-Protocol` → raw/Socket.IO/SockJS/STOMP/graphql-ws
- a real-session capture → the ground-truth frames
- the envelope → the send-shape (raw/`42[...]`/`a[...]`/STOMP/`type:`)

## Phase 3 — the message-side, one field per connection

```bash
# per field, per mechanism — a fresh socket per mutation
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
  --message '{"action":"read","id":"victim"}'          # idor
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
  --message '{"action":"join","room":"admin"}'         # membership
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
  --message '{"action":"admin"}'                        # dispatch
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
  --message '{"from":"victim","action":"flag"}'        # spoof
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
  --message '{"q":"{{7*7}}"}'                           # inject
```

## Phase 4 — the verdict + the route

- a cross-boundary frame (another's object/a privileged action/a
  self-grant/an injection echo) → `hooks.py post-probe --verdict confirms`
  with the verbatim reply
- a state-change → a second read confirms it
- a clean `forbidden`/`unknown`/`dropped` → the measured negative

## Phase 5 — the record + the coverage

- each confirmed frame → the verbatim record + the class route
- each `uniform` cell → the negative record
- the `endpoint × check` matrix → every cell marked
- `../field-notes.md` — the endpoint, the framing, the auth, the verdicts

## The budget ledger

| Class | Probes | Cap |
|---|---|---|
| handshake-side | ~6 | within |
| message-side | ~12 | within |
| the whole socket | ~20 | 25/45 |

Stay inside — a `uniform` cell is a measured cell, not a failure to keep
probing.
