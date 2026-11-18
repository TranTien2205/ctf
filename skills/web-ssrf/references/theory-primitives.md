# Theory primitives — what SSRF actually IS

The conceptual frame — the primitives the whole skill composes —
the "why" behind the checklists.

---

## 1. The primitive — a trusted-position request

```text
SSRF = the server makes a request the requester controls — the
       request originates from a NETWORK-POSITION you couldn't
       reach directly — the server's position is the privilege —
       the fetch carries the server's reach

the two primitives:
  a) position — the server's network-location — loopback, internal-
     net, cloud-metadata, sibling-services — the fetch reaches
     what the position reaches
  b) trust — the server's identity — the request carries the
     server's source-ip, sometimes its auth/cookies — the internal-
     services that trust the server's ip
```

## 2. The three axes — the parameter-space

```text
TARGET   — where the fetch goes — the host/port/scheme — the
           url is the target-selector — the whole bypass-surface
           is about controlling the target past a check
CHANNEL  — what comes back — body/error/status/timing/oob — the
           read-channel — determines what the fetch can tell you
COMPOSITION — what the request IS — GET, headers, body, method —
           the request-shape — a bare-GET is a weak-fetch; a fully-
           composed request is the stronger primitive — crlf/gopher
           give you composition
```

A bare-GET fetch is "the server retrieves a page"; a composed-
request is "the server says what you say" — the composition-
axis is where ssrf becomes request-smuggling.

## 3. The privilege-boundary — what makes it a vulnerability

```text
the fetch crosses a trust-boundary — the server's position has
privileges the requester lacks:
  - loopback-trust — the internal-routes check "is it 127.0.0.1" —
    the fetch IS 127.0.0.1 — the check's answer becomes yes
  - internal-net-trust — the internal-services trust the vpc-net —
    the fetch is inside the perimeter — the services answer it
  - metadata-trust — the metadata-svc trusts the instance — the
    fetch is the instance — the creds come back
  - the egress — the fetcher's egress-ip is a position — you reach
    a third-party AS the server — the "the server visited my-site"
    is the weak-form
the bug is the BOUNDARY-CROSS — the untrusted-input drives a
trusted-position-request — the position is the privilege
```

## 4. The mechanism-layer — where the bug lives

```text
the layers — the bug is in one of:
  1. NO-CONTROL — the url is trusted-input → the fetch — the pure
     ssrf — no filter at all — the happy-path
  2. STRING-CHECK — a filter on the url-string — the bypass is the
     string-family — the check sees the string not the dial
  3. PARSE-CHECK — the filter parses the url — the check reads the
     host-field — the two-parser differential is the bypass
  4. RESOLVE-CHECK — the filter resolves the name — the rebind is
     the bypass — the resolve-twice gap
  5. FETCH-TIME — the resolved-ip is dialled — nothing between —
     the airtight — rebind-or-nothing
  6. PER-HOP — the redirect-hops re-validated — the redirect dies —
     the other mechanisms remain
each layer has its bypass — the layers compose — a real app often
  runs several — the bypass needs the combination
```

## 5. The read-channel hierarchy — richest to poorest

```text
1. full-body echo        — the response IS the content — the read
2. error-echo            — the error carries the content — the
                            red-island shape
3. status/length-diff    — the binary-oracle — per-probe one-bit
4. timing-diff           — the timing-oracle — noisy-one-bit
5. oob-callback          — reachability-only — the canary —
                            "it fetched" not "what it got"
6. state-write           — the write-side — the shared-store —
                            the write-then-read — the blind-shape's
                            answer
7. nothing               — the fetch is unobservable — the
                            dead-channel — escalate
```

## 6. The scope-escalation — where the reach grows

```text
external-you → the server's loopback → the internal-net → the
sibling-services → the metadata → the filesystem → the control-
planes → the execution — the reach-ladder:

  the fetch is one hop — the reach is the position —
  - loopback → the admin-route
  - internal → the data-stores
  - metadata → the creds
  - file:// → the fs
  - gopher → the raw-protocols → the write/RCE
  - the socket → the control-plane → the container-escape
  - the request-composition → the request-injection → desync
each ring is a wider primitive — the chain climbs the rings
```

## 7. The composition-hierarchy — the request-shapes

```text
1. url-only          — the fetch is the app's — GET no-headers —
                       the read is the only move
2. url+path          — you control the path — the route-selector
3. url+host          — the host — the reach
4. url+headers       — via crlf-injection or gopher — the header-
                       control — XFF/Auth/Host — the trust-headers
5. method+body       — POST+body — the write-shape — the
                       internal-API POSTs — gopher/crlf
6. full-composition  — the whole request — the second-request —
                       the desync — request-smuggling
```

## 8. The class-boundary — the mechanism-line

```text
the class-line is "the server fetched a target you chose":
  - a url-param that fetches → ssrf
  - a url-param the browser fetches → bot-visit / xss-adjacent
  - a url-param that becomes a path → lfi/file-read
  - a url-param that becomes a command-arg → command-injection
  - a url-param that splits the request → request-smuggling
  - a url-param the template renders → ssti
  - a url-param that's just stored → stored-xss surface
the mechanism decides the class — the surface (a url-param) is
the same for all — the FETCH is the discriminator
```

## 9. The falsifier-frame — what the class needs

```text
the class dies when:
  - the param is never fetched — the display/template shape
  - the fetcher is fixed-target — the input is a suffix/param not
    the url — param-injection not ssrf
  - the fetch is browser-side — the client-fetch — different class
  - the check is airtight AND no rebind/redirect/diff exists —
    the reach dies — the class exists but unreachable-impact
```

## 10. The "one request" mental-model — the probe-frame

```text
every probe answers one question:
  "what does this url-fetch do when I give it X?"
  - dial-oracle → does it dial?
  - read-oracle → what does it echo?
  - check-oracle → what does the check reject?
  - reach-oracle → what does it reach?
  - fingerprint → what service?
the probe is the question — the response is the answer — the
channel determines which questions have answers
```
