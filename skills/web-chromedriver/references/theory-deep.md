# Theory deep — the formal properties

## The capability-is-not-a-bug property

A WebDriver session is a *capability* — a handle on a fully-powered
browser. The vulnerability is the *exposure* of that handle to an
unauthenticated client, not the browser itself. This is why the
detection question is `POST /session` — the bug is that it answers,
not what it does.

Consequence: the class is proven by the *reach* (a `sessionId`), not
the exploit — but the flag still needs a real read.

## The blind-channel property

A live admin bot is an opaque function: URL in, nothing out. Debugging
against it is a black-box test where each input costs a visit and
returns no signal. The information-theoretic content of a bot visit
is ~zero — you learn "worked or didn't" at best.

A local headless browser is the same function with the internals
exposed: console, errors, DOM, network. The information per iteration
goes from ~1 bit to the full trace. This is the entire economic
argument for the reproduction — it converts a near-zero-information
channel into a full-observability one.

## The reproduction-fidelity property

A reproduction transfers to the live bot iff it matches on the
behaviour-changing axes:

```
transfers(local -> live) iff  local.flags == live.flags
                          AND local.wait   == live.wait
                          AND local.cred   == live.cred
                          AND local.url    == live.url
                          AND local.version ~= live.version
```

A divergence on any axis makes local confirmations non-transferring —
a false positive (fires locally, dead live) or a false negative. This
is why the bot's source is read as a spec, and why unobservable
properties are recorded as assumptions.

## The positional-surface property

The browser's attack surface is *positional*: it sits on the challenge
host, so `localhost` is the app's loopback and `file://` is the
container's filesystem — surfaces an external request cannot reach.
The capability is the bridge to that position. This is the same reason
an SSRF is dangerous: both grant reach into a network position the
requester does not hold. The difference is the mechanism — a browser
(JS+DOM+cookies) vs a bare fetch.

## The jar-vs-view property

`GET /cookies` reads the browser's cookie *jar*; `document.cookie`
reads the JS *view* of it. `HttpOnly` is a restriction on the view,
not the jar — so the jar reads cookies JS cannot. The same flag
cookie is reachable by the jar API when invisible to the JS API.

## The serialisation property

`execute` returns JSON-safe values — the wire protocol serialises the
return across the process boundary. DOM nodes return as references,
functions/undefined as null, circular objects as errors, promises as
pending unless `async`+`awaitPromise`. The property is why `return
el.outerHTML` works and `return el` returns a handle.

## The evidence-tier property

Development evidence (local) and impact evidence (live) are different
tiers — the first proves the reproduction, the second proves the
target. The flag lives only in the second tier, gated through
`pre-flag`. Conflating them is the skill's most dangerous error: a
locally-confirmed payload is a reproduction result, not a target
result.
