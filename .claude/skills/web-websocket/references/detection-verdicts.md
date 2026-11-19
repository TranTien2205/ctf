# Detection verdicts — the reply-shape taxonomy, complete

## The verdict vocabulary — the six verdicts

| Verdict | The reply shape | The meaning |
|---|---|---|
| `oracle` | a cross-boundary reply | the finding — the boundary crossed |
| `uniform` | a measured rejection | a closed cell — the check holds |
| `weak-negative` | a guessed-name rejection | a re-probe — the schema was wrong |
| `gap` | an unresponsive/dropped frame | unmeasured — not a verdict |
| `surface` | a `101`/`pong`/`ok`/`echo`/`Set-Cookie` | not a finding — the happy-path |
| `candidate` | a potential — a `500`/crash/differential | a lead — not a verdict |

## The `oracle` replies — the cross-boundary set

```text
{"id":"<other>","data":...}         another's object -> message-IDOR
{"doc":"<other>","flag":...}         another's doc -> message-IDOR
{"user":"<other>","data":...}        another's record -> message-IDOR
{"admin":true,"flag":...}            a privileged reply -> dispatch
{"flag":"..."}                       the flag -> dispatch/read
{"role":"admin"} accepted            a self-grant
a reply acting-as-<other>            a spoof
49 / "7*7" evaluated                 an injection (ssti)
rows/data after " OR 1=1"           an injection (sqli)
uid=.../root:x:... after ;id/../     an injection (cmdi/lfi)
a server-fetch reply after url:      an injection (ssrf)
a pushed feed after subscribe        a subscription-IDOR
a state-change confirmed by a read   a write-side gap
the victim's data on a foreign socket -> CSWSH
a resumed foreign context            a resumption gap
the internal namespace's frames      a namespace-membership
```

## The `uniform` replies — the real rejections

```text
{"error":"forbidden"}                a real rejection — a role/scope check
{"error":"unauthorized"}             a real rejection — an auth check
{"error":"access denied"}            a real rejection
{"status":403}/{"status":401}        a real rejection
a close-frame 1008                   a policy-violation close
{"error":"not permitted"}            a real rejection
{"error":"insufficient permission"}  a real rejection
```

A `uniform` on EVERY field/action in a mechanism -> the cell is closed.

## The `weak-negative` replies — the guessed-name rejections

```text
{"error":"unknown action"}           the action-NAME is wrong
{"error":"invalid action"}           the action-NAME is wrong
{"error":"unknown field"}            the field-NAME is wrong
{"error":"invalid field"}            the field-NAME is wrong
{"error":"not found"}                the resource does not exist — a
                                     guessed id, not a check
{"error":"invalid id"}               the id-shape is wrong
{"error":"no such object"}           a guessed id
{"error":"malformed"}                the framing is wrong
{"error":"bad request"}              the framing is wrong
{"error":"invalid request"}          the framing is wrong
{"error":"unrecognized"}             a guessed name/shape
{"error":"missing field"}            a missing field — the schema
```

A `weak-negative` means the PROBE was wrong, not the check — the
bundle's real action/field/envelope is the re-probe.

## The `gap` replies — the unmeasured

```text
a 101 + silence/drop on every frame   -> a closed/write-only channel
a frame dropped with no reply         -> the channel may process silently
a timeout                             -> a gap — not a verdict
a pong that never returns data        -> a subscribe-only channel
```

A `gap` is not `uniform` — the channel did not REJECT the frame; it
ignored it. The cell is unmeasured.

## The `surface` replies — the happy-path

```text
HTTP/1.1 101 Switching Protocols      -> the channel exists — surface
{"status":"ok"}/ok                    -> an accept — surface
{"result":"ok"}/{"success":true}      -> an accept — surface
pong / {"type":"pong"}                -> a keepalive — surface
the sent-data echoed back             -> an echo — surface
Set-Cookie / X-User / X-Role          -> the handshake's reply — surface
CONNECTED / CONNACK / connection_ack  -> a protocol-ack — surface
hello / welcome / open                -> a protocol-hello — surface
```

A `surface` reply is the channel working — NOT a finding and NOT a
`uniform`.

## The `candidate` replies — the leads

```text
a 500 / a crash                       -> a parser/branch differential
a foreign-Origin 101                  -> a CSWSH-candidate
a partial-frame / a fragment          -> a framing differential
a ?token=/?jwt= on the URL            -> a credential-in-URL candidate
an unexpected Sec-WebSocket-Protocol  -> a sub-protocol candidate
```

A `candidate` is a lead — verify before a verdict.

## The verdict-record

`verdict: <the reply>: <the verdict-shape>: <the cell's state>` — each
reply mapped to a verdict + the cell's resulting state.
