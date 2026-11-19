# Summary — the parser-differential corpus, in one page

The complete corpus, condensed — the model, the mechanisms, the proof, the falsifiers.

---

## The model

```text
a front-end (a proxy, a gateway, a WAF) parses the request one way; a
back-end (the app) parses it another — the same bytes, two different
interpretations — the disagreement is the vulnerability.
```

## The mechanisms

```text
a hop-by-hop bypass        → a proxy strips its own header → a missing-
                           header fallback → the trust check bypassed
a client-supplied bypass   → a forged proxy header → the app trusts it →
                           the trust check bypassed
a forwarded-host rewrite   → a forged host → the app's links rewritten
a forwarded-scheme downgrade → a forged scheme → the app's links rewritten
an X-Original-URL rewrite  → a forged path → the app's path rewritten
an internal-flag bypass    → a forged internal flag → the check bypassed
an admin-flag bypass       → a forged admin flag → the check bypassed
a forwarded-for spoof      → a forged local IP → the check bypassed
a forwarded-user spoof     → a forged user → the check bypassed
a path-normalization bypass → a normalization differential → a route-confusion
a method-override bypass   → a forged method → a method-override
a multi-proxy differential → a chained normalization → a per-layer differential
```

## The first confirming probe

```bash
# the card's first probe — a normal request then a stripped request
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/restricted" -d 'data'
#   a 401/403 — the normal request is gated
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/restricted" -d 'data' \
  -H 'Connection: keep-alive, X-Real-IP'
#   a 200 — the stripped request reached → the differential confirmed
```

## The falsifiers

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
a proxy that doesn't strip its own header → the hop-by-hop bypass fails
a proxy that strips a client-supplied header → the client-supplied
  bypass fails → the hop-by-hop bypass is the vector
a proxy that verifies the header it added → the client-supplied bypass
  fails → the hop-by-hop bypass is the vector
a non-header check → a different class
the proxy and the app normalize the same way → no confusion
a stored copy → a cache-poisoning
a desync → a request-smuggling
a session check → an auth-session
a host check → a host-header
a fetch → an ssrf
a read → a cors
```

## The class boundary

```text
a parser-differential   → a front-end and a back-end parse differently —
                        a header's trust, a path's normalization, a
                        client-supplied header.
a request-smuggling     → a front-end and a back-end parse the request
                        BOUNDARY differently — a desync.
a cache-poisoning       → a stored copy that serves YOUR input — a
                        key-mismatch — a store.
an auth-session         → a trust check reads a session / a token.
a host-header           → a Host-header injection — a forged host.
an ssrf                 → a server-side fetch — the app fetches a URL.
a cors                  → a cross-origin fetch — the app's bytes read.
```

## The verified card

```text
the NovaCore card — a Traefik hop-by-hop bypass → a cache-daemon strcpy
overflow → a DOM-clobber prototype-pollution → a polyglot exfil. the
first step is the parser-differential: the proxy strips its own
X-Real-IP → the app treats the request as local → the token_required
check bypassed.
```

## The budget

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```

## The corpus map — which module covers what

```text
detection-checklist          → the complete checklist — the proxy, the
                              trust check, the gated route
detection-deep               → the detection deep — the surface map
detection-index              → the detection index — the signal map
detection-surface            → the detection surface — the per-surface map
hop-by-hop                   → the hop-by-hop bypass — the Connection-strip
hop-by-hop-deep              → the hop-by-hop deep — the verified card's
                              mechanism
client-supplied              → the client-supplied bypass — the forged header
client-supplied-deep         → the client-supplied deep — the forged-header
                              surface
proxy-trust                  → the proxy-trust model — the trusted header
proxy-header                 → the proxy-header abuse — the header's reach
header-abuse                 → the header-abuse surface — the per-header map
header-dictionary            → the header dictionary — the proxy's headers
header-map                   → the header map — the per-proxy headers
normalization                → the path-normalization boundary — the
                              traversal/encoding/case differentials
path-normalization           → the path-normalization deep — the path map
protocol-and-vhost           → the protocol-and-vhost boundary — the
                              scheme/host differentials
structured-field-differentials → the structured-field differentials — the
                              Forwarded/Connection/Host parse differences
theory                       → the theory — the parse-mismatch model
theory-deep                  → the theory deep — the parse-mismatch model
                              exhaustively
workflow                     → the workflow — the detection→confirm→
                              readback sequence
workflow-deep                → the workflow deep — the per-surface sequence
field-manual                 → the field manual — the per-surface sequence
exploitation                 → the exploitation — the per-mechanism map
exploitation-playbook        → the exploitation playbook — the named plays
exploitation-shapes          → the exploitation shapes — the named attacks
multi-step-chains            → the multi-step chains — the chained attacks
case-studies                 → the case studies — the verified card
case-studies-deep            → the case studies deep — the verified card +
                              the canonical patterns
verified-chains              → the verified chains — the card's chain map
real-world-cases             → the real-world cases — the published patterns
payload-dictionary           → the payload dictionary — the probes
payload-dictionary-deep      → the payload dictionary deep — the probes
                              exhaustively
payload-variants             → the payload variants — the per-surface variants
payload-corpus               → the payload corpus — the categorized payloads
whitebox-hunt                → the whitebox hunt — the per-surface source map
evidence-rules               → the evidence rules — the proof standard
verification                 → the verification — the differential confirm
readback-oracles             → the readback oracles — the bypass's read
negative-results             → the negative results — the dead paths
common-mistakes              → the common mistakes — the traps
common-questions             → the common questions — the FAQ
class-boundary               → the class boundary — the parse-vs-store split
class-boundary-deep          → the class boundary deep — the neighbor map
boundary-conditions          → the boundary conditions — the falsifiers
evasion                      → the evasion — the per-proxy WAF bypass
evasion-and-waf              → the evasion and WAF — the per-proxy bypass
troubleshoot                 → the troubleshoot — the failures
troubleshoot-deep            → the troubleshoot deep — the failures
                              exhaustively
framework-matrix             → the framework matrix — the per-proxy map
framework-matrix-deep        → the framework matrix deep — the per-proxy
                              map exhaustively
frameworks-deep              → the frameworks deep — the per-framework map
proxy-behavior               → the proxy behavior — the per-proxy map
proxy-behavior-deep          → the proxy behavior deep — the per-proxy map
                              exhaustively
multi-proxy                  → the multi-proxy chain — the chained
                              normalization
multi-proxy-deep             → the multi-proxy deep — the chained
                              normalization exhaustively
extended-corpus              → the extended corpus — the long tail
glossary                     → the glossary — the vocabulary
summary                      → this file — the corpus in one page
```
