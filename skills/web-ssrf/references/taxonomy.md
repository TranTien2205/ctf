# Taxonomy — the SSRF shape-tree

The classification-frame — which SSRF you have determines the
proof-standard, the channel, and the chain. Name the shape first.

---

## 1. By read-channel — what the response carries

```text
FULL-READ     the fetched-content returns — the flag-page echoes —
              the richest — the fetch IS the read
ERROR-READ    the content returns inside an ERROR — "fetch failed:
              <bytes>" — the error-echo — the red-island shape
STATUS-READ   only the status differs — 200 vs 500 — a binary
              oracle — the answer-in-a-code
TIMING-READ   only the elapsed differs — the slow-oracle — the
              timing-channel — noisy but real
OOB-ONLY      nothing returns — the callback is the only channel —
              blind — the state-write-escalation is the chain
```

## 2. By fetch-context — who fetches

```text
SERVER-FETCH   the web-request itself fetches — synchronous — the
               classic — the response carries the result
WORKER-FETCH   a background worker — the deferred — the results-
               page channel — the worker's network-position
BOT-FETCH      a headless-browser — the bot-visit — browser-context
               — the xss-adjacent class — the payload is html+js
RENDERER-FETCH a screenshot/pdf-renderer — the render-output is
               the channel — the image/pdf carries the flag
AGENT-FETCH    a scheduled/cron job — the periodic — the schedule
               matters
```

## 3. By scope — what's reachable

```text
LOOPBACK      only the app's own host — 127.0.0.1 — the loopback-
              admin is the target
INTERNAL-NET  the subnet — sibling-services — the sweep — the
              internal-map
METADATA      the cloud-metadata — 169.254.169.254 — the link-local
              — often reachable when egress is blocked
EGRESS        the public-internet — your-callback — the basic —
              rarely the flag
FILESYSTEM    file:// — the read-path — the file-map
SOCKETS       unix-sockets — the unix-aware fetcher — docker.sock
ANY-SCHEME    gopher/dict/etc — the raw-TCP reach — the service-
              protocols
```

## 4. By check-type — the filter-shape

```text
NO-CHECK        anything fetches — the cleanest — the rare-case
STRING-CHECK    contains/starts-with/ends-with — the string-family
HOST-CHECK      the parsed-host — the parser-differential
IP-BLACKLIST    resolve→check → the rebind/ip-encoding family
PORT-CHECK      allowed-ports — the port-forms
SCHEME-CHECK    allowed-schemes — the scheme-family
FETCH-TIME      resolved-ip is what's dialled — rebind-or-nothing
PER-HOP         re-validates redirects — redirect-family dead
WHITELIST       the allowed-domain — the whitelist-shapes family
```

## 5. By exploit-chain — what it gives

```text
read-file         file:// — the filesystem
read-internal     http://internal — the internal-routes
read-metadata     the cloud-metadata — the creds+user-data
read-store        redis/es/consul/etc — the flag-key
write-store       redis-SET, consul-kv — the write-side
write-file        the webroot-write — gopher→redis→save
exec-code         fastcgi-auto_prepend, expect://, the console
                  RCE-features, container-spawn
request-compose   crlf-injection — the request-injection — desync
send-request      the header-controlled gopher-http — the auth-fwd
```

## 6. The shape-tree — the decision-tree

```text
is the param fetched at all?
  no → not-ssrf — the param is display/template/other — different class
  yes → is the fetch synchronous?
    no → deferred — the results-channel is the oracle — webhook-deferred
    yes → does the response echo?
      yes (body) → full-read — the internal-content IS the flag-path
      yes (error) → error-read — the error-body carries it
      no → which oracle?
        status → binary-oracle
        timing → timing-oracle
        neither → blind → the state-write-escalation
→ then the check-shape → the bypass-family → the internal-target
```

## 7. The class-boundaries — what this is NOT

```text
- "the url reaches a template" → SSTI — the render-context —
  web-ssti — the url is template-input not a fetch-target
- "the url is a file-path" → LFI — the path-param — file-read-
  primitives — the url is a path not a fetch
- "the url is a command-arg" → command-injection — the url is an
  argv — the fetcher is invoked as a process
- "the url is a redirect-target" → open-redirect — the redirect
  goes to the CLIENT — the server doesn't fetch — different class
- "the url is in a header" → host-header — the trusted-header —
  web-host-header — the server-side header-trust
- "the url is a browser-visit" → bot-visit → xss-adjacent — the
  browser-context — the client-side
- "the %0d%0a splits the request" → request-smuggling — the
  request-composition — the boundary the weather-app crossed
- "the url is a path the app JOINs" → path-traversal/LFI — the
  joiner-normalization
```

The boundary-question: who FETCHES — server → SSRF; browser → bot-
visit/xss; the url is a path → LFI; the url splits the request →
request-smuggling.

## 8. The evidence-level mapping — what each level means

```text
SURFACE:   the param exists / the url renders / the form is there —
           the classifier's hint — never a confirm
CLASS:     the server dialled — the fetch-happened — refused-error
           or callback — the class-evidence — the ssrf EXISTS
IMPACT:    internal-content read — the flag-path's bytes — the
           metadata — the internal-route — the flag-level claim —
           the only level that "solves"
```

The evidence-levels gate the ledger — `class` confirms the class;
`impact` confirms the flag-reach — the post-probe verdict maps
to them.

## 9. The probe-budget by shape

```text
each shape has its own mechanism-class — the 5-probe rule applies
PER mechanism:
  the param-discovery set — one class — the url-field-family —
    try the vocabulary, stop when one fires — don't try every
    synonym forever
  the scheme-set — one class — the scheme-table — 5 schemes-then-
    stop — the scheme-list is capped by the fetcher
  the ip-encoding set — one class — the encoding-family — 5 then
    switch-mechanism (rebind/redirect)
  the internal-service set — one fingerprint per open-port —
    cheap — the port-count isn't the probe-count
  the bypass-family — one class per check-type — 5 then switch
  the escalations — different classes — gopher-chain, file-chain,
    meta-chain, socket-chain
```

## 10. The class-vs-subclass — the ctf-web-* subfamily

```text
the web-ssrf class — the ctf-web-ssrf subagent-brief — the
ssrf-family — the sub-shapes are the same class — the mechanism
is "server fetches attacker-controlled url" — the sub-shapes are
the CHANNEL+CHECK+REACH not different classes — the sweep assigns
them to the ssrf-brief
```
