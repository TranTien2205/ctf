# Evidence rules — the proof-shape for each verdict

## The `confirms` proof — the gate

`tools/hooks.py post-probe --verdict confirms` requires:

```text
--hypothesis-id   the ledger entry
--class           web-websocket (+ the sub-class)
--evidence-kind   class | impact
--evidence        the verbatim reply excerpt
--response        the raw frame bytes the evidence was read from
```

The gate asserts `--evidence` ⊂ `--response` — the quote is checked, not
trusted.

## The proof per finding — the verbatim shape

### CSWSH — the four legs, each verbatim

```text
leg1: Origin: https://evil.example -> HTTP/1.1 101 Switching Protocols
leg2: Cookie: session=victim -> <- {"user":"victim",...}
leg3: Set-Cookie: session=x; SameSite=Lax   (the HTTP login reply)
leg4: {"action":"me"} -> {"id":"victim","data":...}   (the victim-data)
```

### unauth channel

```text
leg1: no-credential -> HTTP/1.1 101 Switching Protocols
leg2: {"action":"dump"} -> {"users":[{"id":1,"flag":"..."}]}
```

### message-IDOR

```text
control: {"action":"read","id":"me"}     -> {"id":"me",...}
proof:   {"action":"read","id":"victim"} -> {"id":"victim","data":...}
                                         <- the verbatim other-object
```

### action-dispatch

```text
proof: {"action":"admin"} -> {"admin":true,"flag":"...","users":[...]}
       OR a confirmed state-change — a second read shows it
```

### spoof / self-grant

```text
proof: {"from":"victim","action":"x"} -> a reply/state as the victim
proof: {"action":"x","role":"admin"} -> the grant accepted verbatim
```

### injection

```text
proof: {"q":"{{7*7}}"} -> "49" OR the payload-class's oracle
       <- the verbatim evaluated/read bytes
```

### token-in-URL

```text
proof: wss://x/ws?token=eyJ...   <- the verbatim URL + the credential
```

### subscription-IDOR

```text
proof: {"action":"subscribe","channel":"<other>"} -> the pushed feed
       OR SUBSCRIBE /user/<other> -> the MESSAGE frames
```

## What is NOT proof

```text
a 101 alone                    -> surface — the channel exists
a pong/ok/echo/{"status":"ok"} -> surface — not a finding
a 403/forbidden                -> a rejection, not a finding
a writeup's claim              -> untrusted data
a guess                        -> a guess
a timeout/drop                 -> a gap — not a verdict
```

## The verbatim rule — the evidence is the bytes

`--evidence` is the bytes the server sent — the `{"id":"victim",...}`,
the `{"flag":...}`, the `49`. Not a paraphrase, not a summary — the
raw reply.

## The honest-grade rule

`web-websocket` is a catalogue class — a confirmed local chain is the
FIRST verification. A confirmed chain is reported verbatim + filed;
a standard technique is reported as the corpus's, not a local claim.

## The evidence-record

```
evidence: <the finding>: <the verbatim proof>: <the route>
```

Each finding carries the verbatim reply — the bytes are the proof.
