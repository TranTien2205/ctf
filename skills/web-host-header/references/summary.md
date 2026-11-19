# Summary — the host-header corpus, in one page

The complete corpus, condensed — the model, the mechanisms, the proof, the falsifiers.

---

## The model

```text
a host-header is a HOST-header injection — a forged host → a canonical-
URL rewrite, a reset-link poisoning, a Location redirect, a Set-Cookie
domain, a cache key, a middleware rewrite — the app's trust check reads
the host's value.
```

## The mechanisms

```text
a canonical-URL sink     → a reflected host → the app's links/scripts
                          point to attacker.com — a stored injection
a reset-link sink        → a reflected forwarded header → the reset link
                          points to attacker.com — an account takeover
a Location sink          → a reflected host → the Location points to
                          attacker.com — an open redirect
a Set-Cookie sink        → a reflected host → the cookie domain binds to
                          attacker.com — a session fixation
a cache-key sink         → a reflected host → the cache stores the page
                          under attacker.com — a cache-poisoning feed
a rewrite sink           → a middleware rewrite → a 200 on the gated
                          route — an ACL bypass
a forwarded sink         → a reflected forwarded header → the app's
                          links point to attacker.com — a stored injection
a duplicated Host sink   → a duplicated Host → a parsing differential
a malformed Host sink    → a malformed Host → a parsing edge → a
                          differential
an absolute-URI sink     → an absolute-URI Host → a request-line
                          differential
a multi-header sink      → a combined injection → a privileged route
                          reached
a multi-proxy sink       → a chained normalization → a per-layer
                          differential
```

## The first confirming probe

```bash
# the canonical-URL check — a reflected host
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
#   the canonical URLs point to canary.example → a stored injection
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
#   the page's links/scripts point to canary.example → a stored injection
```

## The falsifiers

```text
a proxy that validates the Host against a server list → a 400 on a bad
host → a negative result, not a retry signal.
a proxy that strips the client-supplied forwarded header → the header
doesn't reach the app → the bypass fails → a different class.
a proxy that verifies the forwarded header it added → a client-supplied
header is rejected → the bypass fails → a different class.
a trust check that reads a different input → a different class.
a session check → an auth-session
a redirect → an open-redirect
a fetch → an ssrf
a read → a cors
a desync → a request-smuggling
a store → a cache-poisoning
a proxy header → a parser-differential
```

## The class boundary

```text
a host-header           → a HOST-header injection — a forged host → a
                        canonical-URL rewrite, a reset-link poisoning,
                        a Location redirect, a Set-Cookie domain, a
                        cache key.
a parser-differential   → a PROXY-header trust — a client-supplied or
                        a missing proxy header's fallback → a trust
                        check bypassed.
a cache-poisoning       → a STORE — a stored copy that serves YOUR
                        input — a key-mismatch — a store.
an auth-session         → a SESSION check — a trust check reads a
                        session / a token.
an open-redirect        → a REDIRECT — the app redirects to a URL the
                        request controls.
an ssrf                 → a FETCH — the app fetches a URL the request
                        controls.
a cors                  → a READ — a cross-origin fetch — the app's
                        bytes read.
a request-smuggling     → a DESYNC — a front-end and a back-end parse
                        the request boundary differently.
```

## The budget

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```

## The corpus map — which module covers what

```text
host-header              → the canonical-URL sink — the generated links
forwarded-headers        → the forwarded headers — the generated URLs,
                          reset links, redirects
rewrite-headers          → the rewrite headers — the middleware rewrites
detection                → the detection — the surface map
detection-checklist      → the detection checklist — the surface map
detection-deep           → the detection deep — the surface map
detection-index          → the detection index — the signal map
detection-matrix         → the detection matrix — the signal map
detection-surface        → the detection surface — the surface map
theory                   → the theory — the trust model
theory-deep              → the theory deep — the trust model exhaustively
workflow                 → the workflow — the detection→confirm→readback
workflow-deep            → the workflow deep — the sequence
field-manual             → the field manual — the per-surface sequence
exploitation             → the exploitation — the per-mechanism map
exploitation-playbook    → the exploitation playbook — the named plays
exploitation-shapes      → the exploitation shapes — the named attacks
multi-step-chains        → the multi-step chains — the chained attacks
case-studies             → the case studies — the canonical patterns
case-studies-deep        → the case studies deep — the canonical patterns
                          exhaustively
verified-chains          → the verified chains — the card's chain map
real-world-cases         → the real-world cases — the published patterns
payload-dictionary       → the payload dictionary — the probes
payload-dictionary-deep  → the payload dictionary deep — the probes
                          exhaustively
payload-variants         → the payload variants — the per-surface variants
payload-corpus           → the payload corpus — the categorized payloads
whitebox-hunt            → the whitebox hunt — the per-surface source map
evidence-rules           → the evidence rules — the proof standard
verification             → the verification — the confirm
readback-oracles         → the readback oracles — the bypass's read
negative-results         → the negative results — the dead paths
negative-results-deep    → the negative results deep — the dead paths
                          exhaustively
common-mistakes          → the common mistakes — the traps
common-questions         → the common questions — the FAQ
class-boundary           → the class boundary — the neighbor map
class-boundary-deep      → the class boundary deep — the neighbor map
boundary-conditions      → the boundary conditions — the falsifiers
evasion                  → the evasion — the per-proxy bypass
evasion-and-waf          → the evasion and WAF — the per-proxy bypass
troubleshoot             → the troubleshoot — the failures
troubleshoot-deep        → the troubleshoot deep — the failures
                          exhaustively
framework-matrix         → the framework matrix — the per-proxy map
framework-matrix-deep    → the framework matrix deep — the per-proxy map
                          exhaustively
frameworks-deep          → the frameworks deep — the per-framework map
proxy-behavior           → the proxy behavior — the per-proxy map
proxy-behavior-deep      → the proxy behavior deep — the per-proxy map
                          exhaustively
multi-proxy              → the multi-proxy chain — the chained
                          normalization
multi-proxy-deep         → the multi-proxy deep — the chained
                          normalization exhaustively
extended-corpus          → the extended corpus — the long tail
glossary                 → the glossary — the vocabulary
summary                  → this file — the corpus in one page
header-dictionary        → the header dictionary — the probes
header-map               → the header map — the per-proxy headers
normalization            → the normalization — the path differentials
path-normalization       → the path normalization — the path map
protocol-and-vhost       → the protocol and vhost — the scheme/host
                          differentials
structured-field-differentials → the structured-field differentials —
                          the Forwarded/Connection/Host parse differences
edge-cases               → the edge cases — the boundary conditions
per-surface              → the per-surface — the surface map
per-check                → the per-check — the check map
per-route                → the per-route — the route map
per-header               → the per-header — the header map
per-boundary             → the per-boundary — the boundary map
per-vector               → the per-vector — the vector map
per-mechanism            → the per-mechanism — the mechanism map
per-falsifier            → the per-falsifier — the falsifier map
per-proxy                → the per-proxy — the proxy map
per-mechanism-index      → the per-mechanism index — the mechanism index
per-surface-deep         → the per-surface deep — the surface map
                          exhaustively
per-check-deep           → the per-check deep — the check map
                          exhaustively
per-header-deep          → the per-header deep — the header map
                          exhaustively
per-vector-deep          → the per-vector deep — the vector map
                          exhaustively
per-mechanism-deep       → the per-mechanism deep — the mechanism map
                          exhaustively
per-proxy-deep           → the per-proxy deep — the proxy map
                          exhaustively
http-host-header         → the HTTP host-header — the core class
```
