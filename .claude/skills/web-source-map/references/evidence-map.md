# Evidence map — what each find is allowed to claim

## The ladder

```
surface  -> a string in the bundle (the client claims it)
claim    -> the call site (the client calls it)
class    -> verified live (the server responds / the key authenticates)
impact   -> the routed class exploits it
flag     -> gated + read from a live/artifact response
```

## The per-find evidence level

| Find | Level | What it may claim |
|---|---|---|
| an endpoint string | surface | "the client references `/api/x`" |
| an endpoint that 200s | class | "the server exposes `/api/x`" |
| a secret candidate | surface | "a key-shaped string exists" |
| a secret that authenticates | class | "a live credential" |
| a feature flag | surface | "the client gates on `feature.X`" |
| a flag whose endpoint is public | class | "a client-side gate, bypassable" |
| a route path | surface | "the SPA knows `/admin`" |
| a route whose endpoint is real | class | "a real admin endpoint" |
| an internal host | surface | "the client calls an internal host" |
| an internal host via SSRF | class | "the internal host is reachable" |
| a flag shape | surface | "a flag-shaped string" |
| a flag gated + read | flag | "the flag" |
| recovered source | surface | "what the build claims the code is" |

## The verbatim-excerpt rule

A `confirms` through `post-probe` requires `--evidence` be a verbatim
substring of `--response` — for a map find, the response the endpoint
returned or the response the secret unlocked. "I found X in the bundle"
is not evidence; the bytes it unlocked are.

## The pre-flag gate

A flag shape in recovered source is a *candidate* — `pre-flag` it; it
counts only when read from a live/artifact response and gated.

## The provenance rule

Every lead carries: source file + verbatim string + verify result. A
lead without provenance is not traceable; a finding without the live
check is not a finding.

## The untrusted-source caveat

The bundle/map are attacker-controlled — a recovered "source" is what
the build *claimed*, a `sources` path is a traversal candidate, a
"secret" may be planted. Read the source as a spec; verify its claims
live; do not execute it.
