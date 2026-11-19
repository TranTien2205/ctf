# Common mistakes (deep) — the failure modes, worked

## Mistake 1: treating a `101` as the finding

```
BAD:  ws_probe -> 101 Switching Protocols -> "the socket is vulnerable"
GOOD: the 101 is the channel; the finding is a frame that crossed a
      boundary — the {"id":"victim"} reply, the {"action":"admin"} reply
```

A `101` means the channel exists. A `pong`/`ok` is surface. No
cross-boundary frame = no finding.

## Mistake 2: two payloads on one socket

```
BAD:  send {"action":"read","id":"victim"} AND {"action":"admin"} on
      one socket -> a reply arrives -> "which caused it?"
GOOD: a fresh socket per mutation — the reply is attributable
```

The channel is async; the reply does not name the frame that caused it.

## Mistake 3: reading the HTTP twin, not the frame

```
BAD:  GET /api/objects/victim -> 403 -> "the object is protected; the
      WS is too"
GOOD: {"action":"read","id":"victim"} over the socket -> the WS authz is
      a SEPARATE, weaker implementation — measure the frame
```

The HTTP `403` does NOT close the WS cell.

## Mistake 4: the wrong envelope

```
BAD:  send {"action":"x"} into a Socket.IO channel -> nothing -> "the
      action is unknown"
GOOD: 42["x",{...}] — the Socket.IO parser needs the envelope
```

A clean-negative at the wrong framing is a framing error, not a finding.

## Mistake 5: CSWSH from a `101` alone

```
BAD:  foreign-Origin 101 -> "CSWSH"
GOOD: foreign-Origin + cookie-binding + SameSite-travels + data-channel
      — all four legs
```

Three legs = a weaker finding (the Origin gap); the four-leg chain is CSWSH.

## Mistake 6: a `weak-negative` reported as `uniform`

```
BAD:  {"action":"admin"} -> {"error":"unknown action"} -> "action is
      protected" -> close the cell
GOOD: "unknown action" means the NAME was wrong — probe the bundle's
      real action set; only a "forbidden" on a REAL action closes it
```

## Mistake 7: the token-in-URL conflated with CSWSH

```
BAD:  wss://x/ws?token=abc -> "the token is the auth; CSWSH needs the
      page to have it" -> CSWSH fails -> "no finding"
GOOD: the ?token= is a SEPARATE finding (credential-in-URL, leaks to
      logs) AND the channel may still carry data — two cells, two checks
```

## Mistake 8: a write-side frame treated as unproven because the reply was `ok`

```
BAD:  {"action":"transfer","to":"me"} -> {"status":"ok"} -> "ok is
      surface, no finding"
GOOD: a second read ({"action":"balance"}) confirms the state changed —
      the write-side oracle is the state-change, not the "ok"
```

## Mistake 9: probing a socket's intended happy path only

```
BAD:  only send the bundle's known-good frames -> "the socket works" ->
      no finding
GOOD: the known-good is the BASELINE — mutate one field per frame to
      find the boundary the happy path never exercises
```

## Mistake 10: ignoring the bundle's schema

```
BAD:  guess {"action":"x"} names -> unknown-action replies -> close
GOOD: bundle_miner + grep the emit/send/action strings -> the REAL
      schema -> probe the real names
```

## Mistake 11: a binary frame read as text

```
BAD:  the frame is \x0a\x05... -> read as text -> garbage -> "unknown"
GOOD: proto_decode.py frame.bin — a protobuf field-stream
```

## Mistake 12: a `SameSite` assumption, not a read

```
BAD:  "the cookie is SameSite=Lax so CSWSH is dead" -> close
GOOD: Lax travels on top-level navigation AND the server still accepts
      the foreign Origin — the SUBSET finding (the Origin gap) stands;
      the browser-CSWSH is the conditional part
```
