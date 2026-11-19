# Onboarding (deep) — the full read-order for a first-timer

## The 10-minute mental model

```text
a WebSocket is an HTTP-upgrade + a bidirectional frame stream.
  - the UPGRADE is the auth/Origin checkpoint (one-shot)
  - the FRAMES are the app's API (per-message)
  - the HTTP app's authz lives in the request-handler;
    the WS's authz must live in the frame-dispatch — and it is
    routinely missing
the gaps:  the handshake (Origin/auth/token/subproto)
           the messages (IDOR/dispatch/spoof/inject)
```

## The read order — the corpus in order

```text
1. SKILL.md              -> the contract, the first probe, the tools
2. mechanism.md          -> the model — the two surfaces, the gaps
3. detection.md          -> how to know a ws surface is present
4. handshake-side.md     -> the upgrade checks — Origin/auth/token/subproto
5. cswsh.md              -> the CSWSH four-leg chain
6. message-side.md       -> the frame checks — IDOR/dispatch/spoof/inject
7. message-idor.md       -> the object-read gap, deepened
8. action-dispatch.md    -> the privileged-action gap, deepened
9. injection-in-frames.md -> the sink carriers
10. framing-protocols.md -> the envelopes — raw/socket.io/sockjs/stomp/
                            graphql-ws/mqtt/protobuf
11. workflow.md          -> the timed pass
12. evidence-rules.md    -> the verbatim-proof discipline
13. falsifiers.md        -> the kill-map
14. the -deep variants   -> the deepened files
15. the per-* maps       -> per-endpoint/per-field/per-transport/
                            per-channel/per-mechanism/per-target
16. the references       -> payload-dictionary, extended-corpus,
                            probe-catalogue, mechanism-catalogue,
                            decision-table, the discipline files
```

## The first exercise — the chat app

```text
a Socket.IO chat: wss://x/socket.io, 'history'/'dm'/'room'/'broadcast'
the pass:
  1. bundle_miner -> the endpoint + the 42["ev",{...}] shape
  2. the handshake -> a foreign-Origin 101 + a cookie-binding +
     SameSite=Lax -> CSWSH-able
  3. 42["history",{"room":"<other>"}] -> another's room -> a room-IDOR
  4. 42["dm",{"to":"admin","from":"x"}] -> a spoof
  5. 42["broadcast",{...}] -> a cross-client write
the verdict: the verbatim replies -> the class route
```

## The second exercise — the doc share

```text
a raw-WS doc app: wss://x/doc, 'open'/'op'/'sync'/'version'
the pass:
  1. the handshake cells
  2. {"action":"open","doc":"<other>"} -> a doc-IDOR
  3. {"action":"op","doc":"<other>","content":"x"} -> a write-side gap
  4. the coverage matrix -> the cells
the verdict: the verbatim replies -> the route
```

## The discipline habits — the muscle-memory

- a `101` is never the finding — the cross-boundary frame is
- one field per connection — the reply must be attributable
- the envelope before the payload — the framing is a precondition
- the bundle is the schema — grep it before guessing
- the HTTP `403` does not close the WS cell — measure the frame
- a `uniform` reply closes a cell — a `weak-neg`/`gap` does not
- CSWSH needs all four legs — the `101` is leg-1 only
- the verbatim reply is the evidence — not a paraphrase

## The vocabulary — the words to know

```
the handshake    -> the HTTP-upgrade + the 101
a frame          -> the transport unit — fin/opcode/masked/len/payload
the envelope     -> the transport's wrapper — 42[...]/a[...]/STOMP/etc.
the dispatch     -> the action/type/event/cmd routing
an oracle        -> a boundary-crossing reply — the proof
a uniform        -> a measured rejection — a closed cell
a weak-neg       -> a guessed-name rejection — a re-probe
a gap            -> an unresponsive cell — not a verdict
CSWSH            -> the four-leg cross-site channel hijack
a message-IDOR   -> a per-frame object gap
a dispatch gap   -> a privileged action with no role check
a self-grant     -> a role/perm/scope field bound by the frame
a spoof          -> a from/user_id/sender the server trusts
```

## The tools — the first commands

```bash
python3 tools/web/ws_probe.py --selftest          # the tool works
python3 tools/web/bundle_miner.py "$BASE" --out /tmp/bundle  # the schema
python3 tools/proto_decode.py frame.bin           # the binary frames
```

## The onboarding-record

`onboarding: <the exercise>: <the verdict>: <the lesson>` — the exercise
is the learning; the lesson is the discipline.
