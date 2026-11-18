# Error analysis — the diagnostic strings and what they mean

The fetcher's error-message tells you WHERE it failed — each
stage's error is a different signal. Read them in order.

---

## 1. The failure-stage ladder

```text
the fetch has stages — the error names the stage it died at:

PARSE      → "invalid url", "malformed", "no host", "unsupported
             scheme" — the url-parser rejected — the SCHEME or the
             SYNTAX failed — the payload's shape is wrong — not a
             network issue — try a different scheme/form

FILTER     → "blocked", "forbidden", "not allowed", "denied",
             "ssrf protection", "blacklist", "disallowed host",
             "must be http(s)", "domain not allowed" — the CHECK
             ran and rejected — the validator exists — WHICH check
             is the bypass-question — see url-parsing.md

DNS        → "name or service not known", "temporary failure in
             name resolution", "no such host", "could not resolve",
             "nodename nor servname" — the RESOLUTION failed — the
             name didn't resolve — either the name is wrong OR the
             egress-dns is dead — the canary-host should resolve —
             if even the canary-host fails → egress-dns-dead —
             internal-only mode

TCP        → "connection refused" (the port's closed — the host
             answered the SYN with RST — the HOST is UP), 
             "connection timed out" (no reply — filtered/host-down),
             "no route to host", "network unreachable",
             "connection reset by peer" — the TRANSPORT failed —
             each differs: refused=host-up-port-closed;
             timeout=filtered/dead; reset=the-service-dropped

TLS        → "certificate verify failed", "ssl error", "handshake
             failure" — the TLS-layer failed — the host reached —
             the cert/name issue — http-fallback may work

HTTP       → "404", "500", "redirect loop", "too many redirects" —
             the http-layer answered — the SERVICE responded — the
             flag-page that 404s is still a live-service — the
             http-error is the most useful — the service EXISTS

APP        → "invalid response", "can't parse", "not an image" —
             the app got the response but rejected it — the fetch
             WORKED — the content-check is the next hurdle —
             content-type-validation — the polyglot path
```

## 2. The refused-vs-timeout diagnostic

```text
"Connection refused"  → SYN reached the host, got RST → the HOST
   is alive, the PORT is closed → internal-host confirmed, port
   is wrong → sweep other ports — the host IS there
"Connection timed out" → SYN got nothing → filtered/dropped/host-
   down → could be egress-firewall OR dead-host — ambiguous —
   probe a known-open port on the same host to disambiguate —
   if port-80 also times out → whole-host unreachable → dead-
   host or hard-egress-block
"No route to host"      → icmp-unreachable — the subnet is dead —
   the host-ip is in a range nothing routes to — the ip is wrong
"Network unreachable"   → same family — the route doesn't exist —
   the ip-range is wrong
```

The KEY diagnostic: refused vs timeout. Refused = "the host is
real, this port is wrong". Timeout = "nothing answered" — could
be the firewall — probe another port on the SAME host to tell
them apart.

## 3. The error-shape per-fetcher

```text
python-requests:  "Failed to establish a new connection: [Errno
   111] Connection refused" / "Read timed out" / "Name or service
   not known" — the urllib3/requests strings
urllib:           "urlopen error [Errno 111] Connection refused" /
   "[Errno -2] Name or service not known"
curl/libcurl:     "Failed to connect to x port N: Connection
   refused" / "Couldn't resolve host" / "URL using bad/illegal
   format" / "Protocol x not supported" — the PROTOCOL string is
   the scheme-unsupported signal — "Protocol 'gopher' not
   supported" → the scheme died at the scheme-list
java:             "java.net.ConnectException: Connection refused" /
   "java.net.UnknownHostException: x" / "MalformedURLException" /
   "no protocol: x" — the java-exception-names — "no protocol" →
   the scheme wasn't registered
php file_get_contents: "failed to open stream: Connection refused"
   / "php_network_getaddresses: getaddrinfo failed" / "Unable to
   find the wrapper x" — "find the wrapper" → the scheme-wrapper
   isn't registered → the scheme-list again
ruby open-uri:    "Errno::ECONNREFUSED" / "SocketError: getaddrinfo"
node:             "ECONNREFUSED" / "ENOTFOUND" / "ETIMEDOUT" /
   "Parse Error" / "Invalid URL" — the node-errno-names
go:               "dial tcp: connect: connection refused" /
   "no such host" / "unsupported protocol scheme" — go's
   scheme-error
dotnet:           "SocketException" / "WebException" / 
   "The remote name could not be resolved"
```

## 4. The scheme-unsupported strings — the scheme-list boundary

