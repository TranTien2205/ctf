# Common mistakes — the failure modes, in order

## 1. Treating a `101` as the finding

```text
BAD:  ws_probe -> 101 Switching Protocols -> "the socket is vulnerable"
GOOD: the 101 is the channel — the finding is a frame the server sent
      that crosses a boundary; a 101+pong/ok is surface
```

## 2. Two payloads on one socket

```text
BAD:  send {"action":"read","id":"victim"} AND {"action":"admin"} on one
      socket -> a reply arrives -> "which caused it?" -> unanswerable
GOOD: a fresh socket per mutation — the reply is attributable
```

## 3. Reading the HTTP twin, not the frame

```text
BAD:  GET /api/objects/victim -> 403 -> "the object is protected; the WS
      is too" -> close the cell
GOOD: {"action":"read","id":"victim"} over the socket -> the WS authz is
      a separate, weaker path — measure the frame
```

## 4. The wrong envelope

```text
BAD:  send {"action":"x"} into a Socket.IO channel -> nothing ->
      "the action is unknown" -> close
GOOD: 42["x",{...}] — the Socket.IO parser needs the envelope
```

## 5. CSWSH from a `101` alone

```text
BAD:  foreign-Origin 101 -> "CSWSH" -> report
GOOD: foreign-Origin + cookie-binding + SameSite-travels + data-channel
      — all four legs; a subset is a weaker finding
```

## 6. A `weak-negative` as `uniform`

```text
BAD:  {"action":"admin"} -> {"error":"unknown action"} -> "the dispatch
      is protected" -> close
GOOD: "unknown action" = the NAME was wrong — the bundle's real action
      set; only a "forbidden" on a REAL action closes the cell
```

## 7. The token-in-URL conflated with CSWSH

```text
BAD:  wss://x/ws?token=abc -> "the token is the auth; CSWSH needs the
      page to have it" -> CSWSH fails -> "no finding"
GOOD: ?token= is a SEPARATE finding (credential-in-URL); the channel
      may still carry the origin/unauth cells
```

## 8. A write-side frame treated as unproven because the reply was `ok`

```text
BAD:  {"action":"transfer","to":"me"} -> {"status":"ok"} -> "ok is
      surface, no finding"
GOOD: a second read — {"action":"balance"}/the HTTP state — confirms
      the state-change; the write-side oracle is the change
```

## 9. The happy-path-only probe

```text
BAD:  only send the bundle's known-good frames -> "the socket works" ->
      no finding
GOOD: the known-good is the BASELINE — mutate one field per frame to
      find the boundary the happy path never exercises
```

## 10. Ignoring the bundle's schema

```text
BAD:  guess {"action":"x"} names -> unknown-action replies -> close
GOOD: bundle_miner + grep the emit/send/action strings -> the REAL
      schema -> probe the real names
```

## 11. A binary frame read as text

```text
BAD:  the frame is \x0a\x05... -> read as text -> garbage -> "unknown"
GOOD: proto_decode.py frame.bin — a protobuf field-stream
```

## 12. A `SameSite` assumption, not a read

```text
BAD:  "the cookie is SameSite=Lax so CSWSH is dead" -> close
GOOD: Lax travels on top-level navigation AND the server still accepts
      the foreign Origin — the SUBSET finding (the Origin gap) stands;
      the browser-CSWSH is the conditional part
```

## 13. A guessed field as a real rejection

```text
BAD:  {"action":"read","theField":"x"} -> {"error":"invalid field"} ->
      "the field is protected" -> close
GOOD: "invalid field" = the field-NAME is wrong — the bundle's real
      field names; a real rejection is "forbidden" on a real field
```

## 14. The membership surface skipped

```text
BAD:  only probe {"action":"read"} / {"action":"x"} -> miss the
      subscribe/join/watch surface -> no finding
GOOD: the subscribe/join/watch/listen/follow is the OTHER read-side —
      another's feed — probe it
```

## The mistake-record

`mistake: <the claim>: <the reality>: <the fix>` — each failure mode
named; the rule that corrects it.
