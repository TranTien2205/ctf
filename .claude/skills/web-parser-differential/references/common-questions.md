# Common questions — the FAQ, exhaustively

The questions that come up — each with its answer.

---

## Q1 — what is a parser differential

```text
a front-end (a proxy, a gateway, a WAF) parses the request one way; a
back-end (the app) parses it another — the same bytes, two different
interpretations — the disagreement is the vulnerability.
```

## Q2 — how is it different from request smuggling

```text
a parser-differential   → a front-end and a back-end parse differently —
                        a header's trust, a path's normalization, a
                        client-supplied header.
a request-smuggling     → a front-end and a back-end parse the request
                        BOUNDARY differently — a content-length vs a
                        transfer-encoding — a desync.
the boundary            → a parse-vs-desync split.
```

## Q3 — how is it different from cache poisoning

```text
a parser-differential   → a front-end and a back-end parse differently —
                        a header's trust, a path's normalization, a
                        client-supplied header.
a cache-poisoning       → a stored copy that serves YOUR input — a
                        key-mismatch — a store.
the boundary            → a parse-vs-store split.
```

## Q4 — what is the hop-by-hop bypass

```text
a proxy strips the headers it names in Connection — naming the proxy's
own header in Connection strips it — the app sees a request without
the trusted header — a missing-header fallback treats it as local —
the trust check bypassed.
```

## Q5 — what is the client-supplied bypass

```text
a client-supplied proxy header → the app trusts it → the app doesn't
verify the proxy added it → the client-supplied header IS trusted →
a forged local IP → a local request → the trust check bypassed.
```

## Q6 — which headers does a proxy add

```text
nginx      → X-Real-IP, X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
Traefik    → X-Real-IP, X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
Apache     → X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
HAProxy    → X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
Cloudflare → CF-Connecting-IP, CF-Ray, CF-Visitor
CloudFront → X-Amzn-Trace-Id, X-Forwarded-For
Akamai     → True-Client-IP, Akamai-Origin-Hop
```

## Q7 — which headers does a proxy strip

```text
a proxy strips a header named in Connection — the hop-by-hop bypass —
the strip is the mechanism — the proxy's own header (the one the app
trusts) is the strip's target — the app's missing-header fallback is
the bypass's reach.
```

## Q8 — which headers does a proxy pass

```text
a proxy passes a client-supplied proxy header unless the config strips
it — the client-supplied bypass is the vector — the app's trust check
reads the client-supplied header's value.
```

## Q9 — what is the missing-header fallback

```text
a missing proxy header → the app treats the request as local or skips
the trust check → a local request bypasses the authentication or the
restriction.
```

## Q10 — what is the trust-check's input

```text
the app's trust check reads the proxy's header — a missing header hits
a fallback — a client-supplied header is trusted — the app doesn't
verify the proxy actually added it.
```

## Q11 — what is the normalization differential

```text
a path the front-end normalizes one way and the back-end another — a
/static/../admin the proxy normalizes to /admin and the app routes to
/admin — a normalization differential — the front-end's check reads a
different path than the app's.
```

## Q12 — which checks does the differential bypass

```text
the differential bypasses a check the proxy's header gates — an
authenticated-only route, an internal route, a restricted endpoint —
the app's trust check reads the missing or client-supplied header's
effect.
```

## Q13 — when does the differential fail

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
```

## Q14 — what is the verified card's mechanism

```text
the NovaCore card — a Traefik hop-by-hop bypass → a cache-daemon strcpy
overflow → a DOM-clobber prototype-pollution → a polyglot exfil. the
first step is the parser-differential: the proxy strips its own
X-Real-IP → the app treats the request as local → the token_required
check bypassed.
```

## Q15 — what is the budget

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