```text
"Protocol 'gopher' not supported or disabled in libcurl"
   → the libcurl build lacks gopher → the gopher-family is dead →
     pivot to http-internal-services
"Unable to find the wrapper "gopher""
   → php-wrapper-missing → the php-wrapper-set is limited → the
     stream-schemes available: http/https/ftp/file/php/data — the
     php://filter family still works
"unknown url type: gopher"
   → python-urllib's scheme-error → urllib is http/ftp/file —
     file:// still works
"no protocol: gopher"
   → java's missing-handler → java's set is http/ftp/file/jar/
     netdoc
"Invalid URL scheme"
   → generic — the app validated the scheme against its own list —
     which-schemes-are-allowed is the next probe — try the whole
     scheme-table
```

## 5. The filter-error vocabulary — which check is running

```text
"Invalid URL" / "Malformed"      → the parser rejected — syntax not
                                   security — the form is wrong
"Domain not allowed" / "not in allowlist" / "must be a valid host"
   → a WHITELIST — the bypass is the allowed-domain tricks — the
     @/#/?/suffix/parser-diff family
"Internal IPs not allowed" / "private address" / "blocked range"
   → an IP-BLACKLIST — the bypass is the ip-encoding/dns-rebind —
     the resolution-vs-string question
"Only http(s) allowed" / "scheme not allowed"
   → a SCHEME-CHECK — the scheme-table — which non-http pass?
"Redirect target not allowed" / "redirect blocked"
   → PER-HOP-VALIDATION — the redirect-chain is dead — the app
     re-checks every hop — pivot to other families
"URL resolves to a private address"
   → RESOLUTION-CHECK — the app resolved and saw internal → the
     rebind is the gap — or the input must be a public-name
"Suspicious URL" / "blocked by security policy"
   → heuristic-filter — pattern-based — the encoding-family beats
     it usually
```

## 6. The http-error ladder — when the service answers

```text
the internal-service ANSWERED — the fetch worked — the http-status
  is the next diagnostic:
200         → the route exists and served — the flag-page?
301/302     → redirect — the response-headers carry the location —
              the fetcher may have followed — or the redirect-target
              is the next url
401/403     → auth-required — the internal-route exists but wants
              auth — the header-forward trick? or the loopback-
              check the SSRF bypasses — the XFF-injection —
              or just wrong-path
404         → the service exists, the route doesn't — path-guess —
              /flag /admin /api /internal — the route-wordlist
405         → method-mismatch — POST vs GET
500         → the route exists and errored — a real-error — the
              error-BODY may leak internals — read it
502/503     → backend-down — the proxy speaks, the upstream died —
              the proxy IS reachable
timeout     → the route hangs — a slow-endpoint — or a read-block
```

## 7. The response-body tells — even on errors

```text
the 404-body → the framework-page — "Cannot GET /x" = express —
   "Not Found" = flask — "404 Not Found" = nginx — the framework-
   fingerprint — narrows the stack
the 500-body → the stack-trace — the file-paths, the framework,
   the internal-structure — errors are the map — read every one
the redirect-location → where it wanted to go — the real-route
the timeout-differential → the slow-route exists — hang vs instant
```

## 8. The false-signals — what errors don't mean

```text
"refused" on a KNOWN-good target → transient — retry once — don't
   build a theory on one refused
silence → could be egress-block — not proof no-fetch — the
   internal-probe decides
"404" on the callback-host → your listener-path is wrong — not a
   fetch-failure
generic "error" → the app swallows the real error → less info —
   the timing+status become the oracles
"blocked" on a PUBLIC url → over-strict filter or no-egress — the
   canary decides which
```

## 9. The error-to-action table

| Error | Stage | Next move |
|---|---|---|
| `malformed`/`invalid url` | parse | fix the url-shape — different scheme |
| `not allowed`/`blocked` | filter | url-parsing.md — the bypass-family |
| `no such host` | dns | the name's wrong OR egress-dns dead |
| `connection refused` | tcp | host-alive-port-closed — sweep ports |
| `timeout` | tcp | filtered/dead — disambiguate via known-port |
| `no route to host` | tcp | wrong-subnet — the ip-range is wrong |
| `cert verify failed` | tls | http-fallback or --insecure-fetcher |
| `404` | http | route-guess — the internal-routes |
| `401`/`403` | http | auth-required — header-injection/XFF |
| `protocol not supported` | scheme | the scheme-list — try http-only chains |
| `no protocol: x` | scheme | java — the jar/netdoc set |
| `find the wrapper x` | scheme | php — the php-wrapper family |
| `redirect blocked` | filter | per-hop-validation — redirect-family dead |
| `resolves to private` | resolution | the rebind-gap |
