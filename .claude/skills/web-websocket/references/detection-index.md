# Detection index — the detection files, mapped

## The detection corpus

| File | Covers |
|---|---|
| `detection.md` | the first-pass detection — the endpoint + the handshake + the first frames |
| `detection-deep.md` | the full signal inventory + the protocol |
| `detection-matrix.md` | the observable→check→verdict matrix |
| `detection-signals.md` | every observable, its confidence, its class |
| `detection-index.md` | this map |
| `detection-checklist.md` | the detection pass, box by box |
| `detection-surface.md` | the per-surface detection order |
| `detection-playbook.md` | the detection playbook — the timed pass |
| `detection-catalogue.md` | the detection payload/observable catalogue |
| `lead-grammar.md` | the lead-vocabulary — the observation→class grammar |

## The detection order

```text
1. the endpoint-signal -> detection.md / detection-deep.md
2. the handshake-signal -> detection-matrix.md / handshake-side-deep.md
3. the schema-signal    -> detection-signals.md / the bundle grep
4. the framing-signal   -> framing-protocols-deep.md / per-transport-deep.md
5. the message-signal   -> detection-matrix.md / message-side-deep.md
6. the verdict          -> detection-matrix.md / decision-table.md
```

## The signal-to-file map

| The observed | The file |
|---|---|
| `new WebSocket`/`wss?://`/`Upgrade` | `detection.md`/`detection-deep.md` |
| `socket.io`/`SockJS`/`stomp`/`pusher`/`ably` | `framing-protocols-deep.md`/`per-transport-deep.md` |
| `?token=`/`?jwt=`/`?key=`/`?auth=` | `handshake-side-deep.md`/`detection-signals.md` |
| `Cookie:`/`Authorization:`/`?token=` | `handshake-side-deep.md`/`cswsh-deep.md` |
| `Sec-WebSocket-Protocol`/`graphql-ws`/`stomp`/`mqtt` | `per-transport-deep.md` |
| `"action":`/`"type":`/`"event":`/`"id":`/`"room":` | `detection-signals.md`/`per-message-field-deep.md` |
| a `101`/a `forbidden`/an `unknown` | `detection-matrix.md`/`decision-table.md` |
| a live chat/feed/doc/metric | `per-surface.md` |

## The detection-confidence ladder

| Confidence | The signal | The weight |
|---|---|---|
| high | `new WebSocket`/`Upgrade`/`socket.io`/`stomp`/`pusher`/`wss?://` | a ws endpoint — start here |
| medium | a live chat/presence/feed/doc | a probable ws — confirm |
| low | a `realtime`/`live` word in the UI | a maybe — grep the bundle |

## The detection-verdict discipline

- the ENDPOINT is detected by the bundle/traffic — `high`
- the CHECK is detected by the handshake probes — the `101`/`403`
- the GAP is detected by the message probes — the `oracle` reply
- the verdict is a measured reply — never an assumed one
